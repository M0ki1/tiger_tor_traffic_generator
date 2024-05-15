import {
	Box,
	Typography,
} from "@mui/material";

function Home() {
	return (
		<Box>
			<Typography
				component="h1"
				variant="h2"
				align="center"
				color="text.primary"
				gutterBottom
			>
				Welcome to Torpedo
			</Typography>
		</Box>
	);
}

export default Home;
