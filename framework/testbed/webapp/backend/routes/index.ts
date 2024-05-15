import { Router } from 'express';
import { authRoutes } from './authRoute';
import { userRoutes } from './userRoute';
import { flowRoutes } from './flowRoute';
import { correlationRoutes } from './correlationRoute';

const router: Router = Router();

router.use('/auth', authRoutes);
router.use('/users', userRoutes);
router.use('/flows', flowRoutes);
router.use('/correlations', correlationRoutes);

export default router;