"""
Utilidades para el traductor de PDFs.

Este módulo proporciona funciones para seguimiento de progreso, logging
y manejo de errores.
"""

import sys
from typing import Optional
from loguru import logger
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
    TimeRemainingColumn,
)
from rich.panel import Panel
from rich.text import Text


class ProgressTracker:
    """Clase para rastrear y mostrar el progreso del procesamiento."""

    def __init__(self):
        """Inicializa el tracker de progreso."""
        self.console = Console()
        self.progress = None
        self.current_task = None

    def start(self, total: int, description: str = "Procesando"):
        """
        Inicia el seguimiento de progreso.

        Args:
            total: Número total de elementos a procesar.
            description: Descripción de la tarea.
        """
        self.progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=self.console,
        )
        self.current_task = self.progress.add_task(description, total=total)
        self.progress.start()

    def update(self, advance: int = 1, description: Optional[str] = None):
        """
        Actualiza el progreso.

        Args:
            advance: Cantidad a avanzar en el progreso.
            description: Nueva descripción opcional.
        """
        if self.progress and self.current_task:
            if description:
                self.progress.update(
                    self.current_task,
                    advance=advance,
                    description=description
                )
            else:
                self.progress.update(self.current_task, advance=advance)

    def finish(self):
        """Finaliza el seguimiento de progreso."""
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.current_task = None

    def print_info(self, message: str):
        """
        Imprime un mensaje informativo en la consola.

        Args:
            message: Mensaje a mostrar.
        """
        self.console.print(Panel(
            Text(message, style="cyan"),
            title="ℹ️  Información",
            border_style="cyan"
        ))

    def print_success(self, message: str):
        """
        Imprime un mensaje de éxito en la consola.

        Args:
            message: Mensaje a mostrar.
        """
        self.console.print(Panel(
            Text(message, style="green"),
            title="✅ Éxito",
            border_style="green"
        ))

    def print_warning(self, message: str):
        """
        Imprime un mensaje de advertencia en la consola.

        Args:
            message: Mensaje a mostrar.
        """
        self.console.print(Panel(
            Text(message, style="yellow"),
            title="⚠️  Advertencia",
            border_style="yellow"
        ))

    def print_error(self, message: str):
        """
        Imprime un mensaje de error en la consola.

        Args:
            message: Mensaje a mostrar.
        """
        self.console.print(Panel(
            Text(message, style="red"),
            title="❌ Error",
            border_style="red"
        ))


def setup_logger(log_file: Optional[str] = None, verbose: bool = False):
    """
    Configura el sistema de logging.

    Args:
        log_file: Archivo donde guardar los logs (opcional).
        verbose: Si es True, muestra logs más detallados.
    """
    # Remover el handler por defecto
    logger.remove()

    # Configurar nivel de log
    log_level = "DEBUG" if verbose else "INFO"

    # Agregar handler para consola
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>",
        level=log_level,
        colorize=True
    )

    # Agregar handler para archivo si se especifica
    if log_file:
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
            level=log_level,
            rotation="10 MB",
            retention="7 days",
            compression="zip"
        )

    return logger


def format_number(n: int) -> str:
    """
    Formatea un número con separadores de miles.

    Args:
        n: Número a formatear.

    Returns:
        Número formateado como string.
    """
    return f"{n:,}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Trunca un texto a una longitud máxima.

    Args:
        text: Texto a truncar.
        max_length: Longitud máxima.

    Returns:
        Texto truncado con "..." si fue cortado.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."
