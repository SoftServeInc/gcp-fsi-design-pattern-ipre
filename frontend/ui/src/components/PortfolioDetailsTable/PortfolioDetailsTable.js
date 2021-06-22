import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableRow from "@material-ui/core/TableRow";
import Paper from "@material-ui/core/Paper";
import StockDetails from "../StockDetails";
import ButtonBase from "@material-ui/core/ButtonBase";
import API from "../../helpers/API";
import { Typography } from "@material-ui/core";

const useStyles = makeStyles({
  table: {
    minWidth: 650,
  },
  cell: {
    borderBottom: 0,
    padding: 10,
  },
  profit: {
    borderBottom: 0,
    fontWeight: 600,
    padding: 10,
  },
  buttonLink: {
    fontSize: 16,
    color: "#02A2CF",
    textDecoration: "underline",
  },
});

const PortfolioDetailsTable = ({ assets, showProfit }) => {
  const [isStockDetailsOpen, setIsStockDetailsOpen] = React.useState(false);
  const [stockDetails, setStockDetails] = React.useState({});
  const [isLoading, setIsLoading] = React.useState(false);

  const fetchStockDetails = async (name) => {
    setIsLoading(true);

    await API.getAsset(name).then((asset) => setStockDetails(asset));

    setIsLoading(false);
  };

  const handleClick = (name) => {
    fetchStockDetails(name);
    setIsStockDetailsOpen(true);
  };

  const classes = useStyles();

  return (
    <>
      <TableContainer component={Paper} elevation={0}>
        <Table className={classes.table} aria-label="portfolio details table">
          <TableBody>
            {assets?.map((asset) => (
              <TableRow key={asset.asset_name}>
                <TableCell className={classes.cell}>
                  {`${asset.part_of_portfolio}%`}
                </TableCell>
                <TableCell className={classes.cell}>
                  {asset.overall_sum}
                </TableCell>
                {showProfit ? (
                  <TableCell className={classes.profit}>
                    {asset.statistics.profit_direction} $
                    {asset.statistics.profit}
                  </TableCell>
                ) : null}
                <TableCell className={classes.cell}>
                  {asset.asset_name}
                </TableCell>
                <TableCell className={classes.cell}>
                  <ButtonBase onClick={() => handleClick(asset.asset_name)}>
                    <Typography className={classes.buttonLink}>
                      {asset.statistics.long_name}
                    </Typography>
                  </ButtonBase>
                </TableCell>
                <TableCell className={classes.cell}>
                  ${asset.statistics.current_price}
                </TableCell>
                <TableCell
                  className={classes.cell}
                  style={
                    asset.statistics.change_for_day_direction === "+"
                      ? { color: "#00C078" }
                      : { color: "#D80000" }
                  }
                >
                  {asset.statistics.change_for_day_direction === "+" ? (
                    <>&uarr; {asset.statistics.change_for_day}%</>
                  ) : (
                    <>&darr; {asset.statistics.change_for_day}%</>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>
      <StockDetails
        isStockDetailsOpen={isStockDetailsOpen}
        stockDetails={stockDetails}
        onClose={() => setIsStockDetailsOpen(false)}
        isLoading={isLoading}
      />
    </>
  );
};
export default PortfolioDetailsTable;
