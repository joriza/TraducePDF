"""
Procesador de texto.

Este módulo se encarga de dividir el texto extraído del PDF en bloques
con overlap para mantener el contexto entre páginas.
"""

from typing import List, Dict, Any
from dataclasses import dataclass, field
from loguru import logger

from pdf_extractor import PageData, TextBlock


@dataclass
class TextBlockWithTranslation:
    """Bloque de texto con su traducción."""

    original: TextBlock
    translated_text: str = ""
    translation_success: bool = False
    translation_error: str = ""


@dataclass
class PageTranslation:
    """Traducción de una página completa."""

    page_num: int
    original_blocks: List[TextBlock] = field(default_factory=list)
    translated_blocks: List[TextBlockWithTranslation] = field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Verifica si todos los bloques fueron traducidos exitosamente."""
        return all(block.translation_success for block in self.translated_blocks)


@dataclass
class TranslationBlock:
    """Bloque de texto para enviar al modelo LLM."""

    text: str
    page_nums: List[int]
    block_indices: List[tuple]  # (page_num, block_index)
    is_overlap: bool = False


class TextProcessor:
    """Procesador de texto para dividir en bloques con overlap."""

    def __init__(self, pages_per_block: int = 2, overlap_percentage: float = 0.25):
        """
        Inicializa el procesador de texto.

        Args:
            pages_per_block: Número de páginas por bloque.
            overlap_percentage: Porcentaje de overlap (0.0 a 1.0).
        """
        self.pages_per_block = pages_per_block
        self.overlap_percentage = overlap_percentage

        if not 0.0 <= overlap_percentage <= 1.0:
            raise ValueError("overlap_percentage debe estar entre 0.0 y 1.0")

        logger.info(
            f"TextProcessor configurado: {pages_per_block} páginas/bloque, {overlap_percentage * 100}% overlap"
        )

    def create_translation_blocks(
        self, pages_data: List[PageData]
    ) -> List[TranslationBlock]:
        """
        Crea bloques de texto para traducción con overlap.

        Args:
            pages_data: Lista de PageData con el contenido extraído.

        Returns:
            Lista de TranslationBlock.
        """
        blocks = []
        total_pages = len(pages_data)

        if total_pages == 0:
            logger.warning("No hay páginas para procesar")
            return blocks

        # Calcular cuántas páginas de overlap incluir
        overlap_pages = max(1, int(self.pages_per_block * self.overlap_percentage))

        # Crear bloques deslizantes
        for start_page in range(0, total_pages, self.pages_per_block):
            end_page = min(start_page + self.pages_per_block, total_pages)

            # Determinar páginas de overlap (de páginas anteriores)
            overlap_start = max(0, start_page - overlap_pages)

            # Recopilar texto de todas las páginas en este bloque
            block_text_parts = []
            page_nums_in_block = []
            block_indices = []

            # Primero agregar el overlap (si existe)
            for page_num in range(overlap_start, start_page):
                page_data = pages_data[page_num]
                for block_idx, text_block in enumerate(page_data.text_blocks):
                    block_text_parts.append(
                        f"[Página {page_num + 1}, Bloque {block_idx + 1}] {text_block.text}"
                    )
                    block_indices.append((page_num, block_idx))

            # Luego agregar las páginas principales
            for page_num in range(start_page, end_page):
                page_data = pages_data[page_num]
                page_nums_in_block.append(page_num)

                for block_idx, text_block in enumerate(page_data.text_blocks):
                    block_text_parts.append(
                        f"[Página {page_num + 1}, Bloque {block_idx + 1}] {text_block.text}"
                    )
                    block_indices.append((page_num, block_idx))

            # Crear el bloque de traducción
            full_text = "\n".join(block_text_parts)

            translation_block = TranslationBlock(
                text=full_text,
                page_nums=page_nums_in_block,
                block_indices=block_indices,
                is_overlap=(overlap_start < start_page),
            )

            blocks.append(translation_block)

            logger.debug(
                f"Bloque creado: páginas {start_page + 1}-{end_page} "
                f"(overlap de {start_page - overlap_start} páginas), "
                f"{len(block_indices)} bloques de texto"
            )

        logger.info(f"Creados {len(blocks)} bloques de traducción")
        return blocks

    def parse_translation_response(
        self, response: str, block: TranslationBlock
    ) -> Dict[tuple, str]:
        """
        Parsea la respuesta del modelo LLM para extraer las traducciones.

        La respuesta esperada tiene el formato:
        [Página X, Bloque Y] texto traducido

        Args:
            response: Respuesta del modelo LLM.
            block: Bloque de traducción original.

        Returns:
            Diccionario mapeando (page_num, block_index) -> texto traducido.
        """
        translations = {}
        import re

        # Regex mejorado para capturar texto multilínea
        # Busca [Página X, Bloque Y] hasta el próximo [Página o fin del texto
        pattern = r"\[Página\s+(\d+)\s*,\s*Bloque\s+(\d+)\]\s*(.*?)(?=\n\[Página|$)"
        matches = re.findall(pattern, response, re.DOTALL | re.IGNORECASE)

        for page_str, block_str, translated_text in matches:
            page_num = int(page_str) - 1  # Convertir a 0-indexed
            block_idx = int(block_str) - 1
            translated_text = translated_text.strip()

            if (page_num, block_idx) in block.block_indices:
                translations[(page_num, block_idx)] = translated_text
            else:
                logger.warning(
                    f"Bloque no encontrado en índices: ({page_num}, {block_idx}). "
                    f"Saltando traducción."
                )

        # Validación: verificar que se parsearon todos los bloques
        expected_count = len(block.block_indices)
        actual_count = len(translations)

        if actual_count < expected_count:
            missing = expected_count - actual_count
            logger.warning(
                f"Faltan {missing} traducciones ({actual_count}/{expected_count}). "
                f"Esto puede indicar que el LLM omitió bloques."
            )

            # Intentar parseo alternativo: buscar etiquetas perdidas
            alt_pattern = r"\[Página\s+(\d+)\s*,\s*Bloque\s+(\d+)\]"
            alt_matches = re.findall(alt_pattern, response, re.IGNORECASE)

            if len(alt_matches) > actual_count:
                logger.info(
                    f"Se encontraron {len(alt_matches)} etiquetas vs {actual_count} traducciones parseadas"
                )

        logger.debug(
            f"Parseadas {len(translations)} traducciones de {len(block.block_indices)} bloques"
        )

        return translations

    def create_page_translations(
        self,
        pages_data: List[PageData],
        translation_blocks: List[TranslationBlock],
        translation_responses: List[Dict[tuple, str]],
    ) -> List[PageTranslation]:
        """
        Crea las traducciones de página a partir de las respuestas del modelo.

        Args:
            pages_data: Datos originales de las páginas.
            translation_blocks: Bloques enviados al modelo.
            translation_responses: Respuestas del modelo para cada bloque.

        Returns:
            Lista de PageTranslation.
        """
        page_translations = []

        # Inicializar traducciones de página
        for page_data in pages_data:
            page_translation = PageTranslation(
                page_num=page_data.page_num,
                original_blocks=page_data.text_blocks.copy(),
            )
            page_translations.append(page_translation)

        # Combinar todas las traducciones
        all_translations: Dict[tuple, str] = {}
        for response in translation_responses:
            all_translations.update(response)

        # Asignar traducciones a los bloques correspondientes
        for page_translation in page_translations:
            for block_idx, original_block in enumerate(
                page_translation.original_blocks
            ):
                key = (page_translation.page_num, block_idx)

                if key in all_translations:
                    translated_block = TextBlockWithTranslation(
                        original=original_block,
                        translated_text=all_translations[key],
                        translation_success=True,
                    )
                else:
                    translated_block = TextBlockWithTranslation(
                        original=original_block,
                        translated_text=original_block.text,  # Mantener original
                        translation_success=False,
                        translation_error="No se encontró traducción en la respuesta",
                    )

                page_translation.translated_blocks.append(translated_block)

        # Log de estadísticas
        total_blocks = sum(len(pt.translated_blocks) for pt in page_translations)
        successful_blocks = sum(
            1
            for pt in page_translations
            for tb in pt.translated_blocks
            if tb.translation_success
        )

        logger.info(
            f"Traducciones de página creadas: {successful_blocks}/{total_blocks} bloques exitosos "
            f"({successful_blocks / total_blocks * 100:.1f}%)"
        )

        return page_translations

    def estimate_token_count(self, text: str) -> int:
        """
        Estima el número de tokens en un texto.

        Esta es una estimación aproximada (aprox. 4 caracteres por token).

        Args:
            text: Texto a estimar.

        Returns:
            Número estimado de tokens.
        """
        return len(text) // 4
