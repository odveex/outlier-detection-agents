import { Button, styled } from "@mui/material";
import React from "react";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

const VisuallyHiddenInput = styled("input")({
  clip: "rect(0 0 0 0)",
  clipPath: "inset(50%)",
  height: 1,
  overflow: "hidden",
  position: "absolute",
  bottom: 0,
  left: 0,
  whiteSpace: "nowrap",
  width: 1,
});

export const FileUploader = ({
  setCsvFile,
}: {
  setCsvFile: (t: string) => void;
}) => {
  const [file, setFile] = React.useState<File | undefined>(undefined);

  const readCSV = (file: File) => {
    const reader = new FileReader();
    reader.onload = (event) => {
      const text = event.target?.result;
      if (typeof text === "string") {
        setFile(file);
        setCsvFile(text);
      }
    };
    reader.readAsText(file);
  };

  return (
    <Button
      component="label"
      role={undefined}
      tabIndex={-1}
      startIcon={<CloudUploadIcon />}
      fullWidth
    >
      {file?.name ?? "Upload file (csv)"}
      <VisuallyHiddenInput
        type="file"
        accept=".csv"
        onChange={(e: any) => readCSV(e.target.files[0])}
      />
    </Button>
  );
};
