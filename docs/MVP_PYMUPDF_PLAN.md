# MVP con PyMuPDF - Plan de Implementación

## Stack (Opción 2 - Sin instalación externa)

```python
# Ya instalado:
PyMuPDF (fitz)        # Extracción HTML básico
beautifulsoup4       # Parsing HTML
requests             # LLM API
loguru               # Logging

# Nuevas dependencias:
weasyprint          # HTML → PDF
```

## Diferencia vs pdf2htmlEX

| Aspecto | pdf2htmlEX | PyMuPDF HTML |
|---------|------------|--------------|
| **Precisión layout** | 🟢 Pixel-perfect | 🟡 Básico |
| **Instalación** | 🔴 Externa | ✅ pip install |
| **Complejidad** | 🟡 Media | 🟢 Baja |
| **Preservación esperada** | 90%+ | 75-85% |

## Pipeline

```
PDF → PyMuPDF (HTML) → BeautifulSoup → LLM (traducir contenido) → WeasyPrint → PDF
```

## Implementación

### Paso 1: Instalar weasyprint
```bash
venv\Scripts\pip install weasyprint
```

### Paso 2: Crear módulo `html_extractor.py`
- Extraer HTML de PDF con PyMuPDF
- Guardar CSS básico

### Paso 3: Crear módulo `html_parser.py`
- Parsear HTML con BeautifulSoup
- Identificar contenido traducible

### Paso 4: Crear módulo `html_translator.py`
- Traducir contenido HTML manteniendo etiquetas
- Prompt específico para HTML

### Paso 5: Crear módulo `pdf_generator.py`
- Generar PDF desde HTML traducido
- Aplicar CSS para layout

### Paso 6: Integrar en CLI nueva
- `--layout-mode` flag para habilitar modo layout

## Próxima acción
Instalar weasyprint y comenzar implementación.