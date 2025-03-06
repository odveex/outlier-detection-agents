import { Button, Stack } from "@mui/material";
import { RulesAlgorithmSelector } from "./RulesAlgorithmSelector";
import { ExpertTextInput } from "./ExpertTextInput";
import { FileUploader } from "./FileUploader";
import { PaperItem } from "../../../core/components/PaperItem";
import { OutlierDetectionAlgorithmSelector } from "./OutlierDetectionAlgorithmSelector";
import { useState } from "react";
import { getSessionId } from "../../../core/utils/query/getSessionId";
import { getOutlierImage } from "../../../core/utils/query/getOutlierImage";
import {
  GET_OUTLIER_TEXT_URL,
  GET_OUTLIER_IMAGE_URL,
  GET_OUTLIER_TEXT_WITH_EXPERT_URL,
  GET_OUTLIER_IMAGE_WITH_EXPERT_URL,
} from "../../../core/model/urls";
import { getOutlierText } from "../../../core/utils/query/getOutlierText";

interface UserPanelProps {
  setIsLoading: (e: boolean) => void;
  setOutlierText: (e: string) => void;
  setOutlierTree: (e: string | undefined) => void;
  setOutlierTextWithExpertInput: (e: string) => void;
  setOutlierTreeWithExpertInput: (e: string | undefined) => void;
}

export const UserPanel = (props: UserPanelProps) => {
  const [rulesAlgorithm, setRulesAlgorithm] = useState("FIGS");
  const [outlierDetectionAlgorithm, setOutlierDetectionAlgorithm] =
    useState("LocalOutlierFactor");

  const [expertInfo, setExpertInfo] = useState("");

  const [csvFile, setCsvFile] = useState("");

  const loadImage = async () => {
    props.setIsLoading(true);
    const sessionId = await getSessionId(
      rulesAlgorithm,
      outlierDetectionAlgorithm,
      expertInfo,
      csvFile,
    );

    if (sessionId) {
      const outlierText = await getOutlierText(sessionId, GET_OUTLIER_TEXT_URL);
      props.setOutlierText(outlierText);

      const outlierTreeImageURL = await getOutlierImage(
        sessionId,
        GET_OUTLIER_IMAGE_URL,
      );
      props.setOutlierTree(outlierTreeImageURL);

      const outlierTextWithExpert = await getOutlierText(
        sessionId,
        GET_OUTLIER_TEXT_WITH_EXPERT_URL,
      );
      props.setOutlierTextWithExpertInput(outlierTextWithExpert);

      const outlierTreeWithExpertInputImageURL = await getOutlierImage(
        sessionId,
        GET_OUTLIER_IMAGE_WITH_EXPERT_URL,
      );
      props.setOutlierTreeWithExpertInput(outlierTreeWithExpertInputImageURL);
    }
    props.setIsLoading(false);
  };

  return (
    <Stack spacing={2}>
      <PaperItem elevation={1} variant="outlined">
        <RulesAlgorithmSelector
          rulesAlgorithm={rulesAlgorithm}
          setRulesAlgorithm={setRulesAlgorithm}
        />
      </PaperItem>
      <PaperItem elevation={1} variant="outlined">
        <OutlierDetectionAlgorithmSelector
          outlierDetectionAlgorithm={outlierDetectionAlgorithm}
          setOutlierDetectionAlgorithm={setOutlierDetectionAlgorithm}
        />
      </PaperItem>
      <PaperItem elevation={1} variant="outlined">
        <ExpertTextInput
          expertInfo={expertInfo}
          setExpertInfo={setExpertInfo}
        />
      </PaperItem>
      <PaperItem elevation={1} variant="outlined">
        <FileUploader setCsvFile={setCsvFile} />
      </PaperItem>
      <Button variant="contained" color="primary" onClick={loadImage}>
        Submit
      </Button>
    </Stack>
  );
};
