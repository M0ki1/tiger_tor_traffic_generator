import { FlowDatabase } from '../database/index';
import { Flow, Type } from '@prisma/client';
import HttpException from '../models/httpException';
import FlowDetailsData from '../models/flowDetailsData';
import PacketData from '../models/packetData';

class FlowService {

    public static createFlow = async (flowData: FlowDetailsData): Promise<number> => {
        if (!flowData) {
            throw new HttpException(400, 'Invalid flow data');
        }

        if (!flowData.csNodeIp || !flowData.entryNodeIp || !flowData.type || !flowData.packets) {
            throw new HttpException(400, 'Invalid flow data');
        }

        //check if type is valid
        if (flowData.type !== Type.CLIENT && flowData.type !== Type.SERVICE) {
            throw new HttpException(400, 'Invalid flow type');
        }

        const id = await FlowDatabase.createFlow(flowData.csNodeIp, flowData.entryNodeIp, flowData.type, flowData.packets);

        if (id === -1) {
            throw new HttpException(500, 'Something went wrong');
        }

        return id;
    }

    public static createFlows = async (flows: FlowDetailsData[]): Promise<number> => {

        flows.forEach((flowData: FlowDetailsData) => {
            if (!flowData) {
                throw new HttpException(400, 'Invalid flow data');
            }
    
            if (!flowData.csNodeIp || !flowData.entryNodeIp || !flowData.type || !flowData.packets) {
                throw new HttpException(400, 'Invalid flow data');
            }
    
            //check if type is valid
            if (flowData.type !== Type.CLIENT && flowData.type !== Type.SERVICE) {
                throw new HttpException(400, 'Invalid flow type');
            }
        });

        const flowsCount = await FlowDatabase.createFlows(flows);

        if (flowsCount === -1) {
            throw new HttpException(500, 'Something went wrong');
        }

        return flowsCount;
    }
    
    public static getAllFlows = async (): Promise<any[]> => {
        const flows = await FlowDatabase.getAllFlows();

        if (!flows) {
            throw new HttpException(404, 'No flow found');
        }

        const aux = flows.map((flow: Flow) => {
            return {
                id: flow.id,
                csNodeIp: flow.csNodeIp,
                entryNodeIp: flow.entryNodeIp,
                type: flow.type,
                isCorrelated: flow.isCorrelated ? 1 : 0
            }
        });
        return aux;
    }

    public static getFlowDetails = async (id: string): Promise<FlowDetailsData> => {
        //validate that id is a number and no interger overflow
        const flowId = Number(id);

        if (isNaN(flowId) || flowId < 0 || flowId > Number.MAX_SAFE_INTEGER) {
            throw new HttpException(400, 'Invalid flow id');
        }
        
        const flow = await FlowDatabase.getFlowDetails(flowId);
        const packets = await FlowDatabase.getPacketsFromFlow(flowId);

        if (!flow || !packets) {
            throw new HttpException(404, 'No flow found');
        }

        //TODO: try change packet retrieval to use include in prisma

        let packetsToSend: PacketData[] = [];

        for (let i = 0; i < packets.length; i++) {
            const packet: PacketData = {
                timestamp: packets[i].timestamp,
                size: packets[i].size,
                sourceIp: packets[i].sourceIp,
                sourcePort: packets[i].sourcePort,
                destIp: packets[i].destIp,
                destPort: packets[i].destPort
            }

            packetsToSend.push(packet);
        }

        const flowDetails: FlowDetailsData = {
            id: flow.id,
            csNodeIp: flow.csNodeIp,
            entryNodeIp: flow.entryNodeIp,
            type: flow.type,
            isCorrelated: flow.isCorrelated,
            packets: packetsToSend
        }

        return flowDetails;
    }
}

export default FlowService;