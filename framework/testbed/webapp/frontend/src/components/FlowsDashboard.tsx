import { useEffect, useState, MouseEvent } from 'react';
import {
  Box,
  Button,
  Chip,
  TableSortLabel,
  TablePagination,
  TableContainer,
  Table,
  TableHead,
  TableBody,
  TableRow,
  TableCell,
  Paper,
} from '@mui/material';
import {
  FlowsRowData,
  createFlowsRowData,
  FlowDetailsData,
  createFlowDetailsData,
  Column
} from "../methods/flowsMethods";
import {
  Order,
  stableSort,
  getComparator
} from "../methods/dashboardMethods";
import { createPacketData } from '../methods/packetMethods';
import { visuallyHidden } from '@mui/utils';
import axios from 'axios';
import FlowDetails from './FlowDetails';

const rowsPerPage = 100;

const columns: readonly Column[] = [
  { id: 'id', label: 'ID', minWidth: 30 },
  {
    id: 'csNodeIp',
    label: 'Client/Service IP',
    minWidth: 70,
  },
  {
    id: 'entryNodeIp',
    label: 'Entry Node IP',
    minWidth: 140,
  },
  {
    id: 'type',
    label: 'Type of Connection',
    minWidth: 170,
    format: (value: string) => {
      if (value === 'CLIENT') {
        return <Chip label="CLIENT" variant="outlined" color="primary" />;
      } else if (value === 'SERVICE') {
        return <Chip label="ONION SERVICE" variant="outlined" color="secondary" />;
      }
    },
  },
  {
    id: 'isCorrelated',
    label: 'Correlated',
    minWidth: 70,
    format: (value: number) => {
      if (value) {
        return <Chip label="YES" variant="outlined" color="success" />;
      } else {
        return <Chip label="NO" variant="outlined" color="error" />;
      }
    }, 
  },
];

interface EnhancedTableProps {
  onRequestSort: (event: MouseEvent<unknown>, property: keyof FlowsRowData) => void;
  order: Order;
  orderBy: string;
}

function EnhancedTableHead(props: EnhancedTableProps) {
  const { order, orderBy, onRequestSort } = props;

  const createSortHandler =
    (property: keyof FlowsRowData) => (event: MouseEvent<unknown>) => {
      onRequestSort(event, property);
    };

  return (
    <TableHead>
      <TableRow>
        {columns.map((column) => {
          return (
            <>
              <TableCell
                key={column.id}
                align={column.align}
                style={{ minWidth: column.minWidth }}
                sortDirection={orderBy === column.id ? order : false}
              >
                <TableSortLabel
                  active={orderBy === column.id}
                  direction={orderBy === column.id ? order : 'asc'}
                  onClick={createSortHandler(column.id)}
                >
                  {column.label}
                  {orderBy === column.id ? (
                    <Box component="span" sx={visuallyHidden}>
                      {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                    </Box>
                  ) : null}
                </TableSortLabel>
              </TableCell>
            </>
          );
        })}
        <TableCell key={'details'}></TableCell>
      </TableRow>
    </TableHead>
  );
}

export default function FlowsDashboard() {
  const [order, setOrder] = useState<Order>('asc');
  const [orderBy, setOrderBy] = useState<keyof FlowsRowData>('id');
  const [page, setPage] = useState(0);
  const [rows, setRows] = useState<FlowsRowData[]>([]);
  const [open, setOpen] = useState(false);
  const [selectedFlow, setSelectedFlow] = useState<FlowDetailsData>(createFlowDetailsData(0, '', '', '', 0, []));

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleViewDetails = async (event: MouseEvent<unknown>, flowInstanceId: number) => {
    try {
      const response = await axios.get('/api/flows/details/' + flowInstanceId);
      const flowDetails = createFlowDetailsData(
        response.data.id,
        response.data.csNodeIp,
        response.data.entryNodeIp,
        response.data.type,
        response.data.isCorrelated,
        response.data.packets.map((packet: any) => {
          return createPacketData(
            packet.timestamp,
            packet.size,
            packet.sourceIp + ' : ' + packet.sourcePort,
            packet.destIp + ' : ' +packet.destPort,
          );
        })
      );
      setSelectedFlow(flowDetails);
      setOpen(true);
    } catch (error) {
      console.error(error);
    }
  };

  const handleRequestSort = (event: MouseEvent<unknown>, property: keyof FlowsRowData) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const getRows = async () => {
    try {
      const response = await axios.get('/api/flows');
      const rows = response.data.map((row: any) => {
        const r = createFlowsRowData( row.id, row.type, row.csNodeIp, row.entryNodeIp, Number(row.isCorrelated) );
        console.log(row);
        return r;
      });
      setRows(rows);

    } catch (error) {
      console.error(error);
    }
  };

  useEffect(() => {
    getRows();
  }, []);

  return (
    <>
      <Paper sx={{ width: '100%', overflow: 'hidden' }}>
        <TableContainer sx={{ maxHeight: "70vh" }}>
          <Table stickyHeader aria-label="sticky table" size="small">
            <EnhancedTableHead
              order={order}
              orderBy={orderBy}
              onRequestSort={handleRequestSort}
            />
            <TableBody>
              {stableSort(rows, getComparator(order, orderBy))
                .slice(page * rowsPerPage, page * rowsPerPage + rowsPerPage)
                .map((row) => {
                  return (
                    <TableRow hover tabIndex={-1} key={row.id}>
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
                      <TableCell key={'details'}>
                        <Button
                          variant="contained"
                          color="primary"
                          size="small"
                          onClick={(event) => handleViewDetails(event, row.id)}
                        >
                          View Details
                        </Button>
                      </TableCell>
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
      <FlowDetails
        open={open}
        setOpen={setOpen}
        flowInstance={selectedFlow}
      />
    </>
  );
}