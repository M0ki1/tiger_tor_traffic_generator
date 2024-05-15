import { Router, Request, Response, NextFunction } from "express";
import { UserService } from "../services/index";

const router = Router();

router.get("/get-user", async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
        const user = await UserService.getUser(req.body.email);
        res.status(200).send(user);
    } catch (err: any) {
        next(err);
    }
});

export const userRoutes: Router = router;