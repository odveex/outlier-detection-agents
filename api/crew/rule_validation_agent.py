from crewai import Agent, Task, Crew, Process
from crewai.tasks.task_output import TaskOutput
from crewai.crew import CrewOutput
import re
import json

class RuleValidationAgent:
    def __init__(self, llm, role, goal, backstory, task_description, expected_output, context=[], rule_sets=[]):        
        self.ai_model = llm
        self.rule_sets = rule_sets  # The two sets of rules to be combined
        self.validated_rules = []  # Store rules in memory instead of writing to file

        # Initialize an Agent instance for this task
        self.agent = Agent(role=role, goal=goal, backstory=backstory, allow_delegation=False, llm=llm)
        
        # Create a Task instance based on the provided parameters
        if len(context) == 0:
            self.task = Task(description=task_description, expected_output=expected_output, agent=self.agent)
        else:
            self.task = Task(description=task_description, expected_output=expected_output, agent=self.agent, context=context)
        
        # Store the original task description for reference
        self.original_task_description = task_description
    
    def extract_rules_from_output(self, output_text):
        """
        Extract rules from the agent's output text.
        Handles various formats (code blocks, quoted text, direct text).
        """
        rules = []
        
        # Try to find rules in code blocks
        code_blocks = re.findall(r'```(?:.*?)\s*([\s\S]*?)\s*```', output_text)
        for block in code_blocks:
            # Try to parse as JSON
            try:
                json_rules = json.loads(block)
                if isinstance(json_rules, list):
                    for rule in json_rules:
                        if isinstance(rule, str) and "IF " in rule and "THEN OUTLIER" in rule:
                            rules.append(rule)
                    continue
                elif isinstance(json_rules, dict) and "new_rules" in json_rules:
                    # Handle the NewRuleList pydantic model output format
                    new_rules = json_rules.get("new_rules", [])
                    if isinstance(new_rules, list):
                        for rule in new_rules:
                            if isinstance(rule, str) and "IF " in rule and "THEN OUTLIER" in rule:
                                rules.append(rule)
                        continue
            except:
                pass
            
            # Process the block line by line
            block_lines = block.strip().split('\n')
            for line in block_lines:
                line = line.strip()
                if line.startswith('"') and "IF " in line and "THEN OUTLIER" in line:
                    rule = line.strip('"').strip("'")
                    rules.append(rule)
                elif line.startswith("IF ") and "THEN OUTLIER" in line:
                    rules.append(line)
        
        # If no rules found in code blocks, try to find rules directly in the text
        if not rules:
            lines = output_text.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith("IF ") and "THEN OUTLIER" in line:
                    rules.append(line)
                # Match lines that look like list items with rules
                elif re.match(r'^\d+\.\s*"IF.*THEN OUTLIER"', line):
                    match = re.search(r'"(IF.*THEN OUTLIER)"', line)
                    if match:
                        rules.append(match.group(1))
                # Match quoted rules
                elif (re.match(r'^"IF.*THEN OUTLIER"', line) or 
                      re.match(r'^\'IF.*THEN OUTLIER\'', line)):
                    rule = line.strip('"').strip("'")
                    rules.append(rule)
        
        return rules
    
    def validate_rules(self, rules):
        """
        Validate the rules against the task description restrictions.
        Returns a tuple of (is_valid, errors).
        """
        errors = []
        
        # Basic validation: check if rules is a list
        if not isinstance(rules, list):
            errors.append("Output must be a list of rules.")
            return False, errors
        
        # Check if there are rules in the output
        if len(rules) == 0:
            errors.append("No rules found in the output.")
            return False, errors
        
        # Validate each rule
        for i, rule in enumerate(rules):
            # Check if rule is a string
            if not isinstance(rule, str):
                errors.append(f"Rule {i+1} must be a string, got {type(rule).__name__}.")
                continue
            
            # Check if rule contains "INLIER" (not allowed)
            if "THEN INLIER" in rule:
                errors.append(f"Rule {i+1} contains INLIER but should only contain OUTLIER: {rule}")
            
            # Check if rule follows the pattern "IF ... THEN OUTLIER"
            if not (rule.startswith("IF ") and "THEN OUTLIER" in rule):
                errors.append(f"Rule {i+1} does not follow pattern 'IF ... THEN OUTLIER': {rule}")
            
            # Check if rule contains "OR" (not allowed)
            if " OR " in rule:
                errors.append(f"Rule {i+1} contains 'OR' which is not allowed: {rule}")
        
        # Additional check for comprehensiveness
        if not errors:
            # Check if all non-contradictory rules from the original sets are included
            # This is a complex task that would require deeper semantic analysis
            # For now, we'll just do basic checks on rule count and uniqueness
            if self.rule_sets and len(self.rule_sets) > 0:
                # Count total input outlier rules
                total_outlier_rules = 0
                for rule_set in self.rule_sets:
                    if isinstance(rule_set, list):
                        for rule in rule_set:
                            if isinstance(rule, str) and "THEN OUTLIER" in rule:
                                total_outlier_rules += 1
                
                # If we have significantly fewer rules than input, that might be an issue
                # (unless many were contradictory or contained "OR" that got split)
                if len(rules) < total_outlier_rules * 0.5 and total_outlier_rules > 2:
                    errors.append(f"Warning: Output has significantly fewer rules ({len(rules)}) than expected. "
                                 f"Make sure no valid rules were skipped.")
        
        return (len(errors) == 0), errors
    
    def recursive_validate_and_fix(self, output_text):
        """
        Validate the rules and recursively fix them if needed.
        Returns the validated rules.
        """
        # Extract rules from the output
        rules = self.extract_rules_from_output(output_text)
        
        # Validate the rules
        is_valid, errors = self.validate_rules(rules)
        
        if not is_valid:
            error_msg = "\n".join(errors)
            print(f"Validation errors: {error_msg}")
            
            # Create a new task to fix the issues
            new_task_description = (
                f"Fix the following validation issues in the rules:\n{error_msg}\n\n"
                f"Original task: {self.original_task_description}\n\n"
                f"Current rules output:\n{json.dumps(rules, indent=2)}\n\n"
                f"Please provide a corrected set of rules that address all the validation issues."
                f"Remember that ALL rules must:\n"
                f"1. Follow the pattern 'IF ... THEN OUTLIER'\n"
                f"2. Not contain 'OR' (split into separate rules)\n"
                f"3. Not contain 'INLIER'\n"
                f"4. Include all non-contradictory rules from both input sets\n"
                f"5. Have no inconsistencies or contradictions"
            )
            
            # Create a new task with the new description
            fix_task = Task(
                description=new_task_description, 
                expected_output="List of rules that follow the required format and constraints.",
                agent=self.agent
            )
            
            # Create a crew to fix the issues
            crew_rule_fixer = Crew(
                agents=[self.agent],
                tasks=[fix_task],
                llm=self.ai_model,
                verbose=True,
                process=Process.sequential
            )
            
            # Kick off the crew
            result = crew_rule_fixer.kickoff()
            
            # Handle the result
            if isinstance(result, TaskOutput):
                return self.recursive_validate_and_fix(result.raw)
            elif isinstance(result, CrewOutput) and hasattr(result, 'output'):
                if hasattr(result.output, 'raw'):
                    return self.recursive_validate_and_fix(result.output.raw)
                else:
                    # Try best effort to get the output
                    for output in result.outputs:
                        if hasattr(output, 'raw'):
                            return self.recursive_validate_and_fix(output.raw)
            
            # If we got here, we couldn't fix the issues, so return an empty list
            return []
        else:
            print("Rules validation successful!")
            # Store validated rules
            self.validated_rules = rules
            return rules


class ChiefQAEngineerWithTask:
    """
    Implementation of the Chief QA Engineer agent for validating and combining rule sets.
    Compatible with CrewAI framework.
    """
    
    def __init__(self, llm, task_config=None, context=None):
        # Store references for later
        self.llm = llm
        self.task_config = task_config
        self.context = context if context else []
        
        # Initialize agent and task
        self._initialize()
    
    def _initialize(self):
        """
        Initialize the agent and task based on configuration.
        """
        # Get the chief_qa_engineer details from agents.yaml
        role = "Chief Quality Assurance Engineer"
        goal = "Create rules set without any contradictions."
        backstory = ("You have a background in both quality assurance and truck operation. "
                    "You are intelligent being with knowledge about how to create rules set without any contradictions. "
                    "You are known for your prudence, and you won't let any contradiction or skipped information slip through your fingers.")
        
        # Initialize the rule sets from context if available
        rule_sets = self._extract_rule_sets_from_context()
        
        # Create a task description based on the task config or use default
        if self.task_config:
            task_description = self.task_config.get('description', '')
            expected_output = self.task_config.get('expected_output', '')
        else:
            # Default task description
            task_description = (
                "Given two provided sets of rules, merge the sets into one set of rules following this thought process:\n"
                "1. Ensure the combined set of rules are consistent and comprehensive.\n"
                "2. Ensure there are no inconsistencies in the combined set of rules.\n"
                "3. Ensure there are no contradictions in the combined set of rules.\n"
                "4. Ensure there is no skipped information in the combined set of rules, meaning under no circumstances "
                "any rule should be skipped or not included in the final output, given particular rule is not contradictory/inconsistent.\n"
                "5. Only rules describing given example being \"OUTLIER\" are to be saved. Rules for \"INLIER\" should be removed from the combined set.\n\n"
                "Note that:\n"
                "- Your task is to not modify particular rules under any circumstances\n"
                "- You must not use \"OR\" under any circumstances, split the rules into separate ones in such case - follow example:\n\n"
                "###EXAMPLE:\n"
                "Incorrect: [\"IF Total no. compaction cycles > 100 AND (Total no. compaction cycles with p>100 bar < 10 OR Total fuel consumed [dm3] > 40) THEN OUTLIER\"]\n"
                "Correct: [  \"IF Total no. compaction cycles > 100 AND Total no. compaction cycles with p>100 bar < 10 THEN OUTLIER\", \n"
                "            \"IF Total no. compaction cycles > 100 AND Total fuel consumed [dm3] > 40 THEN OUTLIER\" ]\n"
                "###END OF EXAMPLE\n\n"
                f"Rule sets to combine: {json.dumps(rule_sets)}"
            )
            expected_output = ("Set of rules merged from two sets of rules, with no contradictions, "
                              "inconsistencies or skipped information without any rules depicting \"INLIER\".")
        
        # Create the validation agent
        self.validator = RuleValidationAgent(
            llm=self.llm,
            role=role, 
            goal=goal, 
            backstory=backstory,
            task_description=task_description,
            expected_output=expected_output,
            context=self.context,
            rule_sets=rule_sets
        )
        
        # Store references to agent and task for CrewAI
        self.agent = self.validator.agent
        
        # Create a new task with our callback
        self.task = Task(
            description=task_description,
            expected_output=expected_output,
            agent=self.agent,
            context=self.context,
            callback=self.callback
        )
    
    def _extract_rule_sets_from_context(self):
        """
        Extract rule sets from context tasks' outputs.
        """
        rule_sets = []
        
        if not self.context:
            return rule_sets
        
        for ctx in self.context:
            # Try to extract rules from the context
            if hasattr(ctx, 'output') and ctx.output:
                # Try direct access to new_rules
                if hasattr(ctx.output, 'new_rules'):
                    rule_sets.append(ctx.output.new_rules)
                # Try accessing output.raw
                elif hasattr(ctx.output, 'raw'):
                    # Extract rules using the extract_rules_from_output method
                    rules = self.validator.extract_rules_from_output(ctx.output.raw) if hasattr(self, 'validator') else []
                    if not rules:
                        # Use the static method if validator is not yet initialized
                        rules = RuleValidationAgent.extract_rules_from_output(None, ctx.output.raw)
                    if rules:
                        rule_sets.append(rules)
        
        return rule_sets
    
    def callback(self, output):
        """
        Callback function for the task. This processes the output from the agent,
        validates and fixes it if necessary, and returns it in the expected format.
        """
        if output is None:
            return {"new_rules": []}
        
        # Use the validator to recursively validate and fix the rules
        validated_rules = self.validator.recursive_validate_and_fix(output.raw)
        
        # Return the validated rules in the correct format
        return {"new_rules": validated_rules}