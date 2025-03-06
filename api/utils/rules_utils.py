import re
import pandas as pd
from typing import Optional

def apply_rules_to_dataset(rules, df) -> pd.DataFrame:
    """
    Applies the given rules to the DataFrame and returns a new column 'rule_outlier'.
    """
    df['outlier'] = False
    
    def parse_condition(cond):
        # Example: '$truck speed$ > 120 km/h'
        match = re.match(r'IF\s*(.*)', cond.strip(), re.IGNORECASE)
        c = match.group(1) if match else cond
        return c.strip()
    
    # Process each rule
    for rule in rules:
        if 'THEN OUTLIER' not in rule:
            continue
        cond_part, _ = rule.split('THEN OUTLIER')
        cond_part = cond_part.replace('IF', '').strip()
        conditions = [parse_condition(c) for c in cond_part.split('AND')]
        
        # Build mask for the current rule
        mask = pd.Series([True]*len(df), index=df.index)
        for c in conditions:
            # Extract param between $...$, operator, and value
            # e.g. '$Distance [km]$ > 135.750'
            pattern = r'\$(.*?)\$\s*(>=|<=|>|<|==)\s*([\d\.]+)\s*(km/h|bar|km|h|dm3|l|kg|t|rpm|liters|kilograms|tons)?'
            match = re.search(pattern, c)
            if not match:
                continue
            col, op, val, _ = match.groups()
            col = col.strip()
            val = float(val)

            if op == '>':
                mask &= df[col] > val
            elif op == '<':
                mask &= df[col] < val
            elif op == '>=':
                mask &= df[col] >= val
            elif op == '<=':
                mask &= df[col] <= val
            elif op == '==':
                mask &= df[col] == val

        df.loc[mask, 'outlier'] = True
        
    return df

def test_rules():
    data = {
        "truck speed": [100, 130, 90],
        "Total no. compaction cycles": [50, 110, 101],
        "Total no. compaction cycles with p>150 bar": [30.0, 243.0, 500.0],
        "Distance [km]": [136.0, 136.0, 0.09],
        "Motohours stop (idle) [h]": [0.25, 10.0, 9.9],
        "Total fuel consumed [dm3]": [425.0, 400.0, 430.0],
        "Motohours (PTO engaged) [h]": [3.0, 2.8, 2.9]
    }
    df = pd.DataFrame(data)
    rules = [
        "IF $Total no. compaction cycles with p>150 bar$ > 391.500 AND $Distance [km]$ <= 135.750 AND $Total fuel consumed [dm3]$ > 473.900 AND $Total fuel consumed [dm3]$ <= 67.000 THEN OUTLIER"
    ]
    df = apply_rules_to_dataset(rules, df)

if __name__ == "__main__":
    test_rules()