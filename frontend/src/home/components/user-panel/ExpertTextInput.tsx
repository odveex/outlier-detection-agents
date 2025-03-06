import { TextField } from "@mui/material";
import React from "react";

interface ExpertTextInputProps {
  expertInfo: string;
  setExpertInfo: (t: string) => void;
}

export const ExpertTextInput = (props: ExpertTextInputProps) => {
  return (
    <div style={{ padding: "5px 10px" }}>
      <TextField
        label="Expert text input"
        multiline
        value={props.expertInfo}
        onChange={(event: React.ChangeEvent<HTMLInputElement>) => {
          props.setExpertInfo(event.target.value);
        }}
        rows={12}
        fullWidth
      />
    </div>
  );
};
