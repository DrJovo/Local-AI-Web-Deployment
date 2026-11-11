import math
from typing import Literal
from pydantic import ConfigDict, BaseModel, Field, field_validator, model_validator
from . import ai_core


data = ai_core.get_ollama_data()

# Define limits based on ollama config data
MAX_TOTAL_CHARS = math.ceil(int(data.get("OLLAMA_CONTEXT_LENGTH", 2048)) * 0.37) * 10
MAX_TOTAL_MESSAGES = int(data.get("max_messages", 200))


class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["user", "assistant"]
    content: str = Field(min_length=0)
    tokens: int
    characters: int

    @field_validator('characters')
    @classmethod
    def check_limit(cls, value):
        if value > MAX_TOTAL_CHARS:
            raise ValueError(f'too many characters. The message contained {value} characters, which exceeds the limit of {MAX_TOTAL_CHARS}.')
        return value


class GuestChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=MAX_TOTAL_MESSAGES)
    model: Literal["qwen3.5:9b", "llama3.2:3b"]
    thinking: bool

    @model_validator(mode="after")
    def check_total_size(self):
        total = sum(len(m.content) for m in self.messages)
        if total > MAX_TOTAL_CHARS:
            raise ValueError(f"The conversation is {total:,} characters; the limit is {MAX_TOTAL_CHARS:,}. Start a new chat or shorten the message. Old messages will be forgotten to save memory.")
        return self