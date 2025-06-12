import os
from typing import Any, Dict

from dify_plugin import ToolProvider
from dify_plugin.errors.tool import ToolProviderCredentialValidationError

from markitdown import MarkItDown, DocumentConverterResult
from openai import OpenAI


class MarkitdownProvider(ToolProvider):
    """Markitdown provider"""

    def _validate_credentials(self, credentials: dict[str, Any]) -> None:
        try:
            if credentials["openai_api_key"] and credentials["openai_base_url"] and credentials["openai_model"]:
                client = OpenAI(
                    api_key=credentials["openai_api_key"],
                    base_url=credentials["openai_base_url"]
                )
                model = credentials["openai_model"]
                markitdown = MarkItDown(llm_client=client, llm_model=model)
            else:
                markitdown = MarkItDown()
            result = markitdown.convert("test_file/hello.jpeg")
            assert isinstance(result, DocumentConverterResult)
        except Exception as e:
            raise ToolProviderCredentialValidationError(str(e)) from e
