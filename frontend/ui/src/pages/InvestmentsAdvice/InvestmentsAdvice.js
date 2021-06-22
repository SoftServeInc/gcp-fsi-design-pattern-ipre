import React from "react";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import Layout from "../../layouts/Layout";
import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";
import PortfolioDetailsTable from "../../components/PortfolioDetailsTable";
import BackButton from "../../components/BackButton";
import InvestmentAdviceComponent from "../../components/InvestmentAdviceComponent";
import throttle from "lodash.throttle";
import API from "../../helpers/API";

const useStyles = makeStyles((theme) => ({
  paper: {
    height: `95%`,
    overflowY: "auto",
    borderRadius: 10,
    padding: 20,
  },
  divider: {
    marginTop: 25,
    marginBottom: 30,
  },
  description: {
    marginBottom: 30,
  },
}));

const InvestmentsAdvice = () => {
  const [assets, setAssets] = React.useState([]);
  const [isLoading, setIsloading] = React.useState(false);
  const classes = useStyles();

  const fetchAdvicedAssets = async () => {
    setIsloading(true);
    await API.getInitialAdvice().then((assets) => setAssets(assets));
    setIsloading(false);
  };

  const throttledFetchAdvicedAssets = throttle(async (risk, amount) => {
    await API.getAdvice(risk, amount).then((assets) => setAssets(assets));
  }, 200);

  React.useEffect(() => {
    fetchAdvicedAssets();
  }, []);

  const fetchNewAdvice = (risk, amount) => {
    throttledFetchAdvicedAssets(risk, amount);
  };

  const { metrics, risk_level, suggested_sum } = assets;

  const investmentAdviceProps = {
    metrics,
    risk_level,
    suggested_sum,
    assets,
  };

  return (
    <Layout>
      <BackButton to="/investments" />
      <Paper elevation={0} className={classes.paper}>
        {isLoading ? (
          <div>Loading...</div>
        ) : (
          <>
            <Typography variant="h2">Investments Advice</Typography>
            <Divider light className={classes.divider} />
            <InvestmentAdviceComponent
              {...investmentAdviceProps}
              fetchNewAdvice={fetchNewAdvice}
            />
            <Typography variant="h2">Portfolio Details</Typography>
            <Divider light className={classes.divider} />
            <PortfolioDetailsTable {...assets} showProfit={false} />
          </>
        )}
      </Paper>
    </Layout>
  );
};

export default InvestmentsAdvice;
