import { UserDatabase } from '../database/index';
import { User } from '@prisma/client';
import HttpException from '../models/httpException';

class UserService {

    public static getUser = async (email: string): Promise<User> => {
        const user = await UserDatabase.getUser(email);

        if (!user) {
			throw new HttpException(401, "Failed to get user; invalid email.");
		}

        return user;
    }
}

export default UserService;