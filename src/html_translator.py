"""
Traductor de contenido HTML usando LLM local.

Este módulo traduce el contenido de bloques HTML manteniendo las etiquetas
y estructura para preservar el layout.
"""

import re
from loguru import logger
from typing import List, Dict

from llm_client import LLMClient, LLMConnectionError, LLMTranslationError
from html_parser import HTMLContentBlock


class HTMLTranslator:
    """Traductor de contenido HTML usando LLM local."""

    def __init__(self, llm_client: LLMClient):
        """
        Inicializa el traductor.

        Args:
            llm_client: Cliente LLM configurado.
        """
        self.llm_client = llm_client

    def translate_html_blocks(
        self,
        html_blocks: List[HTMLContentBlock],
        batch_size: int = 5
    ) -> List[HTMLContentBlock]:
        """
        Traduce bloques HTML manteniendo etiquetas.

        Args:
            html_blocks: Lista de bloques HTML a traducir.
            batch_size: Número de bloques a traducir por lote.

        Returns:
            Lista de bloques HTML traducidos.
        """
        translated_blocks = []

        # Agrupar bloques traducibles en lotes
        translatable_blocks = [
            block for block in html_blocks if block.is_translatable
        ]

        logger.info(f"Traduciendo {len(translatable_blocks)} bloques en lotes de {batch_size}")

        # Procesar en lotes
        for i in range(0, len(translatable_blocks), batch_size):
            batch = translatable_blocks[i:i + batch_size]

            try:
                # Crear prompt para el lote
                prompt = self._build_batch_translation_prompt(batch)

                # Traducir con LLM
                response = self.llm_client.translate(prompt)

                # Parsear respuesta
                translated_batch = self._parse_batch_response(response, batch)

                translated_blocks.extend(translated_batch)

                logger.info(f"Lote {i // batch_size + 1}: {len(translated_batch)} bloques traducidos")

            except (LLMConnectionError, LLMTranslationError) as e:
                logger.error(f"Error al traducir lote {i // batch_size + 1}: {e}")
                # Usar bloques originales como fallback
                translated_blocks.extend(batch)

        # Agregar bloques no traducibles sin cambios
        for block in html_blocks:
            if not block.is_translatable:
                translated_blocks.append(block)

        logger.info(f"Traducción completada: {len(translated_blocks)} bloques totales")
        return translated_blocks

    def _build_batch_translation_prompt(
        self,
        blocks: List[HTMLContentBlock]
    ) -> str:
        """
        Construye el prompt para traducir un lote de bloques HTML.

        Args:
            blocks: Lista de bloques a traducir.

        Returns:
            Prompt completo.
        """
        prompt = """Traduce el siguiente contenido HTML del inglés al español.

INSTRUCCIONES CRÍTICAS:

1. Traduce SOLO el contenido de texto dentro de las etiquetas.
2. NO traduzcas las etiquetas HTML (<div>, <span>, etc.).
3. NO cambies atributos HTML (style, class, etc.).
4. Mantén EXACTAMENTE la estructura de etiquetas.
5. Traduce cada bloque separado por [Bloque X] marca.
6. Si no puedes traducir un bloque, mantén el texto original.

FORMATO DE RESPUESTA REQUERIDO:
[Bloque 1]
<div>texto traducido</div>

[Bloque 2]
<span>texto traducido</span>

Ejemplo:
[Bloque 1]
<div class="page">Página traducida</div>

[Bloque 2]
<span style="left:100pt">Texto traducido</span>

CONTENIDO A TRADUCIRIR:
"""

        # Agregar bloques al prompt
        for i, block in enumerate(blocks, 1):
            prompt += f"\n[Bloque {i}]\n{block.html}\n"

        prompt += "\nRespuesta (SALIDA HTML MANTENIENDO ETIQUETAS):"

        return prompt

    def _parse_batch_response(
        self,
        response: str,
        original_blocks: List[HTMLContentBlock]
    ) -> List[HTMLContentBlock]:
        """
        Parsea la respuesta del LLM para extraer bloques traducidos.

        Args:
            response: Respuesta del LLM.
            original_blocks: Bloques originales para referencia.

        Returns:
            Lista de bloques HTML traducidos.
        """
        translated_blocks = []

        # Dividir por [Bloque X] marcadores
        blocks = re.split(r'\[Bloque\s+\d+\]', response)

        # Cada bloque (después del primero) es un bloque traducido
        for i, html_block in enumerate(blocks[1:], 1):  # Saltar el primero que es vacío
            if not html_block.strip():
                continue

            if i - 1 < len(original_blocks):
                original = original_blocks[i - 1]

                # Crear nuevo bloque con HTML traducido
                translated_block = HTMLContentBlock(
                    html=html_block.strip(),
                    text_content=self._extract_text_from_html(html_block),
                    is_translatable=True,
                    block_type=original.block_type,
                    position=original.position
                )

                translated_blocks.append(translated_block)

        logger.debug(f"Parseados {len(translated_blocks)} bloques de {len(original_blocks)}")
        return translated_blocks

    def _extract_text_from_html(self, html: str) -> str:
        """
        Extrae texto de un bloque HTML.

        Args:
            html: Bloque HTML.

        Returns:
            Texto extraído.
        """
        # Remover etiquetas HTML para obtener texto
        text = re.sub(r'<[^>]+>', '', html)
        return text.strip()

    def translate_single_block(self, block: HTMLContentBlock) -> HTMLContentBlock:
        """
        Traduce un solo bloque HTML.

        Args:
            block: Bloque a traducir.

        Returns:
            Bloque traducido.
        """
        if not block.is_translatable:
            return block

        try:
            # Prompt para bloque único
            prompt = self._build_single_block_prompt(block)

            # Traducir
            response = self.llm_client.translate(prompt)

            # Extraer HTML traducido (remover marca)
            html_translated = response.replace("[HTML_TRADUCIDO]", "").strip()

            # Crear bloque traducido
            translated_block = HTMLContentBlock(
                html=html_translated,
                text_content=self._extract_text_from_html(html_translated),
                is_translatable=True,
                block_type=block.block_type,
                position=block.position
            )

            return translated_block

        except (LLMConnectionError, LLMTranslationError) as e:
            logger.error(f"Error al traducir bloque: {e}")
            return block  # Fallback al original

    def _build_single_block_prompt(self, block: HTMLContentBlock) -> str:
        """
        Construye prompt para traducir un solo bloque.

        Args:
            block: Bloque a traducir.

        Returns:
            Prompt completo.
        """
        prompt = f"""Traduce el contenido HTML del inglés al español.

INSTRUCCIONES CRÍTICAS:
1. Traduce SOLO el texto dentro de las etiquetas HTML.
2. NO traduzcas las etiquetas (<div>, <span>, style, etc.).
3. Mantén EXACTAMENTE la estructura HTML.

Bloque HTML:
{block.html}

Respuesta (HTML con etiquetas manteniendo traducción):
[HTML_TRADUCIDO]
"""

        return prompt