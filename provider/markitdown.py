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
            if credentials["azure_document_intelligence_endpoint"]:
                markitdown_docintel_args: Dict[str, Any] = {}
                markitdown_docintel_args["docintel_endpoint"] = credentials["azure_document_intelligence_endpoint"]

                if credentials["azure_document_intelligence_credential"]:
                    markitdown_docintel_args["docintel_credential"] = credentials["azure_document_intelligence_credential"]

                if credentials["azure_document_intelligence_api_version"]:
                    markitdown_docintel_args["docintel_api_version"] = credentials["azure_document_intelligence_api_version"]

                if credentials["azure_api_key"]:
                    os.environ["AZURE_API_KEY"] = credentials["azure_api_key"]

                markitdown = MarkItDown(**markitdown_docintel_args)
            elif credentials["openai_api_key"] and credentials["openai_base_url"] and credentials["openai_model"]:
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
