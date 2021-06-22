import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Typography from "@material-ui/core/Typography";
import Card from "@material-ui/core/Card";
import Grid from "@material-ui/core/Grid";
import Divider from "@material-ui/core/Divider";
import Box from "@material-ui/core/Box";
import formatRelative from "date-fns/formatRelative";

import { MasterCardIcon } from "../../components/icons/MasterCardIcon";
import API from "../../helpers/API";

const useStyles = makeStyles((theme) => ({
  mainCard: {
    height: "100%",
    maxHeight: "100%",
    overflowY: "auto",
    display: "flex",
    flexDirection: "column",
    padding: "20px 25px",
    borderRadius: 10,
  },
  card: {
    padding: "12px",
    cursor: (props) => (props.isActive ? `initial` : "pointer"),
    background: (props) =>
      props.isActive
        ? theme.palette.background.white
        : theme.palette.background.default,
    border: (props) =>
      props.isActive
        ? `2px solid ${theme.palette.primary.main}`
        : "2px solid #E7E9EF",
    borderRadius: 10,
  },
  divider: {
    margin: "30px 0",
  },
  title: {
    marginBottom: "30px",
  },
  transaction: {
    border: "1px solid #E7E9EF",
    borderRadius: 10,
    padding: 10,
    display: "flex",
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    marginBottom: 12,
    maxHeight: "100%",
  },
}));

const Transaction = ({ created_at, sum, name, sum_direction }) => {
  const classes = useStyles();
  const relativeDate = formatRelative(Date.parse(created_at), Date.now());

  return (
    <Card elevation={0} className={classes.transaction}>
      <Box>
        <Box fontSize={14} fontWeight={600} pb={1}>
          {name}
        </Box>
        <Box fontSize={10} fontWeight={30} pb={1}>
          {relativeDate}
        </Box>
      </Box>
      <Box>{`${sum_direction} $${sum}`}</Box>
    </Card>
  );
};

const AccountTile = (props) => {
  const classes = useStyles(props);

  return (
    <Grid item md={4} onClick={props.onClick}>
      <Card className={classes.card} elevation={0}>
        <Box fontSize={14} fontWeight={600} pb={1}>
          {props.bank_name}
        </Box>

        <Box fontSize={18}>{`$${props.balance}`}</Box>
        <Box
          display="flex"
          justifyContent="space-between"
          alignItems="center"
          pt={5}
        >
          <MasterCardIcon />
          <Box>&bull;&bull;&bull;&bull; {props.card_number.slice(-4)}</Box>
        </Box>
      </Card>
    </Grid>
  );
};

const Wallet = ({ wallets }) => {
  const [activeWallet, setActiveWallet] = React.useState(wallets[0]?.id);
  const [transactions, setTransactions] = React.useState();

  const fetchActiveWalletTransactions = (activeWalletId) =>
    API.getWallet(activeWalletId).then((transactions) =>
      setTransactions(transactions)
    );

  React.useEffect(() => {
    if (activeWallet?.length > 0) {
      fetchActiveWalletTransactions(activeWallet);
    }
  }, [activeWallet]);

  const classes = useStyles();
  return (
    <Card className={classes.mainCard} elevation={0}>
      <Typography variant="h2" className={classes.title}>
        Wallet
      </Typography>
      <Grid container spacing={2}>
        {wallets?.map((wallet) => (
          <AccountTile
            {...wallet}
            key={wallet.id}
            isActive={activeWallet === wallet.id}
            onClick={() => setActiveWallet(wallet.id)}
          />
        ))}
      </Grid>
      <Divider className={classes.divider} variant="middle" />
      <Typography variant="h2" className={classes.title}>
        Transactions
      </Typography>
      {transactions?.map((transaction) => (
        <Transaction {...transaction} key={transaction.created_at} />
      ))}
    </Card>
  );
};

export default Wallet;
