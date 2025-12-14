"""State models for the project plan generator workflow."""

from typing import TypedDict, List, Optional, Annotated
from operator import add


class Epic(TypedDict):
    """Represents an epic in the project plan."""
    id: str
    title: str
    description: str
    stories: List[str]


class UserStory(TypedDict):
    """Represents a user story with acceptance criteria."""
    id: str
    epic_id: str
    title: str
    story: str
    acceptance_criteria: List[str]


class DeliveryPhase(TypedDict):
    """Represents a delivery phase (MVP, V1, V2, etc.)."""
    name: str
    description: str
    stories: List[str]


class ProjectPlanState(TypedDict):
    """The state of the project plan generation workflow."""

    # Input
    requirement: str

    # Analyzed requirements
    functional_requirements: Optional[str]
    non_functional_requirements: Optional[str]
    out_of_scope: Optional[str]

    # Generated components
    epics: Annotated[List[Epic], add]
    user_stories: Annotated[List[UserStory], add]
    delivery_phases: Annotated[List[DeliveryPhase], add]
    definition_of_done: Optional[str]

    # Metadata
    current_step: str
    errors: Annotated[List[str], add]

    # Final output
    final_plan: Optional[str]
