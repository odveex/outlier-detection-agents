import Grid from "@mui/material/Unstable_Grid2";
import { UserPanel } from "./components/user-panel/UserPanel";
import { useState } from "react";
import { DecisionTreeVisualization } from "./components/decision-tree/DecisionTreeVisualization";
import { Backdrop } from "@mui/material";
import { DotLoader } from "react-spinners";

export const Home = () => {
  const [outlierText, setOutlierText] = useState<string>("");
  const [outlierTree, setOutlierTree] = useState<string | undefined>(undefined);
  const [outlierTextWithExpertInput, setOutlierTextWithExpertInput] =
    useState<string>("");
  const [outlierTreeWithExpertInput, setOutlierTreeWithExpertInput] = useState<
    string | undefined
  >(undefined);

  const [isLoading, setIsLoading] = useState(false);

  return (
    <>
      <div style={{ marginTop: "40px" }}>
        <Grid container spacing={3}>
          <Grid xs={6}>
            <div style={{ width: "90%", margin: "auto" }}>
              <UserPanel
                setIsLoading={setIsLoading}
                setOutlierTree={setOutlierTree}
                setOutlierText={setOutlierText}
                setOutlierTextWithExpertInput={setOutlierTextWithExpertInput}
                setOutlierTreeWithExpertInput={setOutlierTreeWithExpertInput}
              />
            </div>
          </Grid>
          <Grid xs={6}>
            <div style={{ width: "90%", margin: "auto" }}>
              <DecisionTreeVisualization
                outlierText={outlierText}
                outlierTree={outlierTree}
                outlierTextWithExpertInput={outlierTextWithExpertInput}
                outlierTreeWithExpertInput={outlierTreeWithExpertInput}
              />
            </div>
          </Grid>
        </Grid>
      </div>
      <Backdrop
        sx={(theme) => ({ color: "#fff", zIndex: theme.zIndex.drawer + 1 })}
        open={isLoading}
      >
        <DotLoader color="#7bbced" size={120} />
      </Backdrop>
    </>
  );
};
