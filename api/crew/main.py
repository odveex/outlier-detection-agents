#!/usr/bin/env python
import warnings
import argparse
import sys
from crew import RulesExtractionAndIntegrationCrew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def parse_args():
    parser = argparse.ArgumentParser(description="Crew runner")
    parser.add_argument("--expert_text", type=str, required=False, default="")
    parser.add_argument("--rules", action='append', default=[])
    parser.add_argument("--dataset_columns", action='append', default=[])
    parser.add_argument("--python_code_path")
    return parser.parse_args()

def run(expert_text:str, rules:list, dataset_columns:list):
    """
    Run the crew.
    """

    inputs = {
        'expert_text': expert_text,
        'rules': rules,
        'dataset_columns': dataset_columns
    }
    
    result = RulesExtractionAndIntegrationCrew().crew().kickoff(inputs=inputs)
    
if __name__ == "__main__":
    if len(sys.argv) == 1:
        run(expert_text="If truck speed > 120 km/h, then it is an outlier. When there is more than 100 high pressure compression cycles in a day then it is not normal.", 
            rules=[
                "IF Total no. compaction cycles > 100 AND Total no. compaction cycles with p>100 bar < 10 THEN outlier",
                "IF Total fuel consumed [dm3] > 40 and Motohours (PTO engaged) [h] < 2 then outlier"
            ],
            dataset_columns=[
                "date",
                "Motohours total [h]",
                "Motohours (PTO engaged) [h]",
                "Motohours stop (idle) [h]",
                "Motohours driving [h]",
                "Distance [km]",
                "Total no. compaction cycles",
                "Total no. compaction cycles with p>100 bar",
                "Total no. compaction cycles with p>150 bar",
                "Total fuel consumed [dm3]"
            ]
        )
    else:
        args = parse_args()
        run(expert_text=args.expert_text, rules=args.rules, dataset_columns=args.dataset_columns)