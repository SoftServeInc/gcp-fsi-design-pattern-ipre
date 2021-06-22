import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import Card from "@material-ui/core/Card";

const useStyles = makeStyles((theme) => ({
  card: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    padding: "20px 25px",
    borderRadius: 10,
    height: `calc(100% - 230px)`,
    marginTop: 20,
  },
}));

const Expenses = () => {
  const classes = useStyles();

  return (
    <Card className={classes.card} elevation={0}>
      <Typography variant="h2">Expenses</Typography>
    </Card>
  );
};

export default Expenses;
