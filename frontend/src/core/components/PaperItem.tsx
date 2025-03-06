import { Paper } from "@mui/material";
import styled from "styled-components";

export const PaperItem = styled(Paper)(({ theme }) => ({
  ...theme.typography.body2,
  padding: theme.spacing(2),
  textAlign: "center",
  fontSize: "500",
}));
