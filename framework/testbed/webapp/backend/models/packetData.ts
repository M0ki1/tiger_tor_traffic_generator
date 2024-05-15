export default interface PacketData {
    timestamp: number; 
    size: number;
    sourceIp: string;
    sourcePort: number;
    destIp: string 
    destPort: number;
    flowId?: number;
}