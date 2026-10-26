from typing import Literal
from pydantic import BaseModel, Field
from pydantic import ConfigDict

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=12000)

class GuestChatRequest(BaseModel):
    messages: list[ChatMessage] = Field(min_length=1, max_length=200)