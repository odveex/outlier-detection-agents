import { Alert, Stack } from "@mui/material";
import CompostOutlinedIcon from "@mui/icons-material/AccountTreeOutlined";
import WarningAmberIcon from "@mui/icons-material/WarningAmber";
export const EmptyTreeInformation = () => {
  return (
    <div style={{ padding: "20px" }}>
      <Stack spacing={3}>
        <Alert
          icon={<CompostOutlinedIcon fontSize="inherit" />}
          severity="info"
        >
          Please submit the algorithm first to generate the decision tree
          visualization
        </Alert>
        <img
          style={{ opacity: "0.1" }}
          src={"decision-tree-mocks/emptyTree.jpg"}
          alt={"EmptyTree"}
          loading="lazy"
        />
        <Alert
          icon={<WarningAmberIcon fontSize="inherit" />}
          severity="warning"
        >
          Generating the visualization may take up to a minute. Please be
          patient
        </Alert>
      </Stack>
    </div>
  );
};
