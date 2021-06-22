import React from "react";
import { withStyles, makeStyles } from "@material-ui/core/styles";
import Slider from "@material-ui/core/Slider";

const marks = [
  {
    value: 0,
    label: "Low",
  },

  {
    value: 50,
    label: "Medium",
  },
  {
    value: 100,
    label: "High",
  },
];

const useStyles = makeStyles((theme) => ({
  root: {
    width: "100%",
    paddingRight: 27,
    paddingBottom: theme.spacing(4),
  },
}));

const CustomSlider = withStyles({
  rail: {
    backgroundImage:
      "linear-gradient(to right, #27ae60, #63ae4a, #8bac38, #ada930, #cda334, #d49634, #da8937, #de7c3d, #ce6635, #bd502e, #ac3a28, #9a2222);",
    borderRadius: 21,
    paddingRight: 27,
    height: 20,
    opacity: 1,
  },
  track: {
    display: "none",
    maxWidth: "95%",
  },
  thumb: {
    width: 44,
    height: 44,
    color: "transparent",
    border: "13px solid white",
    transition: "none",
    marginTop: -12,
    "&:focus, &:hover, &$active": {
      boxShadow: "initial",
    },
    "&:after": {
      boxShadow: `0px 3px 1px -2px rgb(0 0 0 / 20%), 0px 2px 2px 0px rgb(0 0 0 / 14%), 0px 1px 5px 0px rgb(0 0 0 / 12%);`,
      top: -13,
      left: -13,
      right: -13,
      bottom: -13,
    },
  },
  mark: {
    display: "none",
  },
  markActive: {
    display: "none",
  },
  markLabel: {
    top: 50,
    fontSize: 14,
    paddingLeft: 22,
  },
})(Slider);

const RiskSlider = ({ onChange, riskLevel, onRelease }) => {
  const classes = useStyles();

  const handleChange = (event, newValue) => {
    onChange(event, newValue);
  };

  const onChangeCommitted = () => {
    onRelease();
  };

  return (
    <div className={classes.root}>
      <CustomSlider
        marks={marks}
        onChange={handleChange}
        onChangeCommitted={onChangeCommitted}
        value={riskLevel}
      />
    </div>
  );
};

export default RiskSlider;
