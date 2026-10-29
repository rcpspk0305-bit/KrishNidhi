from typing import Literal
from pydantic import BaseModel, Field, ConfigDict


class AssistantMessage(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=4000)


class AssistantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    message: str = Field(min_length=1, max_length=4000)
    language: Literal["en", "te", "hi"] = "en"
    history: list[AssistantMessage] = Field(default_factory=list, max_length=12)


class AssistantResponse(BaseModel):
    reply: str
    language: Literal["en", "te", "hi"]
