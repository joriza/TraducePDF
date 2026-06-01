"""
Extractor de PDFs.

Este módulo se encarga de extraer texto e imágenes de archivos PDF
manteniendo la información de formato, posición y estilo.
"""

import io
from typing import List, Dict, Any, Tuple
from dataclasses import dataclass, field
from PIL import Image
import fitz  # PyMuPDF
from loguru import logger


@dataclass
class TextBlock:
    """Representa un bloque de texto con su información de formato."""

    text: str
    page_num: int
    x0: float
    y0: float
    x1: float
    y1: float
    font: str = ""
    font_size: float = 0.0
    color: Tuple[int, int, int] = (0, 0, 0)
    is_bold: bool = False
    is_italic: bool = False

    @property
    def width(self) -> float:
        """Ancho del bloque de texto."""
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        """Alto del bloque de texto."""
        return self.y1 - self.y0

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el bloque a un diccionario."""
        return {
            "text": self.text,
            "page_num": self.page_num,
            "x0": self.x0,
            "y0": self.y0,
            "x1": self.x1,
            "y1": self.y1,
            "font": self.font,
            "font_size": self.font_size,
            "color": self.color,
            "is_bold": self.is_bold,
            "is_italic": self.is_italic,
        }


@dataclass
class ImageBlock:
    """Representa una imagen extraída del PDF."""

    image: Image.Image
    page_num: int
    x0: float
    y0: float
    x1: float
    y1: float
    image_bytes: bytes = field(default_factory=bytes)

    @property
    def width(self) -> float:
        """Ancho de la imagen."""
        return self.x1 - self.x0

    @property
    def height(self) -> float:
        """Alto de la imagen."""
        return self.y1 - self.y0

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el bloque a un diccionario (sin la imagen)."""
        return {
            "page_num": self.page_num,
            "x0": self.x0,
            "y0": self.y0,
            "x1": self.x1,
            "y1": self.y1,
            "width": self.width,
            "height": self.height,
        }


@dataclass
class PageData:
    """Datos extraídos de una página del PDF."""

    page_num: int
    width: float
    height: float
    text_blocks: List[TextBlock] = field(default_factory=list)
    images: List[ImageBlock] = field(default_factory=list)

    @property
    def text(self) -> str:
        """Texto completo de la página."""
        return "\n".join(block.text for block in self.text_blocks)


class PDFExtractor:
    """Extractor de contenido de PDFs."""

    def __init__(self, pdf_path: str):
        """
        Inicializa el extractor.

        Args:
            pdf_path: Ruta al archivo PDF.
        """
        self.pdf_path = pdf_path
        self.doc = None
        self.pages_data: List[PageData] = []

    def open(self):
        """Abre el archivo PDF."""
        try:
            self.doc = fitz.open(self.pdf_path)
            logger.info(f"PDF abierto: {self.pdf_path}")
            logger.info(f"Número de páginas: {len(self.doc)}")
        except Exception as e:
            logger.error(f"Error al abrir el PDF: {e}")
            raise

    def close(self):
        """Cierra el archivo PDF."""
        if self.doc:
            self.doc.close()
            self.doc = None
            logger.info("PDF cerrado")

    def __enter__(self):
        """Context manager entry."""
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def extract_page(self, page_num: int) -> PageData:
        """
        Extrae el contenido de una página específica.

        Args:
            page_num: Número de página (0-indexed).

        Returns:
            PageData con el contenido extraído.
        """
        if self.doc is None:
            raise RuntimeError("El PDF no está abierto. Llama a open() primero.")

        page = self.doc[page_num]
        rect = page.rect

        page_data = PageData(
            page_num=page_num,
            width=rect.width,
            height=rect.height,
        )

        # Extraer bloques de texto
        text_blocks = self._extract_text_blocks(page, page_num)
        page_data.text_blocks = text_blocks

        # Extraer imágenes
        images = self._extract_images(page, page_num)
        page_data.images = images

        logger.debug(f"Página {page_num + 1}: {len(text_blocks)} bloques de texto, {len(images)} imágenes")

        return page_data

    def extract_all(self) -> List[PageData]:
        """
        Extrae el contenido de todas las páginas.

        Returns:
            Lista de PageData con el contenido de cada página.
        """
        if self.doc is None:
            raise RuntimeError("El PDF no está abierto. Llama a open() primero.")

        self.pages_data = []

        for page_num in range(len(self.doc)):
            page_data = self.extract_page(page_num)
            self.pages_data.append(page_data)

        logger.info(f"Extraídas {len(self.pages_data)} páginas")

        return self.pages_data

    def _extract_text_blocks(self, page, page_num: int) -> List[TextBlock]:
        """
        Extrae los bloques de texto de una página.

        Args:
            page: Página de PyMuPDF.
            page_num: Número de página.

        Returns:
            Lista de TextBlock.
        """
        text_blocks = []

        # Obtener bloques de texto con información detallada
        blocks = page.get_text("dict", sort=True)["blocks"]

        for block in blocks:
            if block["type"] == 0:  # Bloque de texto
                for line in block.get("lines", []):
                    for span in line.get("spans", []):
                        text = span["text"].strip()
                        if text:  # Solo agregar si hay texto
                            # Obtener información de fuente
                            font = span.get("font", "")
                            font_size = span.get("size", 0.0)
                            color = span.get("color", (0, 0, 0))

                            # Determinar si es negrita o cursiva
                            is_bold = "bold" in font.lower()
                            is_italic = "italic" in font.lower()

                            # Obtener coordenadas
                            bbox = span["bbox"]
                            x0, y0, x1, y1 = bbox

                            text_block = TextBlock(
                                text=text,
                                page_num=page_num,
                                x0=x0,
                                y0=y0,
                                x1=x1,
                                y1=y1,
                                font=font,
                                font_size=font_size,
                                color=color,
                                is_bold=is_bold,
                                is_italic=is_italic,
                            )
                            text_blocks.append(text_block)

        return text_blocks

    def _extract_images(self, page, page_num: int) -> List[ImageBlock]:
        """
        Extrae las imágenes de una página.

        Args:
            page: Página de PyMuPDF.
            page_num: Número de página.

        Returns:
            Lista de ImageBlock.
        """
        images = []
        image_list = page.get_images(full=True)

        for img_index, img_info in enumerate(image_list):
            xref = img_info[0]
            if self.doc is None:
                logger.warning(f"PDF no está abierto, saltando imagen {img_index} en página {page_num}")
                continue
            base_image = self.doc.extract_image(xref)
            image_bytes = base_image["image"]

            # Convertir a PIL Image
            image = Image.open(io.BytesIO(image_bytes))

            # Obtener la posición de la imagen en la página
            # Esto es más complejo, necesitamos buscar el rectángulo
            # donde aparece la imagen
            img_rects = page.get_image_rects(xref)

            if img_rects:
                rect = img_rects[0]  # Usar la primera ocurrencia
                x0, y0, x1, y1 = rect
            else:
                # Si no encontramos el rectángulo, usar valores predeterminados
                # Esto puede no ser preciso
                x0, y0, x1, y1 = 0, 0, image.width, image.height

            image_block = ImageBlock(
                image=image,
                page_num=page_num,
                x0=x0,
                y0=y0,
                x1=x1,
                y1=y1,
                image_bytes=image_bytes,
            )
            images.append(image_block)

        return images

    def get_page_count(self) -> int:
        """
        Retorna el número de páginas del PDF.

        Returns:
            Número de páginas.
        """
        if self.doc is None:
            raise RuntimeError("El PDF no está abierto. Llama a open() primero.")
        return len(self.doc)

    def get_page_dimensions(self, page_num: int) -> Tuple[float, float]:
        """
        Retorna las dimensiones de una página.

        Args:
            page_num: Número de página (0-indexed).

        Returns:
            Tupla (ancho, alto).
        """
        if self.doc is None:
            raise RuntimeError("El PDF no está abierto. Llama a open() primero.")
        page = self.doc[page_num]
        rect = page.rect
        return (rect.width, rect.height)
