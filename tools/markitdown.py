import logging
import os
import socket
import re

from collections.abc import Generator
from typing import Any, Dict

from dify_plugin import Tool
from dify_plugin.errors.tool import ToolProviderCredentialValidationError
from dify_plugin.entities.tool import ToolInvokeMessage
from dify_plugin.file.file import File

from markitdown import MarkItDown, StreamInfo
from openai import OpenAI


logger = logging.getLogger(__name__)


class MarkitdownTool(Tool):

    def _invoke(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        yield from self.parser_file(tool_parameters)

    def parser_file(self, tool_parameters: Dict[str, Any]) -> Generator[ToolInvokeMessage, None, None]:
        """Parse file."""
        file: File = tool_parameters.get('file')

        if not re.match(r'^https?://', file.url):
            file.url = f"http://{os.getenv("EXPOSE_PLUGIN_DEBUGGING_HOST", self.get_local_ip())}{file.url}"

        if file is not None:
            extension_hint: str = file.extension
            if extension_hint is not None:
                extension_hint = extension_hint.strip().lower()
                if len(extension_hint) > 0:
                    if not extension_hint.startswith("."):
                        extension_hint = "." + extension_hint

            mime_type_hint: str = file.mime_type
            if mime_type_hint is not None:
                mime_type_hint = mime_type_hint.strip()
                if len(mime_type_hint) > 0:
                    if mime_type_hint.count("/") != 1:
                        logger.error(f"Invalid MIME type: {mime_type_hint}")
                        raise ToolProviderCredentialValidationError(
                            f"Invalid MIME type: {mime_type_hint}"
                        )

            stream_info: StreamInfo = None
            if (
                extension_hint is not None
                or mime_type_hint is not None
            ):
                stream_info = StreamInfo(
                    extension=extension_hint, mimetype=mime_type_hint
                )

            base_url = self.runtime.credentials.get("openai_base_url")
            api_key = self.runtime.credentials.get("openai_api_key")
            model = self.runtime.credentials.get("openai_model")

            if base_url and api_key and model:
                client = OpenAI(
                    base_url=base_url,
                    api_key=api_key
                )
                markitdown = MarkItDown(
                    llm_client=client, llm_model=model
                )
            else:
                markitdown = MarkItDown()

            result = markitdown.convert(
                file.url,
                stream_info=stream_info
            )

            yield self.create_text_message(result.markdown)
            yield self.create_json_message({
                "title": result.title,
                "text_content": result.text_content
            })
        else:
            logger.error(
                "file is required."
            )
            raise ToolProviderCredentialValidationError(
                "file is required."
            )

    @staticmethod
    def get_local_ip() -> str:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"
