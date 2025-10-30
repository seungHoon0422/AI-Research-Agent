import os
from models.azure_openai_model import AzureOpenAIModel
from typing import Any

class Model:

    def __init__(self):
        self.model_runner = None

    def init_model(self):
        model_provider = os.getenv("MODEL_PROVIDER")
        if model_provider == "azure-openai":
            self.model_runner = AzureOpenAIModel()
        else:
            raise ValueError(f"Invalid model provider: {model_provider}")
    
    def client(self):
        return self.model_runner.client

    def model_name(self):
        return self.model_runner.model_name

    def base_model_name(self):
        return self.model_runner.base_model_name

    def api_type(self):
        return self.model_runner.api_type

    def api_version(self):
        return self.model_runner.api_version
    
    def chat(self, messages: list, tools: list = [], temperature: float = 0.4, extra_body: dict = {}) -> Any:
        return self.model_runner.chat(messages, tools, temperature, extra_body)

model = Model()

def init_model():
    model.init_model()