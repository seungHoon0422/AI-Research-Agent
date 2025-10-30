from abc import ABC, abstractmethod
from openai import AzureOpenAI
from typing import Any

class BaseModel(ABC):
    model_name: str

    @abstractmethod
    def get_client(self) -> AzureOpenAI:
        raise NotImplementedError("get_client method must be implemented")

    @abstractmethod
    def get_model_name(self) -> str:
        raise NotImplementedError("get_model_name method must be implemented")

    @abstractmethod
    def get_model_version(self) -> str:
        raise NotImplementedError("get_model_version method must be implemented")
    
    @abstractmethod
    def chat(self, messages: list, tools: list = [], temperature: float = 0.4, extra_body: dict = {}) -> Any:
        raise NotImplementedError("chat method must be implemented")