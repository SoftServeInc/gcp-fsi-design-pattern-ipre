import React from "react";
import Container from "@material-ui/core/Container";
import { makeStyles } from "@material-ui/core/styles";
import Snackbar from "@material-ui/core/Snackbar";

import IconButton from "@material-ui/core/IconButton";
import { CloseIcon } from "../components/icons/CloseIcon";

import SideMenu from "../components/SideMenu";
import TopBar from "../components/TopBar";

import { TOP_BAR_HEIGHT } from "../components/TopBar/TopBar";

const SnackbarInfo = () => {
  const [open, setOpen] = React.useState(true);

  const handleClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }

    setOpen(false);
  };

  return (
    <div>
      <Snackbar
        anchorOrigin={{
          vertical: "bottom",
          horizontal: "center",
        }}
        open={open}
        onClose={handleClose}
        message="This application is for demonstration purpose, it is not intended to be investment advise."
        action={
          <React.Fragment>
            <IconButton
              size="small"
              aria-label="close"
              color="inherit"
              onClick={handleClose}
            >
              <CloseIcon fontSize="small" />
            </IconButton>
          </React.Fragment>
        }
      />
    </div>
  );
};

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    height: "100vh",
    justifyContent: "center",
  },
  appBarSpacer: {
    minHeight: TOP_BAR_HEIGHT,
  },
  content: {
    flexGrow: 1,
    height: "100vh",
    overflow: "auto",
    maxWidth: 1280,
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4),
    minHeight: `calc(100vh - ${TOP_BAR_HEIGHT}px)`,
    maxHeight: "100vh",
    height: 1,
    // overflow: "hidden",
  },
}));

const Layout = ({ children }) => {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <SnackbarInfo />
      <TopBar />
      <SideMenu />
      <main className={classes.content}>
        <div className={classes.appBarSpacer} />
        <Container maxWidth={false} className={classes.container}>
          {children}
        </Container>
      </main>
    </div>
  );
};

export default Layout;
