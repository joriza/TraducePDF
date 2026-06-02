# Implementación MVP - Preservación de Layout (Rama 260601)

## Objetivo

Implementar MVP para traducir PDFs preservando el layout visual con 80-90% de precisión en documentos simples.

## Stack Tecnológico

```python
# Core
pdf2htmlEX          # Extracción layout pixel-perfect
beautifulsoup4      # Parsing HTML
requests            # LLM API
loguru              # Logging

# Traducción
ollama              # LLM local (gemma-4-e2b-it)

# Regeneración
weasyprint          # HTML → PDF con layout preservado
```

## Plan de Implementación

### Fase 1: Instalación y Configuración (Actual)

**Estado:** ✅ Completado

**Tareas:**
- [x] Instalar dependencias básicas
- [x] Crear estructura de proyecto
- [x] Configurar entorno virtual

**Próximo paso:** Instalar pdf2htmlEX

---

### Fase 2: Extracción de PDF a HTML

**Objetivo:** Convertir PDF a HTML preservando layout pixel-perfect

**Tareas:**
- [ ] Instalar pdf2htmlEX
- [ ] Probar extracción de PDF a HTML
- [ ] Validar output HTML
- [ ] Crear módulo `html_extractor.py`

**Script de prueba:**
```bash
pdf2htmlEX --dest-dir html/ input.pdf
```

---

### Fase 3: Parsing HTML

**Objetivo:** Parsear HTML para detectar estructura (títulos, párrafos, tablas)

**Tareas:**
- [ ] Crear módulo `html_parser.py`
- [ ] Detectar tipos de contenido (títulos, párrafos, listas, tablas)
- [ ] Extraer texto manteniendo contexto
- [ ] Clasificar dificultad de traducción

---

### Fase 4: Traducción con LLM

**Objetivo:** Traducir contenido HTML manteniendo etiquetas

**Tareas:**
- [ ] Crear prompt para traducción HTML
- [ ] Traducir solo contenido, NO etiquetas
- [ ] Manejar casos especiales (tablas, fórmulas)
- [ ] Validar que todas las etiquetas se preservan

---

### Fase 5: Regeneración de PDF

**Objetivo:** Convertir HTML traducido a PDF preservando layout

**Tareas:**
- [ ] Instalar weasyprint
- [ ] Crear módulo `pdf_generator.py`
- [ ] Generar PDF desde HTML
- [ ] Validar preservación de layout

---

### Fase 6: Integración y Testing

**Objetivo:** Pipeline completo de end-to-end

**Tareas:**
- [ ] Integrar todos los módulos
- [ ] Crear CLI nueva (o extender existente)
- [ ] Probar con documentos simples
- [ ] Medir preservación de layout
- [ ] Ajustar según resultados

---

## Pipeline Completo

```
PDF Input → pdf2htmlEX → HTML con layout
    ↓
html_parser.py → Detectar estructura
    ↓
llm_client.py → Traducir contenido
    ↓
pdf_generator.py → HTML traducido → PDF output
```

---

## Métricas de Éxito

| Métrica | Objetivo MVP |
|---------|-------------|
| Preservación de layout | 80-90% |
| Tiempo de traducción | 2-5 min por 10 páginas |
| Preservación de texto | 95%+ |
| Errores críticos | 0% |

---

## Archivos Nuevos

- `html_extractor.py` - Extracción PDF → HTML
- `html_parser.py` - Parsing y clasificación HTML
- `pdf_generator.py` - Regeneración HTML → PDF
- `main_layout.py` - Pipeline principal (alternativa o unificada)

---

## Próxima Acción

Instalar pdf2htmlEX y probar extracción básica.