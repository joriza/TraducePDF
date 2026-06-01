#!/usr/bin/env python3
"""
TraducePDF - Traductor de PDFs del inglés al español usando LLM local.

Este script es el punto de entrada principal para traducir documentos PDF
focalizándose solo en el contenido de texto.
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Optional
from datetime import datetime

# Añadir el directorio src al path
sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

from pdf_extractor import PDFExtractor
from text_processor import TextProcessor
from llm_client import LLMClient, LLMConnectionError, LLMTranslationError
from utils import ProgressTracker, setup_logger, format_number, truncate_text


def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.

    Returns:
        Argumentos parseados.
    """
    parser = argparse.ArgumentParser(
        description="Traduce PDFs del inglés al español usando un modelo LLM local.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py documento.pdf
  python main.py documento.pdf -o documento_traducido.txt
  python main.py documento.pdf --verbose --log-file traduccion.log
        """,
    )

    parser.add_argument("input_pdf", help="Ruta al archivo PDF de entrada en inglés")

    parser.add_argument(
        "-o", "--output", help="Ruta del archivo de salida (opcional)", default=None
    )

    parser.add_argument(
        "--server-url",
        help="URL del servidor LLM (default: http://localhost:8080/v1)",
        default=None,
    )

    parser.add_argument(
        "--profile",
        choices=["llama-server", "lm-studio", "ollama"],
        help="Perfil pre-configurado del servidor (sobreescribe --server-url)",
    )

    parser.add_argument(
        "--pages-per-block",
        type=int,
        help="Número de páginas por bloque de traducción (default: 2)",
        default=None,
    )

    parser.add_argument(
        "--overlap",
        type=float,
        help="Porcentaje de overlap entre bloques 0.0-1.0 (default: 0.25)",
        default=None,
    )

    parser.add_argument(
        "--timeout",
        type=int,
        help="Timeout en segundos para peticiones al LLM (default: 300)",
        default=None,
    )

    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Mostrar información detallada de depuración",
    )

    parser.add_argument(
        "--log-file", help="Archivo donde guardar los logs", default=None
    )

    parser.add_argument(
        "--show-details",
        action="store_true",
        help="Mostrar detalles completos de cada traducción en pantalla",
    )

    parser.add_argument(
        "--format",
        choices=["txt", "markdown", "md"],
        default="txt",
        help="Formato de salida (default: txt)",
    )

    return parser.parse_args()


def get_output_path(
    input_path: str,
    output_path: Optional[str] = None,
    output_format: str = "txt",
) -> str:
    """
    Determina la ruta de salida del documento traducido.

    Args:
        input_path: Ruta del PDF de entrada.
        output_path: Ruta de salida opcional.
        output_format: Formato de salida (txt, markdown, md).

    Returns:
        Ruta de salida del documento.
    """
    if output_path:
        return output_path

    # Si no se especifica, agregar "_translated" antes de la extensión
    input_path_obj = Path(input_path)

    # Determinar extensión según formato
    if output_format in ["markdown", "md"]:
        extension = ".md"
    else:
        extension = ".txt"

    return str(input_path_obj.parent / f"{input_path_obj.stem}_translated{extension}")


def validate_input_file(input_path: str) -> bool:
    """
    Valida que el archivo de entrada existe y es un PDF.

    Args:
        input_path: Ruta del archivo a validar.

    Returns:
        True si es válido, False en caso contrario.
    """
    path = Path(input_path)

    if not path.exists():
        print(f"❌ Error: El archivo '{input_path}' no existe.")
        return False

    if not path.is_file():
        print(f"❌ Error: '{input_path}' no es un archivo.")
        return False

    if path.suffix.lower() != ".pdf":
        print(f"❌ Error: '{input_path}' no es un archivo PDF.")
        return False

    return True


def print_separator(char="=", length=80):
    """Imprime un separador."""
    print(char * length)


def clean_text_for_output(text: str) -> str:
    """
    Limpia y formatea el texto para la salida final.

    Args:
        text: Texto a limpiar.

    Returns:
        Texto limpio y formateado.
    """
    import re

    # Eliminar espacios en blanco al inicio y final
    text = text.strip()

    # Reemplazar múltiples espacios en blanco con un solo espacio
    text = re.sub(r" +", " ", text)

    # Eliminar líneas que solo contienen espacios o están vacías
    lines = text.split("\n")
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped:  # Solo mantener líneas con contenido
            cleaned_lines.append(stripped)

    # Unir líneas con espacios, pero mantener párrafos dobles
    result = []
    i = 0
    while i < len(cleaned_lines):
        line = cleaned_lines[i]
        result.append(line)

        # Si la siguiente línea comienza con mayúscula y la actual termina con punto,
        # podría ser un nuevo párrafo
        if i + 1 < len(cleaned_lines):
            next_line = cleaned_lines[i + 1]
            if line.endswith((".", "!", "?", ":", ";")) and next_line[0].isupper():
                result.append("")  # Párrafo vacío para separar
            else:
                result.append(" ")  # Espacio entre líneas del mismo párrafo

        i += 1

    # Unir todo
    final_text = "".join(result)

    # Limpiar espacios múltiples después de la unión
    final_text = re.sub(r" +", " ", final_text)

    # Eliminar espacios antes de puntuación
    final_text = re.sub(r"\s+([.,!?;:])", r"\1", final_text)

    return final_text.strip()


def print_translation_details(
    page_num: int, block_num: int, original: str, translated: str
):
    """
    Imprime detalles de una traducción.

    Args:
        page_num: Número de página.
        block_num: Número de bloque.
        original: Texto original.
        translated: Texto traducido.
    """
    print_separator()
    print(f"📄 PÁGINA {page_num + 1} - BLOQUE {block_num + 1}")
    print_separator()
    print("\n📝 TEXTO ORIGINAL:")
    print_separator("-")
    print(original)
    print_separator("-")
    print("\n✨ TEXTO TRADUCIDO:")
    print_separator("-")
    print(translated)
    print_separator("-")
    print()


def save_translation_to_file(
    output_path: str, page_translations, pages_data, input_pdf_path: str
):
    """
    Guarda la traducción completa en un archivo de texto.

    Args:
        output_path: Ruta del archivo de salida.
        page_translations: Lista de traducciones por página.
        pages_data: Datos originales de las páginas.
        input_pdf_path: Ruta del PDF original.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        # Encabezado
        f.write("=" * 80 + "\n")
        f.write("TRADUCCIÓN DE PDF\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Archivo original: {input_pdf_path}\n")
        f.write(
            f"Fecha de traducción: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        )
        f.write(f"Número de páginas: {len(page_translations)}\n")
        f.write("=" * 80 + "\n\n")

        # Contenido traducido
        for page_trans, page_data in zip(page_translations, pages_data):
            f.write("\n")
            f.write("=" * 80 + "\n")
            f.write(f"PÁGINA {page_trans.page_num + 1}\n")
            f.write("=" * 80 + "\n\n")

            for block_trans in page_trans.translated_blocks:
                if block_trans.translation_success:
                    # Limpiar y formatear el texto antes de guardarlo
                    cleaned_text = clean_text_for_output(block_trans.translated_text)
                    f.write(cleaned_text + "\n\n")
                else:
                    f.write(f"[ERROR: {block_trans.translation_error}]\n")
                    cleaned_original = clean_text_for_output(block_trans.original.text)
                    f.write(cleaned_original + "\n\n")

        # Pie de página
        f.write("\n" + "=" * 80 + "\n")
        f.write("FIN DEL DOCUMENTO\n")
        f.write("=" * 80 + "\n")


def save_translation_to_markdown(
    output_path: str, page_translations, pages_data, input_pdf_path: str
):
    """
    Guarda la traducción completa en formato Markdown.

    Args:
        output_path: Ruta del archivo de salida.
        page_translations: Lista de traducciones por página.
        pages_data: Datos originales de las páginas.
        input_pdf_path: Ruta del PDF original.
    """
    with open(output_path, "w", encoding="utf-8") as f:
        # Encabezado Markdown
        f.write("# Traducción de PDF\n\n")
        f.write(f"**Archivo original:** `{input_pdf_path}`\n\n")
        f.write(
            f"**Fecha de traducción:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        )
        f.write(f"**Número de páginas:** {len(page_translations)}\n\n")
        f.write("---\n\n")

        # Contenido traducido
        for page_trans, page_data in zip(page_translations, pages_data):
            f.write(f"## Página {page_trans.page_num + 1}\n\n")

            for block_trans in page_trans.translated_blocks:
                if block_trans.translation_success:
                    # Limpiar y formatear el texto para Markdown
                    cleaned_text = clean_text_for_output(block_trans.translated_text)
                    markdown_text = text_to_markdown(cleaned_text)
                    f.write(markdown_text + "\n\n")
                else:
                    f.write(f"*⚠️ Error: {block_trans.translation_error}*\n\n")
                    cleaned_original = clean_text_for_output(block_trans.original.text)
                    markdown_original = text_to_markdown(cleaned_original)
                    f.write(markdown_original + "\n\n")

        # Pie de página
        f.write("---\n\n")
        f.write("*Fin del documento*\n")


def text_to_markdown(text: str) -> str:
    """
    Convierte texto plano a formato Markdown básico.

    Args:
        text: Texto plano.

    Returns:
        Texto en formato Markdown.
    """
    import re

    lines = text.split("\n")
    result = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detectar posibles títulos (línea corta, todas mayúsculas o primera letra mayúscula)
        if (
            len(line) < 80
            and line.isupper()
            and not line.endswith(".")
            and not line.endswith(",")
            and not line.endswith(":")
        ):
            # Posible título en mayúsculas
            result.append(f"## {line.title()}")
        elif (
            len(line) < 80
            and line[0].isupper()
            and not line.endswith(".")
            and not line.endswith(",")
        ):
            # Posible título
            result.append(f"### {line}")
        else:
            # Párrafo normal
            result.append(line)

    return "\n\n".join(result)


def main():
    """Función principal del programa."""
    # Configurar encoding UTF-8 para Windows
    if sys.platform == "win32":
        import codecs

        sys.stdout = codecs.getwriter("utf-8")(sys.stdout.buffer)
        sys.stderr = codecs.getwriter("utf-8")(sys.stderr.buffer)

    # Cargar variables de entorno
    load_dotenv()

    # Parsear argumentos
    args = parse_arguments()

    # Configurar logger
    logger = setup_logger(args.log_file, args.verbose)

    # Inicializar tracker de progreso
    progress = ProgressTracker()

    try:
        # Mostrar banner
        print("\n" + "=" * 80)
        print("  TraducePDF - Traductor de PDFs con LLM Local (Modo Texto)")
        print("=" * 80 + "\n")

        # Validar archivo de entrada
        if not validate_input_file(args.input_pdf):
            sys.exit(1)

        # Determinar ruta de salida
        output_path = get_output_path(args.input_pdf, args.output, args.format)
        print(f"📂 Entrada: {args.input_pdf}")
        print(f"📂 Salida: {output_path}")
        print(f"📋 Formato: {args.format.upper()}\n")

        # Obtener configuración
        # Perfiles pre-configurados
        profiles = {
            "llama-server": "http://localhost:8080/v1",
            "lm-studio": "http://localhost:1234/v1",
            "ollama": "http://localhost:11434/v1",
        }

        # Prioridad: profile > server-url > env var > default
        if args.profile:
            server_url = profiles[args.profile]
            print(f"🎯 Usando perfil: {args.profile} ({server_url})")
        else:
            server_url = args.server_url or os.getenv(
                "LLAMA_SERVER_URL", "http://localhost:8080/v1"
            )
        pages_per_block = args.pages_per_block or int(os.getenv("PAGES_PER_BLOCK", "2"))
        overlap = args.overlap or float(os.getenv("OVERLAP_PERCENTAGE", "0.25"))
        timeout = args.timeout or int(os.getenv("LLAMA_SERVER_TIMEOUT", "300"))

        logger.info(
            f"Configuración: servidor={server_url}, páginas/bloque={pages_per_block}, overlap={overlap * 100}%"
        )

        # Paso 1: Verificar conexión con el servidor LLM
        print("🔍 Verificando conexión con Llama Server...")
        llm_client = LLMClient(base_url=server_url, timeout=timeout)

        if not llm_client.check_connection():
            print("❌ Error: No se pudo conectar con Llama Server.")
            print(f"   Asegúrate de que el servidor esté ejecutándose en {server_url}")
            sys.exit(1)

        # Obtener modelo cargado
        model_id = llm_client.get_loaded_model()
        if model_id:
            print(f"✅ Modelo detectado: {model_id}")
        else:
            print(
                "⚠️  No se pudo detectar el modelo, se intentará usar el predeterminado"
            )
        print()

        # Paso 2: Extraer contenido del PDF
        print("📖 Extrayendo contenido del PDF...")
        with PDFExtractor(args.input_pdf) as extractor:
            page_count = extractor.get_page_count()
            print(f"✅ PDF con {page_count} páginas detectado")

            # Extraer todas las páginas
            pages_data = extractor.extract_all()

        total_text_blocks = sum(len(page.text_blocks) for page in pages_data)
        print(f"✅ Extraídos: {format_number(total_text_blocks)} bloques de texto")
        print()

        # Paso 3: Crear bloques de traducción
        print("🔨 Creando bloques de traducción con overlap...")
        text_processor = TextProcessor(
            pages_per_block=pages_per_block, overlap_percentage=overlap
        )
        translation_blocks = text_processor.create_translation_blocks(pages_data)
        print(f"✅ Creados {len(translation_blocks)} bloques de traducción")
        print()

        # Paso 4: Traducir bloques
        print("🚀 Iniciando traducción...\n")
        print_separator()

        translation_responses = []
        failed_blocks = 0
        total_translated = 0

        for i, block in enumerate(translation_blocks):
            try:
                # Mostrar qué páginas se están traduciendo
                page_range = f"{block.page_nums[0] + 1}-{block.page_nums[-1] + 1}"
                print(
                    f"\n📝 Traduciendo bloque {i + 1}/{len(translation_blocks)} (páginas {page_range})"
                )
                print_separator("-")

                # Mostrar el texto a traducir (resumen)
                print(f"\n📄 Texto a traducir ({len(block.text)} caracteres):")
                print_separator(".")
                if args.show_details:
                    print(block.text)
                else:
                    print(truncate_text(block.text, 500))
                    if len(block.text) > 500:
                        print(f"\n... (y {len(block.text) - 500} caracteres más)")
                print_separator(".")
                print()

                # Traducir el bloque
                print("⏳ Enviando al modelo LLM...")
                translated_text = llm_client.translate(block.text, model_id=model_id)
                print("✅ Respuesta recibida\n")

                # Mostrar la traducción
                print(f"📄 Texto traducido ({len(translated_text)} caracteres):")
                print_separator(".")
                if args.show_details:
                    print(translated_text)
                else:
                    print(truncate_text(translated_text, 500))
                    if len(translated_text) > 500:
                        print(f"\n... (y {len(translated_text) - 500} caracteres más)")
                print_separator(".")
                print()

                # Parsear la respuesta
                translations = text_processor.parse_translation_response(
                    translated_text, block
                )

                # Validar que se tradujeron todos los bloques
                expected_count = len(block.block_indices)
                actual_count = len(translations)

                if actual_count < expected_count:
                    missing = expected_count - actual_count
                    logger.warning(
                        f"Bloque {i + 1}: Faltan {missing} traducciones ({actual_count}/{expected_count})."
                    )

                    # Intentar re-parseo con regex alternativo
                    import re

                    alt_response = translated_text

                    # Buscar bloques con formato alternativo sin traducción
                    for page_num, block_idx in block.block_indices:
                        if (page_num, block_idx) not in translations:
                            pattern = rf"\[Página\s+{page_num + 1}\s*,\s*Bloque\s+{block_idx + 1}\](.*)"
                            match = re.search(
                                pattern, alt_response, re.IGNORECASE | re.DOTALL
                            )

                            if match:
                                translations[(page_num, block_idx)] = match.group(
                                    1
                                ).strip()
                                logger.info(
                                    f"Recuperado bloque ({page_num}, {block_idx}) vía parseo alternativo"
                                )
                            else:
                                # Usar texto original como fallback
                                for page_data in pages_data:
                                    if (
                                        page_data.page_num == page_num
                                        and page_data.text_blocks
                                    ):
                                        translations[(page_num, block_idx)] = (
                                            page_data.text_blocks[block_idx].text
                                        )
                                        logger.warning(
                                            f"Usando texto original para bloque ({page_num}, {block_idx})"
                                        )
                                        break

                translation_responses.append(translations)

                translated_count = len(translations)
                total_translated += translated_count
                print(
                    f"✅ Bloque {i + 1} completado: {translated_count} bloques de texto traducidos"
                )
                print_separator()

            except (LLMConnectionError, LLMTranslationError) as e:
                print(f"❌ Error al traducir bloque {i + 1}: {e}")
                failed_blocks += 1
                translation_responses.append({})

        print("\n" + "=" * 80)
        print("  TRADUCCIÓN COMPLETADA")
        print("=" * 80 + "\n")

        if failed_blocks > 0:
            print(f"⚠️  {failed_blocks} bloques fallaron en traducirse")
        else:
            print("✅ Todos los bloques traducidos exitosamente")
        print()

        # Paso 5: Crear traducciones de página
        print("📋 Organizando traducciones por página...")
        page_translations = text_processor.create_page_translations(
            pages_data, translation_blocks, translation_responses
        )

        successful_pages = sum(1 for pt in page_translations if pt.is_complete)
        print(
            f"✅ Traducciones organizadas: {successful_pages}/{len(page_translations)} páginas completas"
        )
        print()

        # Paso 6: Mostrar detalles si se solicita
        if args.show_details:
            print("📖 DETALLES DE TRADUCCIÓN")
            print("=" * 80 + "\n")

            for page_trans in page_translations:
                for block_num, block_trans in enumerate(page_trans.translated_blocks):
                    print_translation_details(
                        page_trans.page_num,
                        block_num,
                        block_trans.original.text,
                        block_trans.translated_text
                        if block_trans.translation_success
                        else "[ERROR]",
                    )

        # Paso 7: Guardar el archivo traducido
        print(f"💾 Guardando traducción en: {output_path}")

        if args.format in ["markdown", "md"]:
            save_translation_to_markdown(
                output_path, page_translations, pages_data, args.input_pdf
            )
        else:
            save_translation_to_file(
                output_path, page_translations, pages_data, args.input_pdf
            )

        print("✅ Archivo guardado exitosamente\n")

        # Resumen final
        print("=" * 80)
        print("  RESUMEN")
        print("=" * 80)
        print(f"  📄 Páginas procesadas: {page_count}")
        print(f"  📝 Bloques de texto: {format_number(total_text_blocks)}")
        print(f"  🔨 Bloques de traducción: {len(translation_blocks)}")
        print(f"  ✅ Bloques traducidos: {total_translated}")
        print(f"  ❌ Bloques fallidos: {failed_blocks}")
        print(f"  💾 Archivo de salida: {output_path}")
        print("=" * 80 + "\n")

        if failed_blocks > 0:
            print(
                "⚠️  Algunos bloques no pudieron traducirse. Revisa el log para más detalles."
            )
            sys.exit(1)
        else:
            print("✅ ¡Traducción completada exitosamente!")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(130)

    except Exception as e:
        logger.exception("Error inesperado")
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
