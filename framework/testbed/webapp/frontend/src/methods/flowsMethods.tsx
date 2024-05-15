import { PacketData } from './packetMethods';

export interface Column {
    id: 'id' | 'type' | 'csNodeIp' | 'entryNodeIp' | 'isCorrelated';
    label?: string;
    minWidth?: number;
    align?: 'right';
    format?: (value: any) => any;
}

export interface FlowsRowData {
    id: number;
    type: string;
    csNodeIp: string;
    entryNodeIp: string;
    isCorrelated: number;
}

export function createFlowsRowData(
    id: number,
    type: string,
    csNodeIp: string,
    entryNodeIp: string,
    isCorrelated: number,
): FlowsRowData {
    return { id, type, csNodeIp, entryNodeIp, isCorrelated };
}

export interface FlowDetailsData {
    id: number;
    type: string;
    csNodeIp: string;
    entryNodeIp: string;
    isCorrelated: number;
    packets: PacketData[];
}

export function createFlowDetailsData(
    id: number,
    csNodeIp: string,
    entryNodeIp: string,
    type: string,
    isCorrelated: number,
    packets: PacketData[],
): FlowDetailsData {
    return { id, csNodeIp, entryNodeIp, type, isCorrelated, packets };
}

