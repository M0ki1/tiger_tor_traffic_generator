import bcrypt from 'bcryptjs';
import HttpException from '../models/httpException';
import UserRegisterData from '../models/userRegisterData';
import LoginData from '../models/loginData';
import UserLoggedData from '../models/userLoggedData';
import { UserDatabase } from '../database/index';
import { User } from '@prisma/client';


class AuthService {

	private static nameRegex = /^[a-zA-Z]([a-zA-Z ]){3,}$/;
	private static emailRegex = /^([a-zA-Z0-9\.\-_]){4,60}@([a-zA-Z\.\-_]){1,30}.([a-zA-Z]){1,4}$/;
	private static passwordRegex = /^(?=(.*[a-z]){1,})(?=(.*[A-Z]){1,})(?=(.*[0-9]){1,})(?=(.*[!@#$%^&*()\-_+.]){1,}).{8,32}$/;
	// Minimum of: 1 lowercase, 1 uppercase, 1 number, 1 special character. Total: 8 to 32 chars -> ADD TO FRONTEND!

	private static checkUserUniqueness = async (email: string): Promise<boolean> => {
		return !(await UserDatabase.getUser(email));
	};

	//========================================================================================
	//-------------------------------------REGISTER CLIENT------------------------------------
	//========================================================================================

	public static registerUser = async (user: UserRegisterData): Promise<void> => {

		const name = user.name?.trim();
		const email = user.email?.trim();
		const password = user.password?.trim();

		if (!email || !name || !password || !this.passwordRegex.test(password) || !this.emailRegex.test(email) || !this.nameRegex.test(name)) {
			throw new HttpException(400, "Invalid or missing credentials. Please try again.");
		}

		const unique = await this.checkUserUniqueness(email);

		if (!unique) {
			throw new HttpException(422, "This email is already taken. Please try with a different email.");
		}

		const hashedPassword = await bcrypt.hash(password, 10);

		const success = await UserDatabase.createUser(name, email, hashedPassword);

		if (!success) {
			throw new HttpException(500, "The user could not be created. Please try again.");
		}
	};

	//========================================================================================
	//-------------------------------------LOGIN----------------------------------------------
	//========================================================================================

	public static loginVerification = async (loginData: LoginData): Promise<User> => {
		const email = loginData.email?.trim();
		const password = loginData.password?.trim();

		if (!email || !password) {
			throw new HttpException(400, "Invalid or missing credentials. Please try again.");
		}

		let user: User | null;

		user = await UserDatabase.getUser(email);

		if (!user) {
			throw new HttpException(401, "Invalid email or password.");
		}

		const isPasswordMatching = await bcrypt.compare(password, user.password);

		if (!isPasswordMatching) {
			throw new HttpException(401, "Invalid email or password.");
		}

		return user;
	}

	public static logoutUser = async (): Promise<void> => {
		//TODO: Implement logout	
	};
}

export default AuthService;