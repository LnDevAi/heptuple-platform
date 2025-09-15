"""
Client pour l'API DeepSeek (compatible OpenAI chat/completions)
"""
import os
import json
import logging
from typing import List, Dict, Optional, Any

import httpx

try:
    # Exécution depuis le répertoire backend
    from config import config as app_config  # type: ignore
except Exception:
    # Exécution depuis la racine du projet
    from backend.config import config as app_config  # type: ignore

logger = logging.getLogger(__name__)


class DeepSeekService:
    """Service pour interagir avec l'API DeepSeek."""

    def __init__(self,
                 api_key: Optional[str] = None,
                 api_base: Optional[str] = None,
                 model: Optional[str] = None,
                 request_timeout_seconds: Optional[int] = None):
        self.api_key = api_key or app_config.DEEPSEEK_API_KEY or os.getenv("DEEPSEEK_API_KEY", "")
        self.api_base = (api_base or app_config.DEEPSEEK_API_BASE or os.getenv("DEEPSEEK_API_BASE", "https://api.deepseek.com")).rstrip("/")
        self.model = model or app_config.DEEPSEEK_MODEL or os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        self.timeout = request_timeout_seconds or app_config.DEEPSEEK_TIMEOUT or int(os.getenv("DEEPSEEK_TIMEOUT", "30"))

        if not self.api_key:
            logger.warning("DEEPSEEK_API_KEY non configuré. Le service DeepSeek est inactif.")

        self._client = httpx.AsyncClient(
            base_url=self.api_base,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            },
            timeout=self.timeout
        )

    async def close(self) -> None:
        try:
            await self._client.aclose()
        except Exception:
            pass

    async def chat(self, messages: List[Dict[str, str]],
                   temperature: Optional[float] = 0.7,
                   max_tokens: Optional[int] = None,
                   stream: bool = False,
                   response_format: Optional[Dict[str, Any]] = None,
                   extra_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Appelle l'endpoint chat/completions de DeepSeek.

        Retourne la réponse brute JSON de l'API DeepSeek.
        """
        if not self.api_key:
            raise RuntimeError("DEEPSEEK_API_KEY manquant. Configurez la clé d'API pour utiliser DeepSeek.")

        payload: Dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if response_format is not None:
            payload["response_format"] = response_format
        if extra_params:
            payload.update(extra_params)

        try:
            url = "/chat/completions"
            logger.debug(f"Appel DeepSeek {url} payload={json.dumps(payload)[:500]}")
            resp = await self._client.post(url, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data
        except httpx.HTTPStatusError as e:
            detail = e.response.text if e.response is not None else str(e)
            logger.error(f"Erreur HTTP DeepSeek: {e} | {detail}")
            raise
        except Exception as e:
            logger.error(f"Erreur d'appel DeepSeek: {e}")
            raise

