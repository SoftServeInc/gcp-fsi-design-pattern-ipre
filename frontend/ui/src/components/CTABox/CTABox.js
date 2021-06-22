import React from "react";
import Card from "@material-ui/core/Card";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import CTAButton from "../CTAButton";

const useStyles = makeStyles((theme) => ({
  Card: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    padding: "20px 25px",
    border: `2px solid ${theme.palette.primary.main}`,
    borderRadius: 10,
  },
  Title: {
    paddingBottom: theme.spacing(6),
  },
  Subtitle: {
    fontSize: 16,
    fontWeight: "lighter",
    marginBottom: theme.spacing(3),
  },
}));

const CTABox = () => {
  const classes = useStyles();

  return (
    <Card className={classes.Card} elevation={0}>
      <Typography className={classes.Title} variant="h2">
        Did you know?
      </Typography>
      <Typography
        variant="subtitle1"
        align="center"
        className={classes.Subtitle}
      >
        You can earn more by making investments
      </Typography>
      <CTAButton />
    </Card>
  );
};

export default CTABox;
