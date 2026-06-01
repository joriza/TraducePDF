# TraducePDF

Traductor de PDFs del inglés al español utilizando un modelo LLM local (LM Studio, Llama Server u Ollama).

## Características

- ✅ Traducción automática de PDFs del inglés al español
- ✅ Compatible con múltiples proveedores LLM locales (LM Studio, Llama Server, Ollama)
- ✅ Enfoque en contenido de texto (sin formato visual ni imágenes)
- ✅ **Formateo prolijo de oraciones** - El texto se reescribe de forma natural y legible
- ✅ Eliminación de saltos de línea innecesarios del PDF original
- ✅ Procesamiento en bloques con overlap para mantener contexto
- ✅ Compatible con documentos largos (cientos de páginas)
- ✅ Detección automática del modelo cargado
- ✅ Visualización detallada del proceso de traducción
- ✅ Salida en formato de texto plano legible
- ✅ Reintentos automáticos en caso de fallos
- ✅ Logging detallado para debugging
- ✅ **Compatible con Windows** (soporte UTF-8)

## Requisitos

- Python 3.8 o superior
- Un servidor LLM local corriendo:
 - **LM Studio** (http://localhost:1234/v1)
 - **Llama Server** (http://localhost:8080/v1)
 - **Ollama** (http://localhost:11434/v1)
- Un modelo LLM cargado en el servidor

## Instalación

### Método rápido (recomendado)

Ejecuta el script de instalación automática:

```bash
python setup.py
```

Este script realizará automáticamente:
1. Verificar la versión de Python
2. Crear el entorno virtual
3. Actualizar pip
4. Instalar todas las dependencias
5. Crear el archivo de configuración `.env`

### Método manual

#### 1. Crear entorno virtual

**En Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**En Linux/Mac:**
```bash
python -m venv venv
source venv/bin/activate
```

#### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 3. Crear archivo de configuración (opcional)

```bash
copy .env.example .env
```

Edita `.env` según tus necesidades:

```env
# URL del servidor LLM (ejemplos)
LM_STUDIO_URL=http://localhost:1234/v1
LLAMA_SERVER_URL=http://localhost:8080/v1
OLLAMA_URL=http://localhost:11434/v1

LLM_SERVER_TIMEOUT=300
PAGES_PER_BLOCK=2
OVERLAP_PERCENTAGE=0.25
OUTPUT_SUFFIX=_translated
```

## Uso

### Activar el entorno virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Modos de uso

#### Opción 1: Usar perfiles pre-configurados (recomendado)

```bash
# LM Studio
python src/main.py archivo.pdf --profile lm-studio

# Llama Server (llama.cpp)
python src/main.py archivo.pdf --profile llama-server

# Ollama
python src/main.py archivo.pdf --profile ollama
```

#### Opción 2: URL directa

```bash
# URL personalizada
python src/main.py archivo.pdf --server-url http://localhost:1234/v1
```

#### Opción 3: Uso básico (usa configuración del .env o default)

```bash
python src/main.py archivo.pdf
```

### Opciones adicionales

```bash
# Especificar archivo de salida
python src/main.py archivo.pdf -o resultado.txt

# Ajustar parámetros de procesamiento
python src/main.py archivo.pdf --pages-per-block 3 --overlap 0.2

# Verbose y logging
python src/main.py archivo.pdf --verbose --log-file traduccion.log

# Mostrar detalles completos de traducción
python src/main.py archivo.pdf --show-details

# Combinar opciones
python src/main.py archivo.pdf --profile lm-studio --pages-per-block 3 --overlap 0.2 -v
```

### Ayuda

```bash
python src/main.py --help
```

## Argumentos de línea de comandos

| Argumento | Descripción | Default |
|-----------|-------------|---------|
| `input_pdf` | Ruta al PDF de entrada (requerido) | - |
| `--profile` | Perfil: `llama-server`, `lm-studio`, `ollama` | - |
| `--server-url` | URL del servidor LLM | `http://localhost:8080/v1` |
| `--pages-per-block` | Páginas por bloque de traducción | `2` |
| `--overlap` | Porcentaje de overlap 0.0-1.0 | `0.25` |
| `--timeout` | Timeout en segundos para peticiones | `300` |
| `-v, --verbose` | Mostrar información detallada | `False` |
| `--log-file` | Archivo donde guardar los logs | `None` |
| `--show-details` | Mostrar detalles completos de traducción | `False` |

## Configuración de servidores LLM

### LM Studio

1. Descarga e instala [LM Studio](https://lmstudio.ai/)
2. Carga un modelo (ej: Llama, Gemma, Mistral)
3. Habilita el servidor en `Settings → Server`
4. Puerto default: `1234`

### Llama Server (llama.cpp)

```bash
llama-server --model tu_modelo.gguf --port 8080
```

### Ollama

```bash
# Instalar Ollama
# Descargar desde https://ollama.ai/

# Descargar modelo
ollama pull llama2

# Iniciar servidor (Ollama API es compatible con OpenAI)
# Configurado en el puerto 11434 por defecto
```

## Cómo funciona

```
┌─────────────┐
│ PDF Input │
└──────┬──────┘
 │
 ▼
┌─────────────────┐
│ Extracción de │ Solo texto
│ Texto │
└──────┬──────────┘
 │
 ▼
┌─────────────────┐
│ División en │ Bloques con overlap
│ Bloques │
└──────┬──────────┘
 │
 ▼
┌─────────────────┐
│ Traducción con │ LM Studio / Llama Server / Ollama
│ LLM Local │
└──────┬──────────┘
 │
 ▼
┌─────────────────┐
│ Organización │ Por página
│ de Resultados │
└──────┬──────────┘
 │
 ▼
┌─────────────────┐
│ Guardado en │ Archivo de texto
│ Archivo TXT │
└──────┬──────────┘
 │
 ▼
┌─────────────┐
│ TXT Output │
└─────────────┘
```

## Formateo Prolijo del Texto

TraducePDF aplica un formateo automático para mejorar la legibilidad del texto traducido:

### Características del formateo

- **Eliminación de saltos de línea innecesarios**: El texto del PDF original suele tener saltos de línea arbitrarios que no corresponden a pausas naturales en el texto. Estos se eliminan.

- **Reescritura de oraciones completas**: Las oraciones que estaban cortadas en medio de una línea en el PDF original se unen para formar oraciones completas y naturales.

- **Párrafos bien estructurados**: El texto se organiza en párrafos lógicos, separando ideas relacionadas con espacios apropiados.

- **Limpieza de espacios múltiples**: Se eliminan espacios extra y se corrige la puntuación.

### Ejemplo

**Texto original del PDF:**
```
Este es un ejemplo de texto
que tiene saltos de línea
innecesarios y corta oraciones
en medio de una línea.
```

**Texto traducido y formateado:**
```
Este es un ejemplo de texto que tiene saltos de línea innecesarios y corta oraciones en medio de una línea.
```

El modelo LLM está instruido para reescribir el texto de forma natural mientras mantiene el significado original.

## Estructura del proyecto

```
TraducePDF/
├── src/
│ ├── __init__.py # Inicialización del paquete
│ ├── main.py # Script principal
│ ├── pdf_extractor.py # Extracción de texto e imágenes
│ ├── text_processor.py # Procesamiento con overlap
│ ├── llm_client.py # Cliente LLM (LM Studio, Llama Server, Ollama)
│ └── utils.py # Utilidades
├── setup.py # Script de instalación automática
├── requirements.txt # Dependencias
├── .env.example # Ejemplo de configuración
├── .gitignore # Archivos ignorados por Git
└── README.md # Este archivo
```

## Solución de problemas

### Error de conexión con el servidor LLM

```
❌ Error: No se pudo conectar con el servidor
```

**Solución:**
1. Verifica que el servidor esté ejecutándose
2. Usa `--profile` con el proveedor correcto
3. Verifica que el puerto sea correcto (LM Studio: 1234, Llama Server: 8080, Ollama: 11434)
4. Verifica que el modelo esté cargado

### Timeout en la traducción

```
❌ Error: Timeout después de 300 segundos
```

**Solución:**
1. Aumenta el timeout con `--timeout 600`
2. Reduce las páginas por bloque con `--pages-per-block 1`
3. Usa un modelo más rápido o con menos parámetros

### Traducciones incompletas o con errores

**Solución:**
1. Revisa el log para ver detalles de los errores
2. Algunos bloques pueden fallar si el texto es muy complejo
3. Usa `--verbose` para más información de depuración

### Texto duplicado en el archivo de salida

**Solución:**
1. Esto puede ocurrir debido al overlap entre bloques
2. Es normal en los bordes de los bloques de traducción
3. Puedes ajustar el overlap con `--overlap 0.1` para reducirlo

## Limitaciones

- Solo se procesa el contenido de texto (no se preserva formato visual ni imágenes)
- La calidad de la traducción depende del modelo LLM utilizado
- Texto muy técnico puede requerir revisión manual
- Algunos elementos complejos (tablas, fórmulas matemáticas) pueden no traducirse perfectamente
- El overlap entre bloques puede causar duplicación de texto en los bordes
- El formateo prolijo puede alterar ligeramente la estructura original del documento

## Cambios recientes

### v0.1 (2026-06-01)

- ✅ Soporte para múltiples proveedores LLM (LM Studio, Llama Server, Ollama)
- ✅ Compatibilidad con Windows (corrección de encoding UTF-8)
- ✅ Limpieza de dependencias y código muerto
- ✅ Corrección de errores de type checking

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Autor

TraducePDF - 2024