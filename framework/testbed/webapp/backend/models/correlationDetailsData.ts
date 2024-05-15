import FlowDetailsData from './flowDetailsData';

export default interface CorrelationDetailsData {
    clientFlow: FlowDetailsData;
    serviceFlow: FlowDetailsData;
}