# Project Plan Generator

An intelligent LangGraph-based agentic AI system that generates comprehensive project plans from high-level requirements. This system uses multiple specialized AI agents working together to transform simple requirements into detailed, actionable project plans with epics, user stories, acceptance criteria, and delivery phases.

## Features

- 📋 **Requirement Analysis**: Automatically structures requirements into functional, non-functional, and out-of-scope categories
- 🎯 **Epic Generation**: Identifies and creates high-level feature areas
- 📝 **Story Creation**: Generates detailed user stories with Given/When/Then acceptance criteria
- 🚀 **Delivery Planning**: Organizes stories into MVP, V1, V2+ phases
- 📄 **Professional Output**: Produces ready-to-use project plans in markdown format
- 🤖 **Multi-Agent System**: Uses LangGraph to orchestrate specialized agents
- 🔄 **Flexible LLM Support**: Works with OpenAI GPT-4 or Anthropic Claude

## Architecture

The system uses a LangGraph workflow with the following specialized agents:

```
Requirement → Analyzer → Epic Generator → Story Generator → Delivery Planner → Formatter → Plan
```

### Agents

1. **Requirement Analyzer**: Structures raw requirements into categories
2. **Epic Generator**: Identifies major feature areas and capabilities
3. **Story Generator**: Creates detailed user stories with acceptance criteria
4. **Delivery Planner**: Organizes stories into delivery phases
5. **Plan Formatter**: Produces the final formatted document

## Installation

### Prerequisites

- Python 3.11 or higher
- Poetry (recommended) or pip
- OpenAI API key or Anthropic API key

### Setup

1. Clone or navigate to the project:

```bash
cd project-plan-generator
```

2. Install dependencies using Poetry:

```bash
poetry install
```

Or using pip:

```bash
pip install -r requirements.txt
```

3. Configure environment variables:

```bash
cp .env.example .env
```

Edit `.env` and add your API key:

```bash
# For Anthropic Claude (recommended)
ANTHROPIC_API_KEY=your_api_key_here
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022

# OR for OpenAI
# OPENAI_API_KEY=your_api_key_here
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4-turbo-preview
```

## Usage

### Basic Usage

Generate a plan from a requirement file:

```bash
poetry run python main.py examples/messaging_app_requirement.txt
```

Or provide the requirement directly:

```bash
poetry run python main.py "Create a task management app with team collaboration features"
```

### With Options

Save to a specific output file:

```bash
poetry run python main.py examples/messaging_app_requirement.txt -o my_plan.md
```

Enable verbose output to see agent progress:

```bash
poetry run python main.py examples/messaging_app_requirement.txt -v
```

### Command Line Options

- `requirement`: Requirement text or path to requirement file (required)
- `-o, --output`: Output file path (default: `outputs/plan_TIMESTAMP.md`)
- `-v, --verbose`: Enable verbose output showing agent progress
- `-h, --help`: Show help message

## Example Output

The system generates a comprehensive project plan including:

1. **Product Requirements**
   - Functional requirements organized by category
   - Non-functional requirements (security, performance, accessibility, etc.)
   - Out-of-scope items for future consideration

2. **Epics, Stories, and Acceptance Criteria**
   - High-level epics grouping related features
   - Detailed user stories following "As a [user], I can [action] so that [benefit]" format
   - Acceptance criteria using Given/When/Then format
   - Edge cases and error handling

3. **Delivery Plan**
   - MVP: Core functionality for initial launch
   - V1: Enhanced features
   - V2+: Advanced capabilities and optimizations

4. **Definition of Done**
   - Quality criteria applicable to all stories
   - Testing, accessibility, security requirements

## Project Structure

```
project-plan-generator/
├── agents/                    # Specialized AI agents
│   ├── requirement_analyzer.py
│   ├── epic_generator.py
│   ├── story_generator.py
│   ├── delivery_planner.py
│   └── plan_formatter.py
├── workflows/                 # LangGraph workflows
│   └── plan_workflow.py
├── models/                    # State and data models
│   └── state.py
├── utils/                     # Utilities
│   └── llm_factory.py
├── examples/                  # Example requirements
│   └── messaging_app_requirement.txt
├── outputs/                   # Generated plans (auto-created)
├── main.py                    # Entry point
├── pyproject.toml            # Poetry dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

## How It Works

1. **Input**: You provide a high-level requirement (text or file)

2. **Analysis**: The Requirement Analyzer structures it into:
   - Functional requirements
   - Non-functional requirements
   - Out-of-scope items

3. **Epic Generation**: The Epic Generator identifies major feature areas

4. **Story Creation**: For each epic, the Story Generator creates:
   - User stories in standard format
   - Detailed acceptance criteria
   - Edge cases and error scenarios

5. **Delivery Planning**: The Delivery Planner organizes stories into phases:
   - MVP (minimum viable product)
   - V1 (first full release)
   - V2+ (future enhancements)

6. **Formatting**: The Plan Formatter creates a polished markdown document

7. **Output**: A complete, ready-to-use project plan

## Customization

### Using Different LLM Models

Edit your `.env` file:

```bash
# For Claude Opus (more powerful, slower)
LLM_MODEL=claude-3-opus-20240229

# For GPT-4 Turbo
LLM_PROVIDER=openai
LLM_MODEL=gpt-4-turbo-preview
```

### Adjusting Agent Behavior

Each agent in the `agents/` directory has configurable prompts and temperature settings. You can modify:

- Prompt templates for different output styles
- Temperature values for more/less creative outputs
- Parsing logic for custom formats

### Adding New Agents

1. Create a new agent in `agents/`
2. Add it to `workflows/plan_workflow.py`
3. Update the state model in `models/state.py` if needed

## Best Practices

### Input Requirements

For best results, your input requirement should:

- Be clear and specific about the core functionality
- Mention key user types and their needs
- Include any critical constraints or requirements
- Specify the type of application (web, mobile, etc.)

### Good Examples

✅ "Create a task management app for remote teams with real-time collaboration, file attachments, and mobile support"

✅ "Build an e-commerce platform for handmade crafts with seller profiles, shopping cart, payment processing, and order tracking"

❌ "Make an app" (too vague)

❌ "Create Facebook" (too broad, needs more specifics)

## Troubleshooting

### Common Issues

**"No JSON found in response"**
- The LLM returned unexpected format
- Try running again or using a different model
- Check your API key is valid

**"Rate limit exceeded"**
- You've hit your API rate limit
- Wait a few moments and try again
- Consider upgrading your API plan

**"Module not found"**
- Dependencies not installed
- Run `poetry install` or `pip install -r requirements.txt`

### Verbose Mode

Use `-v` flag to see detailed agent progress:

```bash
poetry run python main.py examples/messaging_app_requirement.txt -v
```

## Development

### Running Tests

```bash
poetry run pytest
```

### Code Formatting

```bash
poetry run black .
poetry run ruff check .
```

### Adding Dependencies

```bash
poetry add package_name
```

## Contributing

Contributions are welcome! Areas for improvement:

- Additional agent types (technical architecture, API design, etc.)
- Support for more output formats (JSON, YAML, Jira import)
- Enhanced parsing and validation
- Interactive mode with human-in-the-loop
- Multi-language support

## License

MIT License - feel free to use this in your projects!

## Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent workflow orchestration
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [Anthropic Claude](https://www.anthropic.com/) / [OpenAI GPT-4](https://openai.com/) - Language models

## Support

For issues, questions, or contributions, please open an issue on GitHub.

---

**Happy Planning! 🚀**
