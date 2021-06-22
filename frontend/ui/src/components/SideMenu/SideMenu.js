import React from "react";
import Drawer from "@material-ui/core/Drawer";
import List from "@material-ui/core/List";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import { HomeIcon } from "../icons/HomeIcon";
import { InvestmentsIcon } from "../icons/InvestmentsIcon";
import { makeStyles } from "@material-ui/core/styles";
import Toolbar from "@material-ui/core/Toolbar";
import { Link as RouterLink, useLocation } from "react-router-dom";
import Box from "@material-ui/core/Box";

const DRAWER_WIDTH = 250;
const MENU_ELEMENTS = [
  { icon: <HomeIcon />, text: "Home", path: "/home" },
  { icon: <InvestmentsIcon />, text: "Investments", path: "/investments" },
];

const useStyles = makeStyles((theme) => ({
  drawer: {
    width: DRAWER_WIDTH,
    flexShrink: 0,
  },
  drawerPaper: {
    width: DRAWER_WIDTH,
    borderRight: "1px solid #EEE",
  },
  drawerContainer: {
    overflow: "auto",
    paddingTop: 40,
  },
  icon: {
    minWidth: 0,
    marginRight: 15,
    marginLeft: 15,
  },
  active: {
    borderLeft: `5px solid ${theme.palette.primary.main}`,
  },
  inactive: {
    borderLeft: "5px solid transparent",
  },
}));

const MenuElement = ({ icon, text, path, isActive }) => {
  const classes = useStyles();

  return (
    <ListItem
      button
      component={RouterLink}
      to={path}
      className={isActive ? classes.active : classes.inactive}
    >
      <ListItemIcon className={classes.icon}>
        {React.cloneElement(icon, {
          color: isActive ? "primary" : "inherit",
        })}
      </ListItemIcon>
      <Box fontSize={14} fontWeight={700} component="span">
        <ListItemText primary={text} disableTypography={true} />
      </Box>
    </ListItem>
  );
};

const SideMenu = () => {
  const classes = useStyles();
  const currentPath = useLocation().pathname;

  return (
    <Drawer
      className={classes.drawer}
      variant="permanent"
      classes={{
        paper: classes.drawerPaper,
      }}
    >
      <Toolbar />
      <div className={classes.drawerContainer}>
        <List>
          {MENU_ELEMENTS.map((element) => (
            <MenuElement
              {...element}
              isActive={currentPath.includes(element.path)}
              key={element.path}
            />
          ))}
        </List>
      </div>
    </Drawer>
  );
};

export default SideMenu;
