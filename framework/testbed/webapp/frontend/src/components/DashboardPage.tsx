import {
	Box,
	Button,
	Stack,
	Typography,
} from "@mui/material";
import FilterListIcon from '@mui/icons-material/FilterList';
import { ReactNode } from "react";

interface DashboardPageProps {
    dashboard: ReactNode;
    title: string;
}

function DashboardPage(props: DashboardPageProps) {
    const { dashboard, title } = props;
	return (
		<Box sx={{ bgcolor: "background.paper" }}>
			<Stack direction="row" alignItems="baseline" justifyContent="space-between">	
				<Typography
					component="h2"
					variant="h3"
					color="text.primary"
					gutterBottom
				>
					{title}
				</Typography>
				<Button
					sx = {{width: 100, height: 35}}
					variant="contained"
				>	
					<FilterListIcon sx={{mr: 0.5}}/>
					Filter
				</Button>
			</Stack>
			{dashboard}
		</Box>
	);
}

export default DashboardPage;
