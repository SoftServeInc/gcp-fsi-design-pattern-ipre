import React from "react";
import ButtonBase from "@material-ui/core/ButtonBase";
import { makeStyles } from "@material-ui/core/styles";

const useStyles = makeStyles((theme) => ({
  button: {
    width: (props) => props.width ?? "auto",
    color: (props) => (props.inverted ? "#00C078" : "#FFF"),
    backgroundColor: (props) => (props.inverted ? "#FFF" : "#00C078"),
    border: (props) =>
      props.inverted ? "1px solid #00C078" : "1 px solid #FFF",
    maxWidth: 300,
    height: 40,
    borderRadius: 99,
    justifyContent: "center",
    fontWeight: 700,
    fontSize: 16,
    alignSelf: "center",
    padding: "10px 20px",
    marginBottom: theme.spacing(1),
  },
}));

const CTAButton = (props) => {
  const classes = useStyles(props);

  return (
    <ButtonBase className={classes.button} {...props}>
      {props.children}
    </ButtonBase>
  );
};

export default CTAButton;
