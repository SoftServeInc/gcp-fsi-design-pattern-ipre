import React from "react";
import Typography from "@material-ui/core/Typography";
import Grid from "@material-ui/core/Grid";
import RiskSlider from "./RiskSlider";
import InvestBox from "./InvestBox";

const translateRisk = (newValue) => {
  if (newValue <= 33) {
    return "low";
  } else if (newValue <= 66) {
    return "medium";
  } else {
    return "high";
  }
};

const InvestmentsAdviceComponent = ({
  metrics,
  risk_level,
  suggested_sum,
  assets,
  fetchNewAdvice,
}) => {
  const [amount, setAmount] = React.useState(suggested_sum);
  const [risk, setRisk] = React.useState(risk_level);

  const handleAmountChange = (newValue) => {
    setAmount(newValue);
  };

  const handleRiskChange = (event, newValue) => {
    setRisk(newValue);
  };

  return (
    <>
      <Typography>
        Based on your profile we suggest to invest
        <strong>{` $${amount}`}</strong> in stocks with
        <strong>{` ${translateRisk(risk)}`}</strong> risk portfolio.
      </Typography>
      <Grid container>
        <Grid item md={10}>
          <InvestBox
            onChange={handleAmountChange}
            amount={amount}
            setAmount={setAmount}
            maxAmount={suggested_sum}
            risk={translateRisk(risk)}
            metrics={metrics}
            {...assets}
          />
          <RiskSlider
            onChange={handleRiskChange}
            onRelease={() => fetchNewAdvice(risk, amount)}
            riskLevel={risk}
          />
        </Grid>
      </Grid>
    </>
  );
};

export default InvestmentsAdviceComponent;
