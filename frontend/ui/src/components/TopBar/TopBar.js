import React from "react";
import AppBar from "@material-ui/core/AppBar";
import Box from "@material-ui/core/Box";
import Typography from "@material-ui/core/Typography";
import Avatar from "@material-ui/core/Avatar";
import Toolbar from "@material-ui/core/Toolbar";
import Notifications from "../Notifications";
import { LogoIcon } from "../icons/LogoIcon";
import Menu from "@material-ui/core/Menu";
import MenuItem from "@material-ui/core/MenuItem";
import { makeStyles } from "@material-ui/core/styles";
import API from "../../helpers/API";
import { useHistory } from "react-router";
export const TOP_BAR_HEIGHT = 90;

const useStyles = makeStyles((theme) => ({
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    height: TOP_BAR_HEIGHT,
    backgroundColor: "#FFF",
    boxShadow: "none",
    border: "1px solid #EEE",
  },
  toolBar: {
    height: TOP_BAR_HEIGHT,
  },
  avatar: {
    width: 36,
    height: 36,
    marginLeft: 12,
  },
  user: {
    display: "flex",
  },
}));

const User = () => {
  const [anchorEl, setAnchorEl] = React.useState(null);

  const history = useHistory();

  const handleClick = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = async () => {
    await API.logout();
    history.push("/login");
    localStorage.removeItem("AUTH_TOKEN");
    API.setHeaderOnInstance("Authorization", "");
  };

  const classes = useStyles();

  return (
    <>
      <Typography>
        <Box
          fontWeight={600}
          fontSize={16}
          onClick={handleClick}
          component="span"
        >
          John Doe
        </Box>
      </Typography>
      <Avatar className={classes.avatar}></Avatar>
      <Menu
        id="logout-menu"
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleClose}
      >
        <MenuItem onClick={handleLogout}>Log out</MenuItem>
      </Menu>
    </>
  );
};

const SideMenu = () => {
  const classes = useStyles();

  return (
    <AppBar position="fixed" className={classes.appBar}>
      <Toolbar className={classes.toolBar}>
        <LogoIcon />
        <Box component="span" display="flex" alignItems="center" ml="auto">
          <Notifications />
          <User />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default SideMenu;
