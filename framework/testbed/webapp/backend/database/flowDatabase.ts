import { Flow, Type, Packet } from "@prisma/client";
import prisma from "../prisma/client"
import PacketData from '../models/packetData';
import FlowDetailsData from "../models/flowDetailsData";

class FlowDatabase {

	public static createFlow = async (csNodeIp: string, entryNodeIp: string, type: Type, packets: PacketData[]): Promise<number> => {
		//return id of the flow created
		try {
			const flow = await prisma.flow.create({
				data: {
					csNodeIp: csNodeIp,
					entryNodeIp: entryNodeIp,
					type: type,
					packets: {
						createMany: {
							data: packets,
							skipDuplicates: false,
						},
					},
				},
			});
			return flow.id;
		} catch (err) {
			return -1;
		}
	}

	public static createFlows = async (flows: FlowDetailsData[]): Promise<number> => {
		//return number of created flows
		try {

			const packetsData = flows.map((flowData) => flowData.packets).flat();

			return await prisma.$transaction(async (tx) => {
				const flowsRes = await tx.flow.createMany({
					data: flows.map((flowData) => {
						return {
							csNodeIp: flowData.csNodeIp,
							entryNodeIp: flowData.entryNodeIp,
							type: flowData.type as Type,
							isCorrelated: flowData.isCorrelated
						}
					}),
					skipDuplicates: true,
				});



				await tx.packet.createMany({
					data: packetsData.map((packet) => {
						return {
							timestamp: packet.timestamp,
							size: packet.size,
							sourceIp: packet.sourceIp,
							sourcePort: packet.sourcePort,
							destIp: packet.destIp,
							destPort: packet.destPort,
							flowId: packet.flowId!
						}
					})
				});
					
				return flowsRes.count;
			});
			
		} catch (err) {
			return -1;
		}
	}

	public static getFlowDetails = async (id: number): Promise<Flow | null> => {
		try {
			const flowDetails = await prisma.flow.findUnique({
				where: {
					id: id
				}
			});
			return flowDetails;
		} catch (err) {
			return null;
		}
	}

	public static getPacketsFromFlow = async (id: number): Promise<Packet[] | null> => {
		try {
			const packets = await prisma.packet.findMany({
				where: {
					flowId: id
				}
			});
			return packets;
		} catch (err) {
			return null;
		}
	}


	public static getAllFlows = async (): Promise<Flow[] | null> => {
		try {
			const flow = await prisma.flow.findMany();
			return flow;
		} catch (err) {
			return null;
		}
	}
}


export default FlowDatabase;
