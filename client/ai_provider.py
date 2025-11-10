from typing import Protocol


class AIProvider(Protocol):
    
    async def generate_text(
        self, 
        prompt: str, 
    ) -> str:
        ...