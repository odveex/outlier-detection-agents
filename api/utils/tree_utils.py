import re

def parse_tree_to_rules(tree_text):
    """
    Parses a textual representation of a decision tree (similar to sklearn's text export)
    into a list of rules in the format:
    
    IF <condition1> AND <condition2> AND ... THEN <INLIER|OUTLIER>
    """
    
    # Split the text into lines
    lines = tree_text.strip().splitlines()
    
    # A stack for the current path of conditions
    path_stack = []
    
    # This will hold final rules
    rules = []
    
    # Regex to detect lines with conditions, e.g.:
    # '|   |--- feature_8 <= 462.55'
    condition_pattern = re.compile(r'^\s*\|(?P<indent>[\|\s-]+)\s+(?P<feature>feature_\d+)\s*(?P<op><=|>|<=|>=)\s*(?P<value>[0-9\.]+)\s*$')
    
    # Regex to detect lines with leaf info, e.g.:
    # '|   |   |--- weights: [0.00, 6.00] class: 1.0'
    leaf_pattern = re.compile(
        r'^\s*\|(?P<indent>[\|\s-]+)\s+weights:\s*\[(?P<w0>[0-9\.]+),\s*(?P<w1>[0-9\.]+)\]\s+class:\s*(?P<cls>[0-9\.]+)\s*$'
    )
    
    # We will track how "deep" each line is by counting occurrences of "|   "
    # so we can pop from the path_stack if we move back up the tree
    def get_depth(line):
        # Each "   " after a "|" is one depth. Counting them can help.
        # Alternatively, we can count the number of occurrences of "|   " 
        # at the line start.
        return line.count("|   ")
    
    prev_depth = 0
    
    for line in lines:
        # Check if line is a condition node
        condition_match = condition_pattern.match(line)
        leaf_match = leaf_pattern.match(line)
        
        if condition_match:
            # Extract depth
            depth = get_depth(line)
            feature = condition_match.group("feature")
            operator = condition_match.group("op")
            value = condition_match.group("value")
            
            # If we moved back up in depth, pop from path_stack
            while len(path_stack) > depth:
                path_stack.pop()
                
            # Add condition to the path stack
            path_stack.append((feature, operator, value))
            
            # Update prev_depth
            prev_depth = depth
            
        elif leaf_match:
            # Extract depth
            depth = get_depth(line)
            w0 = float(leaf_match.group("w0"))
            w1 = float(leaf_match.group("w1"))
            leaf_class = float(leaf_match.group("cls"))
            
            # If we moved back up in depth, pop from path_stack
            while len(path_stack) > depth:
                path_stack.pop()
            
            # Now the path_stack is the list of conditions for this leaf
            # Convert them into textual form
            conditions_text = []
            for (feat, op, val) in path_stack:
                # e.g. "feature_8 <= 462.55"
                conditions_text.append(f"{feat} {op} {val}")
            
            # Determine status
            if leaf_class == 0.0:
                status = "INLIER"
            else:
                status = "OUTLIER"
            
            # Build the final rule text
            if conditions_text:
                rule_text = "IF " + " AND ".join(conditions_text) + f" THEN {status}"
            else:
                # If for some reason we had no conditions (root-only tree?), fallback
                rule_text = f"IF <no conditions> THEN {status}"
            
            # Store it
            rules.append(rule_text)
            
            # Update prev_depth
            prev_depth = depth
            
        else:
            # Some lines might be empty or not match anything
            # We don't do anything with them
            continue
    
    return rules

if __name__ == "__main__":
    # Example usage with the provided textual tree
    tree_string = """|--- feature_8 <= 462.55
|   |--- feature_5 <= 83.50
|   |   |--- feature_8 <= 247.35
|   |   |   |--- weights: [0.00, 6.00] class: 1.0
|   |   |--- feature_8 >  247.35
|   |   |   |--- weights: [6.00, 0.00] class: 0.0
|   |--- feature_5 >  83.50
|   |   |--- feature_7 <= 279.00
|   |   |   |--- feature_4 <= 222.10
|   |   |   |   |--- feature_3 <= 4.35
|   |   |   |   |   |--- feature_7 <= 242.50
|   |   |   |   |   |   |--- weights: [0.00, 151.00] class: 1.0
|   |   |   |   |   |--- feature_7 >  242.50
|   |   |   |   |   |   |--- feature_6 <= 303.50
|   |   |   |   |   |   |   |--- weights: [1.00, 0.00] class: 0.0
|   |   |   |   |   |   |--- feature_6 >  303.50
|   |   |   |   |   |   |   |--- weights: [0.00, 9.00] class: 1.0
|   |   |   |   |--- feature_3 >  4.35
|   |   |   |   |   |--- feature_0 <= 7.65
|   |   |   |   |   |   |--- weights: [1.00, 0.00] class: 0.0
|   |   |   |   |   |--- feature_0 >  7.65
|   |   |   |   |   |   |--- weights: [0.00, 2.00] class: 1.0
|   |   |   |--- feature_4 >  222.10
|   |   |   |   |--- weights: [1.00, 0.00] class: 0.0
|   |   |--- feature_7 >  279.00
|   |   |   |--- feature_4 <= 61.30
|   |   |   |   |--- feature_5 <= 518.00
|   |   |   |   |   |--- weights: [1.00, 0.00] class: 0.0
|   |   |   |   |--- feature_5 >  518.00
|   |   |   |   |   |--- feature_8 <= 300.20
|   |   |   |   |   |   |--- weights: [0.00, 6.00] class: 1.0
|   |   |   |   |   |--- feature_8 >  300.20
|   |   |   |   |   |   |--- weights: [1.00, 0.00] class: 0.0
|   |   |   |--- feature_4 >  61.30
|   |   |   |   |--- weights: [4.00, 0.00] class: 0.0
|--- feature_8 >  462.55
|   |--- weights: [11.00, 0.00] class: 0.0
"""

    # Parse tree and print rules
    all_rules = parse_tree_to_rules(tree_string)
    for rule in all_rules:
        print(rule)