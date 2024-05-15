import { useNavigate } from "react-router-dom";
import { useEffect, useState, MouseEvent } from 'react';
import {
  Box,
  Button,
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
  CorrelationsRowData,
  createCorrelationsRowData,
  Column
} from "../methods/correlationMethods";
import {
  Order,
  stableSort,
  getComparator
} from "../methods/dashboardMethods";
import { visuallyHidden } from '@mui/utils';
import axios from 'axios';

const rowsPerPage = 100;

const columns: readonly Column[] = [
  { id: 'id', label: 'ID', minWidth: 100 },
  { id: 'clientId', label: 'Client ID', minWidth: 100 },
  { id: 'clientIp', label: 'Client IP', minWidth: 100 },
  { id: 'serviceId', label: 'Service ID', minWidth: 100 },
  { id: 'serviceIp', label: 'Service IP', minWidth: 100 },
];

interface EnhancedTableProps {
  onRequestSort: (event: MouseEvent<unknown>, property: keyof CorrelationsRowData) => void;
  order: Order;
  orderBy: string;
  columnSeparator?: Object;
}

function EnhancedTableHead(props: EnhancedTableProps) {
  const { order, orderBy, onRequestSort, columnSeparator } = props;

  const createSortHandler =
    (property: keyof CorrelationsRowData) => (event: MouseEvent<unknown>) => {
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
                style={Object.assign({ minWidth: column.minWidth}, column.id === 'serviceId' && columnSeparator)}
                sortDirection={orderBy === column.id ? order : false}
              >
                <TableSortLabel
                  active={orderBy === column.id}
                  direction={orderBy === column.id ? order : 'asc'}
                  onClick={createSortHandler(column.id)}
                >
                  {column.label}
                  {orderBy === column.id && (
                    <Box component="span" sx={visuallyHidden}>
                      {order === 'desc' ? 'sorted descending' : 'sorted ascending'}
                    </Box>
                  )}
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

export default function CorrelationsDashboard() {
  const navigate = useNavigate();
  const [order, setOrder] = useState<Order>('asc');
  const [orderBy, setOrderBy] = useState<keyof CorrelationsRowData>('id');
  const [page, setPage] = useState(0);
  const [rows, setRows] = useState<CorrelationsRowData[]>([]);

  const columnSeparator = { borderLeft: "solid 1px #666666" };

  const handleChangePage = (event: unknown, newPage: number) => {
    setPage(newPage);
  };

  const handleViewDetails = async (event: MouseEvent<unknown>, corrInstanceId: number) => {
    try {
      navigate(`/correlations/${corrInstanceId}`);
    } catch (error) {
      console.error(error);
    }
  };

  const handleRequestSort = (event: MouseEvent<unknown>, property: keyof CorrelationsRowData) => {
    const isAsc = orderBy === property && order === 'asc';
    setOrder(isAsc ? 'desc' : 'asc');
    setOrderBy(property);
  };

  const getRows = async () => {
    try {
      const response = await axios.get('/api/correlations');
      const rows = response.data.map((row: any) => {
        const r = createCorrelationsRowData(
          row.id,
          row.clFlowId,
          row.clientFlow.csNodeIp,
          row.srvFlowId,
          row.serviceFlow.csNodeIp,
        );
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
        <TableContainer sx={{ maxHeight: "65vh" }}>
          <Table aria-label="sticky table" size="small">
            <EnhancedTableHead
              order={order}
              orderBy={orderBy}
              onRequestSort={handleRequestSort}
              columnSeparator={columnSeparator}
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
                            <TableCell key={column.id} align={column.align} sx={column.id === 'serviceId' ? columnSeparator : undefined}>
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
    </>
  );
}