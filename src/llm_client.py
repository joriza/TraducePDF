"""
Cliente para comunicación con Llama Server.

Este módulo proporciona una interfaz para comunicarse con un servidor
Llama local y realizar traducciones de texto.
"""

import time
from typing import Optional, Dict, Any
import requests
from loguru import logger


class LLMClientError(Exception):
    """Excepción base para errores del cliente LLM."""
    pass


class LLMConnectionError(LLMClientError):
    """Error de conexión con el servidor LLM."""
    pass


class LLMTranslationError(LLMClientError):
    """Error durante la traducción."""
    pass


class LLMClient:
    """Cliente para comunicarse con Llama Server."""

    def __init__(
        self,
        base_url: str = "http://localhost:8080/v1",
        timeout: int = 300,
        max_retries: int = 3,
        retry_delay: float = 5.0
    ):
        """
        Inicializa el cliente LLM.

        Args:
            base_url: URL base del servidor Llama.
            timeout: Timeout en segundos para las peticiones.
            max_retries: Número máximo de reintentos.
            retry_delay: Delay entre reintentos en segundos.
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self._model_id: Optional[str] = None

        logger.info(f"LLMClient inicializado: {base_url}")

    def check_connection(self) -> bool:
        """
        Verifica si el servidor está disponible.

        Returns:
            True si el servidor está disponible, False en caso contrario.
        """
        try:
            response = requests.get(
                f"{self.base_url}/models",
                timeout=10
            )
            if response.status_code == 200:
                logger.info("Conexión con Llama Server exitosa")
                return True
            else:
                logger.warning(f"Servidor respondió con status {response.status_code}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error de conexión: {e}")
            return False

    def get_loaded_model(self) -> Optional[str]:
        """
        Obtiene el ID del modelo cargado en el servidor.

        Returns:
            ID del modelo o None si no se pudo obtener.
        """
        try:
            response = requests.get(
                f"{self.base_url}/models",
                timeout=10
            )
            response.raise_for_status()

            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                # Usar el primer modelo disponible
                model_id = data["data"][0]["id"]
                self._model_id = model_id
                logger.info(f"Modelo detectado: {model_id}")
                return model_id
            else:
                logger.warning("No se encontraron modelos en la respuesta")
                return None

        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener modelo: {e}")
            return None

    def translate(
        self,
        text: str,
        source_lang: str = "inglés",
        target_lang: str = "español",
        model_id: Optional[str] = None
    ) -> str:
        """
        Traduce un texto usando el modelo LLM.

        Args:
            text: Texto a traducir.
            source_lang: Idioma de origen.
            target_lang: Idioma de destino.
            model_id: ID del modelo a usar (si None, usa el detectado).

        Returns:
            Texto traducido.

        Raises:
            LLMConnectionError: Si hay error de conexión.
            LLMTranslationError: Si hay error en la traducción.
        """
        # Obtener modelo si no se especificó
        if model_id is None:
            if self._model_id is None:
                self._model_id = self.get_loaded_model()
            model_id = self._model_id

        if model_id is None:
            raise LLMConnectionError(
                "No se pudo determinar el modelo a usar. "
                "Verifica que el servidor esté ejecutándose."
            )

        # Construir el prompt
        prompt = self._build_translation_prompt(text, source_lang, target_lang)

        # Realizar la petición con reintentos
        for attempt in range(self.max_retries):
            try:
                return self._make_request(prompt, model_id)
            except (requests.exceptions.RequestException, LLMTranslationError) as e:
                if attempt < self.max_retries - 1:
                    logger.warning(
                        f"Intento {attempt + 1}/{self.max_retries} falló. "
                        f"Reintentando en {self.retry_delay}s... Error: {e}"
                    )
                    time.sleep(self.retry_delay)
                else:
                    logger.error(f"Todos los intentos fallaron: {e}")
                    raise LLMTranslationError(f"Error después de {self.max_retries} intentos: {e}")

        # Este punto nunca debería alcanzarse, pero añadimos el raise para satisfacer al type checker
        raise LLMTranslationError("Número inesperado de reintentos agotados sin lanzar excepción")

    def _build_translation_prompt(
        self,
        text: str,
        source_lang: str,
        target_lang: str
    ) -> str:
        """
        Construye el prompt para el modelo.

        Args:
            text: Texto a traducir.
            source_lang: Idioma de origen.
            target_lang: Idioma de destino.

        Returns:
            Prompt completo.
        """
        prompt = f"""Traduce el siguiente texto del {source_lang} al {target_lang}.

INSTRUCCIONES IMPORTANTES:
1. Traduce SOLO el contenido de texto, manteniendo el formato exacto de las etiquetas.
2. NO traduzcas las etiquetas [Página X, Bloque Y].
3. REESCRIBE el texto traducido de forma prolija y natural:
   - Elimina saltos de línea innecesarios
   - NO cortes oraciones arbitrariamente en medio de una línea
   - Usa párrafos completos y bien estructurados
   - Mantén el significado original pero mejora la legibilidad
4. Si hay términos técnicos que no tienen traducción directa, déjalos en inglés.
5. Responde con el texto traducido en un formato limpio y legible.

Texto a traducir:
{text}

Respuesta:"""

        return prompt

    def _make_request(self, prompt: str, model_id: str) -> str:
        """
        Realiza la petición al servidor Llama.

        Args:
            prompt: Prompt a enviar.
            model_id: ID del modelo.

        Returns:
            Respuesta del modelo.

        Raises:
            LLMConnectionError: Si hay error de conexión.
            LLMTranslationError: Si hay error en la respuesta.
        """
        try:
            logger.debug(f"Enviando petición al modelo {model_id}...")

            response = requests.post(
                f"{self.base_url}/chat/completions",
                json={
                    "model": model_id,
                    "messages": [
                        {
                            "role": "system",
                            "content": "Eres un traductor profesional experto en traducir documentos técnicos del inglés al español. Tu traducción debe ser precisa, mantener el formato y ser fiel al significado original."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    "temperature": 0.3,  # Baja temperatura para traducciones más consistentes
                    "max_tokens": 4096,
                },
                timeout=self.timeout
            )

            response.raise_for_status()

            data = response.json()

            # Extraer la respuesta
            if "choices" in data and len(data["choices"]) > 0:
                translated_text = data["choices"][0]["message"]["content"].strip()
                logger.debug(f"Respuesta recibida ({len(translated_text)} caracteres)")
                return translated_text
            else:
                raise LLMTranslationError("Formato de respuesta inválido: no se encontró 'choices'")

        except requests.exceptions.Timeout:
            raise LLMConnectionError(f"Timeout después de {self.timeout} segundos")
        except requests.exceptions.ConnectionError as e:
            raise LLMConnectionError(f"Error de conexión: {e}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                raise LLMConnectionError("Endpoint no encontrado. Verifica la URL del servidor.")
            elif e.response.status_code == 500:
                raise LLMTranslationError("Error interno del servidor LLM")
            else:
                raise LLMTranslationError(f"Error HTTP {e.response.status_code}: {e}")
        except (KeyError, IndexError) as e:
            raise LLMTranslationError(f"Error al parsear respuesta: {e}")
        except requests.exceptions.RequestException as e:
            raise LLMConnectionError(f"Error en la petición: {e}")

    def get_model_info(self) -> Dict[str, Any]:
        """
        Obtiene información detallada del modelo cargado.

        Returns:
            Diccionario con información del modelo.
        """
        try:
            response = requests.get(
                f"{self.base_url}/models",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error al obtener información del modelo: {e}")
            return {}
