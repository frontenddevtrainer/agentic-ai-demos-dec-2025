"""Agent for formatting the final project plan document."""

from typing import Dict, Any
from models.state import ProjectPlanState


class PlanFormatter:
    """Formats all generated components into a final project plan document."""

    def format(self, state: ProjectPlanState) -> Dict[str, Any]:
        """
        Format the complete project plan.

        Args:
            state: Current workflow state with all generated components

        Returns:
            Updated state with formatted final plan
        """
        try:
            sections = []

            # Title
            sections.append("# PROJECT PLAN")
            sections.append("")

            # 1. Product Requirements
            sections.append("## 1) Product Requirements")
            sections.append("")

            # Functional Requirements
            sections.append("### Functional Requirements")
            sections.append("")
            sections.append(state.get("functional_requirements", ""))
            sections.append("")

            # Non-Functional Requirements
            sections.append("### Non-Functional Requirements (NFRs)")
            sections.append("")
            sections.append(state.get("non_functional_requirements", ""))
            sections.append("")

            # Out of Scope
            sections.append("### Out of Scope (for MVP)")
            sections.append("")
            sections.append(state.get("out_of_scope", ""))
            sections.append("")

            # 2. Epics, Stories, and Acceptance Criteria
            sections.append("## 2) Epics, Stories, and Acceptance Criteria")
            sections.append("")

            epics = state.get("epics", [])
            stories = state.get("user_stories", [])

            for epic in epics:
                sections.append(f"### {epic['id']} — {epic['title']}")
                sections.append("")
                sections.append(epic['description'])
                sections.append("")

                # Find stories for this epic
                epic_stories = [s for s in stories if s.get("epic_id") == epic["id"]]

                for story in epic_stories:
                    sections.append(f"#### {story['id']}. {story['title']}")
                    sections.append("")
                    sections.append(f"**Story:** {story['story']}")
                    sections.append("")
                    sections.append("**Acceptance Criteria:**")
                    for criterion in story["acceptance_criteria"]:
                        sections.append(f"- {criterion}")
                    sections.append("")

            # 3. Delivery Plan
            sections.append("## 3) Delivery Plan (Phases)")
            sections.append("")

            phases = state.get("delivery_phases", [])
            for phase in phases:
                sections.append(f"### {phase['name']}")
                sections.append("")
                sections.append(phase['description'])
                sections.append("")

                # List stories in this phase
                for story_id in phase['stories']:
                    # Find the story
                    story = next((s for s in stories if s['id'] == story_id), None)
                    if story:
                        sections.append(f"- {story['title']} ({story_id})")

                sections.append("")

            # 4. Definition of Done
            sections.append("## 4) Definition of Done (DoD) for Stories")
            sections.append("")
            sections.append(state.get("definition_of_done", ""))
            sections.append("")

            final_plan = "\n".join(sections)

            return {
                "final_plan": final_plan,
                "current_step": "completed",
            }

        except Exception as e:
            return {
                "errors": [f"Plan formatting error: {str(e)}"],
                "current_step": "error",
            }
