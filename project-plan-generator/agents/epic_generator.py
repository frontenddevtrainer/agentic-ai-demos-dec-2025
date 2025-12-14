"""Agent for generating epics from requirements."""

import json
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.state import ProjectPlanState, Epic
from utils import get_llm


EPIC_GENERATION_PROMPT = """You are a senior product manager skilled at breaking down requirements into epics.

Original requirement:
{requirement}

Functional requirements:
{functional_requirements}

Your task is to identify the key EPICS (large feature areas) that organize this work. Each epic should:
- Represent a significant feature area or capability
- Group related functionality together
- Be deliverable incrementally
- Have clear boundaries

Based on the example format, typical epics for applications include:
- Authentication & User Management
- Core functionality (the main feature)
- Sharing & Collaboration
- Media & Content handling
- Notifications & Communication
- Search & Discovery
- Privacy, Safety & Moderation
- Admin & Operations

Generate 5-8 epics that cover the functional requirements comprehensively.

Return your response as a JSON array of objects with this structure:
[
  {{
    "id": "EPIC-A",
    "title": "Authentication & Profiles",
    "description": "Brief description of what this epic encompasses"
  }},
  ...
]

IMPORTANT: Return ONLY the JSON array, no additional text or markdown formatting.
"""


class EpicGenerator:
    """Generates epics from analyzed requirements."""

    def __init__(self):
        self.llm = get_llm(temperature=0.5)
        self.prompt = ChatPromptTemplate.from_template(EPIC_GENERATION_PROMPT)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate(self, state: ProjectPlanState) -> Dict[str, Any]:
        """
        Generate epics from requirements.

        Args:
            state: Current workflow state

        Returns:
            Updated state with generated epics
        """
        try:
            result = self.chain.invoke({
                "requirement": state["requirement"],
                "functional_requirements": state.get("functional_requirements", ""),
            })

            # Clean up the result to extract JSON
            json_str = self._extract_json(result)
            epics_data = json.loads(json_str)

            # Convert to Epic TypedDict format
            epics: List[Epic] = []
            for epic_data in epics_data:
                epic: Epic = {
                    "id": epic_data["id"],
                    "title": epic_data["title"],
                    "description": epic_data.get("description", ""),
                    "stories": [],  # Will be populated by story generator
                }
                epics.append(epic)

            return {
                "epics": epics,
                "current_step": "epics_generated",
            }

        except Exception as e:
            return {
                "errors": [f"Epic generation error: {str(e)}"],
                "current_step": "error",
            }

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text that might contain markdown or other formatting."""
        text = text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json or ```)
            lines = lines[1:]
            # Remove last line (```)
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        # Find JSON array
        start = text.find("[")
        end = text.rfind("]") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON array found in response")

        return text[start:end]
