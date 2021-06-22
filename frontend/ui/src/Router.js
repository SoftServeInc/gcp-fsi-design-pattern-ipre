import React from "react";
import { Switch, Route } from "react-router-dom";

import Homepage from "./pages/Homepage";
import Investments from "./pages/Investments";
import InvestmentsAdvice from "./pages/InvestmentsAdvice";
import Login from "./pages/Login";

const Router = () => (
  <Switch>
    <Route exact path={`/home`} component={Homepage} />
    <Route exact path={`/investments`} component={Investments} />
    <Route exact path={`/investments-advice`} component={InvestmentsAdvice} />
    <Route exact path={`/login`} component={Login} />
    <Route path={`/`} component={Homepage} />
  </Switch>
);

export default Router;
