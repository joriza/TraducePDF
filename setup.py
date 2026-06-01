#!/usr/bin/env python3
"""
Script de instalación y configuración para TraducePDF.

Este script ayuda a configurar el entorno virtual e instalar las dependencias.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


def print_header(text: str):
    """Imprime un encabezado con formato."""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_step(step: int, total: int, text: str):
    """Imprime un paso del proceso."""
    print(f"[{step}/{total}] {text}")


def run_command(command: list, description: str) -> bool:
    """
    Ejecuta un comando y muestra el resultado.

    Args:
        command: Comando a ejecutar como lista.
        description: Descripción del comando.

    Returns:
        True si el comando fue exitoso, False en caso contrario.
    """
    print(f"\n▶ {description}")
    print(f"   Comando: {' '.join(command)}\n")

    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"✅ {description} completado")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en {description}")
        print(f"   Código de salida: {e.returncode}")
        return False


def check_python_version() -> bool:
    """Verifica que la versión de Python sea compatible."""
    print_step(1, 6, "Verificando versión de Python...")

    version = sys.version_info
    min_version = (3, 8)

    if version >= min_version:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detectado")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} no es compatible")
        print(f"   Se requiere Python {min_version[0]}.{min_version[1]} o superior")
        return False


def create_virtualenv() -> bool:
    """Crea el entorno virtual."""
    print_step(2, 6, "Creando entorno virtual...")

    venv_path = Path("venv")

    if venv_path.exists():
        print("⚠️  El entorno virtual ya existe")
        response = input("   ¿Deseas recrearlo? (s/N): ").strip().lower()
        if response == 's':
            import shutil
            shutil.rmtree(venv_path)
            print("   Entorno virtual eliminado")
        else:
            print("   Usando entorno virtual existente")
            return True

    return run_command(
        [sys.executable, "-m", "venv", "venv"],
        "Creación de entorno virtual"
    )


def get_venv_python() -> str:
    """Retorna la ruta al ejecutable Python del entorno virtual."""
    system = platform.system()

    if system == "Windows":
        return str(Path("venv/Scripts/python.exe"))
    else:
        return str(Path("venv/bin/python"))


def get_venv_pip() -> str:
    """Retorna la ruta al ejecutable pip del entorno virtual."""
    system = platform.system()

    if system == "Windows":
        return str(Path("venv/Scripts/pip.exe"))
    else:
        return str(Path("venv/bin/pip"))


def upgrade_pip() -> bool:
    """Actualiza pip a la última versión."""
    print_step(3, 6, "Actualizando pip...")

    pip_path = get_venv_pip()
    return run_command(
        [pip_path, "install", "--upgrade", "pip"],
        "Actualización de pip"
    )


def install_dependencies() -> bool:
    """Instala las dependencias del proyecto."""
    print_step(4, 6, "Instalando dependencias...")

    pip_path = get_venv_pip()

    if not Path("requirements.txt").exists():
        print("❌ No se encontró requirements.txt")
        return False

    return run_command(
        [pip_path, "install", "-r", "requirements.txt"],
        "Instalación de dependencias"
    )


def create_env_file() -> bool:
    """Crea el archivo .env si no existe."""
    print_step(5, 6, "Configurando variables de entorno...")

    env_path = Path(".env")
    env_example = Path(".env.example")

    if env_path.exists():
        print("⚠️  El archivo .env ya existe")
        response = input("   ¿Deseas sobrescribirlo? (s/N): ").strip().lower()
        if response != 's':
            print("   Manteniendo archivo .env existente")
            return True

    if env_example.exists():
        import shutil
        shutil.copy(env_example, env_path)
        print("✅ Archivo .env creado desde .env.example")
        print("   Puedes editarlo para ajustar la configuración")
        return True
    else:
        print("⚠️  No se encontró .env.example, creando .env con valores por defecto")

    env_content = """# Configuración del servidor Llama
LLAMA_SERVER_URL=http://localhost:8080/v1
LLAMA_SERVER_TIMEOUT=300

# Configuración de procesamiento
PAGES_PER_BLOCK=2
OVERLAP_PERCENTAGE=0.25

# Configuración de salida
OUTPUT_SUFFIX=_translated
"""

    with open(env_path, "w") as f:
        f.write(env_content)

    print("✅ Archivo .env creado con valores por defecto")
    return True


def print_activation_instructions():
    """Imprime instrucciones para activar el entorno virtual."""
    print_step(6, 6, "Instrucciones de uso")

    system = platform.system()

    print("\n📝 Para usar el traductor, primero activa el entorno virtual:\n")

    if system == "Windows":
        print("   En CMD:")
        print("   venv\\Scripts\\activate")
        print("\n   En PowerShell:")
        print("   venv\\Scripts\\Activate.ps1")
    else:
        print("   source venv/bin/activate")

    print("\n📝 Luego ejecuta el traductor:")
    print("   python src/main.py archivo.pdf")

    print("\n📝 Para ver todas las opciones:")
    print("   python src/main.py --help")

    print("\n📝 Para desactivar el entorno virtual:")
    print("   deactivate")

    print("\n" + "=" * 60)
    print("  ¡Instalación completada!")
    print("=" * 60 + "\n")


def main():
    """Función principal del script de instalación."""
    print_header("TraducePDF - Script de Instalación")

    steps = [
        check_python_version,
        create_virtualenv,
        upgrade_pip,
        install_dependencies,
        create_env_file,
    ]

    for step in steps:
        if not step():
            print("\n❌ La instalación falló. Por favor, revisa los errores arriba.")
            sys.exit(1)

    print_activation_instructions()


if __name__ == "__main__":
    main()
