"""
TraducePDF - Traductor de PDFs del inglés al español usando LLM local.

Este paquete proporciona herramientas para traducir documentos PDF manteniendo
el formato visual original y las imágenes, utilizando un modelo LLM local
a través de Llama Server.
"""

__version__ = "1.0.0"
__author__ = "TraducePDF"

from pdf_extractor import PDFExtractor
from text_processor import TextProcessor
from llm_client import LLMClient
from pdf_rebuilder import PDFRebuilder
from utils import ProgressTracker, setup_logger

__all__ = [
    "PDFExtractor",
    "TextProcessor",
    "LLMClient",
    "PDFRebuilder",
    "ProgressTracker",
    "setup_logger",
]
