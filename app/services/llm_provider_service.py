from ollama import Client
from typing import List, Dict, Optional, Union
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class LLMProviderService:
    def __init__(self):
        self.client = Client(host=settings.OLLAMA_HOST)
        self.model_name = settings.LLM_MODEL
        self.small_model_name = settings.SMALL_LLM_MODEL

    async def chat(
        self,
        messages: List[Dict[str, str]],
        use_small: bool = False
    ) -> Union[object, Dict]:
        """
        Send messages to the Ollama model and return either the raw response object or an error dict.
        Pass use_small=True to use the smaller LLM model.
        """
        model_to_use = self.small_model_name if use_small else self.model_name
        try:
            # Ollama Client.chat may be blocking; wrap or use threads if necessary
            response = self.client.chat(
                model=model_to_use,
                messages=messages
            )
            return response
        except Exception as e:
            logger.error("Error communicating with LLM: %s", e)
            return {
                "error": str(e),
                "message": {"role": "assistant", "content": "Sorry, I couldn't process that."}
            }

    async def generate_response(
        self,
        prompt: str,
        history: Optional[List[Dict[str, str]]] = None,
        use_small: bool = False
    ) -> str:
        """
        Build a single-turn chat completion for the given prompt,
        with optional history, and return the assistant's content.
        """
        messages: List[Dict[str, str]] = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": prompt})

        response_obj = await self.chat(messages, use_small=use_small)

        # If the response is an error dict, pull from its message field
        if isinstance(response_obj, dict) and "error" in response_obj:
            msg = response_obj.get("message", {})
            return msg.get("content", "Sorry, an error occurred.")

        # Otherwise assume it's the Ollama response object with a .message attribute
        msg = getattr(response_obj, "message", None)
        if isinstance(msg, dict):
            return msg.get("content", "")
        # If msg is an object with content
        content = getattr(msg, "content", None)
        if isinstance(content, str):
            return content

        logger.error("Unexpected LLM response format: %r", response_obj)
        return "Sorry, an unexpected error occurred with the LLM."

# Singleton instance
llm_service = LLMProviderService()
