import os

from openai import OpenAI

BASE_URL = "https://libra-ai-interviews.services.ai.azure.com/api/projects/proj-default/openai/v1"

_client: OpenAI | None = None


def get_client() -> OpenAI:
    global _client
    if _client is None:
        api_key = (
            os.environ.get("OPENAI_KEY")
            or os.environ.get("OPEN_AI_KEY")
            or os.environ.get("OPENAI_API_KEY")
        )
        if not api_key:
            raise EnvironmentError("OPENAI_KEY not set in environment")
        _client = OpenAI(api_key=api_key, base_url=BASE_URL)
    return _client
