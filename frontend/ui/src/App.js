import React from "react";
import Router from "./Router";
import { ThemeProvider } from "@material-ui/core/styles";
import CssBaseline from "@material-ui/core/CssBaseline";
import { useAuthState } from "./helpers/auth-context";
import { theme } from "./helpers/theme";
import Login from "./pages/Login";

function App() {
  const { user } = useAuthState();

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {user ? <Router /> : <Login />}
    </ThemeProvider>
  );
}

export default App;
