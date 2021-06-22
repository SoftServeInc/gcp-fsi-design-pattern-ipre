import React from "react";
import { useHistory } from "react-router-dom";
import { makeStyles } from "@material-ui/core/styles";
import Grid from "@material-ui/core/Grid";
import TextField from "@material-ui/core/TextField";
import InputAdornment from "@material-ui/core/InputAdornment";
import PrimaryButton from "../../components/PrimaryButton";

import { LogoIcon } from "../../components/icons/LogoIcon";
import { UserIcon } from "../../components/icons/UserIcon";
import { LockIcon } from "../../components/icons/LockIcon";

import { AuthContext } from "../../helpers/auth-context";
import API from "../../helpers/API";

const useStyles = makeStyles((theme) => ({
  root: {
    borderRadius: 70,
    border: "px solid #E7E9EF",
    backgroundColor: "#fff",
    margin: theme.spacing(2),
    width: 300,
    height: 40,
  },
}));

const LoginForm = () => {
  const [credentials, setCredentials] = React.useState({
    username: "",
    password: "",
  });

  React.useEffect(() => {
    localStorage.removeItem("AUTH_TOKEN");
    API.setHeaderOnInstance("Authorization", "");
  }, []);

  const { setSentLoginReq } = React.useContext(AuthContext);

  const classes = useStyles();
  let history = useHistory();

  const handleLogin = () => {
    API.login(credentials).then((data) => {
      const token = `token ${data.key}`;
      localStorage.setItem("AUTH_TOKEN", token);
      API.setHeaderOnInstance("Authorization", token);
      setSentLoginReq(true);
      history.push("/home/");
    });
  };

  return (
    <>
      <LogoIcon size="large" />
      <TextField
        variant="outlined"
        placeholder="Username"
        value={credentials.username}
        InputProps={{
          classes,
          startAdornment: (
            <InputAdornment position="end">
              <UserIcon />
            </InputAdornment>
          ),
        }}
      />
      <TextField
        variant="outlined"
        placeholder="Password"
        type="password"
        value={credentials.password}
        InputProps={{
          classes,
          startAdornment: (
            <InputAdornment position="end">
              <LockIcon />
            </InputAdornment>
          ),
        }}
      />
      <PrimaryButton onClick={handleLogin}>Login</PrimaryButton>
      <PrimaryButton
        onClick={() =>
          setCredentials({ username: "johnwick", password: "johnwick" })
        }
      >
        Fill User #1
      </PrimaryButton>
      <PrimaryButton
        onClick={() =>
          setCredentials({ username: "lyraking", password: "lyraking" })
        }
      >
        Fill User #2
      </PrimaryButton>
      <PrimaryButton
        onClick={() =>
          setCredentials({ username: "alexray", password: "alexray" })
        }
      >
        Fill User #3
      </PrimaryButton>
    </>
  );
};

const Login = () => (
  <Grid
    container
    spacing={0}
    direction="column"
    alignItems="center"
    justify="center"
    style={{ minHeight: "100vh" }}
  >
    <Grid
      container
      direction="column"
      alignItems="center"
      justify="center"
      item
      xs={3}
    >
      <LoginForm />
    </Grid>
  </Grid>
);

export default Login;
