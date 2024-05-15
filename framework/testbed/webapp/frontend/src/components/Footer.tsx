import { 
	Container, 
	Grid, 
	Typography, 
	Link, 
	GlobalStyles 
} from "@mui/material";
import Copyright from "./Copyright";
import React from "react";

const footers = [
	{
		title: "Company",
		description: [
			{ name: "Team", href: "/" },
			{ name: "Contact us", href: "/" },
			{ name: "Locations", href: "/" },
		],
	},
	{
		title: "Services",
		description: [
			{ name: "Credit Cards", href: "/services/credit-cards" },
			{ name: "Mortgages", href: "/services/mortgages" },
			{ name: "Loans", href: "/services/loans" },
		],
	},
	{
		title: "Products",
		description: [{ name: "Stocks", href: "/products/stocks" }],
	},
	{
		title: "Legal",
		description: [
			{ name: "Privacy policy", href: "/" },
			{ name: "Terms of use", href: "/" },
		],
	},
];

function Footer() {
	return (
		<>
			<GlobalStyles
				styles={{ ul: { margin: 0, padding: 0, listStyle: "none" } }}
			/>
			<Container
				maxWidth="md"
				component="footer"
				sx={{
					mt: 8,
					py: [3, 6],
				}}
			>
				<Grid container spacing={4} justifyContent="space-evenly">
					{footers.map((footer) => (
						<Grid item xs={6} sm={3} key={footer.title}>
							<Typography variant="h6" color="text.primary" gutterBottom>
								{footer.title}
							</Typography>
							<ul>
								{footer.description.map((item) => (
									<li key={item.name}>
										<Link
											href={item.href}
											variant="subtitle1"
											color="text.secondary"
											style={{ textDecoration: "none" }}
										>
											{item.name}
										</Link>
									</li>
								))}
							</ul>
						</Grid>
					))}
				</Grid>
				<Copyright />
			</Container>
		</>
	);
}

export default Footer;
