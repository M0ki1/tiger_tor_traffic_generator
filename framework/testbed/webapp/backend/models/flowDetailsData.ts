import PacketData  from './packetData';

export default interface FlowDetailsData {
    id?: number;
    csNodeIp: string;
    entryNodeIp: string;
    type: string;
    isCorrelated?: boolean;
    packets: PacketData[];
}