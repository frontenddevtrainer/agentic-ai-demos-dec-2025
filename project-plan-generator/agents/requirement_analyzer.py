"""Agent for analyzing and structuring requirements."""

from typing import Dict, Any
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from models.state import ProjectPlanState
from utils import get_llm


REQUIREMENT_ANALYSIS_PROMPT = """You are a senior product manager and business analyst. Your task is to analyze the given requirement and structure it into clear categories.

Given requirement:
{requirement}

Analyze this requirement and provide:

1. FUNCTIONAL REQUIREMENTS
   - Break down into specific functional areas
   - Be comprehensive but concise
   - Group related features together

2. NON-FUNCTIONAL REQUIREMENTS (NFRs)
   - Security considerations
   - Privacy requirements
   - Performance targets
   - Reliability goals
   - Scalability needs
   - Accessibility standards
   - Compliance requirements

3. OUT OF SCOPE (for MVP)
   - Features that should be deferred
   - Nice-to-haves for future versions
   - Complex features that aren't essential

Format your response as follows:

## FUNCTIONAL REQUIREMENTS

[Your functional requirements here, organized by category]

## NON-FUNCTIONAL REQUIREMENTS

[Your NFRs here, organized by category]

## OUT OF SCOPE

[Items to defer, with brief reasoning]

Be thorough, practical, and consider real-world product development constraints.
"""


class RequirementAnalyzer:
    """Analyzes and structures product requirements."""

    def __init__(self):
        self.llm = get_llm(temperature=0.3)
        self.prompt = ChatPromptTemplate.from_template(REQUIREMENT_ANALYSIS_PROMPT)
        self.chain = self.prompt | self.llm | StrOutputParser()

    def analyze(self, state: ProjectPlanState) -> Dict[str, Any]:
        """
        Analyze the requirement and structure it.

        Args:
            state: Current workflow state

        Returns:
            Updated state with analyzed requirements
        """
        try:
            result = self.chain.invoke({"requirement": state["requirement"]})

            # Parse the structured output
            sections = self._parse_sections(result)

            return {
                "functional_requirements": sections.get("functional_requirements"),
                "non_functional_requirements": sections.get("non_functional_requirements"),
                "out_of_scope": sections.get("out_of_scope"),
                "current_step": "requirements_analyzed",
            }

        except Exception as e:
            return {
                "errors": [f"Requirement analysis error: {str(e)}"],
                "current_step": "error",
            }

    def _parse_sections(self, text: str) -> Dict[str, str]:
        """Parse the structured output into sections."""
        sections = {}
        current_section = None
        current_content = []

        for line in text.split("\n"):
            line = line.strip()

            if line.startswith("## FUNCTIONAL REQUIREMENTS"):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "functional_requirements"
                current_content = []
            elif line.startswith("## NON-FUNCTIONAL REQUIREMENTS"):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "non_functional_requirements"
                current_content = []
            elif line.startswith("## OUT OF SCOPE"):
                if current_section and current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = "out_of_scope"
                current_content = []
            elif current_section:
                current_content.append(line)

        # Don't forget the last section
        if current_section and current_content:
            sections[current_section] = "\n".join(current_content).strip()

        return sections
