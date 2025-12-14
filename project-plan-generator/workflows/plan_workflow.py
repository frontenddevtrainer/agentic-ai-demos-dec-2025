"""LangGraph workflow for orchestrating the project plan generation."""

from typing import Literal
from langgraph.graph import StateGraph, END
from models.state import ProjectPlanState
from agents import (
    RequirementAnalyzer,
    EpicGenerator,
    StoryGenerator,
    DeliveryPlanner,
    PlanFormatter,
)


def create_plan_workflow() -> StateGraph:
    """
    Create the LangGraph workflow for project plan generation.

    The workflow follows these steps:
    1. Analyze requirements → structure into functional, NFRs, out-of-scope
    2. Generate epics → high-level feature areas
    3. Generate user stories → detailed stories with acceptance criteria for each epic
    4. Plan delivery → organize stories into MVP/V1/V2+ phases
    5. Format plan → create final formatted document

    Returns:
        Compiled StateGraph workflow
    """
    # Initialize agents
    requirement_analyzer = RequirementAnalyzer()
    epic_generator = EpicGenerator()
    story_generator = StoryGenerator()
    delivery_planner = DeliveryPlanner()
    plan_formatter = PlanFormatter()

    # Create workflow graph
    workflow = StateGraph(ProjectPlanState)

    # Add nodes (agents)
    workflow.add_node("analyze_requirements", requirement_analyzer.analyze)
    workflow.add_node("generate_epics", epic_generator.generate)
    workflow.add_node("generate_stories", story_generator.generate)
    workflow.add_node("plan_delivery", delivery_planner.plan)
    workflow.add_node("format_plan", plan_formatter.format)

    # Define the workflow edges
    workflow.set_entry_point("analyze_requirements")

    workflow.add_edge("analyze_requirements", "generate_epics")
    workflow.add_edge("generate_epics", "generate_stories")
    workflow.add_edge("generate_stories", "plan_delivery")
    workflow.add_edge("plan_delivery", "format_plan")
    workflow.add_edge("format_plan", END)

    # Compile and return
    return workflow.compile()


def should_continue(state: ProjectPlanState) -> Literal["continue", "error", "end"]:
    """
    Determine if workflow should continue based on current state.

    Args:
        state: Current workflow state

    Returns:
        Decision on next step
    """
    current_step = state.get("current_step", "")

    if state.get("errors"):
        return "error"
    elif current_step == "completed":
        return "end"
    else:
        return "continue"
