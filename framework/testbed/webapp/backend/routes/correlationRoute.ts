import { Router, Request, Response, NextFunction } from "express";
import { CorrelationService } from "../services/index";

const router = Router();

router.get("/", async (req: Request, res: Response, next: NextFunction) => {
    try {
        const flow = await CorrelationService.getAllCorrelations();
        res.status(200).json(flow);
    } catch (err) {
        next(err);
    }
});

router.get("/details/:id", async (req: Request, res: Response, next: NextFunction) => {
    try {
        const details = await CorrelationService.getCorrelationDetails(req.params.id);
        res.status(200).json(details);
    } catch (err) {
        next(err);
    }
});

router.post("/create", async (req: Request, res: Response, next: NextFunction) => {
    try {
        await CorrelationService.createCorrelation(req.body.id1, req.body.id2);
        res.status(200).json({ message: "Correlation created successfully" });
    } catch (err) {
        next(err);
    }
});

router.post("/create-many", async (req: Request, res: Response, next: NextFunction) => {
    try {
        await CorrelationService.createCorrelations(req.body);
        res.status(200).json({ message: "Correlations created successfully" });
    } catch (err) {
        next(err);
    }
});


export const correlationRoutes: Router = router;