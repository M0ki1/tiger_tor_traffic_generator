import { Router, Request, Response, NextFunction } from "express";
import { FlowService } from "../services/index";
import FlowDetailsData from "../models/flowDetailsData";

const router = Router();

router.get("/", async (req: Request, res: Response, next: NextFunction) => {
    try {
        const flow = await FlowService.getAllFlows();
        res.status(200).json(flow);
    } catch (err) {
        next(err);
    }
});

router.get("/details/:id", async (req: Request, res: Response, next: NextFunction) => {
    try {
        const details = await FlowService.getFlowDetails(req.params.id);
        res.status(200).json(details);
    } catch (err) {
        next(err);
    }
});

router.post("/create", async (req: Request, res: Response, next: NextFunction) => {
    try {
        await FlowService.createFlow(req.body as FlowDetailsData);
        res.status(200).json({ message: "Flow created" });
    } catch (err) {
        next(err);
    }
});

router.post("/create-many", async (req: Request, res: Response, next: NextFunction) => {
    try {
        await FlowService.createFlows(req.body as FlowDetailsData[]);
        res.status(200).json({ message: "Flow created" });
    } catch (err) {
        next(err);
    }
});


export const flowRoutes: Router = router;