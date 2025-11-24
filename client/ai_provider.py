from typing import Protocol


class AIProvider(Protocol):
    def generate_text(
        self,
        prompt: str,
    ) -> str: ...
