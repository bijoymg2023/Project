import express from "express";
import path from "path";
import bodyParser from "body-parser";
import dotenv from "dotenv";
import { GoogleGenerativeAI } from "@google/generative-ai";
import { fileURLToPath } from "url";
import { dirname } from "path";

// Load environment variables from .env.local
dotenv.config({ path: ".env.local" });

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const app = express();

// Middleware to parse JSON requests
app.use(bodyParser.json());

// Serve static files (e.g., HTML, CSS, JS)
app.use(express.static(path.join(__dirname, "ROSETTACODE-main"), { index: false }));

app.get("/", (req, res) => {
    res.sendFile(path.join(__dirname, "ROSETTACODE-main", "landing.html"));
});

// Define a route for the landing page
app.get("/index", (req, res) => {
    res.sendFile(path.join(__dirname, "ROSETTACODE-main", "index.html"));
});

// Initialize Google Generative AI client
const genAI = new GoogleGenerativeAI(process.env.GOOGLE_API_KEY);

// Define an API endpoint for code conversion
app.post("/api", async (req, res) => {
    const { input, fromLang, toLang } = req.body;

    try {
        console.log("API Key available:", !!process.env.GOOGLE_API_KEY);
        
        // Create a prompt for code conversion
        const prompt = `Convert the following ${fromLang} code to ${toLang}. \n\n${input}`;
        
        // Use the gemini-1.5-pro model
        const model = genAI.getGenerativeModel({ model: "gemini-1.5-pro" });
        
        console.log(`Converting from ${fromLang} to ${toLang}`);

        // Generate content using the Gemini API
        const result = await model.generateContent(prompt);

        let convertedCode = "";
        
        if (result && result.response && result.response.candidates && 
            result.response.candidates[0] && result.response.candidates[0].content && 
            result.response.candidates[0].content.parts && 
            result.response.candidates[0].content.parts[0] && 
            result.response.candidates[0].content.parts[0].text) {
            
            convertedCode = result.response.candidates[0].content.parts[0].text;
        } else {
            convertedCode = "// Could not parse the response from the API";
            console.error("Unexpected response structure:", result);
        }
        
        res.json({ convertedCode: convertedCode.trim() });
        
    } catch (error) {
        console.error("Error in /api route:", error.message);
        res.status(500).json({ 
            error: "Failed to convert code.", 
            details: error.message 
        });
    }
});

// Start the server
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Server is running on http://localhost:${PORT}`);
    console.log(`Using API Key (masked): ${process.env.GOOGLE_API_KEY ? "****" + process.env.GOOGLE_API_KEY.substring(process.env.GOOGLE_API_KEY.length - 4) : "Not found"}`);
});
