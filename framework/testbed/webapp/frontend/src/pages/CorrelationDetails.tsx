import { useParams } from "react-router-dom";
import {
	Box,
	Button,
	Chip,
	Divider,
	Paper,
	Stack,
	Table,
	TableBody,
	TableCell,
	TableContainer,
	TableHead,
	TablePagination,
	TableRow,
	Typography,
} from "@mui/material";
import {
	ArrowLeft as ArrowLeftIcon,
	KeyboardDoubleArrowRight as KeyboardDoubleArrowRightIcon,
} from '@mui/icons-material';
import { useEffect, useState } from "react";
import { createPacketData } from "../methods/packetMethods";
import axios from "axios";
import { CorrelationDetailsData, createCorrelationDetailsData } from "../methods/correlationMethods";
import { FlowDetailsData, createFlowDetailsData } from "../methods/flowsMethods";

const rowsPerPage = 20;

interface Column {
	id: 'timestamp' | 'size' | 'source' | 'dest';
	label: string;
	minWidth?: number;
	align?: 'right';
	format?: (value: any) => any;
}

const columns: readonly Column[] = [
	{
		id: 'timestamp',
		label: 'Timestamp',
		minWidth: 80,
		format: (value: number) => new Date(value).toISOString().slice(0, 19).replace('T', ' '),
	},
	{ id: 'source', label: 'Source', minWidth: 80 },
	{ id: 'dest', label: 'Destination', minWidth: 100 },
	{ 
		id: 'size', 
		label: 'Size', 
		minWidth: 30,
		format: (value: number) => value + " B",
	},
];

interface FlowCardProps {
	flow: FlowDetailsData;
}

function FlowCard(props: FlowCardProps) {
	const { flow } = props;
	const rows = flow.packets;
	const type = flow.type === "CLIENT" ? "Client" : "Service";
	const typeColor = flow.type === "CLIENT" ? "primary" : "secondary";
	const [page, setPage] = useState(0);

	const handleChangePage = (event: unknown, newPage: number) => {
		setPage(newPage);
	};

	return (
		<Paper sx={{ width: '47%', overflow: 'hidden', overflowY: 'scroll', height: "80vh" }}>
			<Box sx={{ p: 3 }}>
				<Stack direction="row" alignItems="center">
					<Typography variant="h4" sx={{ py: 1 }}>Flow - #{flow.id}</Typography>
					<Box sx={{ flexGrow: 1 }} />
					<Chip label={type} variant="outlined" color={typeColor} sx={{ fontSize: 20 }} />
				</Stack>
				
				<Divider />

				<Typography sx={{ py: 2, fontSize: 17 }}>{type} Ip: {flow.csNodeIp} </Typography>
				<Typography sx={{ py: 2, fontSize: 17 }}>Entry Node Ip: {flow.entryNodeIp} </Typography>

				<Divider />
				<Typography variant="h4" sx={{ py: 1 }}>Packets: </Typography>
				<Paper sx={{ width: '100%' }}>
					<TableContainer sx={{ maxHeight: "35vh" }}>
						<Table aria-label="sticky table" >
							<TableHead>
								<TableRow>
									{columns.map((column) => {
										return (
											<>
												<TableCell
													key={column.id}
													align={column.align}
													style={{ minWidth: column.minWidth, fontSize: 15 }}
												>
													{column.label}
												</TableCell>
											</>
										);
									})}
								</TableRow>
							</TableHead>
							<TableBody>
								{rows
									.slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
									.map((row) => {
										return (
											<TableRow hover role="checkbox" tabIndex={-1} key={row.timestamp}>
												{columns.map((column) => {
													const value = row[column.id];
													return (
														<>
															<TableCell key={column.id} align={column.align} style={{ fontSize: 12 }}>
																{column.format ? column.format(value) : value}
															</TableCell>
														</>
													);
												})}
											</TableRow>
										);
									})}
							</TableBody>
						</Table>
					</TableContainer>
					<TablePagination
						rowsPerPageOptions={[]}
						component="div"
						count={rows.length}
						rowsPerPage={rowsPerPage}
						page={page}
						onPageChange={handleChangePage}
					/>
				</Paper>
			</Box>
		</Paper>
	);
}


function CorrelationDetails() {
	const routeParams = useParams();
	const [correlation, setCorrelation] = useState<CorrelationDetailsData>(createCorrelationDetailsData(createFlowDetailsData(1, "", "", "", 0, []), createFlowDetailsData(1, "", "", "", 0, [])));

	const getCorrelation = async () => {
		try {
			const response = await axios.get('/api/correlations/details/' + routeParams.id);
			const data = response.data;

			const corr = createCorrelationDetailsData(
				createFlowDetailsData(
					data.clientFlow.id,
					data.clientFlow.csNodeIp,
					data.clientFlow.entryNodeIp,
					data.clientFlow.type,
					data.clientFlow.isCorrelated,
					data.clientFlow.packets.map((packet: any) => {
						return createPacketData(
							packet.timestamp,
							packet.size,
							packet.sourceIp + ' : ' + packet.sourcePort,
							packet.destIp + ' : ' + packet.destPort,
						);
					})
				),
				createFlowDetailsData(
					data.serviceFlow.id,
					data.serviceFlow.csNodeIp,
					data.serviceFlow.entryNodeIp,
					data.serviceFlow.type,
					data.serviceFlow.isCorrelated,
					data.serviceFlow.packets.map((packet: any) => {
						return createPacketData(
							packet.timestamp,
							packet.size,
							packet.sourceIp + ' : ' + packet.sourcePort,
							packet.destIp + ' : ' + packet.destPort,
						);
					})
				)
			);

			setCorrelation(corr);
		} catch (error) {
			console.error(error);
		}
	};

	useEffect(() => {
		getCorrelation();
	}, []);


	return (
		<Box sx={{ bgcolor: "background.paper" }}>
			<Stack direction="row"  >
				<Button
					variant="contained"
					startIcon={<ArrowLeftIcon />}
					onClick={() => window.history.back()}
				>
					Back
				</Button>
				<Box sx={{ flexGrow: 1 }} />
			</Stack>
			<Stack direction="row" alignItems={"center"} sx={{ mt: 3 }}>
				<FlowCard flow={correlation.clientFlow} />
				<KeyboardDoubleArrowRightIcon sx={{ fontSize: 40 }} />
				<FlowCard flow={correlation.serviceFlow} />
			</Stack>
		</Box>
	);
}

export default CorrelationDetails;

