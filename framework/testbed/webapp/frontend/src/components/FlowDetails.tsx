import {
    Box,
    Button,
    Chip,
    Divider,
    Paper,
    Stack,
    SwipeableDrawer,
    Table,
    TableBody,
    TableCell,
    TableContainer,
    TableHead,
    TablePagination,
    TableRow,
    Typography
} from '@mui/material';
import {
    ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { FlowDetailsData } from '../methods/flowsMethods';
import { useState } from 'react';


const rowsPerPage = 20;

interface Props {
    open: boolean;
    flowInstance: FlowDetailsData;
    setOpen: (open: boolean) => void;
}

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
        minWidth: 100, 
        format: (value: number) => new Date(value).toISOString().slice(0, 19).replace('T', ' '), 
    },
    { id: 'source', label: 'Source', minWidth: 100 },
    { id: 'dest', label: 'Destination', minWidth: 100 },
    { 
		id: 'size', 
		label: 'Size', 
		minWidth: 30,
		format: (value: number) => value + " B",
	},
];

export default function FlowDetails(props: Props) {
    const { open, flowInstance, setOpen } = props;
    const rows = flowInstance.packets;
    const [page, setPage] = useState(0);

    const toggleDrawer = (open: boolean) => () => {
        setOpen(open);
    };

    const handleChangePage = (event: unknown, newPage: number) => {
        setPage(newPage);
    };

    return (
        <SwipeableDrawer
            anchor={"bottom"}
            open={open}
            onClose={toggleDrawer(false)}
            onOpen={toggleDrawer(true)}
            PaperProps={{
                elevation: 0,
                style: { borderTopRightRadius: 20, borderTopLeftRadius: 20 }
            }}
        >

            <Box sx={{
                display: 'flex',
                flexDirection: 'column',
                pb: 3,
                px: 4,
            }}>
                <Button onClick={toggleDrawer(false)} sx={{ alignSelf: 'center' }}>
                    <ExpandMoreIcon />
                </Button>
                <Typography variant="h5" sx={{ pb: 2 }}>Flow Details: </Typography>
                <Stack direction="row">
                    <Paper sx={{ width: '95vw', overflow: 'hidden', maxHeight: '60vh' }}>
                        <Typography variant="h6" sx={{ pl: 2, py: 1 }}>Packets: </Typography>
                        <TableContainer sx={{ maxHeight: "40vh" }}>
                            <Table stickyHeader aria-label="sticky table" >
                                <TableHead>
                                    <TableRow>
                                        {columns.map((column) => {
                                            return (
                                                <>
                                                    <TableCell
                                                        key={column.id}
                                                        align={column.align}
                                                        style={{ minWidth: column.minWidth }}
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
                                                            <TableCell key={column.id} align={column.align}>
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
                    <Stack direction="column" alignItems="left" sx={{ width: '30vw', px: 2 }}>
                        <Paper sx={{ overflow: 'hidden', p: 2 }}>
                            <Stack direction="row" alignItems="center" sx={{ pb: 2 }}>
                                <Typography variant="h6">Flow #{flowInstance.id}: </Typography>
                                <Box sx={{ flexGrow: 1 }} />
                                {flowInstance.type === 'CLIENT' &&
                                    <Chip label="CLIENT" variant="outlined" color="primary" />
                                }
                                {flowInstance.type === 'SERVICE' &&
                                    <Chip label="ONION SERVICE" variant="outlined" color="secondary" />
                                }
                            </Stack>
                            <Divider />
                            {flowInstance.type === 'CLIENT' &&
                                <Typography variant="body1" sx={{ pt: 2, pl: 2 }}>Client IP: {flowInstance.csNodeIp}</Typography>
                            }
                            {flowInstance.type === 'SERVICE' &&
                                <Typography variant="body1" sx={{ pt: 2, pl: 2 }}>Service IP: {flowInstance.csNodeIp}</Typography>
                            }
                            <Typography variant="body1" sx={{ pb: 2, pl: 2 }}>Entry Node IP: {flowInstance.entryNodeIp}</Typography>
                            <Divider />
                            {/*add start and end time*/}
                            <Typography variant="body1" sx={{ py: 2, pl: 2 }}>
                                Total Packets: {flowInstance.packets.length}
                            </Typography>
                            <Divider />
                            <Typography variant="body1" sx={{ pt: 2, pl: 2 }}>
                                Correlated: {flowInstance.isCorrelated ? 'Yes' : 'No'}
                            </Typography>
                        </Paper>
                    </Stack>
                </Stack>
            </Box>
        </SwipeableDrawer>
    );
}
