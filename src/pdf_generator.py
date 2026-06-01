"""
Generador de PDF desde HTML usando WeasyPrint.

Este módulo genera archivos PDF desde HTML preservando el layout
visual lo mejor posible.
"""

from pathlib import Path
from loguru import logger
from typing import Optional
import weasyprint


class PDFGenerator:
    """Generador de PDF desde HTML usando WeasyPrint."""

    def __init__(self):
        """Inicializa el generador."""
        logger.info("PDFGenerator inicializado")

    def generate_from_html(
        self,
        html_content: str,
        output_path: str,
        css: Optional[str] = None
    ) -> bool:
        """
        Genera un PDF desde contenido HTML.

        Args:
            html_content: Contenido HTML completo.
            output_path: Ruta donde guardar el PDF.
            css: CSS opcional para mejorar el layout.

        Returns:
            True si se generó exitosamente, False en caso contrario.
        """
        try:
            logger.info(f"Generando PDF desde HTML: {output_path}")

            # Generar PDF usando WeasyPrint
            weasyprint.HTML(string=html_content).write_pdf(
                output_path,
                stylesheets=[weasyprint.CSS(string=css)] if css else None
            )

            logger.info(f"PDF generado exitosamente: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Error al generar PDF: {e}")
            return False

    def generate_from_html_file(
        self,
        html_path: str,
        output_path: str,
        css_path: Optional[str] = None
    ) -> bool:
        """
        Genera un PDF desde un archivo HTML.

        Args:
            html_path: Ruta del archivo HTML.
            output_path: Ruta donde guardar el PDF.
            css_path: Ruta opcional del archivo CSS.

        Returns:
            True si se generó exitosamente, False en caso contrario.
        """
        try:
            logger.info(f"Generando PDF desde archivo HTML: {html_path}")

            # Leer HTML
            with open(html_path, "r", encoding="utf-8") as f:
                html_content = f.read()

            # Leer CSS si se especificó
            css = None
            if css_path and Path(css_path).exists():
                with open(css_path, "r", encoding="utf-8") as f:
                    css = f.read()

            return self.generate_from_html(html_content, output_path, css)

        except Exception as e:
            logger.error(f"Error al leer HTML: {e}")
            return False

    def get_default_css(self) -> str:
        """
        Retorna CSS por defecto para mejorar el layout.

        Returns:
            CSS por defecto.
        """
        return """
        @page {
            size: A4;
            margin: 0;
        }

        body {
            margin: 0;
            padding: 0;
            font-family: Arial, Helvetica, sans-serif;
            font-size: 12pt;
            line-height: 1.4;
        }

        .page {
            position: relative;
            margin: 0;
            page-break-after: always;
        }

        .text-block {
            position: absolute;
            white-space: pre-wrap;
            word-wrap: break-word;
        }
        """

    def rebuild_html_from_blocks(
        self,
        translated_blocks: list,
        original_pages: int
    ) -> str:
        """
        Reconstruye HTML completo desde bloques traducidos.

        Args:
            translated_blocks: Lista de bloques traducidos.
            original_pages: Número de páginas original.

        Returns:
            HTML completo reconstruido.
        """
        html_parts = ["<!DOCTYPE html>", "<html>", "<head>"]
        html_parts.append("<meta charset='utf-8'>")
        html_parts.append("<style>")
        html_parts.append(self.get_default_css())
        html_parts.append("</style>")
        html_parts.append("</head>")
        html_parts.append("<body>")

        # Reconstruir por página (simplificado)
        current_page = 0

        for block in translated_blocks:
            # Si necesitamos cambiar de página
            # (esto es una simplificación, MVP)
            if current_page < original_pages - 1:
                html_parts.append(block.html)

        html_parts.append("</body>")
        html_parts.append("</html>")

        return "\n".join(html_parts)