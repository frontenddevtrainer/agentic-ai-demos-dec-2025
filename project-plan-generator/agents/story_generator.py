"""Agent for generating user stories with acceptance criteria."""

import json
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.state import ProjectPlanState, UserStory
from utils import get_llm


STORY_GENERATION_PROMPT = """You are a senior product manager and agile coach. Your task is to generate detailed user stories with acceptance criteria for a specific epic.

Original requirement:
{requirement}

Functional requirements:
{functional_requirements}

EPIC to create stories for:
ID: {epic_id}
Title: {epic_title}
Description: {epic_description}

Generate 2-5 user stories for this epic. Each story should:
- Follow the format: "As a [user type], I can [action] so that [benefit]"
- Be specific and testable
- Include 3-5 clear acceptance criteria using Given/When/Then format
- Cover both happy paths and edge cases
- Consider accessibility, errors, and offline scenarios

Example acceptance criteria format:
- "Given [context], when [action], then [expected result]"
- "Given [edge case], when [user attempts], then [system responds with clear error]"

Return your response as a JSON array:
[
  {{
    "id": "{epic_id}.1",
    "title": "Short descriptive title",
    "story": "As a user, I can... so that...",
    "acceptance_criteria": [
      "Given..., when..., then...",
      "Given..., when..., then..."
    ]
  }},
  ...
]

IMPORTANT: Return ONLY the JSON array, no additional text or markdown formatting.
"""


class StoryGenerator:
    """Generates user stories with acceptance criteria for epics."""

    def __init__(self):
        self.llm = get_llm(temperature=0.6)
        self.prompt = ChatPromptTemplate.from_template(STORY_GENERATION_PROMPT)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def generate(self, state: ProjectPlanState) -> Dict[str, Any]:
        """
        Generate user stories for all epics.

        Args:
            state: Current workflow state

        Returns:
            Updated state with generated stories
        """
        all_stories: List[UserStory] = []
        updated_epics = []

        try:
            for epic in state.get("epics", []):
                # Generate stories for this epic
                stories = self._generate_stories_for_epic(
                    state["requirement"],
                    state.get("functional_requirements", ""),
                    epic
                )

                all_stories.extend(stories)

                # Update epic with story IDs
                updated_epic = epic.copy()
                updated_epic["stories"] = [s["id"] for s in stories]
                updated_epics.append(updated_epic)

            return {
                "user_stories": all_stories,
                "epics": updated_epics,
                "current_step": "stories_generated",
            }

        except Exception as e:
            return {
                "errors": [f"Story generation error: {str(e)}"],
                "current_step": "error",
            }

    def _generate_stories_for_epic(
        self,
        requirement: str,
        functional_requirements: str,
        epic: Dict[str, Any]
    ) -> List[UserStory]:
        """Generate stories for a single epic."""
        result = self.chain.invoke({
            "requirement": requirement,
            "functional_requirements": functional_requirements,
            "epic_id": epic["id"],
            "epic_title": epic["title"],
            "epic_description": epic["description"],
        })

        # Clean up and parse JSON
        json_str = self._extract_json(result)
        stories_data = json.loads(json_str)

        # Convert to UserStory format
        stories: List[UserStory] = []
        for story_data in stories_data:
            story: UserStory = {
                "id": story_data["id"],
                "epic_id": epic["id"],
                "title": story_data["title"],
                "story": story_data["story"],
                "acceptance_criteria": story_data["acceptance_criteria"],
            }
            stories.append(story)

        return stories

    def _extract_json(self, text: str) -> str:
        """Extract JSON from text that might contain markdown or other formatting."""
        text = text.strip()

        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split("\n")
            lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            text = "\n".join(lines)

        # Find JSON array
        start = text.find("[")
        end = text.rfind("]") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON array found in response")

        return text[start:end]
