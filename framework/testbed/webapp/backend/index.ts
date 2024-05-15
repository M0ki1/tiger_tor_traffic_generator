import express from "express";
import morgan from "morgan";
import bodyParser from 'body-parser';
import cookieParser from 'cookie-parser';
import HttpException from "./models/httpException";
import routes from "./routes/index";

const app = express();

// Parsers middleware
app.use(morgan("tiny"));
app.use(bodyParser.json({limit: "50mb"}));
app.use(cookieParser());
// add no cors 

app.use("/api", routes);

app.get("/user", (req: any, res: any) => {
    
    res.send("Hello World!");
});

// Error handling middleware
app.use((err: any, req: any, res: any, next: any) => {
    console.error(err);
    if (err instanceof HttpException) {
        res.status(err.errorCode).send(err.message);
    } else if (err instanceof Error) {
        res.status(500).send("Something went wrong.");
    }
});

// Start the server
const host = "0.0.0.0";//process.env.HOST || "localhost";
const port = process.env.PORT || "4000";

app.listen(parseInt(port), host, () => {
    console.log("⚡️[server]: Server is running at http://" + host + ":" + port);
});