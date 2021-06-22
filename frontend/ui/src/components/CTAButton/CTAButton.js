import React from "react";
import { Link as RouterLink } from "react-router-dom";

import PrimaryButton from "../PrimaryButton";

const CTAButton = () => {
  return (
    <PrimaryButton component={RouterLink} to="/investments-advice">
      Receive Investments Advice
    </PrimaryButton>
  );
};

export default CTAButton;
