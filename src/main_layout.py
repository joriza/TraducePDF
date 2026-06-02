#!/usr/bin/env python3
"""
TraducePDF - Modo Layout Preserving.

Script principal para traducir PDFs preservando el layout visual
usando PyMuPDF + BeautifulSoup + LLM + WeasyPrint.
"""

import sys
import argparse
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from html_extractor import HTMLExtractor
from html_parser import HTMLParser
from html_translator import HTMLTranslator
from pdf_generator import PDFGenerator
from llm_client import LLMClient
from utils import setup_logger, format_number


def parse_arguments():
    """
    Parsea los argumentos de línea de comandos.

    Returns:
        Argumentos parseados.
    """
    parser = argparse.ArgumentParser(
        description="Traduce PDFs del inglés al español preservando layout visual.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main_layout.py documento.pdf
  python main_layout.py documento.pdf --output documento_traducido.pdf
  python main_layout.py documento.pdf --profile lm-studio --verbose
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
        help="Perfil pre-configurado del servidor",
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        help="Bloques a traducir por lote (default: 5)",
        default=5,
    )

    parser.add_argument(
        "--timeout", type=int, help="Timeout en segundos (default: 300)", default=300
    )

    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Mostrar información detallada"
    )

    parser.add_argument(
        "--log-file", help="Archivo donde guardar los logs", default=None
    )

    parser.add_argument(
        "--keep-html",
        action="store_true",
        help="Guardar el HTML intermedio para debugging",
    )

    return parser.parse_args()


def get_output_path(input_path: str, output_path: str | None = None) -> str:
    """
    Determina la ruta de salida del PDF traducido.

    Args:
        input_path: Ruta del PDF de entrada.
        output_path: Ruta de salida opcional.

    Returns:
        Ruta de salida del documento.
    """
    if output_path:
        return output_path

    input_path_obj = Path(input_path)
    return str(input_path_obj.parent / f"{input_path_obj.stem}_translated_layout.pdf")


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

    try:
        print("\n" + "=" * 80)
        print("  TraducePDF - Traductor de PDFs con Preservación de Layout")
        print("=" * 80 + "\n")

        # Validar archivo de entrada
        if not Path(args.input_pdf).exists():
            print(f"❌ Error: El archivo '{args.input_pdf}' no existe.")
            sys.exit(1)

        if not Path(args.input_pdf).suffix.lower() == ".pdf":
            print(f"❌ Error: '{args.input_pdf}' no es un archivo PDF.")
            sys.exit(1)

        # Determinar ruta de salida
        output_path = get_output_path(args.input_pdf, args.output)
        print(f"📂 Entrada: {args.input_pdf}")
        print(f"📂 Salida: {output_path}\n")

        # Obtener configuración del servidor
        profiles = {
            "llama-server": "http://localhost:8080/v1",
            "lm-studio": "http://localhost:1234/v1",
            "ollama": "http://localhost:11434/v1",
        }

        if args.profile:
            server_url = profiles[args.profile]
            print(f"🎯 Usando perfil: {args.profile} ({server_url})")
        else:
            server_url = args.server_url or os.getenv(
                "LLM_SERVER_URL", "http://localhost:8080/v1"
            )

        print(f"🔧 Lote size: {args.batch_size} bloques\n")

        # Paso 1: Verificar conexión LLM
        print("🔍 Verificando conexión con LLM...")
        llm_client = LLMClient(base_url=server_url, timeout=args.timeout)

        if not llm_client.check_connection():
            print("❌ Error: No se pudo conectar con el servidor LLM.")
            print(f"   Asegúrate de que el servidor esté ejecutándose en {server_url}")
            sys.exit(1)

        model_id = llm_client.get_loaded_model()
        if model_id:
            print(f"✅ Modelo detectado: {model_id}")
        else:
            print("⚠️  No se pudo detectar el modelo")
        print()

        # Paso 2: Extraer HTML del PDF
        print("📖 Extrayendo HTML del PDF...")
        with HTMLExtractor(args.input_pdf) as extractor:
            page_count = extractor.get_page_count()
            print(f"✅ PDF con {page_count} páginas detectado")

            html_content = extractor.extract_to_html()

        print(f"✅ HTML extraído: {format_number(len(html_content))} caracteres")

        if args.keep_html:
            html_path = Path(args.input_pdf).stem + "_layout.html"
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            print(f"✅ HTML guardado: {html_path}")
        print()

        # Paso 3: Parsear HTML
        print("🔨 Parseando HTML...")
        html_parser = HTMLParser(html_content)
        content_blocks = html_parser.parse()

        translatable_count = len(html_parser.get_translatable_blocks())
        stats = html_parser.get_block_count()

        print(f"✅ Parseados {stats['total']} bloques totales")
        print(f"✅ Traducibles: {translatable_count} bloques")
        print(f"✅ Por tipo: {stats['by_type']}\n")

        # Paso 4: Traducir contenido HTML
        print("🚀 Iniciando traducción de HTML...")

        translator = HTMLTranslator(llm_client)
        translated_blocks = translator.translate_html_blocks(
            content_blocks, batch_size=args.batch_size
        )

        print(f"✅ Traducción completada: {len(translated_blocks)} bloques\n")

        # Paso 5: Generar PDF desde HTML traducido
        print("💾 Generando PDF con layout preservado...")

        # Reconstruir HTML desde bloques traducidos
        pdf_generator = PDFGenerator()

        # Para MVP simplificado, generamos HTML básico
        translated_html = _build_translated_html(translated_blocks)

        if args.keep_html:
            translated_html_path = Path(args.input_pdf).stem + "_translated_layout.html"
            with open(translated_html_path, "w", encoding="utf-8") as f:
                f.write(translated_html)
            print(f"✅ HTML traducido guardado: {translated_html_path}")

        # Generar PDF
        success = pdf_generator.generate_from_html(
            translated_html, output_path, css=pdf_generator.get_default_css()
        )

        if success:
            print(f"✅ PDF generado: {output_path}\n")
        else:
            print("❌ Error al generar PDF\n")
            sys.exit(1)

        # Resumen final
        print("=" * 80)
        print("  RESUMEN")
        print("=" * 80)
        print(f"  📄 Páginas procesadas: {page_count}")
        print(f"  📝 Bloques de texto: {stats['total']}")
        print(f"  ✅ Bloques traducidos: {translatable_count}")
        print(f"  💾 Archivo de salida: {output_path}")
        print("=" * 80 + "\n")
        print("✅ ¡Traducción con layout preservado completada!")
        sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Proceso interrumpido por el usuario")
        sys.exit(130)

    except Exception as e:
        logger.exception("Error inesperado")
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)


def _build_translated_html(blocks: list) -> str:
    """
    Construye HTML completo desde bloques traducidos.

    Args:
        blocks: Lista de bloques traducidos.

    Returns:
        HTML completo.
    """
    html_parts = ["<!DOCTYPE html>", "<html>", "<head>"]
    html_parts.append("<meta charset='utf-8'>")
    html_parts.append("<style>")
    html_parts.append("""
        @page {
            size: A4;
            margin: 0;
        }
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
        }
        .page {
            position: relative;
            width: 595pt;
            height: 842pt;
            margin: 0 auto;
            border: 1px solid #ccc;
            page-break-after: always;
            overflow: hidden;
        }
        .text-block {
            position: absolute;
            white-space: pre-wrap;
        }
    """)
    html_parts.append("</style>")
    html_parts.append("</head>")
    html_parts.append("<body>")

    # Agrupar bloques por página basado en posición top
    if not blocks:
        return "".join(html_parts) + "</body></html>"

    # Ordenar bloques por posición (top, left)
    sorted_blocks = sorted(blocks, key=lambda b: (b.position[1], b.position[0]))

    # Detectar saltos de página (cuando top disminuye significativamente)
    current_page_blocks = []
    current_y = 0
    page_count = 0

    for block in sorted_blocks:
        y_pos = block.position[1]

        # Detectar salto de página (coordenada top disminuye más de 100pt)
        if y_pos < current_y - 100:
            # Generar página actual y empezar nueva
            if current_page_blocks:
                html_parts.append('<div class="page">')
                for page_block in current_page_blocks:
                    html_parts.append(page_block.html)
                html_parts.append("</div>")
                page_count += 1

            current_page_blocks = [block]
            current_y = y_pos
        else:
            current_page_blocks.append(block)
            current_y = y_pos if y_pos > current_y else current_y

    # Agregar última página
    if current_page_blocks:
        html_parts.append('<div class="page">')
        for page_block in current_page_blocks:
            html_parts.append(page_block.html)
        html_parts.append("</div>")
        page_count += 1

    html_parts.append("</body>")
    html_parts.append("</html>")

    return "\n".join(html_parts)


if __name__ == "__main__":
    main()
