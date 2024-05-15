import { Router, Request, Response, NextFunction } from "express";
import LoginData from "../models/loginData";
import UserRegisterData from "../models/userRegisterData";
import { AuthService } from "../services/index";

const router = Router();

router.post("/register-client", async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
        await AuthService.registerUser(req.body as UserRegisterData);
        res.sendStatus(200);
    } catch (err: any) {
        next(err);
    }
});

router.post("/login", async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
        const loginData = {
            email: req.body.email,
            password: req.body.password,
        }

        const userLogged = await AuthService.loginVerification(loginData as LoginData);

        res.status(200).json(userLogged);

    } catch (err: any) {
        next(err);
    }
});

//#TODO: Implement logout
router.get("/logout",  async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
        //await AuthService.logoutUser();
        res.sendStatus(401);
    } catch (err: any) {
        next(err);
    }
});

export const authRoutes: Router = router;