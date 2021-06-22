import React from "react";
import Paper from "@material-ui/core/Paper";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import Snackbar from "@material-ui/core/Snackbar";
import { CloseIcon } from "../../components/icons/CloseIcon";

import IconButton from "@material-ui/core/IconButton";

import Box from "@material-ui/core/Box";
import Divider from "@material-ui/core/Divider";
import Chip from "@material-ui/core/Chip";

import Layout from "../../layouts/Layout";
import CTAButton from "../../components/CTAButton";
import PortfolioDetailsTable from "../../components/PortfolioDetailsTable";
import RoRChart from "../../components/RoRChart";
import { UpIcon } from "../../components/icons/UpIcon";
import { SuccessIcon } from "../../components/icons/SuccessIcon";

import API from "../../helpers/API";

const DRAWER_WIDTH = 250;

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
  paper: {
    minHeight: `100%`,
    borderRadius: 10,
    padding: 20,
  },
  divider: {
    marginTop: theme.spacing(3),
    marginBottom: theme.spacing(3),
  },
  description: {
    marginBottom: 30,
  },
  chip: {
    backgroundColor: theme.palette.primary.main,
    color: "#FFF",
  },
  cta: {
    width: 170,
    textAlign: "right",
    marginRight: theme.spacing(2),
  },
  snackbarIcon: {
    marginRight: theme.spacing(2),
  },
  snackbarContent: {
    backgroundColor: "#00C078",
    borderRadius: 10,
    fontSize: 18,
    fontWeight: 600,
  },
  stocksTitle: {
    marginTop: theme.spacing(3),
    marginBottom: theme.spacing(3),
  },
}));

const NoInvestments = () => {
  const classes = useStyles();

  return (
    <>
      <Typography variant="h2">Assets Portfolio</Typography>
      <Divider light className={classes.divider} />
      <Box
        display="flex"
        flexDirection="column"
        alignItems="center"
        marginTop={10}
      >
        <Box fontWeight={400} fontSize={24} className={classes.description}>
          Currently you have no assets in portfolio
        </Box>
        <CTAButton />
      </Box>
    </>
  );
};

const AssetsStatistics = ({ invested_sum, metrics }) => {
  const classes = useStyles();

  return (
    <>
      <Typography>
        <Box component="span" fontSize={16} fontWeight={600}>
          Total Value
        </Box>
      </Typography>

      <Box display="flex" marginBottom={3}>
        <Typography>
          <Box fontSize={40} fontWeight={600} component="span" marginRight={2}>
            ${invested_sum}
          </Box>
        </Typography>
        <Box display="flex" flexDirection="column" marginX={2} fontWeight={600}>
          Expected RoR
          <Chip
            icon={<UpIcon style={{ color: "#FFF" }} />}
            size="small"
            label={`${metrics.rate_of_return}%`}
            className={classes.chip}
          />
        </Box>
        <Box display="flex" flexDirection="column" marginX={2} fontWeight={600}>
          Volatility
          <Chip
            size="small"
            label={`${metrics.volatility}%`}
            className={classes.chip}
          />
        </Box>
        <Box display="flex" flexDirection="column" marginX={2} fontWeight={600}>
          VaR
          <Chip
            size="small"
            label={`${metrics.value_at_risk}%`}
            className={classes.chip}
          />
        </Box>
      </Box>
    </>
  );
};

const InvestmentsContent = ({ assets }) => {
  const classes = useStyles();

  if (!assets) return <NoInvestments />;

  const { invested_sum, metrics } = assets;

  return (
    <>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h2">Assets Portfolio</Typography>
        <Box display="flex">
          <Typography variant="body2" component="div" className={classes.cta}>
            You can earn more by making investments
          </Typography>
          <CTAButton />
        </Box>
      </Box>

      <Divider light className={classes.divider} />
      <AssetsStatistics invested_sum={invested_sum} metrics={metrics} />
      <RoRChart value={invested_sum} rateOfReturn={metrics.rate_of_return} />
      <Typography variant="h2" className={classes.stocksTitle}>
        All Stocks
      </Typography>
      <PortfolioDetailsTable {...assets} showProfit={true} />
    </>
  );
};

const Investments = () => {
  const [assets, setAssets] = React.useState(null);
  const [isLoading, setIsLoading] = React.useState(true);
  const [alertOpen, setAlertOpen] = React.useState(false);

  const classes = useStyles();

  const handleAlertClose = (event, reason) => {
    if (reason === "clickaway") {
      return;
    }

    setAlertOpen(false);
  };

  const fetchAssets = async () => {
    setIsLoading(true);
    try {
      await API.getAssets().then((assets) => setAssets(assets));
    } catch (error) {
      setAssets(null);
    }
    setIsLoading(false);
  };

  React.useEffect(() => {
    fetchAssets();
  }, []);

  const toastMessage = (
    <Box display="flex">
      <SuccessIcon fontSize="small" className={classes.icon} /> Successfully
      invested!
    </Box>
  );

  return (
    <Layout>
      <Paper elevation={0} className={classes.paper}>
        {isLoading ? (
          <div>Loading...</div>
        ) : (
          <InvestmentsContent assets={assets} />
        )}
        <Snackbar
          anchorOrigin={{ vertical: "top", horizontal: "center" }}
          open={alertOpen}
          autoHideDuration={3000}
          onClose={handleAlertClose}
          message={toastMessage}
          ContentProps={{
            classes: {
              root: classes.snackbarContent,
            },
          }}
          action={
            <React.Fragment>
              <IconButton
                size="small"
                aria-label="close"
                color="inherit"
                onClick={handleAlertClose}
              >
                <CloseIcon />
              </IconButton>
            </React.Fragment>
          }
        />
      </Paper>
    </Layout>
  );
};

export default Investments;
