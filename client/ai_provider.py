from typing import Protocol


class AIProvider(Protocol):
    
    def generate_text_async(
        self, 
        prompt: str,
    ) -> str:
        ...