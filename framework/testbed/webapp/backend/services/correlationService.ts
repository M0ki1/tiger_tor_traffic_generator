import { CorrelationDatabase } from '../database/index';
import { FlowCorrelation } from '@prisma/client';
import HttpException from '../models/httpException';
import CorrelationDetailsData from '../models/correlationDetailsData';
import FlowDetailsData from '../models/flowDetailsData';

class CorrelationService {

    public static createCorrelation = async (id1: number, id2: number): Promise<number> => {

        if (!id1 || !id2) {
            throw new HttpException(400, "The correlation couldn't be created");
        }

        const correlation = await CorrelationDatabase.createCorrelation(id1, id2);

        if (correlation === -1) {
            throw new HttpException(400, "The correlation couldn't be created");
        }
        
        return correlation;
    }

    public static createCorrelations = async (ids: number[][]): Promise<number> => {

        if (!ids) {
            throw new HttpException(400, "The correlation(s) couldn't be created");
        }

        const createdCorrelationCount = await CorrelationDatabase.createCorrelations(ids);

        if (createdCorrelationCount === -1) {
            throw new HttpException(400, "The correlation(s) couldn't be created");
        }

        return createdCorrelationCount;
    }


    public static getAllCorrelations = async (): Promise<FlowCorrelation[]> => {
        const correlation = await CorrelationDatabase.getAllCorrelations();

        if (!correlation) {
            throw new HttpException(404, 'No correlation found');
        }

        return correlation;
    }

    public static getCorrelationDetails = async (id: string): Promise<CorrelationDetailsData> => {
        //validate that id is a number and no interger overflow
        const corrId = Number(id);

        if (isNaN(corrId) || corrId < 0 || corrId > Number.MAX_SAFE_INTEGER) {
            throw new HttpException(400, 'Invalid correlation id');
        }
        
        const correlation = await CorrelationDatabase.getCorrelation(corrId);
        if (!correlation) {
            throw new HttpException(404, 'No correlation found');
        }

        const correlationDetails: CorrelationDetailsData = {
            clientFlow: correlation.clientFlow as FlowDetailsData,
            serviceFlow: correlation.serviceFlow as FlowDetailsData,
        }

        return correlationDetails;
    }
}

export default CorrelationService;