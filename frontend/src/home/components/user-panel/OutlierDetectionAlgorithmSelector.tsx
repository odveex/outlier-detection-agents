import {
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  SelectChangeEvent,
} from "@mui/material";
import React from "react";

interface OutlierDetectionAlgorithmSelectoProps {
  outlierDetectionAlgorithm: string;
  setOutlierDetectionAlgorithm: (t: string) => void;
}

export const OutlierDetectionAlgorithmSelector = (
  props: OutlierDetectionAlgorithmSelectoProps,
) => {
  return (
    <div style={{ padding: "10px" }}>
      <FormControl fullWidth>
        <InputLabel>Select data outlier detection algorithm</InputLabel>
        <Select
          label="Select data outlier detection algorithm"
          value={props.outlierDetectionAlgorithm}
          onChange={(e: SelectChangeEvent) =>
            props.setOutlierDetectionAlgorithm(e.target.value)
          }
        >
          <MenuItem value={"LocalOutlierFactor"}>Local Outlier Factor</MenuItem>
          <MenuItem value={"IsolationForest"}>Isolation Forest</MenuItem>
          <MenuItem value={"OneClassSVM"}>One-Class SVM</MenuItem>
        </Select>
      </FormControl>
    </div>
  );
};
