# TraducePDF

Traductor de PDFs del inglés al español utilizando un modelo LLM local (Llama Server).

## Características

- ✅ Traducción automática de PDFs del inglés al español
- ✅ Enfoque en contenido de texto (sin formato visual ni imágenes)
- ✅ **Formateo prolijo de oraciones** - El texto se reescribe de forma natural y legible
- ✅ Eliminación de saltos de línea innecesarios del PDF original
- ✅ Procesamiento en bloques con overlap para mantener contexto
- ✅ Compatible con documentos largos (cientos de páginas)
- ✅ Detección automática del modelo cargado en Llama Server
- ✅ Visualización detallada del proceso de traducción
- ✅ Salida en formato de texto plano legible
- ✅ Reintentos automáticos en caso de fallos
- ✅ Logging detallado para debugging

## Requisitos

- Python 3.8 o superior
- Llama Server ejecutándose en `http://localhost:8080/v1`
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

Si prefieres instalar manualmente:

#### 1. Clonar o descargar el proyecto

```bash
cd TraducePDF
```

#### 2. Crear entorno virtual

```bash
python -m venv venv
```

#### 3. Activar el entorno virtual

**En Windows:**
```bash
venv\Scripts\activate
```

**En Linux/Mac:**
```bash
source venv/bin/activate
```

#### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

#### 5. Configurar variables de entorno (opcional)

Copia el archivo de ejemplo:
```bash
copy .env.example .env
```

Edita `.env` según tus necesidades:
```env
LLAMA_SERVER_URL=http://localhost:8080/v1
LLAMA_SERVER_TIMEOUT=300
PAGES_PER_BLOCK=2
OVERLAP_PERCENTAGE=0.25
OUTPUT_SUFFIX=_translated
```

## Uso

### Uso básico

```bash
python src/main.py archivo.pdf
```

Esto creará un archivo `archivo_translated.txt` en el mismo directorio con el texto traducido.

### Especificar archivo de salida

```bash
python src/main.py archivo.pdf -o resultado.txt
```

### Mostrar detalles completos de traducción

```bash
python src/main.py archivo.pdf --show-details
```

Esta opción muestra el texto original y traducido de cada bloque en pantalla.

### Configurar servidor Llama

```bash
python src/main.py archivo.pdf --server-url http://localhost:8080/v1
```

### Ajustar parámetros de procesamiento

```bash
python src/main.py archivo.pdf --pages-per-block 2 --overlap 0.25
```

### Verbose y logging

```bash
python src/main.py archivo.pdf --verbose --log-file traduccion.log
```

### Ver ayuda

```bash
python src/main.py --help
```

## Argumentos de línea de comandos

| Argumento | Descripción | Default |
|-----------|-------------|---------|
| `input_pdf` | Ruta al PDF de entrada (requerido) | - |
| `-o, --output` | Ruta del archivo de salida | `{input}_translated.txt` |
| `--server-url` | URL del servidor Llama | `http://localhost:8080/v1` |
| `--pages-per-block` | Páginas por bloque de traducción | `2` |
| `--overlap` | Porcentaje de overlap (0.0-1.0) | `0.25` |
| `--timeout` | Timeout en segundos para peticiones | `300` |
| `-v, --verbose` | Mostrar información detallada | `False` |
| `--log-file` | Archivo de logs | `None` |
| `--show-details` | Mostrar detalles completos de traducción | `False` |

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
│  Traducción con │  Llama Server
│  LLM Local      │
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
│  Guardado en    │  Archivo de texto
│  Archivo TXT    │
└──────┬──────────┘
       │
       ▼
┌─────────────┐
│ TXT Output  │
└─────────────┘
```

## Configuración de Llama Server

Asegúrate de tener Llama Server ejecutándose con un modelo cargado:

```bash
# Ejemplo de inicio de Llama Server
llama-server --model tu_modelo.gguf --port 8080
```

El servidor debe estar accesible en `http://localhost:8080/v1`.

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
│   ├── __init__.py          # Inicialización del paquete
│   ├── main.py              # Script principal
│   ├── pdf_extractor.py     # Extracción de texto e imágenes
│   ├── text_processor.py    # Procesamiento con overlap
│   ├── llm_client.py        # Cliente Llama Server
│   ├── pdf_rebuilder.py     # Reconstrucción del PDF
│   └── utils.py             # Utilidades
├── setup.py                 # Script de instalación automática
├── requirements.txt         # Dependencias
├── .env                     # Configuración (creado por setup.py)
├── .env.example            # Ejemplo de configuración
├── .gitignore              # Archivos ignorados por Git
└── README.md               # Este archivo
```

## Solución de problemas

### Error de conexión con Llama Server

```
❌ Error: No se pudo conectar con Llama Server
```

**Solución:**
1. Verifica que Llama Server esté ejecutándose
2. Verifica que el puerto sea correcto (8080 por defecto)
3. Verifica que el modelo esté cargado

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

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un issue o pull request.

## Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

## Autor

TraducePDF - 2024
