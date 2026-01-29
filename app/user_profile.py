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
    name="Abhinav",
    interests=[
        "Technology",
        "AI",
        "Software Engineering",
        "Programming",
        "Operating Systems",
        "Machine Learning",
        "Deep Learning",
        "Data Science",
        "Data Engineering",
        "Data Analysis",
        "Data Visualization",
        "Data Science",
        "Data Engineering",
        "Data Analysis",
        "Data Visualization",
        "Stock Market",
        "Finance",
    ],
    technical_level="Expert"
)
