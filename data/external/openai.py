

from openai import OpenAI


class OpenAIData:
    def __init__(self, key: str) :
        self.open_ai = OpenAI(key= key)