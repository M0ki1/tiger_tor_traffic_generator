import { FlowDetailsData } from "../methods/flowsMethods"

export interface Column {
    id: "id" | "clientId" | "clientIp" | "serviceId" | "serviceIp";
    label?: string;
    minWidth?: number;
    align?: 'right';
    format?: (value: any) => any;
}

export interface CorrelationsRowData {
    id: number;
    clientId: number;
    clientIp: string;
    serviceId: number;
    serviceIp: string;
}

export function createCorrelationsRowData(
    id: number,
    clientId: number,
    clientIp: string,
    serviceId: number,
    serviceIp: string,
): CorrelationsRowData {
    return { id, clientId, clientIp, serviceId, serviceIp };
}

export interface CorrelationDetailsData {
    clientFlow: FlowDetailsData;
    serviceFlow: FlowDetailsData;
}

export function createCorrelationDetailsData(
    clientFlow: FlowDetailsData,
    serviceFlow: FlowDetailsData,
): CorrelationDetailsData {
    return { clientFlow, serviceFlow };
}


