# Rules Extraction and Integration Agentic System

This system implements an advanced multi-agent workflow for extracting, validating, and integrating truck operation rules using the CrewAI framework.

## Architecture

The system is built around a crew of specialized AI agents that work together in a sequential process:

1. **Parameter Identification**: Identifies critical parameters that affect truck operations
2. **Rule Extraction**: Derives operational rules based on the identified parameters
3. **Rule Integration**: Ensures new rules integrate properly with existing systems
4. **Rule Validation**: Verifies the correctness and consistency of the rules
5. **Rule Formatting**: Prepares the rules for deployment in production systems

## Agents

The system employs the following specialist agents:

- **Truck Operation Analyst**: Expert in day-to-day truck operations
- **Lead Truck Operation Analyst**: Senior expert providing oversight
- **Machinery Professor**: Academic expert on engineering principles
- **Chief QA Engineer**: Validates rules for consistency and accuracy
- **Data Engineer**: Formats rules for system integration

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env to include your OPENAI_API_KEY
   ```

3. Configure agents and tasks:
   - Update configuration in `config/agents.yaml`
   - Update task definitions in `config/tasks.yaml`

## Usage

```python
from crew.crew import RulesExtractionAndIntegrationCrew

# Initialize the crew
rules_crew = RulesExtractionAndIntegrationCrew()

# Run the crew workflow
results = rules_crew.crew().kickoff()

# Access the formatted rules
formatted_rules = results.output.new_rules
```

## Configuration

### Agent Configuration Example

```yaml
truck_operation_analyst:
  role: "Truck Operation Analyst"
  goal: "Identify key parameters affecting truck operations"
  backstory: "You are an expert in analyzing truck operations with 15 years of experience..."
```

### Task Configuration Example

```yaml
identify_parameters_task:
  description: "Identify and document all critical parameters for truck operations"
  expected_output: "A structured list of parameters with descriptions and units"
```

## Logs

Execution logs are stored in the `logs` directory with a unique run ID for each execution.
