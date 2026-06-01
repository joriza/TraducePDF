"""
TraducePDF - Traductor de PDFs del inglés al español usando LLM local.

Este paquete proporciona herramientas para traducir documentos PDF, incluyendo:
- Traducción de texto plano (rama master)
- Preservación de layout visual (rama 260601)
utilizando un modelo LLM local.
"""

__version__ = "1.0.0"
__author__ = "TraducePDF"

# Módulos principales (rama master)
from pdf_extractor import PDFExtractor
from text_processor import TextProcessor
from llm_client import LLMClient
from utils import ProgressTracker, setup_logger

# Módulos MVP Layout Preservation (rama 260601)
from html_extractor import HTMLExtractor
from html_parser import HTMLParser
from html_translator import HTMLTranslator
from pdf_generator import PDFGenerator

__all__ = [
    # Módulos principales
    "PDFExtractor",
    "TextProcessor",
    "LLMClient",
    "ProgressTracker",
    "setup_logger",
    # Módulos MVP
    "HTMLExtractor",
    "HTMLParser",
    "HTMLTranslator",
    "PDFGenerator",
]
