import React from "react";
import Badge from "@material-ui/core/Badge";
import Drawer from "@material-ui/core/Drawer";
import ButtonBase from "@material-ui/core/ButtonBase";
import { withStyles, makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import Box from "@material-ui/core/Box";

import { CloseIcon } from "../icons/CloseIcon";
import { NotificationsIcon } from "../icons/NotificationsIcon";

import CTABox from "../CTABox";

const StyledButton = withStyles((theme) => ({
  root: {
    background: "#F5F6FA",
    border: 0,
    borderRadius: 99,
    color: "#212121",
    height: 35,
    padding: "7px 12px",
    marginRight: 24,
    "& p": {
      paddingLeft: 10,
    },
  },
}))(ButtonBase);

const StyledBadge = withStyles((theme) => ({
  badge: {
    right: 6,
    top: 6,
    backgroundColor: "#00C078",
    height: 10,
  },
}))(Badge);

const useStyles = makeStyles((theme) => ({
  drawerPaper: {
    width: 380,
    display: "flex",
    flexDirection: "column",
    padding: "20px 30px",
  },
}));

const Notifications = () => {
  const [isDrawerOpen, setIsDrawerOpen] = React.useState(false);

  const classes = useStyles();

  return (
    <>
      <StyledButton onClick={() => setIsDrawerOpen(true)}>
        <StyledBadge color="primary" variant="dot">
          <NotificationsIcon />
        </StyledBadge>
        <Typography>
          <Box fontWeight={600} fontSize={16} component="span">
            Notifications
          </Box>
        </Typography>
      </StyledButton>
      <Drawer
        anchor="right"
        open={isDrawerOpen}
        onClose={() => setIsDrawerOpen(false)}
        classes={{
          paper: classes.drawerPaper,
        }}
      >
        <Box
          component="span"
          display="flex"
          flexDirection="row"
          justifyContent="space-between"
          mb={5}
        >
          <Typography>
            <Box fontSize={16} fontWeight={700} component="span">
              Notifications
            </Box>
          </Typography>
          <CloseIcon
            fontSize="default"
            onClick={() => setIsDrawerOpen(false)}
          />
        </Box>
        <CTABox />
      </Drawer>
    </>
  );
};

export default Notifications;
