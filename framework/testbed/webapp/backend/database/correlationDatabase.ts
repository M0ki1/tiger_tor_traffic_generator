import { FlowCorrelation } from "@prisma/client";
import CorrelationDetailsData from "../models/correlationDetailsData";
import FlowDetailsData from "../models/flowDetailsData";
import prisma from "../prisma/client"

class CorrelationDatabase {

	public static createCorrelation = async (clFlowId: number, srvFlowId: number): Promise<number> => {

		if (!clFlowId || !srvFlowId) {
			return -1;
		}

		try {

			const flows = await prisma.flow.findMany({
				where: {
					OR: [
						{
							id: clFlowId,
							type: "CLIENT"
						},
						{
							id: srvFlowId,
							type: "SERVICE"
						}
					]
				}
			});

			if (flows.length !== 2) {
				throw new Error("Type mismatch in flows");
			}

			return await prisma.$transaction(async (tx) => {
				const correlation = await tx.flowCorrelation.create({
					data: {
						clFlowId: clFlowId,
						srvFlowId: srvFlowId,
					},
				});

				await tx.flow.update({
					where: {
						id: clFlowId
					},
					data: {
						isCorrelated: true,
					}
				});

				return correlation.id;
			});
		} catch (err) {
			return -1;
		}
	}

	public static createCorrelations = async (ids: number[][]): Promise<number> => {

		if (ids.length === 0) {
			return 0;
		}

		try{

			const clFlowIds = ids.map((id: number[]) => {
				if (id.length !== 2)
					throw new Error("Invalid correlation data");
				return id[0];
			});

			const srvFlowIds = ids.map((id: number[]) => {
				return id[1];
			});

			const flows = await prisma.flow.findMany({
				where: {
					OR: [
						{
							id: {in: clFlowIds},
							type: "CLIENT"
						},
						{
							id: {in: srvFlowIds},
							type: "SERVICE"
						}
					]
				}
			});

			if (flows.length !== ids.length * 2) {
				throw new Error("Type mismatch in flows");
			}

			return await prisma.$transaction(async (tx) => {

				const correlations = await tx.flowCorrelation.createMany({
					data: ids.map((id: number[]) => {
						return {
							clFlowId: id[0],
							srvFlowId: id[1],
						}
					}),
					skipDuplicates: true,
				});

				await tx.flow.updateMany({
					where: {
						id: {in: clFlowIds}
					},
					data: {
						isCorrelated: true,
					}
				});

				return correlations.count;
			});
		}
		
		catch (err) {
			console.log(err);
			return -1;
		}
	}

	public static getCorrelation = async (id: number): Promise<CorrelationDetailsData & { clientFlow: FlowDetailsData, serviceFlow: FlowDetailsData } | null> => {
		try {
			const correlation = await prisma.flowCorrelation.findUnique({
				where: {
					id: id
				},
				include: {
					clientFlow: {
						include: {
							packets: true
						},
					},
					serviceFlow: {
						include: {
							packets: true
						},
					}
				}
			});

			return correlation;
		} catch (err) {
			return null;
		}
	}

	public static getAllCorrelations = async (): Promise<FlowCorrelation[] | null> => {
		try {
			const correlation = await prisma.flowCorrelation.findMany(
				{
					include: {
						clientFlow: true,
						serviceFlow: true
					}
				}
			);
			return correlation;
		} catch (err) {
			return null;
		}
	}
}


export default CorrelationDatabase;
