"""
Extractor de HTML desde PDF usando PyMuPDF.

Este módulo extrae contenido HTML básico de PDFs para preservar
mejor el layout visual que el texto plano.
"""

import fitz
from loguru import logger
from pathlib import Path
from typing import Optional


class HTMLExtractor:
    """Extractor de HTML desde PDF usando PyMuPDF."""

    def __init__(self, pdf_path: str):
        """
        Inicializa el extractor.

        Args:
            pdf_path: Ruta al archivo PDF.
        """
        self.pdf_path = pdf_path
        self.doc = None

    def open(self):
        """Abre el archivo PDF."""
        try:
            self.doc = fitz.open(self.pdf_path)
            logger.info(f"PDF abierto para extracción HTML: {self.pdf_path}")
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

    def extract_to_html(self, output_path: Optional[str] = None) -> str:
        """
        Extrae el contenido del PDF a HTML.

        PyMuPDF tiene soporte limitado para HTML pero suficiente para MVP.
        Extrae texto con posiciones absolutas para preservar layout básico.

        Args:
            output_path: Ruta opcional para guardar el HTML en disco.

        Returns:
            String con el contenido HTML extraído.
        """
        if self.doc is None:
            raise RuntimeError("El PDF no está abierto. Llama a open() primero.")

        html_parts = ["<!DOCTYPE html>", "<html>", "<head>", "<meta charset='utf-8'>"]
        html_parts.append("<style>")
        html_parts.append("""
            body { margin: 0; padding: 0; font-family: Arial, sans-serif; }
            .page {
                position: relative;
                width: 595pt; /* A4 width */
                height: 842pt; /* A4 height */
                margin: 0 auto;
                border: 1px solid #ccc;
            }
            .text-block {
                position: absolute;
                left: 0;
                top: 0;
                white-space: pre;
            }
        """)
        html_parts.append("</style>")
        html_parts.append("</head>")
        html_parts.append("<body>")

        # Extraer cada página
        for page_num in range(len(self.doc)):
            page = self.doc[page_num]
            rect = page.rect

            html_parts.append(f'<div class="page" style="width:{rect.width}pt; height:{rect.height}pt;">')

            # Extraer bloques de texto con posiciones
            blocks = page.get_text("dict", sort=True)["blocks"]

            for block in blocks:
                if block["type"] == 0:  # Bloque de texto
                    for line in block.get("lines", []):
                        for span in line.get("spans", []):
                            text = span["text"].strip()
                            if text:
                                # Obtener coordenadas
                                bbox = span["bbox"]
                                x0, y0, x1, y1 = bbox

                                # Obtener información de fuente
                                font = span.get("font", "")
                                font_size = span.get("size", 12)
                                is_bold = "bold" in font.lower()

                                # Crear bloque HTML con posicionamiento absoluto
                                font_style = "font-weight: bold;" if is_bold else ""

                                html_parts.append(f'<div class="text-block" style="left:{x0}pt; top:{y0}pt; font-size:{font_size}pt; {font_style}">')
                                html_parts.append(text)
                                html_parts.append("</div>")

            html_parts.append("</div>")

        html_parts.append("</body>")
        html_parts.append("</html>")

        html_content = "\n".join(html_parts)

        # Guardar en disco si se especificó
        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"HTML guardado en: {output_path}")

        logger.debug(f"HTML extraído: {len(html_content)} caracteres")
        return html_content

    def get_page_count(self) -> int:
        """
        Retorna el número de páginas del PDF.

        Returns:
            Número de páginas.
        """
        if self.doc is None:
            raise RuntimeError("El PDF no está abierto. Llama a open() primero.")
        return len(self.doc)