import SvgIcon from "@material-ui/core/SvgIcon";

export const LockIcon = (props) => (
  <SvgIcon {...props}>
    <rect
      x="8.75"
      y="3.75"
      width="6.5"
      height="10.5"
      rx="3.25"
      stroke="#212121"
      strokeWidth="1.5"
    />
    <rect
      x="6.5"
      y="9.5"
      width="11"
      height="10"
      rx="2.5"
      fill="#212121"
      stroke="#212121"
    />
    <circle cx="12" cy="13.25" r="1.25" fill="white" />
    <path
      d="M11.5833 13.6667H12.4166L12.8333 17.0001H11.1666L11.5833 13.6667Z"
      fill="white"
    />
  </SvgIcon>
);
