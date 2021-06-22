import { createMuiTheme } from "@material-ui/core/styles";

export const theme = createMuiTheme({
  palette: {
    background: {
      default: "#F5F6FA",
      white: "#FFFFFF",
    },
    text: {
      primary: "#212121",
    },
    primary: {
      main: "#00C078",
    },
  },
  typography: {
    fontFamily: "'Open Sans', san-serif",
    fontWeightLight: 300,
    fontWeightRegular: 400,
    fontWeightMedium: 600,
    fontWeightBold: 700,
    htmlFontSize: 16,
    fontSize: 16,

    h2: {
      fontSize: "1.375rem",
      fontWeight: 700,
    },
  },
  props: {
    MuiButtonBase: {
      disableRipple: true,
    },
  },
});
