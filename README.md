## Rules Extraction and Integration System

This application represents a sophisticated system for extracting, validating, and integrating operational rules using multi-agent AI collaboration. The system employs CrewAI to orchestrate a crew of specialized AI agents that work together to identify parameters, extract rules, integrate them, validate, and format them for application.

## Architecture Overview

The system is composed of three main components working in concert:

### 1. Backend API
- Python-based FastAPI application providing RESTful endpoints
- AI processing with CrewAI framework for orchestrating intelligent agents
- Sequential task execution pipeline with dependency management
- Machine learning models for rule extraction and validation:
  - Outlier detection algorithms (LocalOutlierFactor, IsolationForest, OneClassSVM)
  - Interpretable rule extraction models (FIGSClassifier, OptimalTreeClassifier, GreedyTreeClassifier)
- Data modeling through Pydantic schemas (Parameter, ParameterList, NewRuleList)
- Unique UUID generation for traceability of all processing sessions
- Comprehensive logging system for debugging and audit trails

### 2. Frontend
- React application (TypeScript) with component-based architecture
- Interactive rule management interface
- Visualization components for rule relationships and data patterns
- API integration layer for backend communication
- Serves static content via Nginx for optimal performance

### 3. Redis Cache
- Provides data persistence and caching for high throughput
- Enables efficient data sharing between components
- Serialization of complex data structures for storage
- Supports session management and temporary data storage

## Core Components

### CrewAI Agent System

The core of the application is the `RulesExtractionAndIntegrationCrew` which coordinates specialized AI agents:

- **Truck Operation Analyst**: Analyzes operations data and identifies patterns in truck operations
- **Lead Truck Operation Analyst**: Provides expert oversight and validates initial findings
- **Machinery Professor**: Contributes domain knowledge about equipment specifications and limitations
- **Data Engineer**: Formats and processes rule data for integration into systems
- **Chief QA Engineer**: Validates and verifies rules against established standards

Each agent is configured through YAML files and leverages the OpenAI API (default model: gpt-4o-mini) for specialized tasks. The system uses the CrewAI framework to manage agent interactions and sequential task processing.

### Agent Roles and Collaboration

The agents work together in a structured workflow:

1. **Truck Operation Analyst** begins the process by analyzing raw operational data
2. **Lead Truck Operation Analyst** reviews initial findings and adds expert context
3. **Machinery Professor** contributes technical constraints and domain expertise
4. **Chief QA Engineer** validates the combined rules against best practices
5. **Data Engineer** finalizes the rules into implementable formats

This multi-agent approach ensures comprehensive rule creation with built-in validation.

### Process Flow

The system follows a sequential process:
1. Parameter identification
2. Rule extraction
3. Rule integration
4. Validation and verification
5. Formatting rules for application

### Machine Learning Capabilities

The system utilizes multiple machine learning approaches:
- Outlier detection (LocalOutlierFactor, IsolationForest, OneClassSVM)
- Rule extraction models (FIGSClassifier, OptimalTreeClassifier, GreedyTreeClassifier)

## Setup and Installation

### Prerequisites
- Docker and Docker Compose
- OpenAI API key

### Installation Steps

1. Clone the repository
2. Create an `.env` file in the `api` directory with:
```
OPENAI_API_KEY=your_openai_api_key
```

3. Run the application:
```bash
./run.sh
```

### Docker configuration
The application uses multi-container Docker setup:

- `Frontend`: Builds from Node.js and deploys to Nginx
- `API`: Python 3.11 with scientific computing dependencies
- `Redis`: Alpine-based Redis instance

### Usage
Once running:

- Access the frontend at http://localhost:80
- API endpoints are available at http://localhost:8000
- Output logs are stored in the logs directory

### Development
The application is structured for extension and modification:

- Agent configurations in agents.yaml
- Task configurations in tasks.yaml
- Model implementations in utility modules

### Output

The system produces rule lists and validation outputs, which are stored as logs with unique UUIDs for traceability.