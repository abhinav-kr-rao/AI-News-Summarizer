from pydantic import BaseModel
from typing import List

class UserProfile(BaseModel):
    name: str
    interests: List[str]
    technical_level: str # e.g. "Expert", "Intermediate", "Beginner"
    
    def get_prompt_description(self) -> str:
        return (
            f"User '{self.name}' is a {self.technical_level} in technology. "
            f"Their specific interests are: {', '.join(self.interests)}."
        )

# Default Profile - User should edit this
default_profile = UserProfile(
    name="Shashank",
    interests=[
        "Large Language Models (LLMs)",
        "Generative AI Agents",
        "OpenAI o1 and reasoning models",
        "Anthropic Claude updates",
        "AI Architecture and System Design",
        "Python and FastAi"
    ],
    technical_level="Expert"
)
