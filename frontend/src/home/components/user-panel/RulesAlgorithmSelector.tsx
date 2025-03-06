import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
} from "@mui/material";

interface RulesAlgorithmSelectorProps {
  rulesAlgorithm: string;
  setRulesAlgorithm: (t: string) => void;
}

export const RulesAlgorithmSelector = (props: RulesAlgorithmSelectorProps) => {
  return (
    <div style={{ padding: "10px" }}>
      <FormControl fullWidth>
        <InputLabel>Select rules algorithm</InputLabel>
        <Select
          label="Select rules algorithm"
          value={props.rulesAlgorithm}
          onChange={(e: SelectChangeEvent) =>
            props.setRulesAlgorithm(e.target.value)
          }
        >
          <MenuItem value={"FIGS"}>FIGS</MenuItem>
          <MenuItem value={"OptimalTree"}>Optimal Tree</MenuItem>
          <MenuItem value={"GreedyTree"}>Greedy Tree</MenuItem>
        </Select>
      </FormControl>
    </div>
  );
};
