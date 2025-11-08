from typing import Protocol


class AIProvider(Protocol):
    
    def generate_text(
        self, 
        prompt: str, 
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        ...