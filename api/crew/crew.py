"""
Rules Extraction and Integration System

This module implements an agentic system that extracts, validates, and integrates rules
for truck operations using a multi-agent workflow approach with CrewAI.

The system follows a sequential process:
1. Parameter identification
2. Rule extraction
3. Rule integration
4. Rule validation
5. Rule formatting
"""

from typing import List, Optional, Dict, Any
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os
import uuid
import logging
from pathlib import Path

from crew.rule_validation_agent import ChiefQAEngineerWithTask

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
if not os.environ.get('OPENAI_API_KEY'):
    raise EnvironmentError("OPENAI_API_KEY environment variable not set. Please configure it in your .env file.")


class Parameter(BaseModel):
    """Defines a single truck operation parameter with its metadata."""
    
    parameter: str = Field(..., description="Name of the parameter")
    description: str = Field(..., description="Detailed description of the parameter")
    unit: str = Field(..., description="Unit of measurement for the parameter")
    
    class Config:
        """Pydantic configuration."""
        schema_extra = {
            "example": {
                "parameter": "engine_temperature",
                "description": "Temperature of the engine during operation",
                "unit": "°C"
            }
        }
    

class ParameterList(BaseModel):
    """Collection of truck operation parameters."""
    
    parameters: List[Parameter] = Field(..., description="List of parameters")
    
    
class NewRuleList(BaseModel):
    """Collection of extracted or refined rules."""
    
    new_rules: List[str] = Field(..., description="List of rules")
       

@CrewBase
class RulesExtractionAndIntegrationCrew:
    """
    Crew responsible for extracting, validating and integrating operational rules for trucks.
    
    This crew leverages multiple expert agents to identify important parameters,
    extract operational rules, integrate them with existing systems, and ensure
    their correctness through validation.
    
    Attributes:
        agents_config (str): Path to the YAML configuration file for agents
        tasks_config (str): Path to the YAML configuration file for tasks
        llm (LLM): Language model instance used by the agents
    """
    
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    # Initialize LLM with appropriate settings
    llm = LLM(
        model="gpt-4o-mini", 
        temperature=0.1, 
        api_key=os.environ.get('OPENAI_API_KEY')
    ) 

    ### Agents ###
    @agent
    def truck_operation_analyst(self) -> Agent:
        """
        Create a truck operation analyst agent.
        
        This agent specializes in understanding truck operations and identifying
        key operational parameters and constraints.
        
        Returns:
            Agent: Configured truck operation analyst agent
        """
        return Agent(
            config=self.agents_config['truck_operation_analyst'],
            tools=[],
            verbose=True,
            memory=False,
            llm=self.llm
        )
    
    @agent
    def lead_truck_operation_analyst(self) -> Agent:
        """
        Create a lead truck operation analyst agent.
        
        This senior agent oversees the analysis process and provides expert 
        guidance on truck operations best practices.
        
        Returns:
            Agent: Configured lead truck operation analyst agent
        """
        return Agent(
            config=self.agents_config['lead_truck_operation_analyst'],
            tools=[],
            verbose=True,
            memory=False,
            llm=self.llm
        )
    
    @agent
    def machinery_professor(self) -> Agent:
        """
        Create a machinery professor agent.
        
        This agent has deep academic knowledge about machinery systems,
        engineering principles, and technical standards.
        
        Returns:
            Agent: Configured machinery professor agent
        """
        return Agent(
            config=self.agents_config['machinery_professor'],
            tools=[],
            verbose=True,
            memory=False,
            llm=self.llm
        )

    @agent
    def data_engineer(self) -> Agent:
        """
        Create a data engineer agent.
        
        This agent specializes in formatting and structuring rules data
        for optimal integration with existing systems.
        
        Returns:
            Agent: Configured data engineer agent
        """
        return Agent(
            config=self.agents_config['data_engineer'],
            tools=[],
            verbose=True,
            memory=False,
            llm=self.llm
        )

    ### Tasks ###
    @task
    def identify_parameters_task(self) -> Task:
        """
        Create a task to identify relevant operational parameters.
        
        This task focuses on discovering and documenting all parameters
        that are important for truck operations.
        
        Returns:
            Task: Configured parameter identification task
        """
        return Task(
            config=self.tasks_config['identify_parameters_task'],
            output_pydantic=ParameterList
        )
    
    @task
    def extract_rules_task(self) -> Task:
        """
        Create a task to extract rules based on identified parameters.
        
        This task uses the identified parameters to extract operational rules
        that should govern truck operations.
        
        Returns:
            Task: Configured rule extraction task
        """
        return Task(
            config=self.tasks_config['extract_rules_task'],
            context=[self.identify_parameters_task()],
            output_pydantic=NewRuleList
        )
    
    @task
    def integrate_rules_task(self) -> Task:
        """
        Create a task to integrate newly extracted rules with existing systems.
        
        This task ensures the new rules work well with existing operational frameworks.
        
        Returns:
            Task: Configured rule integration task
        """
        return Task(
            config=self.tasks_config['integrate_rules_task'],
            context=[self.extract_rules_task()],
            output_pydantic=NewRuleList
        )
    
    @task
    def format_rules_task(self) -> Task:
        """
        Create a task to format the final set of rules for implementation.
        
        This task structures the validated rules in a format suitable for
        deployment in production systems.
        
        Returns:
            Task: Configured rule formatting task
        """
        return Task(
            config=self.tasks_config['format_rules_task'],
            output_pydantic=NewRuleList
        )

    @crew
    def crew(self) -> Crew:
        """
        Create the complete RulesExtractionAndIntegrationCrew.
        
        Assembles all agents and tasks into a cohesive workflow for
        extracting, validating, and integrating truck operation rules.
        
        Returns:
            Crew: Configured crew ready for execution
        """
        try:
            # Create the QA validator agent and task
            chief_qa_validator = ChiefQAEngineerWithTask(
                llm=self.llm,
                task_config=self.tasks_config['combine_and_verify_rules_task'],
                context=[self.extract_rules_task(), self.integrate_rules_task()]
            )
            
            # Generate a unique run ID for tracking this execution
            run_id = uuid.uuid4()

            # Ensure logs directory exists
            log_dir = Path('logs')
            log_dir.mkdir(exist_ok=True)
            
            log_file_path = log_dir / f"crew_output_{run_id}.log"
            logger.info(f"Creating new crew execution with ID: {run_id}")
            logger.info(f"Logs will be saved to: {log_file_path}")

            # Assemble and return the complete crew
            return Crew(
                agents=self.agents[:-1] + [chief_qa_validator.agent] + [self.data_engineer()], 
                tasks=self.tasks[:-1] + [chief_qa_validator.task] + [self.format_rules_task()],
                process=Process.sequential,
                verbose=True,
                output_log_file=str(log_file_path)
            )
        except Exception as e:
            logger.error(f"Error creating crew: {str(e)}")
            raise