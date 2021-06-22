import React from "react";
import Drawer from "@material-ui/core/Drawer";
import { makeStyles } from "@material-ui/core/styles";
import { CloseIcon } from "../icons/CloseIcon";
import Typography from "@material-ui/core/Typography";
import Box from "@material-ui/core/Box";
import Card from "@material-ui/core/Card";
import Chip from "@material-ui/core/Chip";
import Divider from "@material-ui/core/Divider";
import StockChart from "../StockChart";
import format from "date-fns/format";
import { UpIcon } from "../icons/UpIcon";
import { DownIcon } from "../icons/DownIcon";

const useStyles = makeStyles((theme) => ({
  drawerPaper: {
    width: 380,
    display: "flex",
    flexDirection: "column",
    padding: "20px 30px",
  },
  newsCard: {
    display: "flex",
    alignItems: "center",
    flexDirection: "row",
    marginBottom: theme.spacing(1),
  },
  chip: {
    backgroundColor: (props) =>
      props.change_for_day_direction === "+"
        ? theme.palette.primary.main
        : "#D80000",
    color: "#FFF",
  },
  newsImage: {
    borderRadius: 3,
    height: 56,
    width: 56,
  },
  div: {
    height: 64,
    width: 64,
    marginRight: theme.spacing(2),
    padding: 4,
    backgroundColor: "rgba(200, 203, 204, 0.4)",
    borderRadius: 6,
  },
  divider: {
    backgroundColor: "#212121",
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  sectionContainer: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  change: {
    color: (props) =>
      props.change_for_day_direction === "+"
        ? theme.palette.primary.main
        : "#D80000",
  },
}));

const PriceDetails = ({
  timestamp,
  timezone,
  currency,
  exchange,
  current_price,
  volume,
  change_for_day,
  change_for_day_direction,
  change_for_day_sum,
  change_for_day_sum_direction,
}) => {
  const classes = useStyles({ change_for_day_direction });

  const priceChange = (
    <span className={classes.change}>
      {change_for_day_sum_direction}
      {change_for_day_sum}
    </span>
  );

  const priceChangeIcon =
    change_for_day_direction === "+" ? (
      <UpIcon style={{ color: "#FFF" }} />
    ) : (
      <DownIcon style={{ color: "#FFF" }} />
    );

  const [currentPriceDollars, currentPriceCents] = current_price
    .toString()
    .split(".");

  return (
    <>
      <Typography>
        <Box fontSize={24} fontWeight={700} component="span">
          ${currentPriceDollars}.
        </Box>
        <Box fontSize={16} fontWeight={400} component="span">
          {currentPriceCents}
        </Box>
      </Typography>
      <Box display="flex" alignItems="baseline" marginTop={1} marginBottom={2}>
        <Box mr={2}>
          {" "}
          <Chip
            icon={priceChangeIcon}
            size="small"
            label={`${change_for_day}%`}
            className={classes.chip}
          />
        </Box>
        <Typography>
          <Box fontSize={12} fontWeight={700} component="span">
            {priceChange} {volume}
          </Box>
        </Typography>
      </Box>
      <Typography>
        <Box fontSize={12} fontWeight={400} component="span" marginBottom={2}>
          {format(new Date(timestamp), "LLL, hh:mm:ss b ")}
          {timezone} · {currency} · {exchange}
        </Box>
      </Typography>
      <Divider className={classes.divider} />
    </>
  );
};

const StockStats = ({
  day_range_low,
  day_range_high,
  year_range_high,
  year_range_low,
  previous_close,
}) => {
  const classes = useStyles();

  return (
    <Box className={classes.sectionContainer}>
      <Box display="flex" flexDirection="column" fontSize={12}>
        <Box display="flex" flexDirection="row" justifyContent="space-between">
          <span>Previous Close</span>
          <span>${previous_close}</span>
        </Box>
        <Box display="flex" flexDirection="row" justifyContent="space-between">
          <span>Day Range</span>
          <span>
            ${day_range_low} – ${day_range_high}
          </span>
        </Box>
        <Box display="flex" flexDirection="row" justifyContent="space-between">
          <span>Year Range</span>
          <span>
            ${year_range_low} – ${year_range_high}
          </span>
        </Box>
      </Box>
    </Box>
  );
};

const StockNews = () => {
  const classes = useStyles();

  return (
    <Box className={classes.sectionContainer}>
      <Typography>
        <Box fontSize={16} fontWeight={700} component="span">
          News
        </Box>
      </Typography>

      <Card elevation={0} className={classes.newsCard} square>
        <div className={classes.div}>
          <img
            src="https://via.placeholder.com/58x58"
            alt="wall-street"
            className={classes.newsImage}
          />
        </div>
        <Typography>
          <Box fontSize={12} fontWeight={700} component="span">
            Reuters &bull;
          </Box>
          <Box fontSize={12} fontWeight={400} component="span">
            1 day ago
          </Box>
          <Box fontSize={12} fontWeight={400} component="span" display="flex">
            S&P 500 slips in choppy trade as energy, financials tumble
          </Box>
        </Typography>
      </Card>

      <Card elevation={0} className={classes.newsCard} square>
        <div className={classes.div}>
          <img
            src="https://via.placeholder.com/58x58"
            alt="wall-street"
            className={classes.newsImage}
          />
        </div>
        <Typography>
          <Box fontSize={12} fontWeight={700} component="span">
            Reuters &bull;
          </Box>
          <Box fontSize={12} fontWeight={400} component="span">
            1 day ago
          </Box>
          <Box fontSize={12} fontWeight={400} component="span" display="flex">
            S&P 500 slips in choppy trade as energy, financials tumble
          </Box>
        </Typography>
      </Card>

      <Card elevation={0} className={classes.newsCard} square>
        <div className={classes.div}>
          <img
            src="https://via.placeholder.com/58x58"
            alt="wall-street"
            className={classes.newsImage}
          />
        </div>
        <Typography>
          <Box fontSize={12} fontWeight={700} component="span">
            Reuters &bull;
          </Box>
          <Box fontSize={12} fontWeight={400} component="span">
            1 day ago
          </Box>
          <Box fontSize={12} fontWeight={400} component="span" display="flex">
            S&P 500 slips in choppy trade as energy, financials tumble
          </Box>
        </Typography>
      </Card>
    </Box>
  );
};

const StockDetails = ({
  stockDetails,
  isStockDetailsOpen,
  onClose,
  isLoading,
}) => {
  const classes = useStyles();
  const {
    timestamp,
    timezone,
    currency,
    exchange,
    current_price,
    volume,
    change_for_day,
    change_for_day_direction,
    change_for_day_sum,
    change_for_day_sum_direction,
    day_range_low,
    day_range_high,
    year_range_high,
    year_range_low,
    history,
    previous_close,
  } = stockDetails;

  const priceDetailsProps = {
    timestamp,
    timezone,
    currency,
    exchange,
    current_price,
    volume,
    change_for_day,
    change_for_day_direction,
    change_for_day_sum,
    change_for_day_sum_direction,
  };

  const StockStatsProps = {
    day_range_low,
    day_range_high,
    year_range_high,
    year_range_low,
    previous_close,
  };

  return (
    <>
      <Drawer
        anchor="right"
        open={isStockDetailsOpen}
        onClose={onClose}
        classes={{
          paper: classes.drawerPaper,
        }}
      >
        {isLoading ? (
          <div>Loading</div>
        ) : (
          <>
            <Box
              display="flex"
              flexDirection="row"
              justifyContent="space-between"
              mb={3}
            >
              <Typography>
                <Box fontSize={16} fontWeight={700} component="span">
                  {stockDetails.long_name}
                </Box>
              </Typography>
              <CloseIcon fontSize="default" onClick={onClose} />
            </Box>
            <PriceDetails {...priceDetailsProps} />
            <Typography>
              <Box fontSize={16} fontWeight={700} component="span">
                Stats
              </Box>
            </Typography>
            <StockChart history={history} />
            <StockStats {...StockStatsProps} />
            <Divider />
            <StockNews />
          </>
        )}
      </Drawer>
    </>
  );
};

export default StockDetails;
