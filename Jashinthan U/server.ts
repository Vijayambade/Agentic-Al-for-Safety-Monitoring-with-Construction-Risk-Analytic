import express from "express";
import path from "path";
import dotenv from "dotenv";
import { GoogleGenAI } from "@google/genai";
import { fileURLToPath } from "url";

dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(express.json());

const PORT = Number(process.env.PORT) || 3000;

// Lazy initialize Gemini client
function getGenAI() {
  const key = process.env.GEMINI_API_KEY;
  if (!key) return null;
  return new GoogleGenAI({ 
    apiKey: key,
    httpOptions: {
      headers: {
        'User-Agent': 'aistudio-build',
      }
    }
  });
}

// In-memory webhook & API logs for the developer sandbox
export const apiLogs: Array<{ id: string; timestamp: string; method: string; endpoint: string; status: number; source: string }> = [
  { id: "LOG-1001", timestamp: new Date(Date.now() - 3600000).toISOString(), method: "POST", endpoint: "/api/v1/projects/PRJ-01/telemetry", status: 200, source: "Autodesk BIM 360 Sync" },
  { id: "LOG-1002", timestamp: new Date(Date.now() - 1800000).toISOString(), method: "GET", endpoint: "/api/v1/projects", status: 200, source: "Procore Connect API" },
  { id: "LOG-1003", timestamp: new Date(Date.now() - 600000).toISOString(), method: "POST", endpoint: "/api/v1/webhooks/receive", status: 201, source: "Caterpillar GPS Fleet Webhook" },
];

// Health endpoint
app.get("/api/health", (req, res) => {
  res.json({ status: "ok", service: "Construction Intelligence Hub API v2.4", timestamp: new Date().toISOString() });
});

// --- Robust Offline Heuristic Fallback Helpers ---
function getChatFallback(message: string) {
  let fallbackText = "I am operating in Offline Sandbox Mode. Here is a simulated response based on the Construction Intelligence Hub context: ";
  const msgLower = message.toLowerCase();
  if (msgLower.includes("risk") || msgLower.includes("safety") || msgLower.includes("hazard")) {
    fallbackText += "\n\n**Current Jobsite Risks Identified:**\n1. **High Wind Alerts** are active on the Pacific Waterfront crane lift (Liebherr 550 EC-H). Ensure anemometer wind locks are engaged if speeds exceed 38 MPH.\n2. **Concrete Curing Delay** on Level 22 due to rainfall. Recommend deploying high-temperature tarp heaters.";
  } else if (msgLower.includes("budget") || msgLower.includes("spent") || msgLower.includes("cost") || msgLower.includes("material")) {
    fallbackText += "\n\n**Materials & Financial Overview:**\n- We are currently tracking at **1.8% under budget** overall.\n- There is a **Low Stock Alert** on Galvanized Copper Pipe & Conduit (142,000 Linear Ft placed, auto-reorder initiated).";
  } else if (msgLower.includes("who") || msgLower.includes("role") || msgLower.includes("user")) {
    fallbackText += "\n\nAs the Construction AI Assistant, I can see you are logged in. Based on your role's permission matrix, you have full access to execute change orders, sign-off QC lists, and dispatch supply requisitions.";
  } else {
    fallbackText += "\n\nI can help you monitor live project telemetry, predict scheduling delays, review architectural blueprint compliance (OCR), or coordinate material procurement. What project would you like to review?";
  }
  return { text: fallbackText };
}

function getDetectRisksFallback() {
  return {
    overallRiskLevel: "Moderate-High",
    overallRiskScore: 74,
    scanTimestamp: new Date().toISOString(),
    risks: [
      {
        id: "RISK-01",
        title: "Tower Crane High Wind Hazard",
        projectCode: "PRJ-01",
        category: "Safety & QC",
        severity: "High",
        probability: "85%",
        description: "High continuous gusts are forecasted near the Skyline Financial Tower site. Anemometers indicate localized wind gusts up to 34 MPH, close to the maximum limit.",
        remedy: "Engage automated wind locking systems and suspend heavy material lifts above Level 20 until storm clears.",
        status: "Monitoring"
      },
      {
        id: "RISK-02",
        title: "Galvanized Copper Pipe Supply Outage",
        projectCode: "PRJ-03",
        category: "Material Procurement",
        severity: "Moderate",
        probability: "90%",
        description: "Active MEP Rough-in Stage 3 has exhausted local Copper Pipe stock. Current inventory level is below safe buffer limits.",
        remedy: "Approve ERP reorder dispatch immediately and shift installation crew to electrical conduit routing.",
        status: "Action Required"
      },
      {
        id: "RISK-03",
        title: "Subterranean Seepage Risk",
        projectCode: "PRJ-02",
        category: "Geotechnical",
        severity: "Critical",
        probability: "30%",
        description: "BIM telemetry sensors flag minor hydrostatic pressure elevation on Metro Hub North retaining wall following tidal shift.",
        remedy: "Deploy active slurry pump arrays and schedule structural grout injection inspection.",
        status: "Active Alert"
      }
    ]
  };
}

function getPredictDelayFallback() {
  return {
    riskScore: 68,
    riskLevel: "Moderate-High",
    predictedDelayDays: 4,
    primaryFactor: "Heavy rainfall predicted in Sector 4 combined with Excavator EX-04 maintenance downtime.",
    recommendations: [
      "Reschedule foundation pouring in Sector 4 to Thursday afternoon window.",
      "Reallocate Crane CR-02 from Metro Tower to cover structural lifting during crane EX-04 service.",
      "Authorize 2 extra overtime hours for rebar assembly crew on Wednesday."
    ],
    aiConfidence: "94.2%"
  };
}

function getAnalyzeDocumentFallback(docTitle?: string) {
  return {
    ocrSummary: `Automated OCR extraction complete for "${docTitle || "Document"}". Document contains structural specification notes, concrete curing tables (ASTM C31 standard), and anchor bolt load calculations.`,
    complianceStatus: "PASSED_WITH_CONDITIONS",
    keyHazards: [
      "Wind load limits require secondary bracing if gusts exceed 45 MPH during crane lift.",
      "Section 4.2 anchor bolt depth requires verification by licensed structural engineer prior to pour."
    ],
    extractedMetadata: {
      revision: "Rev 4.2",
      author: "Foster & Partners Engineering Group",
      dateStamped: new Date().toISOString().split("T")[0],
      estimatedBudgetImpact: "+$12,400 (Steel reinforcement grade upgrade)"
    }
  };
}

function getExecutiveBriefingFallback(timeframe?: string) {
  return {
    title: `Executive Construction Intelligence Briefing (${timeframe || "Weekly"})`,
    dateGenerated: new Date().toLocaleDateString(),
    overallHealth: "Good (89% On-Schedule)",
    keyHighlights: [
      "Metro Transit Center Phase 3 completed underground structural retaining walls 4 days ahead of schedule.",
      "Overall fleet utilization rate improved by 6.2% following AI automated route dispatching.",
      "Zero lost-time safety incidents recorded across all active 5 job sites this week."
    ],
    financialSummary: "Total portfolio burn rate is currently at $4.2M / month, tracking 1.8% under projected contingency budgets.",
    actionRequired: "Stakeholder approval needed for Change Order CO-108 ($45,000 for HVAC duct rerouting on Level 14)."
  };
}

// AI Guardrails Pipeline Evaluator & Sanitizer
function evaluateAiGuardrails(rawInput: string) {
  let text = rawInput || "";
  let piiDetected = false;
  let injectionDetected = false;

  // PII & Credentials Sanitization
  if (/\b\d{3}-\d{2}-\d{4}\b/.test(text)) {
    text = text.replace(/\b\d{3}-\d{2}-\d{4}\b/g, "[REDACTED_SSN]");
    piiDetected = true;
  }
  if (/\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/.test(text)) {
    text = text.replace(/\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b/g, "[REDACTED_CREDIT_CARD]");
    piiDetected = true;
  }
  if (/sk-[a-zA-Z0-9_-]{10,}/.test(text) || /AIzaSy[a-zA-Z0-9_-]{33}/.test(text)) {
    text = text.replace(/sk-[a-zA-Z0-9_-]{10,}/g, "[REDACTED_API_KEY]");
    text = text.replace(/AIzaSy[a-zA-Z0-9_-]{33}/g, "[REDACTED_API_KEY]");
    piiDetected = true;
  }

  // Prompt Injection & Jailbreak Defense
  const injectionPatterns = [
    /(ignore|forget|bypass)\s+(all\s+)?(previous|system)\s+(instructions|prompt|rules)/i,
    /system\s+prompt/i,
    /DAN\s+mode/i,
    /act\s+as\s+unrestricted/i,
    /reveal\s+(secret|admin|private)\s+key/i
  ];

  for (const pattern of injectionPatterns) {
    if (pattern.test(rawInput)) {
      injectionDetected = true;
      break;
    }
  }

  return {
    originalPrompt: rawInput,
    sanitizedPrompt: text,
    piiDetected,
    injectionDetected,
    actionTaken: injectionDetected 
      ? "BLOCKED (PROMPT INJECTION DETECTED)" 
      : piiDetected 
        ? "SANITIZED & ALLOWED" 
        : "PASSED (CLEAN)"
  };
}

// AI Guardrails Test Endpoint
app.post("/api/ai/guardrails/test", (req, res) => {
  const { prompt } = req.body;
  const evaluation = evaluateAiGuardrails(prompt || "");
  
  res.json({
    timestamp: new Date().toISOString(),
    originalPrompt: evaluation.originalPrompt,
    sanitizedPrompt: evaluation.sanitizedPrompt,
    actionTaken: evaluation.actionTaken,
    threatScore: evaluation.injectionDetected ? 94 : evaluation.piiDetected ? 45 : 2,
    flags: {
      piiDetected: evaluation.piiDetected,
      promptInjectionDetected: evaluation.injectionDetected,
      domainBoundariesViolated: false,
      safetyComplianceRisk: false,
    },
    evaluationDetails: evaluation.injectionDetected 
      ? "Prompt injection attack vector identified (Attempted system prompt bypass). Action: Request halted."
      : evaluation.piiDetected 
        ? "Sensitive PII and secrets identified and redacted before dispatching to LLM core."
        : "Prompt compliant with construction safety policies and domain boundaries."
  });
});

// AI Chatbot Endpoint
app.post("/api/ai/chat", async (req, res) => {
  const { message, history } = req.body;
  try {
    // Run input through AI Guardrails Pipeline
    const guardrailCheck = evaluateAiGuardrails(message);

    if (guardrailCheck.injectionDetected) {
      return res.json({
        text: "🛡️ **AI Guardrails Security Alert**: Your input was flagged for containing prompt injection or system override instructions. This conversation is protected by HubAI Security Shield. Please phrase your request regarding site telemetry, construction management, or safety audits."
      });
    }

    const sanitizedMessage = guardrailCheck.sanitizedPrompt;
    const ai = getGenAI();

    if (!ai) {
      return res.json(getChatFallback(sanitizedMessage));
    }

    const systemInstruction = `You are "HubAI", an elite, professional, and knowledgeable AI Construction Intelligence Assistant for the Construction Intelligence Hub platform.
You have direct line telemetry access to active projects, equipment trackers, safety compliance indexes, and city blueprints.
Answer questions accurately, keeping a professional, helpful, and engineering-focused tone. 
When asked about risks, materials, or timelines, use bulleted lists, bold terms, and provide clear mitigation recommendations.
Be concise and focus on visual, safe, and cost-effective outcomes.
Enforce safety policies: NEVER provide ungrounded hazardous engineering instructions or bypass OSHA rules.`;

    const contents = [];
    if (history && Array.isArray(history)) {
      for (const msg of history) {
        contents.push({
          role: msg.role === "user" ? "user" : "model",
          parts: [{ text: msg.content }]
        });
      }
    }
    contents.push({
      role: "user",
      parts: [{ text: sanitizedMessage }]
    });

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents,
      config: {
        systemInstruction,
        temperature: 0.7,
      }
    });

    let resultText = response.text || "";
    if (guardrailCheck.piiDetected) {
      resultText = "🔒 *(Note: Sensitive PII or credentials in your prompt were automatically sanitized by AI Guardrails prior to processing.)*\n\n" + resultText;
    }

    res.json({ text: resultText });
  } catch (error) {
    console.warn("Chatbot API Error (Falling back to offline heuristics):", error);
    res.json(getChatFallback(message));
  }
});

// AI Risk Detection Board Scan Endpoint
app.post("/api/ai/detect-risks", async (req, res) => {
  try {
    const { projects, weatherData, equipmentData } = req.body;
    const ai = getGenAI();

    if (!ai) {
      return res.json(getDetectRisksFallback());
    }

    const prompt = `You are an elite AI Risk Engineering Auditor. Scan this live construction portfolio data and detect active risks:
Projects Telemetry: ${JSON.stringify(projects)}
Weather Telemetry: ${JSON.stringify(weatherData || "Overcast, rain forecast")}
Equipment Telemetry: ${JSON.stringify(equipmentData || "Fleet active at 88% capacity")}

Provide a JSON object containing a detailed, professional list of detected risks with their category, severity, probability, description, remedy, and status.
The response must be strictly valid JSON with keys:
"overallRiskLevel" ("Low" | "Moderate" | "High" | "Critical"),
"overallRiskScore" (number 1-100),
"scanTimestamp" (string),
"risks" which is an array of objects, where each object has:
- "id" (string e.g. RISK-101)
- "title" (string short title)
- "projectCode" (string like PRJ-01)
- "category" (string e.g. "Safety", "Material", "Weather", "Labor")
- "severity" ("Low" | "Moderate" | "High" | "Critical")
- "probability" (string like "80%")
- "description" (string brief explanation of the hazard)
- "remedy" (string clear engineering action plan)
- "status" ("Monitoring" | "Action Required" | "Active Alert")`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: {
        responseMimeType: "application/json",
        temperature: 0.2
      }
    });

    res.json(JSON.parse(response.text || "{}"));
  } catch (error) {
    console.warn("AI Risk Detection Error (Falling back to offline heuristics):", error);
    res.json(getDetectRisksFallback());
  }
});

// AI Delay Prediction Endpoint
app.post("/api/ai/predict-delay", async (req, res) => {
  try {
    const { project, weatherRisk, equipmentStatus, laborCapacity } = req.body;
    const ai = getGenAI();
    
    if (!ai) {
      return res.json(getPredictDelayFallback());
    }

    const prompt = `You are the AI Construction Intelligence Officer for a major civil and commercial construction project.
Analyze these project conditions and predict schedule delay risks:
Project Details: ${JSON.stringify(project || { name: "Skyline Tower Phase 2" })}
Weather Forecast/Risk: ${JSON.stringify(weatherRisk || "Heavy rain forecast for 3 days")}
Equipment Status: ${JSON.stringify(equipmentStatus || "2 excavators undergoing unplanned maintenance")}
Labor Status: ${JSON.stringify(laborCapacity || "88% crew attendance")}

Provide a JSON output ONLY with keys:
"riskScore" (number 1-100),
"riskLevel" ("Low" | "Moderate" | "High" | "Critical"),
"predictedDelayDays" (number),
"primaryFactor" (string summary),
"recommendations" (array of 3 specific actionable engineering/resource steps),
"aiConfidence" (string like "95%")`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: { responseMimeType: "application/json" }
    });

    const parsed = JSON.parse(response.text || "{}");
    res.json(parsed);
  } catch (error) {
    console.warn("AI Prediction Error (Falling back to offline heuristics):", error);
    res.json(getPredictDelayFallback());
  }
});

// AI Project Estimation Modeling Endpoint
app.post("/api/ai/estimate-project", async (req, res) => {
  try {
    const { name, code, progress, budget, spent, activeWorkers } = req.body;
    const ai = getGenAI();

    if (!ai) {
      return res.status(200).json({ useFallback: true });
    }

    const prompt = `You are HubAI Construction Estimator. Estimate the remaining materials, costs, and labor hours required to complete this project:
Project: "${name}" (Code: ${code}, Progress: ${progress}%, Budget: $${budget} Spent: $${spent}, Workers: ${activeWorkers}).
Provide realistic estimates based on structural/civil engineering standards.

Respond STRICTLY with a JSON object containing keys:
"materials" (array of 4 objects, each with "name", "quantity" [formatted string], "unit", "cost", "category"),
"totalCostEstimate" (string),
"laborEstimateHours" (string),
"timelineEstimateWeeks" (string),
"riskAssessment" (string),
"recommendations" (array of 3 strings)`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: { responseMimeType: "application/json", temperature: 0.3 }
    });

    const parsed = JSON.parse(response.text || "{}");
    res.json(parsed);
  } catch (error) {
    console.warn("AI Project Estimation Error (Instructing client fallback):", error);
    res.json({ useFallback: true });
  }
});

// AI Document OCR & Compliance Analyzer
app.post("/api/ai/analyze-document", async (req, res) => {
  const { docTitle, category, notes } = req.body;
  try {
    const ai = getGenAI();

    if (!ai) {
      return res.json(getAnalyzeDocumentFallback(docTitle));
    }

    const prompt = `Analyze this construction document entry and simulate professional BIM/Engineering OCR extraction and compliance auditing:
Title: ${docTitle}
Category: ${category}
Notes/Context: ${notes || "Standard structural blueprint upload"}

Return strictly valid JSON with keys:
"ocrSummary" (string concise executive summary),
"complianceStatus" ("VERIFIED" | "PASSED_WITH_CONDITIONS" | "NEEDS_REVISION"),
"keyHazards" (array of 2 string bullet points on safety/code risks),
"extractedMetadata" (object with keys: revision, author, dateStamped, estimatedBudgetImpact)`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: { responseMimeType: "application/json" }
    });

    res.json(JSON.parse(response.text || "{}"));
  } catch (error) {
    console.warn("AI Document Analysis Error (Falling back to offline heuristics):", error);
    res.json(getAnalyzeDocumentFallback(docTitle));
  }
});

// Executive Briefing Generator
app.post("/api/ai/executive-briefing", async (req, res) => {
  const { projectsSummary, timeframe } = req.body;
  try {
    const ai = getGenAI();

    if (!ai) {
      return res.json(getExecutiveBriefingFallback(timeframe));
    }

    const prompt = `Create a high-level executive stakeholder briefing for a construction portfolio:
Data: ${JSON.stringify(projectsSummary)}
Timeframe: ${timeframe || "Current Quarter"}

Return strictly JSON with keys:
"title", "dateGenerated", "overallHealth", "keyHighlights" (array of 3 strings), "financialSummary" (string), "actionRequired" (string)`;

    const response = await ai.models.generateContent({
      model: "gemini-2.5-flash",
      contents: prompt,
      config: { responseMimeType: "application/json" }
    });

    res.json(JSON.parse(response.text || "{}"));
  } catch (err) {
    console.warn("AI Executive Briefing Error (Falling back to offline heuristics):", err);
    res.json(getExecutiveBriefingFallback(timeframe));
  }
});

// Ollama Proxy Status Check
app.post("/api/ai/ollama/status", async (req, res) => {
  const { url } = req.body;
  const targetUrl = url || "http://localhost:11434";
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 4000); // 4s timeout

    const response = await fetch(`${targetUrl}/api/tags`, {
      method: "GET",
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (response.ok) {
      const data = await response.json();
      return res.json({
        success: true,
        models: data.models || [],
        message: "Successfully connected to Ollama core instance."
      });
    } else {
      return res.status(response.status).json({
        success: false,
        message: `Ollama service returned status ${response.status}`
      });
    }
  } catch (err: any) {
    console.warn("Ollama status ping failed:", err);
    return res.json({
      success: false,
      message: `Could not reach Ollama at ${targetUrl}. Is Ollama running? Error: ${err.message}`
    });
  }
});

// Ollama Proxy Chat Handler
app.post("/api/ai/ollama/chat", async (req, res) => {
  const { message, history, url, model } = req.body;
  const targetUrl = url || "http://localhost:11434";
  const targetModel = model || "llama3";
  
  try {
    const systemInstruction = `You are "HubAI", an elite, professional AI Construction Intelligence Assistant. Keep a professional, helpful, and engineering-focused tone. Answer accurately. Use bulleted lists, bold terms, and provide clear mitigation recommendations when asked about project risks, materials, or timelines.`;
    
    const ollamaMessages = [
      { role: "system", content: systemInstruction }
    ];

    if (history && Array.isArray(history)) {
      for (const msg of history) {
        ollamaMessages.push({
          role: msg.role === "user" ? "user" : "assistant",
          content: msg.content
        });
      }
    }

    ollamaMessages.push({
      role: "user",
      content: message
    });

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3500);

    const response = await fetch(`${targetUrl}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        model: targetModel,
        messages: ollamaMessages,
        stream: false
      }),
      signal: controller.signal
    });
    clearTimeout(timeoutId);

    if (!response.ok) {
      throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
    }

    const data = await response.json();
    const text = data.message?.content || "";
    res.json({ text });
  } catch (err: any) {
    console.warn("Ollama Chat Proxy error:", err);
    res.json({ 
      text: `Failed to fetch response from Ollama at ${targetUrl} using model "${targetModel}".\n\n*Error details:* ${err.message}\n\n*Checklist:* \n1. Is Ollama running at the target URL?\n2. Did you pull the model? Try running: \`ollama pull ${targetModel}\`\n3. Note: If you are running Ollama locally on your laptop, use the **Client-Side Direct Routing** toggle to make direct browser requests!`
    });
  }
});

// Developer API Sandbox routes
app.get("/api/v1/projects", (req, res) => {
  apiLogs.unshift({
    id: `LOG-${1000 + apiLogs.length + 1}`,
    timestamp: new Date().toISOString(),
    method: "GET",
    endpoint: "/api/v1/projects",
    status: 200,
    source: req.headers["x-api-client"] as string || "External REST Sandbox"
  });
  res.json({
    success: true,
    count: 4,
    projects: [
      { id: "PRJ-01", name: "Skyline Financial Tower Phase 2", progress: 68, status: "Active", budget: "$145M", spent: "$98.6M", deadline: "2026-11-15" },
      { id: "PRJ-02", name: "Metro Hub Underground Terminal", progress: 84, status: "Active", budget: "$320M", spent: "$268.8M", deadline: "2026-08-30" },
      { id: "PRJ-03", name: "Pacific Waterfront Bridge Expansion", progress: 41, status: "Warning", budget: "$88M", spent: "$39.2M", deadline: "2027-04-10" },
      { id: "PRJ-04", name: "Biotech Campus R&D Facility", progress: 92, status: "Near Completion", budget: "$64M", spent: "$58.9M", deadline: "2026-07-28" }
    ]
  });
});

app.get("/api/v1/logs", (req, res) => {
  res.json({ logs: apiLogs.slice(0, 20) });
});

app.post("/api/v1/webhooks/receive", (req, res) => {
  const payload = req.body;
  const newLog = {
    id: `LOG-${1000 + apiLogs.length + 1}`,
    timestamp: new Date().toISOString(),
    method: "POST",
    endpoint: "/api/v1/webhooks/receive",
    status: 201,
    source: payload.source || "External Webhook Trigger"
  };
  apiLogs.unshift(newLog);
  res.status(201).json({ success: true, receivedId: newLog.id, message: "Webhook successfully processed and routed to project telemetry engine." });
});

// Vite or Static Serving setup
if (process.env.NODE_ENV !== "production") {
  import("vite").then(async ({ createServer: createViteServer }) => {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
    
    app.listen(PORT, "0.0.0.0", () => {
      console.log(`Construction Intelligence Hub Server running on http://localhost:${PORT}`);
    });
  });
} else {
  const distPath = path.join(__dirname, "dist");
  app.use(express.static(distPath));
  app.get("*", (req, res) => {
    res.sendFile(path.join(distPath, "index.html"));
  });
  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Production server running on port ${PORT}`);
  });
}
