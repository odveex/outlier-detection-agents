import { AppBar, createTheme, Toolbar, Typography } from "@mui/material";
import { ThemeProvider } from "styled-components";
import { Home } from "../home/Home";

const darkTheme = createTheme({
  palette: {
    mode: "dark",
    primary: {
      dark: "#1976d2",
      main: "#757ce8",
    },
  },
});

const AppBarLabel = ({ label }: { label: string }) => {
  return (
    <Toolbar variant="dense">
      <img
        src="favicon.ico"
        alt="logo"
        width={30}
        style={{ marginRight: "5px" }}
      />
      <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
        <b>{label}</b>
      </Typography>
    </Toolbar>
  );
};

export const App = () => (
  <ThemeProvider theme={darkTheme}>
    <AppBar position="static" color="default">
      <AppBarLabel label={"odveex"} />
    </AppBar>
    <div style={{ padding: "10px", maxWidth: "2000px", margin: "auto" }}>
      <Home />
    </div>
  </ThemeProvider>
);
