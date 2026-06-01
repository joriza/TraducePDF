"""
Reconstructor de PDFs.

Este módulo se encarga de reconstruir un PDF con el texto traducido,
manteniendo el formato visual original y las imágenes.
"""

import io
from typing import List, Optional
import fitz  # PyMuPDF
from loguru import logger

from pdf_extractor import PageData, ImageBlock
from text_processor import PageTranslation, TextBlockWithTranslation


class PDFRebuilder:
    """Reconstructor de PDFs traducidos."""

    def __init__(self, original_pdf_path: str):
        """
        Inicializa el reconstructor.

        Args:
            original_pdf_path: Ruta al PDF original.
        """
        self.original_pdf_path = original_pdf_path
        self.original_doc = None
        self.new_doc = None

    def open_original(self):
        """Abre el PDF original."""
        try:
            self.original_doc = fitz.open(self.original_pdf_path)
            logger.info(f"PDF original abierto: {self.original_pdf_path}")
        except Exception as e:
            logger.error(f"Error al abrir el PDF original: {e}")
            raise

    def close_original(self):
        """Cierra el PDF original."""
        if self.original_doc:
            self.original_doc.close()
            self.original_doc = None

    def create_new(self):
        """Crea un nuevo documento PDF vacío."""
        self.new_doc = fitz.open()
        logger.info("Nuevo documento PDF creado")

    def close_new(self):
        """Cierra el nuevo documento PDF."""
        if self.new_doc:
            self.new_doc.close()
            self.new_doc = None

    def __enter__(self):
        """Context manager entry."""
        self.open_original()
        self.create_new()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_original()
        self.close_new()

    def rebuild_page(
        self, page_translation: PageTranslation, original_page_data: PageData
    ):
        """
        Reconstruye una página con el texto traducido.

        Args:
            page_translation: Traducción de la página.
            original_page_data: Datos originales de la página.
        """
        if self.original_doc is None or self.new_doc is None:
            raise RuntimeError("Los documentos no están abiertos")

        # Obtener la página original
        original_page = self.original_doc[page_translation.page_num]

        # Crear una nueva página con las mismas dimensiones
        new_page = self.new_doc.new_page(
            width=original_page_data.width, height=original_page_data.height
        )

        # Copiar el fondo de la página original
        self._copy_page_background(original_page, new_page)

        # Insertar las imágenes
        for image_block in original_page_data.images:
            self._insert_image(new_page, image_block)

        # Insertar el texto traducido
        self._insert_translated_text(new_page, page_translation)

        logger.debug(f"Página {page_translation.page_num + 1} reconstruida")

    def rebuild_all(
        self,
        page_translations: List[PageTranslation],
        original_pages_data: List[PageData],
    ):
        """
        Reconstruye todas las páginas del PDF.

        Args:
            page_translations: Lista de traducciones de página.
            original_pages_data: Lista de datos originales de página.
        """
        if len(page_translations) != len(original_pages_data):
            raise ValueError(
                f"Número de traducciones ({len(page_translations)}) "
                f"no coincide con número de páginas ({len(original_pages_data)})"
            )

        for page_translation, original_data in zip(
            page_translations, original_pages_data
        ):
            self.rebuild_page(page_translation, original_data)

        logger.info(f"Reconstruidas {len(page_translations)} páginas")

    def _copy_page_background(self, source_page, dest_page):
        """
        Copia el fondo de una página a otra.

        Args:
            source_page: Página de origen.
            dest_page: Página de destino.
        """
        # Copiar el rectángulo de la página
        dest_page.set_cropbox(source_page.rect)

        # Copiar dibujos y formas (si los hay)
        # Esto es más complejo y puede requerir procesamiento adicional
        # Por ahora, dejamos la página en blanco con el color de fondo

    def _insert_image(self, page, image_block: ImageBlock):
        """
        Inserta una imagen en la página.

        Args:
            page: Página donde insertar.
            image_block: Bloque de imagen a insertar.
        """
        try:
            # Crear un rectángulo para la imagen
            rect = fitz.Rect(
                image_block.x0, image_block.y0, image_block.x1, image_block.y1
            )

            # Insertar la imagen
            page.insert_image(
                rect, stream=io.BytesIO(image_block.image_bytes), keep_proportion=True
            )

            logger.debug(
                f"Imagen insertada en página {image_block.page_num + 1} "
                f"en ({image_block.x0:.1f}, {image_block.y0:.1f})"
            )
        except Exception as e:
            logger.warning(
                f"Error al insertar imagen en página {image_block.page_num + 1}: {e}"
            )

    def _insert_translated_text(self, page, page_translation: PageTranslation):
        """
        Inserta el texto traducido en la página.

        Args:
            page: Página donde insertar.
            page_translation: Traducción de la página.
        """
        for translated_block in page_translation.translated_blocks:
            original = translated_block.original

            # Determinar el texto a usar (traducido o original)
            text = (
                translated_block.translated_text
                if translated_block.translation_success
                else original.text
            )

            # Crear rectángulo para el texto
            rect = fitz.Rect(original.x0, original.y0, original.x1, original.y1)

            # Determinar el color
            color = original.color

            # Determinar flags de fuente
            font_flags = 0
            if original.is_bold:
                font_flags |= fitz.TEXT_FONT_BOLD
            if original.is_italic:
                font_flags |= fitz.TEXT_FONT_ITALIC

            # Intentar usar la misma fuente, si no está disponible usar una estándar
            font_name = self._get_available_font(original.font)

            try:
                # Insertar el texto usando TextWriter con la API correcta de PyMuPDF
                tw = fitz.TextWriter(page.rect)

                # Configurar el punto de inserción
                point = fitz.Point(original.x0, original.y0 + original.font_size)

                # Añadir el texto con la API correcta
                tw.append(point, text, fontsize=int(original.font_size))

                # Escribir en la página
                tw.write_text(page)

            except Exception as e:
                logger.warning(
                    f"Error al insertar texto en página {page_translation.page_num + 1}: {e}"
                )
                # Intento alternativo con insert_text simple
                try:
                    page.insert_text(
                        fitz.Point(original.x0, original.y0 + original.font_size),
                        text,
                        fontsize=original.font_size,
                        fontname=font_name,
                        color=color,
                    )
                except Exception as e2:
                    logger.error(f"Error en intento alternativo: {e2}")

    def _get_available_font(self, original_font: str) -> str:
        """
        Retorna una fuente disponible similar a la original.

        Args:
            original_font: Nombre de la fuente original.

        Returns:
            Nombre de una fuente disponible.
        """
        # Lista de fuentes disponibles en PyMuPDF
        available_fonts = [
            "helv",  # Helvetica
            "tiro",  # Times Roman
            "cour",  # Courier
            "arial",
            "times-roman",
            "times-new-roman",
        ]

        original_lower = original_font.lower()

        # Intentar encontrar una fuente similar
        if "helvetica" in original_lower or "arial" in original_lower:
            return "helv"
        elif "times" in original_lower:
            return "tiro"
        elif "courier" in original_lower:
            return "cour"
        else:
            # Por defecto usar Helvetica
            return "helv"

    def save(self, output_path: str):
        """
        Guarda el PDF reconstruido.

        Args:
            output_path: Ruta donde guardar el PDF.
        """
        if self.new_doc is None:
            raise RuntimeError("No hay documento nuevo para guardar")

        try:
            # Guardar con optimización
            self.new_doc.save(
                output_path,
                garbage=4,  # Limpiar objetos no usados
                deflate=True,  # Comprimir
            )
            logger.info(f"PDF guardado en: {output_path}")
        except Exception as e:
            logger.error(f"Error al guardar el PDF: {e}")
            raise

    def get_page_count(self) -> int:
        """
        Retorna el número de páginas del nuevo documento.

        Returns:
            Número de páginas.
        """
        if self.new_doc is None:
            return 0
        return len(self.new_doc)
