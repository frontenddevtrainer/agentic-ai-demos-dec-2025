#!/usr/bin/env python3
"""Main entry point for the project plan generator."""

import sys
import argparse
from pathlib import Path
from datetime import datetime
from models.state import ProjectPlanState
from workflows import create_plan_workflow


def load_requirement(requirement_input: str) -> str:
    """
    Load requirement from file or use as direct input.

    Args:
        requirement_input: File path or direct requirement text

    Returns:
        Requirement text
    """
    # Check if it's a file path
    path = Path(requirement_input)
    if path.exists() and path.is_file():
        return path.read_text(encoding="utf-8")
    else:
        # Treat as direct input
        return requirement_input


def save_plan(plan: str, output_path: str):
    """
    Save the generated plan to a file.

    Args:
        plan: The generated plan content
        output_path: Path to save the plan
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(plan, encoding="utf-8")
    print(f"\n✓ Plan saved to: {output_file}")


def main():
    """Main function to run the project plan generator."""
    parser = argparse.ArgumentParser(
        description="Generate comprehensive project plans from requirements using AI agents."
    )
    parser.add_argument(
        "requirement",
        help="Requirement text or path to requirement file"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file path (default: outputs/plan_TIMESTAMP.md)",
        default=None
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output showing agent progress"
    )

    args = parser.parse_args()

    try:
        # Load requirement
        if args.verbose:
            print("📋 Loading requirement...")
        requirement = load_requirement(args.requirement)

        if args.verbose:
            print(f"✓ Requirement loaded ({len(requirement)} characters)")
            print("\n🤖 Starting plan generation workflow...\n")

        # Create workflow
        workflow = create_plan_workflow()

        # Initialize state
        initial_state: ProjectPlanState = {
            "requirement": requirement,
            "functional_requirements": None,
            "non_functional_requirements": None,
            "out_of_scope": None,
            "epics": [],
            "user_stories": [],
            "delivery_phases": [],
            "definition_of_done": None,
            "current_step": "initialized",
            "errors": [],
            "final_plan": None,
        }

        # Run workflow
        final_state = workflow.invoke(initial_state)

        # Check for errors
        if final_state.get("errors"):
            print("❌ Errors occurred during generation:")
            for error in final_state["errors"]:
                print(f"  - {error}")
            sys.exit(1)

        # Get final plan
        final_plan = final_state.get("final_plan")
        if not final_plan:
            print("❌ No plan was generated")
            sys.exit(1)

        # Display or save plan
        if args.output:
            output_path = args.output
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"outputs/plan_{timestamp}.md"

        save_plan(final_plan, output_path)

        if args.verbose:
            print("\n" + "="*80)
            print("GENERATED PLAN")
            print("="*80)
            print(final_plan)

        print("\n✅ Plan generation completed successfully!")

    except KeyboardInterrupt:
        print("\n\n⚠️  Plan generation interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
