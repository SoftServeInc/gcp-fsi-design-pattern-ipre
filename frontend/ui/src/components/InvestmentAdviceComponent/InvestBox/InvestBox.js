import React from "react";
import { useHistory } from "react-router-dom";
import { makeStyles } from "@material-ui/core/styles";
import Card from "@material-ui/core/Card";
import Typography from "@material-ui/core/Typography";
import Table from "@material-ui/core/Table";
import TableBody from "@material-ui/core/TableBody";
import TableCell from "@material-ui/core/TableCell";
import TableContainer from "@material-ui/core/TableContainer";
import TableRow from "@material-ui/core/TableRow";
import TableHead from "@material-ui/core/TableHead";
import Box from "@material-ui/core/Box";
import FormControl from "@material-ui/core/FormControl";
import InputAdornment from "@material-ui/core/InputAdornment";
import InputBase from "@material-ui/core/InputBase";
import Modal from "@material-ui/core/Modal";
import PrimaryButton from "../../PrimaryButton";

import API from "../../../helpers/API";

const useStyles = makeStyles((theme) => ({
  Card: {
    display: "flex",
    flexDirection: "column",
    justifyContent: "space-between",
    padding: "20px 25px",
    backgroundColor: "#212121",
    color: "#FFF",
    borderRadius: 10,
    marginTop: theme.spacing(3),
    marginBottom: theme.spacing(4),
  },
  Title: {
    paddingBottom: theme.spacing(6),
  },
  Subtitle: {
    fontSize: 16,
    fontWeight: "lighter",
    marginBottom: theme.spacing(3),
  },
  table: {
    backgroundColor: "#212121",
    color: "#FFF",
    borderBottom: "1px solid #F5F6FA",
    marginBottom: theme.spacing(3),
  },
  columnName: {
    fontSize: 18,
    fontWeight: 600,
    color: "#FFF",
    border: 0,
    padding: 0,
  },
  cell: {
    border: 0,
    padding: 0,
    paddingBottom: theme.spacing(2),
    color: "#FFF",
    fontSize: 24,
    fontWeight: 800,
    verticalAlign: "top",
  },
  percentage: {
    fontSize: 36,
    fontWeight: 600,
  },
  form: {
    width: 180,
  },
  input: {
    color: "#fff",
    fontSize: 36,
    fontWeight: 800,
    marginRight: 0,
  },
  modal: {
    position: "absolute",
    width: 420,
    backgroundColor: theme.palette.background.paper,
    borderRadius: 4,
    boxShadow: theme.shadows[5],
    padding: theme.spacing(4, 4),
    left: "50%",
    top: "50%",
    transform: "translate(-50%, -50%)",
  },
}));

const InvestModal = ({ modalOpen, handleClose, handleClick, amount, risk }) => {
  const classes = useStyles();

  return (
    <Modal
      open={modalOpen}
      onClose={handleClose}
      aria-labelledby="confirm-investment-modal"
    >
      <Box className={classes.modal} display="flex" flexDirection="column">
        <Box marginBottom={5}>
          <Typography align="center">
            You are going to invest <strong>${amount}</strong> in stocks with
            <strong> {risk} risk portfolio</strong>.
          </Typography>
        </Box>
        <PrimaryButton width={220} onClick={handleClick}>
          Agree and Invest!
        </PrimaryButton>
        <PrimaryButton width={220} inverted="true" onClick={handleClose}>
          Cancel
        </PrimaryButton>
      </Box>
    </Modal>
  );
};

const InvestBox = ({
  onChange,
  amount,
  setAmount,
  risk,
  maxAmount,
  metrics,
  assets,
}) => {
  const [modalOpen, setModalOpen] = React.useState(false);

  let history = useHistory();
  const classes = useStyles();

  const handleOpen = () => {
    setModalOpen(true);
  };

  const handleClose = () => {
    setModalOpen(false);
  };

  const handleChange = (event) => {
    onChange(event.target.value);
  };

  const handleClick = () => {
    setModalOpen(false);
    const data = {
      assets,
      metrics,
      invested_sum: amount,
    };

    API.postAssets(data).then(() =>
      history.push({
        pathname: "/investments",
        state: { showToast: true },
      })
    );
  };

  return (
    <Card className={classes.Card} elevation={0}>
      <TableContainer elevation={0}>
        <Table className={classes.table} aria-label="portfolio details table">
          <TableHead>
            <TableRow>
              <TableCell className={classes.columnName}>
                Expected Rate of Return
              </TableCell>
              <TableCell align="left" className={classes.columnName}>
                Volatility
              </TableCell>
              <TableCell align="left" className={classes.columnName}>
                VaR
              </TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            <TableRow>
              <TableCell className={classes.cell}>
                <Typography>
                  <Box fontSize={52} fontWeight={800} component="span">
                    {metrics?.rate_of_return}
                    <span className={classes.percentage}>%</span>
                  </Box>
                </Typography>
              </TableCell>
              <TableCell align="left" className={classes.cell}>
                {metrics?.volatility}
              </TableCell>
              <TableCell align="left" className={classes.cell}>
                {metrics?.value_at_risk}
              </TableCell>
            </TableRow>
          </TableBody>
        </Table>
      </TableContainer>
      <Box display="flex" justifyContent="start">
        <FormControl className={classes.form}>
          <InputBase
            className={classes.input}
            id="investment-amount"
            value={amount}
            onChange={handleChange}
            type="number"
            inputProps={{
              max: maxAmount,
              onBlur: () =>
                parseInt(amount, 10) > parseInt(maxAmount, 10)
                  ? setAmount(maxAmount)
                  : null,
            }}
            startAdornment={
              <InputAdornment
                disableTypography
                className={classes.input}
                position="start"
              >
                $
              </InputAdornment>
            }
          />
        </FormControl>
        <PrimaryButton width={220} onClick={handleOpen}>
          Invest
        </PrimaryButton>
      </Box>
      <InvestModal
        modalOpen={modalOpen}
        handleClose={handleClose}
        handleClick={handleClick}
        amount={amount}
        risk={risk}
      />
    </Card>
  );
};

export default InvestBox;
