import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Grid from "@material-ui/core/Grid";
import CTABox from "../../components/CTABox";

import Layout from "../../layouts/Layout";
import Wallet from "../../components/Wallet";
import Expenses from "../../components/Expenses";

import API from "../../helpers/API";

const useStyles = makeStyles((theme) => ({
  Grid: {
    height: "100%",
  },
}));

const Homepage = () => {
  const [wallets, setWallets] = React.useState([]);
  const [isLoading, setIsLoading] = React.useState(false);

  React.useEffect(() => {
    setIsLoading(true);
    API.getWallets()
      .then((wallets) => setWallets(wallets))
      .then(() => setIsLoading(false));
  }, []);
  const classes = useStyles();

  return (
    <Layout>
      <Grid container spacing={2} className={classes.Grid}>
        <Grid item md={7}>
          {isLoading ? <p>Loading...</p> : <Wallet wallets={wallets} />}
        </Grid>
        <Grid item md={5}>
          <CTABox />
          <Expenses />
        </Grid>
      </Grid>
    </Layout>
  );
};

export default Homepage;
