from openai import AzureOpenAI
import os
from dotenv import load_dotenv
from models.base_model import BaseModel
from typing import Any
load_dotenv()

class AzureOpenAIModel(BaseModel):

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.model_name = os.getenv("OPENAI_BASE_MODEL_NAME")
        self.api_type = os.getenv("OPENAI_API_TYPE")
        self.api_version = os.getenv("OPENAI_API_VERSION")
        self.base_model_name = os.getenv("OPENAI_BASE_MODEL_NAME")

        self.client = self._init_client()

    def _init_client(self) -> AzureOpenAI:
        return AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version
        )
    
    def chat(self, messages: list, tools: list = [], temperature: float = 0.4, extra_body: dict = {}) -> Any:
        # extra_body는 Azure OpenAI의 확장 파라미터(예: data_sources)를 전달하기 위해 사용됨
        create_kwargs = {
            "model": self.base_model_name,
            "messages": messages,
            "temperature": temperature,
        }

        # tools가 비어있으면 필드를 생략 (Azure OpenAI는 빈 리스트를 허용하지 않음)
        if tools and len(tools) > 0:
            create_kwargs["tools"] = tools

        if extra_body:
            create_kwargs["extra_body"] = extra_body

        return self.client.chat.completions.create(**create_kwargs)

    @property
    def get_client(self) -> AzureOpenAI:
        return self.client
        
    @property
    def get_model_name(self) -> str:
        return self.model_name

    @property
    def get_model_version(self) -> str:
        return self.api_version

