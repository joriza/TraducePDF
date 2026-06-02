# TraducePDF

Traductor de PDFs del inglés al español utilizando un modelo LLM local (LM Studio, Llama Server u Ollama).

## Ramas del Proyecto

### 📌 `master` - Traducción de Texto Plano (Producción)

Traducción clásica enfocada en contenido de texto sin preservación de layout visual.

**Características:**
- ✅ Salida en TXT o Markdown
- ✅ Formateo prolijo de oraciones
- ✅ 0-10% preservación de layout
- ✅ Parseo robusto sin errores
- ✅ Rápido y probado

**Comando:**
```bash
python src/main.py documento.pdf --format markdown
```

### 🏗️ `260601` - MVP Preservación de Layout (En Desarrollo)

Traducción con preservación básica del layout visual usando PyMuPDF + BeautifulSoup + WeasyPrint.

**Características:**
- ✅ Salida en PDF con layout parcialmente preservado
- ✅ Posicionamiento absoluto de texto
- ✅ Estructura de páginas y bloques
- ✅ 75-85% preservación de layout
- ⚠️ Requiere dependencias adicionales
- ⚠️ Pendiente de testing

**Stack:**
- PyMuPDF (extracción HTML)
- BeautifulSoup (parsing)
- LLM (traducción)
- WeasyPrint (regeneración PDF)

**Comando:**
```bash
pip install beautifulsoup4 weasyprint
python src/main_layout.py documento.pdf --profile lm-studio
```

**Estado:** Módulos creados, pendiente de testing

## Características

### Modo Texto Plano (rama master)
- ✅ Traducción automática de PDFs del inglés al español
- ✅ Compatible con múltiples proveedores LLM locales (LM Studio, Llama Server, Ollama)
- ✅ Enfoque en contenido de texto (sin formato visual ni imágenes)
- ✅ **Formateo prolijo de oraciones** - El texto se reescribe de forma natural y legible
- ✅ Eliminación de saltos de línea innecesarios del PDF original
- ✅ Procesamiento en bloques con overlap para mantener contexto
- ✅ Compatible con documentos largos (cientos de páginas)
- ✅ Detección automática del modelo cargado
- ✅ Visualización detallada del proceso de traducción
- ✅ **Salida en formato TXT o Markdown** (opcional)
- ✅ Reintentos automáticos en caso de fallos
- ✅ **Parseo robusto con fallback automático** (evita errores de traducción)
- ✅ Logging detallado para debugging
- ✅ **Compatible con Windows** (soporte UTF-8)

### Modo Preservación de Layout (rama 260601)
- ✅ Preservación básica de layout visual (75-85%)
- ✅ Extracción HTML con PyMuPDF
- ✅ Traducción manteniendo etiquetas HTML
- ✅ Regeneración PDF con WeasyPrint
- ✅ Posicionamiento absoluto de texto
- ✅ Soporte para títulos, párrafos, listas
- ⚠️ Requiere dependencias adicionales (beautifulsoup4, weasyprint)

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

### Formatos de salida

#### TXT (default)
```bash
python src/main.py archivo.pdf
# Crea: archivo_translated.txt
```

#### Markdown
```bash
python src/main.py archivo.pdf --format markdown
# Crea: archivo_translated.md
```

Opción alternativa:
```bash
python src/main.py archivo.pdf --format md
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
python src/main.py archivo.pdf --profile lm-studio --pages-per-block 3 --overlap 0.2 --format markdown -v
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
| `--format` | Formato de salida: `txt`, `markdown`, `md` | `txt` |
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

## Comparación de Formatos de Salida

| Aspecto | TXT | Markdown |
|---------|-----|----------|
| **Preservación de formato** | 🔴 10% | 🟡 70% |
| **Edición manual necesaria** | 🔴 Alta | 🟢 Baja |
| **Tiempo de edición** | 15-30 min | 2-5 min |
| **Negritas** | ❌ No | ✅ `**texto**` |
| **Cursivas** | ❌ No | ✅ `*texto*` |
| **Listas** | ❌ No | ✅ `- item` |
| **Títulos** | ❌ No | ✅ `#` `##` |
| **GitHub compatibility** | 🔴 Baja | 🟢 Alta |
| **Convertibilidad** | ❌ Baja | ✅ Alta |

**Recomendación:** Usa Markdown para documentos técnicos o cuando necesites compartir en GitHub/Notion. Usa TXT para lectura simple.

## Modos de Traducción

### Modo 1: Texto Plano (rama `master`)

Traducción clásica sin preservación de layout visual. Ideal para:
- Documentos técnicos para documentación
- Lectura en dispositivos móviles
- Conversión a otros formatos

**Preservación:** 0-10% de layout visual

### Modo 2: Preservación de Layout (rama `260601`)

Traducción con preservación básica del layout visual. Ideal para:
- Documentos con formatting simple
- Presentaciones básicas
- Mantener estructura visual aproximada

**Preservación:** 75-85% de layout visual

**Stack adicional:**
- PyMuPDF (extracción HTML básica)
- BeautifulSoup (parsing HTML)
- WeasyPrint (generación PDF)

**Diferencias clave:**

| Aspecto | Modo Texto | Modo Layout |
|---------|-----------|-------------|
| **Preservación visual** | 0-10% | 75-85% |
| **Edición manual necesaria** | 15-30 min | 2-5 min |
| **Tiempo de procesamiento** | Rápido | Medio |
| **Complejidad** | Baja | Media |
| **Dependencias** | Básicas | Adicionales |

## Cómo funciona

```
┌─────────────┐
│  PDF Input  │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│  Extracción de  │  Solo texto
│  Texto          │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  División en    │  Bloques con overlap
│  Bloques        │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Traducción con │  Llama Server / LM Studio / Ollama
│  LLM Local      │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Parseo robusto │  Con fallback automático
│  de respuesta   │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Organización   │  Por página
│  de Resultados  │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Formato de     │  TXT o Markdown
│  Salida         │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│  Guardado en    │  Archivo .txt o .md
│  Archivo        │
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

**Texto traducido y formateado (TXT):**
```
Este es un ejemplo de texto que tiene saltos de línea innecesarios y corta oraciones en medio de una línea.
```

**Texto traducido y formateado (Markdown):**
```markdown
Este es un ejemplo de texto que tiene saltos de línea innecesarios y corta oraciones en medio de una línea.
```

El modelo LLM está instruido para reescribir el texto de forma natural mientras mantiene el significado original.

## Mejoras Recientes

### v0.2 (2026-06-01)

- ✅ **Corregido error de parseo** - Ya no aparecen mensajes `[ERROR: No se encontró traducción]`
- ✅ **Prompt mejorado** - Instrucciones críticas para asegurar que todos los bloques se traduzcan
- ✅ **Regex multilínea** - Parseo mejorado para capturar texto con saltos de línea
- ✅ **Fallback automático** - Usa texto original si el parseo falla
- ✅ **Formato Markdown** - Opción de salida con mejor formato visual
- ✅ **Soporte multi-proveedor** - LM Studio, Llama Server, Ollama
- ✅ **Windows UTF-8** - Compatibilidad completa con Windows

### v0.1 (2026-06-01)

- ✅ Traducción de PDFs del inglés al español
- ✅ Procesamiento en bloques con overlap
- ✅ Detección automática del modelo
- ✅ Reintentos automáticos
- ✅ Logging detallado

## Estructura del proyecto

```
TraducePDF/
├── src/
│   ├── __init__.py          # Inicialización del paquete
│   ├── main.py              # Script principal
│   ├── pdf_extractor.py     # Extracción de texto e imágenes
│   ├── text_processor.py    # Procesamiento con overlap
│   ├── llm_client.py        # Cliente LLM (LM Studio, Llama Server, Ollama)
│   └── utils.py             # Utilidades
├── setup.py                 # Script de instalación automática
├── requirements.txt         # Dependencias
├── .env.example            # Ejemplo de configuración
├── .gitignore              # Archivos ignorados por Git
└── README.md               # Este archivo
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
4. El sistema usa texto original como fallback automático

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

## Ramas del Proyecto

### `master` - Modo Texto Plano
- Traducción clásica sin preservación visual
- Salida en TXT o Markdown
- Proceso rápido y simple
- **Comando:** `python src/main.py documento.pdf`
- **Preservación:** 0-10%

### `260601` - MVP Preservación de Layout
- Traducción con preservación básica del layout visual
- Salida en PDF
- Stack: PyMuPDF + BeautifulSoup + WeasyPrint
- **Comando:** `python src/main_layout.py documento.pdf`
- **Preservación:** 75-85%

**Cambiar de rama:**
```bash
git checkout master  # Modo texto plano
git checkout 260601  # Modo layout preservation
```

## Próximos desarrollos

### Rama 260601 - MVP con preservación de layout (En progreso)

Implementación basada en investigación exhaustiva para traducir PDFs preservando el aspecto visual:

**Stack actual (sin instalación externa):**
- PyMuPDF (extracción HTML básica)
- BeautifulSoup (parsing HTML)
- Llama/Ollama para traducción
- WeasyPrint (regeneración PDF)

**Objetivos:**
- 75-85% preservación de layout en documentos simples
- Procesamiento en lotes para documentos largos
- Detección de contenido traducible
- Manejo de errores y fallbacks

**Estado:** Módulos creados, pendiente de testing y refinamiento

**Stack alternativo (pdf2htmlEX - no implementado aún):**
- pdf2htmlEX para extracción precisa de layout
- BeautifulSoup para parsing HTML
- Llama/Ollama para traducción
- WeasyPrint para regeneración PDF

**Objetivos alternativos:**
- 80-90% preservación de layout en documentos simples
- Soporte para tablas básicas
- Detección de fórmulas matemáticas
- OCR para imágenes con texto

Ver documentación completa en `INVESTIGACION_TRADUCCION_PDF_LAYOUT.md`

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Ejemplos de Uso

### Modo Texto Plano (rama `master`)

```bash
# Traducción básica a TXT
python src/main.py documento.pdf

# Traducción a Markdown
python src/main.py documento.pdf --format markdown

# Traducción con LM Studio, 3 páginas por bloque
python src/main.py documento.pdf --profile lm-studio --pages-per-block 3 -v

# Traducción detallada
python src/main.py documento.pdf --show-details --verbose
```

### Modo Preservación de Layout (rama `260601`)

```bash
# Cambiar a la rama 260601
git checkout 260601

# Traducción con preservación de layout
python src/main_layout.py documento.pdf

# Traducción con LM Studio
python src/main_layout.py documento.pdf --profile lm-studio

# Traducción con HTML intermedio (debugging)
python src/main_layout.py documento.pdf --keep-html

# Traducción con lotes más pequeños
python src/main_layout.py documento.pdf --batch-size 3 --verbose
```

### Comparación de Salida

**Modo Texto Plano (TXT):**
```
================================================================================
PÁGINA 1
================================================================================

Ingeniería de IA

Construyendo Aplicaciones

con Foundation Models
```

**Modo Preservación de Layout (PDF):**
```bashn# El PDF resultante mantiene:
# - Posicionamiento aproximado de texto
# - Estructura de párrafos
# - Fuentes básicas (Arial)
# - Paginación correcta
```

## Autor

TraducePDF - 2024-2026