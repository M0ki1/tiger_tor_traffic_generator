import { Typography, Link } from "@mui/material";

function Copyright() {
	return (
		<Typography
			variant="body2"
			color="text.secondary"
			align="center"
			sx={{ mt: 5 }}
		>
			{"V3ry S3cur3 © "}
			<Link color="inherit" href="https://github.com/DavidAkaFunky/SIRS2022">
				Github
			</Link>{" "}
			{new Date().getFullYear()}.
		</Typography>
	);
}

export default Copyright;
