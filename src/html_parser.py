"""
Parser de HTML para traducción.

Este módulo parsea HTML extraído de PDFs para identificar contenido
traducible y mantener la estructura.
"""

from bs4 import BeautifulSoup
from loguru import logger
from typing import List, Dict, Tuple
from dataclasses import dataclass


@dataclass
class HTMLContentBlock:
    """Bloque de contenido HTML extraído."""

    html: str
    text_content: str
    is_translatable: bool
    block_type: str  # "text", "heading", "list", "table"
    position: Tuple[float, float] = (0, 0)


class HTMLParser:
    """Parser de HTML para identificar contenido traducible."""

    def __init__(self, html_content: str):
        """
        Inicializa el parser.

        Args:
            html_content: Contenido HTML a parsear.
        """
        self.html_content = html_content
        self.soup = BeautifulSoup(html_content, "html.parser")
        self.content_blocks: List[HTMLContentBlock] = []

    def parse(self) -> List[HTMLContentBlock]:
        """
        Parsea el HTML y extrae bloques de contenido.

        Returns:
            Lista de bloques de contenido.
        """
        self.content_blocks = []

        # Encontrar todas las páginas
        pages = self.soup.find_all("div", class_="page")
        logger.info(f"Encontradas {len(pages)} páginas")

        for page in pages:
            page_blocks = self._parse_page(page)
            self.content_blocks.extend(page_blocks)

        logger.info(f"Parseados {len(self.content_blocks)} bloques de contenido")
        return self.content_blocks

    def _parse_page(self, page_soup) -> List[HTMLContentBlock]:
        """
        Parsea una página específica.

        Args:
            page_soup: BeautifulSoup de la página.

        Returns:
            Lista de bloques de contenido de la página.
        """
        blocks = []

        # Encontrar todos los bloques de texto
        text_blocks = page_soup.find_all("div", class_="text-block")

        for block in text_blocks:
            html = str(block)
            text = block.get_text().strip()

            # Determinar si es traducible
            is_translatable = self._is_translatable(text)

            # Clasificar tipo de bloque
            block_type = self._classify_block(text)

            # Extraer posición si está disponible
            position = self._extract_position(block)

            content_block = HTMLContentBlock(
                html=html,
                text_content=text,
                is_translatable=is_translatable,
                block_type=block_type,
                position=position
            )

            blocks.append(content_block)

        return blocks

    def _is_translatable(self, text: str) -> bool:
        """
        Determina si un texto es traducible.

        Args:
            text: Texto a evaluar.

        Returns:
            True si es traducible, False en caso contrario.
        """
        if not text or len(text) < 2:
            return False

        # No traducir números solos o caracteres especiales
        if text.isdigit() or text in ["", ".", ",", "!", "?", ":", ";"]:
            return False

        # No traducir texto que parece código o técnica sin contexto
        if any(char in text for char in ["{", "}", "<", ">", "\\"]):
            return False

        return True

    def _classify_block(self, text: str) -> str:
        """
        Clasifica el tipo de bloque.

        Args:
            text: Texto a clasificar.

        Returns:
            Tipo de bloque ("text", "heading", "list", "table").
        """
        # Detectar títulos (texto corto, todas mayúsculas o primera mayúscula)
        if (
            len(text) < 80
            and text.isupper()
            and not text.endswith((".", ",", ":", ";"))
        ):
            return "heading"
        elif (
            len(text) < 80
            and text[0].isupper()
            and not text.endswith((".", ",", ":", ";"))
        ):
            return "heading"

        # Detectar listas (comienza con guión, número, etc.)
        if text.startswith(("-", "•", "*", "1.", "2.", "3.")):
            return "list"

        # Por defecto, texto normal
        return "text"

    def _extract_position(self, block_soup) -> Tuple[float, float]:
        """
        Extrae posición (x, y) del bloque si está disponible.

        Args:
            block_soup: BeautifulSoup del bloque.

        Returns:
            Tupla (x, y) con posición.
        """
        style = block_soup.get("style", "")
        if not style:
            return (0, 0)

        # Extraer left y top del style
        x = 0.0
        y = 0.0

        for prop in style.split(";"):
            if not prop:
                continue

            if prop.strip().startswith("left:"):
                try:
                    x = float(prop.split(":")[1].strip().replace("pt", ""))
                except ValueError:
                    pass
            elif prop.strip().startswith("top:"):
                try:
                    y = float(prop.split(":")[1].strip().replace("pt", ""))
                except ValueError:
                    pass

        return (x, y)

    def get_translatable_blocks(self) -> List[HTMLContentBlock]:
        """
        Retorna solo los bloques traducibles.

        Returns:
            Lista de bloques traducibles.
        """
        return [block for block in self.content_blocks if block.is_translatable]

    def get_block_count(self) -> Dict[str, int]:
        """
        Retorna estadísticas de bloques.

        Returns:
            Diccionario con contadores por tipo.
        """
        stats = {
            "total": len(self.content_blocks),
            "translatable": len(self.get_translatable_blocks()),
            "by_type": {}
        }

        for block in self.content_blocks:
            block_type = block.block_type
            stats["by_type"][block_type] = stats["by_type"].get(block_type, 0) + 1

        return stats