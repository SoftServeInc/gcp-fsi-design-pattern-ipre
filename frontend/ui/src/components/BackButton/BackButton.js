import React from "react";
import ButtonBase from "@material-ui/core/ButtonBase";
import { makeStyles } from "@material-ui/core/styles";

import { Link as RouterLink } from "react-router-dom";
import { ArrowLeftIcon } from "../icons/ArrowLeftIcon";

const useStyles = makeStyles((theme) => ({
  button: {
    marginBottom: theme.spacing(4),
  },
}));

const BackButton = ({ to }) => {
  const classes = useStyles();

  return (
    <ButtonBase component={RouterLink} to={to} className={classes.button}>
      <ArrowLeftIcon />
      <span>Back to Assets Portfolio</span>
    </ButtonBase>
  );
};

export default BackButton;
