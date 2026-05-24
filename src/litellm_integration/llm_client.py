"""
LiteLLM Client Wrapper

Unified interface for LLM calls across multiple providers (Anthropic, OpenAI, etc.)
"""

import logging
from typing import Optional, List, Dict, Any
from litellm import acompletion

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Wrapper around LiteLLM for unified LLM access.

    Supports:
    - Multiple providers (Anthropic, OpenAI, etc.)
    - Multiple models per provider
    - Caching and rate limiting (via LiteLLM)
    - Error handling and retries
    """

    def __init__(
        self,
        model: str,
        provider: str = "anthropic",
        temperature: float = 0.5,
        max_tokens: Optional[int] = None,
        **kwargs
    ):
        """
        Initialize LLM client.

        Args:
            model: Model name (e.g., "claude-3-5-sonnet-20241022")
            provider: Provider name (anthropic, openai, etc.)
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens in response
            **kwargs: Additional parameters for the model
        """
        self.model = model
        self.provider = provider
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.kwargs = kwargs

        logger.debug(f"Initialized LLMClient (model: {model}, provider: {provider}, temperature: {temperature})")

    async def call(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **options
    ) -> str:
        """
        Make async LLM call.

        Args:
            messages: List of messages in OpenAI format
            temperature: Override default temperature
            max_tokens: Override default max_tokens
            **options: Additional options

        Returns:
            Response text from the model

        Raises:
            Exception: If LLM call fails
        """
        try:
            # Build full model name with provider
            full_model = f"{self.provider}/{self.model}"

            # Use provided values or defaults
            temp = temperature if temperature is not None else self.temperature
            tokens = max_tokens if max_tokens is not None else self.max_tokens

            # Make async call
            response = await acompletion(
                model=full_model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens,
                **{**self.kwargs, **options}
            )

            # Extract response text
            response_text = response.choices[0].message.content

            logger.debug(f"LLM call successful (model: {self.model}, input_tokens: {len(str(messages))}, output_length: {len(response_text)})")

            return response_text

        except Exception as e:
            logger.error(f"LLM call failed (model: {self.model}, error_type: {type(e).__name__}): {e}")
            raise

    async def call_json(
        self,
        messages: List[Dict[str, str]],
        temperature: Optional[float] = None,
        **options
    ) -> Dict[str, Any]:
        """
        Make LLM call expecting JSON response.

        Args:
            messages: List of messages
            temperature: Override temperature
            **options: Additional options

        Returns:
            Parsed JSON response

        Raises:
            ValueError: If response is not valid JSON
        """
        import json

        response_text = await self.call(messages, temperature=temperature, **options)

        try:
            return json.loads(response_text)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON response: {e}")
            raise ValueError(f"Invalid JSON response: {response_text}") from e

    @staticmethod
    async def batch_call(
        clients: List["LLMClient"],
        messages: List[Dict[str, str]],
    ) -> List[str]:
        """
        Make multiple LLM calls in parallel.

        Args:
            clients: List of LLMClient instances
            messages: Messages for all calls

        Returns:
            List of responses in order
        """
        import asyncio

        tasks = [client.call(messages) for client in clients]
        return await asyncio.gather(*tasks)
