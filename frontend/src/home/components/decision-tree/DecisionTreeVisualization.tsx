import {
  Accordion,
  AccordionDetails,
  AccordionSummary,
  Stack,
} from "@mui/material";
import { PaperItem } from "../../../core/components/PaperItem";
import { EmptyTreeInformation } from "./EmptyTreeInformation";
import { DecisionTreeImage } from "./DecisionTreeImage";
import TextArea from "./TextArea";
import ExpandMoreIcon from "@mui/icons-material/ExpandMore";

interface DecisionTreeVisualizationProps {
  outlierText: string;
  outlierTree: string | undefined;
  outlierTextWithExpertInput: string;
  outlierTreeWithExpertInput: string | undefined;
}

const NoImage = () => (
  <div style={{ color: "gray", paddingBottom: "10px" }}>No Image</div>
);

export const DecisionTreeVisualization = (
  props: DecisionTreeVisualizationProps,
) => {
  return (
    <Stack spacing={4}>
      {props.outlierText || props.outlierTextWithExpertInput ? (
        <>
          <PaperItem elevation={1} variant="outlined">
            {props.outlierTree ? (
              <DecisionTreeImage imageUrl={props.outlierTree} />
            ) : (
              <NoImage />
            )}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                Outlier Text
              </AccordionSummary>
              <AccordionDetails>
                <TextArea text={props.outlierText} />
              </AccordionDetails>
            </Accordion>
          </PaperItem>
          <PaperItem elevation={1} variant="outlined">
            {props.outlierTreeWithExpertInput ? (
              <DecisionTreeImage imageUrl={props.outlierTreeWithExpertInput} />
            ) : (
              <NoImage />
            )}
            <Accordion>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                Outlier Text With Expert Input
              </AccordionSummary>
              <AccordionDetails>
                <TextArea text={props.outlierTextWithExpertInput} />
              </AccordionDetails>
            </Accordion>
          </PaperItem>
        </>
      ) : (
        <PaperItem elevation={1} variant="outlined">
          <EmptyTreeInformation />
        </PaperItem>
      )}
    </Stack>
  );
};
