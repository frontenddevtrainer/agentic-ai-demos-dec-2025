"""Agent for planning delivery phases and defining Definition of Done."""

import json
from typing import Dict, Any, List
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.state import ProjectPlanState, DeliveryPhase
from utils import get_llm


DELIVERY_PLANNING_PROMPT = """You are a senior product manager and delivery lead. Your task is to organize user stories into delivery phases.

Original requirement:
{requirement}

User Stories:
{user_stories_summary}

Your task:
1. Organize stories into delivery phases (MVP, V1, V2+)
2. Create a Definition of Done (DoD) that applies to all stories

DELIVERY PHASES:
- MVP: Core functionality needed for initial launch. Focus on the most critical user journeys.
- V1: Enhanced features that improve the product significantly but aren't required for initial launch.
- V2+: Advanced features, optimizations, and nice-to-haves for future iterations.

Consider:
- Dependencies between features
- User value and impact
- Technical complexity
- Risk and uncertainty
- "Walking skeleton" principle - get end-to-end flow working first

Return your response as JSON:
{{
  "delivery_phases": [
    {{
      "name": "MVP",
      "description": "Brief description of MVP scope and goals",
      "stories": ["EPIC-A.1", "EPIC-A.2", "EPIC-B.1"]
    }},
    {{
      "name": "V1",
      "description": "Brief description",
      "stories": ["EPIC-C.1", "EPIC-D.1"]
    }},
    {{
      "name": "V2+",
      "description": "Future enhancements",
      "stories": ["EPIC-E.1"]
    }}
  ],
  "definition_of_done": [
    "Acceptance criteria met + test cases pass",
    "Analytics event for key actions",
    "Accessibility checks for core flows",
    "Error states handled (offline, retry, invalid input)",
    "Security review for sensitive operations",
    "Documentation updated"
  ]
}}

IMPORTANT: Return ONLY the JSON object, no additional text or markdown formatting.
"""


class DeliveryPlanner:
    """Plans delivery phases and creates Definition of Done."""

    def __init__(self):
        self.llm = get_llm(temperature=0.4)
        self.prompt = ChatPromptTemplate.from_template(DELIVERY_PLANNING_PROMPT)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def plan(self, state: ProjectPlanState) -> Dict[str, Any]:
        """
        Create delivery plan from user stories.

        Args:
            state: Current workflow state

        Returns:
            Updated state with delivery phases and DoD
        """
        try:
            # Create summary of user stories for the prompt
            stories_summary = self._create_stories_summary(state.get("user_stories", []))

            result = self.chain.invoke({
                "requirement": state["requirement"],
                "user_stories_summary": stories_summary,
            })

            # Clean up and parse JSON
            json_str = self._extract_json(result)
            plan_data = json.loads(json_str)

            # Convert to DeliveryPhase format
            phases: List[DeliveryPhase] = []
            for phase_data in plan_data["delivery_phases"]:
                phase: DeliveryPhase = {
                    "name": phase_data["name"],
                    "description": phase_data["description"],
                    "stories": phase_data["stories"],
                }
                phases.append(phase)

            # Format Definition of Done
            dod_items = plan_data["definition_of_done"]
            dod = "\n".join(f"- {item}" for item in dod_items)

            return {
                "delivery_phases": phases,
                "definition_of_done": dod,
                "current_step": "delivery_planned",
            }

        except Exception as e:
            return {
                "errors": [f"Delivery planning error: {str(e)}"],
                "current_step": "error",
            }

    def _create_stories_summary(self, stories: List[Dict[str, Any]]) -> str:
        """Create a summary of all user stories for the prompt."""
        summary_lines = []
        for story in stories:
            summary_lines.append(f"[{story['id']}] {story['title']}")
            summary_lines.append(f"  Story: {story['story']}")
            summary_lines.append("")

        return "\n".join(summary_lines)

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

        # Find JSON object
        start = text.find("{")
        end = text.rfind("}") + 1

        if start == -1 or end == 0:
            raise ValueError("No JSON object found in response")

        return text[start:end]
