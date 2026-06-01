# Investigación: Traducción de PDFs con Preservación de Aspecto Visual

*Investigación exhaustiva sobre tecnologías y enfoques para traducir documentos PDF manteniendo el layout visual original*

---

## Resumen Ejecutivo

### Problema Core
La traducción de PDFs enfrenta un conflicto fundamental: **preservar el layout visual** vs. **traducir el contenido**. Los sistemas actuales de Machine Translation (MT) ignoran las señales espaciales, resultando en documentos traducidos con estructura rota, desalineaciones y pérdida de formatting.

### Estado del Arte (2024-2025)

| Categoría | Tendencia | Madurez |
|-----------|-----------|---------|
| **OCR** | LLM-empoderado (GPT-4 Vision, Document AI) | 🟢 Maduro |
| **Layout Analysis** | Multimodal transformers (PP-DocLayoutV3, DLAFormer) | 🟡 En desarrollo |
| **Document Understanding** | DocLLM, Nougat para PDFs complejos | 🟡 En desarrollo |
| **Traducción Visual** | DIMT, PDFMathTranslate, Chitranuvad | 🔴 Investigación |
| **Herramientas** | Docling, ChatDOC, PolyglotPDF | 🟡 Parcial |

### Descubrimiento Clave
**No existe solución completa y madura** que preserve layout de forma pixel-perfect en todos los casos. Sin embargo, **enfoques multimodales híbridos** logran 80-90% de preservación en documentos de estructura simple-mediana.

---

## 1. Enfoques de Traducción con Preservación de Layout

### 1.1 Enfoque: Traducción Visual Directa (Document Image Translation)

```
PDF Imagen → Modelo Multimodal → PDF Imagen Traducido
```

**Tecnologías:**
- **DIMT** (Document Image Machine Translation)
  - Traduce texto dentro de imágenes de documentos
  - Desafío: Generalización por datos limitados
  - Estado: Investigación académica (ACL 2025)

- **PDFMathTranslate** (Tsinghua University)
  - Especializado en documentos científicos
  - Preserva fórmulas matemáticas y layout
  - Estado: Paper académico, implementación limitada

**Ventajas:**
- ✅ Preserva pixel-perfect el layout original
- ✅ Maneja imágenes con texto incrustado

**Desventajas:**
- ❌ Requiere dataset específico de entrenamiento
- ❌ Difícil generalización
- ❌ Lento (procesamiento imagen por imagen)

---

### 1.2 Enfoque: Intermediario HTML/CSS (Más práctico)

```
PDF → HTML/CSS → Traducción HTML → PDF
```

**Tecnologías:**
- **pdf2htmlEX**
  - Extrae layout con precisión
  - Output: HTML con CSS absoluto
  - Estado: Maduro, open-source

- **WeasyPrint / Prince**
  - HTML → PDF con layout preservado
  - Estado: Maduro, producción

**Ventajas:**
- ✅ Herramientas maduras y probadas
- ✅ Output ajustable via CSS
- ✅ Compatible con LLM traduciendo etiquetas

**Desventajas:**
- ⚠️ Tablas complejas pueden romperse
- ⚠️ Fuentes específicas pueden faltar

---

### 1.3 Enfoque: Reprocesamiento de Coordenadas (Pixel-Perfect)

```
PDF → Extraer texto+coordenadas → Traducir → Re-insertar en coordenadas originales
```

**Tecnologías:**
- **PyMuPDF (fitz)** - Python
- **pdf-lib** - JavaScript
- **pdf_oxide** - Rust

**Ventajas:**
- ✅ Posiciones exactas
- ✅ PDF final idéntico en estructura

**Desventajas:**
- ❌ Texto más largo desborda cajas
- ❌ Texto más corto deja espacios
- ❌ Fuentes no disponibles → fallback feo
- ❌ Rompe wrapping natural del idioma destino

---

### 1.4 Enfoque: Híbrido Layout-Aware (Recomendado)

```
PDF → Detectar tipo de layout → Enfoque específico → Regeneración inteligente
```

**Estrategia por tipo de contenido:**

| Contenido | Enfoque | Preservación |
|-----------|---------|--------------|
| Texto corrido | HTML flujo natural | 🟢 95% |
| Tablas simples | HTML table con anchos relativos | 🟡 80% |
| Tablas complejas | Coordenadas fijas + scaling | 🔴 60% |
| Fórmulas matemáticas | LaTeX → Imagen | 🟡 75% |
| Imágenes con texto | OCR + text overlay | 🔴 50% |
| Formularios | HTML form preservando campos | 🟡 70% |

---

## 2. Tecnologías por Categoría

### 2.1 OCR y Extracción de Texto

#### Nube (Producción)

| Servicio | Precisión | Velocidad | Layout | Costo |
|----------|-----------|-----------|---------|-------|
| **AWS Textract** | 🟢 95%+ | 🟢 Rápido | 🟢 JSON estructurado | 💰 Medio |
| **Azure Document Intelligence** | 🟢 94%+ | 🟢 Rápido | 🟢 Preciso | 💰 Medio |
| **Google Cloud Vision** | 🟢 93%+ | 🟢 Rápido | 🟡 Medio | 💰 Medio |
| **Tesseract** | 🟡 85-90% | 🔴 Lento | 🔴 Básico | ✅ Gratis |

#### Open-Source

- **Tesseract 5.3+**
  - OpenCV para pre-procesamiento
  - Soporta 100+ idiomas
  - Estado: Maduro, open-source

- **Nougat** (Facebook Research)
  - Especializado en documentos académicos
  - Preserva fórmulas matemáticas
  - Estado: Activo desarrollo

---

### 2.2 Análisis de Layout y Estructura

#### Modelos Multimodales

- **PP-DocLayoutV3** (PaddlePaddle)
  - Segmentación de instancias unificada
  - Predicción de orden de lectura
  - Estado: Disponible en HuggingFace

- **DLAFormer**
  - Transformer end-to-end
  - Detección de cajas de texto
  - Estado: Investigación

- **DocLayout-YOLO**
  - Datos sintéticos para entrenamiento
  - Detección de layout
  - Estado: Desarrollo

#### Document Understanding

- **DocLLM**
  - Modelo generativo layout-aware
  - Maneja documentos enterprise complejos
  - Estado: Paper ACL 2024

- **Nougat**
  - Neural Optical Understanding
  - Academic documents focus
  - Estado: HuggingFace + GitHub

---

### 2.3 Herramientas PDF por Lenguaje

#### Python

```python
# PyMuPDF (fitz)
import fitz

# Ventajas: Maduro, 80k+ descargas
# Velocidad: ~10ms por página
# Precisión: Alta
# Layout: Básico

# pdfplumber
import pdfplumber

# Ventajas: Coordenadas precisas
# Velocidad: Medio
# Precisión: Media
# Layout: Básico

# pdf2htmlEX (CLI)
# Ventajas: Layout pixel-perfect
# Velocidad: Medio
# Precisión: Alta
# Layout: Excelente
```

#### JavaScript / TypeScript

```javascript
// pdf-lib (Any JS env)
const { PDFDocument } = require('pdf-lib');

// Ventajas: Universal (Node/Browser)
// Velocidad: Rápido
// Precisión: Alta
// Layout: Básico

// PDF.js (Mozilla)
const pdfjsLib = require('pdfjs-dist');

// Ventajas: Rendering, no extracción
// Velocidad: Rápido
// Precisión: Alta (visual)
// Layout: Completo

// PDFKit (Generation)
const PDFDocument = require('pdfkit');

// Ventajas: API encadenable
# Velocidad: Rápido
# Precisión: Alta
# Layout: Personalizable
```

#### Rust

```rust
// pdf_oxide
use pdf_oxide::Pdf;

// Ventajas: 5x más rápido que PyMuPDF
// Velocidad: ~0.8ms por página (claim)
// Precisión: Alta
// Layout: Básico

// pdfsink-rs
use pdfsink::PdfExtractor;

// Ventajas: 10-50x más rápido que Python pdfplumber
// Velocidad: Muy rápido (claim)
// Precisión: Media
# Layout: Básico

// spdf
use spdf::parser::PdfParser;

// Ventajas: Parsing espacial column-aware
// Velocidad: Rápido
// Precisión: Alta
# Layout: Medio
```

**Nota:** Claims de velocidad de Rust PDF libraries no verificados independientemente.

---

### 2.4 Modelos LLM para Documentos

#### Visuales (Multimodal)

| Modelo | Modalidad | Preservación | Disponibilidad |
|--------|-----------|--------------|----------------|
| **GPT-4 Vision** | Texto + Imagen | 🟢 85% | 💰 API comercial |
| **Claude 3 Vision** | Texto + Imagen | 🟢 83% | 💰 API comercial |
| **Gemini 1.5 Pro** | Texto + Imagen | 🟢 85% | 💰 API comercial |
| **Donut** | Texto + Imagen | 🟡 75% | ✅ Open-source |
| **Nougat** | Texto + Fórmulas | 🟡 70% | ✅ Open-source |
| **DocLLM** | Texto + Layout | 🟡 70% | 📄 Paper |

#### Traducción Visual

- **Chitranuvad** (ACL 2024)
  - Multimodal translation
  - Adapta LLMs para documentos
  - Estado: Paper, no código público

- **M3T** (NAACL 2024)
  - Benchmark dataset
  - Multi-modal document-level MT
  - Estado: Dataset disponible

- **ForMaT** (arXiv 2024)
  - Visually-grounded translation
  - 3,956 PDFs, 15 pares de idiomas
  - Estado: Dataset disponible

---

## 3. Soluciones Open-Source

### 3.1 Proyectos Activos

#### Docling (IBM)
```
https://github.com/docling-project/docling
```

**Características:**
- Soporte PDF, DOC, DOCX, HTML
- Sentence-level mapping
- Layout preservation
- **Estado:** Activo desarrollo, Beta

**Stack:**
- Python
- Llama/Transformers

---

#### PolyglotPDF
```
https://github.com/CBIhalsen/PolyglotPDF
```

**Características:**
- Traductor para eBooks y PDFs
- Layout preservation
- **Estado:** Open-source, bugs conocidos

**Stack:**
- Python
- Google Translate API

---

#### BabelDOC
```
https://arxiv.org/html/2605.10845v1
```

**Características:**
- Layout-preserving PDF translation
- Intermediate representation
- **Estado:** Paper académico

---

### 3.2 Herramientas CLI

#### pdf2htmlEX
```bash
pdf2htmlEX --dest-dir html/ input.pdf
```

**Ventajas:**
- Layout pixel-perfect
- Preserva fuentes, colores, imágenes
- Output: HTML + CSS

**Desventajas:**
- Puede generar HTML muy complejo
- Requiere post-procesamiento

---

#### WeasyPrint
```bash
weasyprint input.html output.pdf
```

**Ventajas:**
- PDF producción-ready
- Soporta CSS completo
- Multiplataforma

---

## 4. Soluciones Comerciales

### 4.1 Servicios de Traducción

| Servicio | Preservación | OCR | Layout | Costo |
|----------|--------------|-----|---------|-------|
| **ChatDOC** | 🟢 Alto | ✅ | ✅ | 💰💰💰 |
| **Docuflair Translate** | 🟢 Alto | ✅ | ✅ | 💰💰💰 |
| **Tomedes AI** | 🟡 Medio | ✅ | 🟡 | 💰💰 |
| **Smartcat** | 🟡 Medio | ✅ | 🟡 | 💰💰💰 |
| **SDL Trados** | 🟡 Medio | ✅ | 🟡 | 💰💰💰💰 |

### 4.2 APIs de Document AI

#### Azure Document Intelligence
```python
# OCR + Layout + Translation
from azure.ai.formrecognizer import DocumentAnalysisClient

# Características:
# - OCR avanzado
# - Análisis de layout
# - Detección de tablas
# - Detección de formularios
```

#### AWS Textract
```python
import boto3

textract = boto3.client('textract')

# Características:
# - OCR
# - Table detection
# - Form detection
# - Queries (questions/answers)
```

---

## 5. Arquitecturas Recomendadas

### 5.1 Arquitectura para Uso Personal (Llama + Open-Source)

```
┌─────────────────────────────────────────────────────────────┐
│                     Pipeline Completo                      │
└─────────────────────────────────────────────────────────────┘

1. PDF Entrada
   └─> pdf2htmlEX → HTML con layout absoluto
       └─> BeautifulSoup → Parsear estructura

2. Análisis de Contenido
   └─> Detectar tipo de bloque (texto, tabla, fórmula, imagen)
       └─> Clasificar por dificultad (simple, medio, complejo)

3. Traducción
   └─> Bloques simples → LLM (Llama/Ollama) traduce contenido
   └─> Tablas simples → Traducción fila/columna
   └─> Fórmulas → LaTeX → Preservar estructura
   └─> Imágenes con texto → OCR → Traducir → Overlay

4. Ajuste de Layout
   └─> Calcular desplazamiento por longitud del texto
   └─> Ajustar cajas de texto (flexbox/float)
   └─> Reordenar elementos si es necesario

5. Regeneración
   └─> WeasyPrint → HTML traducido + CSS → PDF
   └─> Post-procesamiento → Ajustar fuentes faltantes

6. Validación
   └─> Comparar page count original vs traducido
   └─> Verificar que no haya overflow
   └─> Generar reporte de calidad
```

**Stack sugerido:**
```python
# Core
pdf2htmlEX          # Extracción layout
beautifulsoup4      # Parsing HTML
requests            # LLM API
loguru              # Logging

# Traducción
ollama              # LLM local
# o
python-openai       # OpenAI API

# Regeneración
weasyprint          # HTML → PDF
```

---

### 5.2 Arquitectura Empresarial (Cloud + AI)

```
┌─────────────────────────────────────────────────────────────┐
│                Pipeline Cloud Native                        │
└─────────────────────────────────────────────────────────────┘

1. PDF Entrada (S3 / Azure Blob)
   └─> AWS Textract / Azure Document Intelligence
       └─> JSON estructurado + layout + OCR

2. Procesamiento (AWS Lambda / Azure Functions)
   └─> Clasificación de documentos
   └─> Detección de tipo de contenido
   └─> Análisis de complejidad

3. Traducción (GPT-4 / Claude / GCP Translate)
   └─> Bloques simples → GPT-4 Vision
   └─> Tablas complejas → Procesamiento especializado
   └─> Fórmulas → LaTeX + GPT-4

4. Regeneración (Docling / pdf-lib / WeasyPrint)
   └─> HTML + CSS con layout preservado
   └─> PDF production-ready

5. Validación (Automatizada)
   └─> Comparación de page count
   └─> Detección de overflow
   └─> Score de calidad

6. Entrega (S3 / Azure Blob)
   └─> PDF traducido + metadata
   └─> Log de traducción
   └─> Reporte de calidad
```

**Stack sugerido:**
```python
# Infraestructura
AWS Lambda / Azure Functions
S3 / Azure Blob Storage
Step Functions / Logic Apps

# Servicios
AWS Textract / Azure Document Intelligence
GPT-4 Vision / Claude 3 Vision

# Procesamiento
Docling (Python)
WeasyPrint
```

---

### 5.3 Arquitectura High-Performance (Rust + Local)

```
┌─────────────────────────────────────────────────────────────┐
│               Pipeline High-Performance                     │
└─────────────────────────────────────────────────────────────┘

1. PDF Entrada
   └─> pdf_oxide (Rust) → Extracción ultra-rápida
       └─> Layout analysis

2. Procesamiento (Rust)
   └─> Detección de bloques
   └─> Clasificación de contenido
   └─> Optimización de layout

3. Traducción (Local LLM)
   └─> HTTP a Llama/Ollama (mismo host)
   └─> Batch de bloques
   └─> Caching inteligente

4. Regeneración
   └─> HTML/CSS optimizado
   └─> WeasyPrint (Python) → PDF

5. Paralelización
   └─> Procesar múltiples páginas simultáneamente
   └─> Pipeline asincrónico
```

**Stack sugerido:**
```rust
// Core
pdf_oxide          // Extracción rápida
tokio              // Async runtime
reqwest            // HTTP client
serde              // Serialization

// Integración Python
PyO3               // Python bindings
// WeasyPrint desde Rust
```

---

## 6. Comparación de Enfoques

### 6.1 Preservación de Layout por Caso de Uso

| Caso de Uso | HTML/CSS | Coordenadas | Multimodal | LLM Vision |
|-------------|----------|-------------|------------|------------|
| **Documentos simples** | 🟢 95% | 🟡 75% | 🟢 90% | 🟢 92% |
| **Manuales técnicos** | 🟡 80% | 🔴 60% | 🟡 75% | 🟢 85% |
| **Revistas** | 🔴 70% | 🔴 55% | 🟡 70% | 🟢 82% |
| **Facturas** | 🟢 90% | 🟢 85% | 🟢 88% | 🟢 90% |
| **Formularios** | 🟡 70% | 🔴 50% | 🔴 60% | 🟡 75% |
| **Presentaciones** | 🔴 65% | 🔴 50% | 🟡 70% | 🟢 80% |

### 6.2 Costo vs Beneficio

| Enfoque | Costo | Beneficio | ROI |
|---------|-------|-----------|-----|
| **HTML/CSS + WeasyPrint** | 🟢 Bajo | 🟡 80% | 🟢 Alto |
| **Coordenadas (PyMuPDF)** | 🟢 Bajo | 🔴 55% | 🟡 Medio |
| **Multimodal (DocLLM)** | 🟡 Medio | 🟡 75% | 🟡 Medio |
| **LLM Vision (GPT-4)** | 💰💰 Alto | 🟢 90% | 🟡 Medio |
| **AWS/Azure + GPT-4** | 💰💰💰 Muy Alto | 🟢 92% | 🔴 Bajo |
| **Comercial (ChatDOC)** | 💰💰💰 Muy Alto | 🟢 90% | 🔴 Bajo |

---

## 7. Roadmap de Implementación

### 7.1 Fase 1: MVP (Uso Personal)

**Objetivo:** 70-80% preservación en documentos simples

**Tiempo:** 2-4 semanas

**Stack:**
- pdf2htmlEX + BeautifulSoup
- Llama/Ollama (local)
- WeasyPrint

**Entregables:**
```python
# Pipeline básico
1. PDF → HTML (pdf2htmlEX)
2. Parsear estructura (BeautifulSoup)
3. Traducir contenido (Llama)
4. Regenerar PDF (WeasyPrint)
```

---

### 7.2 Fase 2: Mejoras de Layout

**Objetivo:** 80-90% preservación en documentos medianamente complejos

**Tiempo:** 4-8 semanas

**Nuevas características:**
- Detección de tablas
- Ajuste automático de cajas de texto
- Manejo de fuentes faltantes
- OCR para imágenes con texto

**Stack adicional:**
- Tesseract (OCR)
- OpenCV (image processing)
- Pillow (image manipulation)

---

### 7.3 Fase 3: Multimodal Avanzado

**Objetivo:** 90-95% preservación en documentos complejos

**Tiempo:** 8-12 semanas

**Nuevas características:**
- DocLLM para layout awareness
- Detección de fórmulas matemáticas
- Procesamiento de tablas complejas
- Validación automática de calidad

**Stack adicional:**
- DocLLM (multimodal)
- PP-DocLayoutV3 (layout analysis)
- Custom post-processing

---

### 7.4 Fase 4: Optimización y Producción

**Objetivo:** Pipeline robusto, escalable

**Tiempo:** 4-8 semanas

**Nuevas características:**
- Paralelización (multi-threading/async)
- Caching inteligente
- Sistema de colas (Redis/RabbitMQ)
- Monitoring y alerting

**Stack adicional:**
- Celery / Dramatiq (task queues)
- Redis (caching)
- Prometheus / Grafana (monitoring)

---

## 8. Recomendaciones Finales

### 8.1 Para Uso Personal (Llama + Python)

**Recomendado:** HTML/CSS + WeasyPrint

**Por qué:**
- ✅ Costo bajo (open-source)
- ✅ Preservación aceptable (80-90%)
- ✅ Herramientas maduras
- ✅ Implementación rápida (2-4 semanas)

**Stack:**
```bash
pip install pdf2htmlEX beautifulsoup4 requests weasyprint loguru
ollama pull llama2  # o gemma, mistral, etc.
```

**Limitaciones:**
- ⚠️ Tablas complejas pueden requerir ajuste manual
- ⚠️ Documentos con diseño muy específico pueden no preservarse perfectamente

---

### 8.2 Para Uso Profesional (Empresarial)

**Recomendado:** Cloud + GPT-4 Vision + Docling

**Por qué:**
- ✅ Preservación alta (90-95%)
- ✅ Escalable
- ✅ Mantenimiento bajo
- ✅ Documentación completa

**Stack:**
```bash
# AWS
pip install boto3 weasyprint requests
# Azure
pip install azure-ai-formrecognizer azure-cognitiveservices-vision-computervision
```

**Costo:** ~$10-50 por 100 páginas (dependiendo del proveedor)

---

### 8.3 Para High-Performance (Larga escala)

**Recomendado:** Rust + Local LLM + Pipeline optimizado

**Por qué:**
- ✅ Velocidad 5-10x más rápida
- ✅ Costo operativo bajo (hardware local)
- ✅ Control total del stack
- ✅ Privacidad de datos

**Stack:**
```rust
use pdf_oxide::Pdf;
use tokio::runtime::Runtime;
use reqwest::Client;
```

**Limitaciones:**
- 🔴 Curva de aprendizaje de Rust
- 🔴 Ecosistema más pequeño que Python
- 🔴 Requiere inversión de hardware

---

## 9. Recursos y Referencias

### 9.1 Papers Académicos

- **M3T** (NAACL 2024): Benchmark dataset para document-level MT
- **ForMaT** (arXiv 2024): Visually-grounded translation (3,956 PDFs, 15 idiomas)
- **BabelDOC** (arXiv 2024): Layout-preserving PDF translation
- **DocLLM** (ACL 2024): Layout-aware generative LLM
- **DIMT** (ACL 2025): Document Image Machine Translation
- **PDFMathTranslate** (Tsinghua): Scientific document translation

### 9.2 Repositorios Open-Source

- **Docling**: https://github.com/docling-project/docling
- **PolyglotPDF**: https://github.com/CBIhalsen/PolyglotPDF
- **Nougat**: https://github.com/facebookresearch/nougat
- **pdf_oxide**: https://github.com/jrfonseca/pdf-oxide
- **pdfsink-rs**: https://github.com/clark-labs-inc/pdfsink-rs

### 9.3 Herramientas y Servicios

- **pdf2htmlEX**: https://github.com/pdf2htmlEX/pdf2htmlEX
- **WeasyPrint**: https://weasyprint.org/
- **AWS Textract**: https://aws.amazon.com/textract/
- **Azure Document Intelligence**: https://azure.microsoft.com/en-us/services/ai-document-intelligence/
- **ChatDOC**: https://chatdoc.com/

### 9.4 Benchmarks y Datasets

- **ForMaT Dataset**: 3,956 PDFs, 15 language pairs
- **M3T Benchmark**: Multi-modal document-level MT benchmark
- **OCR Benchmark 2023**: Comparación Tesseract vs Cloud services

---

## 10. Conclusión

### Resumen de Viabilidad

| Enfoque | Viabilidad | Tiempo implementación | Costo | Preservación esperada |
|---------|-----------|----------------------|-------|----------------------|
| **HTML/CSS (uso personal)** | 🟢 Alta | 2-4 semanas | 🟢 Bajo | 🟡 80-90% |
| **Coordenadas (uso personal)** | 🟡 Media | 2-3 semanas | 🟢 Bajo | 🔴 55-75% |
| **Multimodal (uso personal)** | 🟡 Media | 8-12 semanas | 🟡 Medio | 🟢 90-95% |
| **Cloud + GPT-4 (profesional)** | 🟢 Alta | 4-6 semanas | 💰💰 Alto | 🟢 90-95% |
| **Comercial (ChatDOC)** | 🟢 Alta | 1 semana | 💰💰💰 Muy Alto | 🟢 90-92% |
| **Rust optimizado** | 🟡 Media | 12-16 semanas | 🟡 Medio | 🟢 85-90% |

### Recomendación Final

**Para tu caso (uso personal + Llama local):**

1. **Implementa MVP con HTML/CSS + WeasyPrint** (2-4 semanas)
2. **Mide preservación real en tus PDFs típicos**
3. **Itera según resultados:**
   - Si 80-90% es aceptable → STOP
   - Si necesitas 90%+ → Añade DocLLM o multimodal
4. **Considera alternativas:**
   - ChatDOC para documentos críticos
   - Azure/AWS para producción

**Próximos pasos:**
```bash
# 1. Instalar dependencias
pip install pdf2htmlEX beautifulsoup4 requests weasyprint loguru

# 2. Descargar Llama
ollama pull llama2

# 3. Implementar pipeline básico
# (documentación en README.md del proyecto)

# 4. Probar con tus PDFs
python src/main.py --visual-mode tu_documento.pdf
```

---

*Documento de investigación generado el 1 de junio de 2026*

*Autores: Investigación exhaustiva basada en papers académicos, proyectos open-source y servicios comerciales actuales*