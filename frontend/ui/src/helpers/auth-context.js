import React from "react";
import API from "./API";

export const AuthContext = React.createContext();

const AuthProvider = ({ children }) => {
  const [sentLoginReq, setSentLoginReq] = React.useState(null);
  const [state, setState] = React.useState({
    status: "pending",
    error: null,
    user: null,
  });

  React.useEffect(() => {
    API.getUser().then(
      (user) => setState({ status: "success", error: null, user }),
      (error) => setState({ status: "error", error: error, user: null })
    );
  }, [sentLoginReq]);

  return (
    <AuthContext.Provider value={{ state, setSentLoginReq }}>
      {state.status === "pending" ? "Loading..." : children}
    </AuthContext.Provider>
  );
};

const useAuthState = () => {
  const { state } = React.useContext(AuthContext);

  const isPending = state.status === "pending";
  const isError = state.status === "error";
  const isSuccess = state.status === "success";
  const isAuthenticated = state.user && isSuccess;
  return {
    ...state,
    isPending,
    isError,
    isSuccess,
    isAuthenticated,
  };
};

export { AuthProvider, useAuthState };
