export interface PacketData {
    timestamp: number; 
    size: number;
    source: string;
    dest: string;
}

export function createPacketData(
    timestamp: number,
    size: number,
    source: string,
    dest: string
): PacketData {
    return { timestamp, size, source, dest };
}