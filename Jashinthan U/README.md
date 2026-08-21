🏗️ Construction Intelligence Hub

AI-powered construction portfolio management, BIM telemetry intelligence, field engineering support, and developer API sandbox.

Construction Intelligence Hub is a full-spectrum construction management platform designed to connect executive decision-making with real-time jobsite operations. The system combines project tracking, AI-driven risk analysis, schedule-delay prediction, project estimation, document/OCR compliance analysis, an AI construction assistant, offline field workflows, role-based access concepts, and API integration capabilities.

The system specification describes Hub Intelligence v4.2 as an enterprise cloud and field-tablet platform that can process telemetry from IoT crane sensors, BIM systems, financial connectors, and field devices operating in low-connectivity environments.

✨ Key Features

📊 Construction Portfolio Management

Real-time project portfolio monitoring

Project progress, budget, spending, status, and deadlines

Construction KPI tracking

Executive-level portfolio insights

🤖 HubAI Construction Assistant

AI chat assistant for construction-related questions

Uses Google Gemini when GEMINI_API_KEY is available

Construction-focused system instructions

Safety-oriented response constraints

Offline heuristic fallback when Gemini is unavailable

🛡️ AI Security Guardrails

The backend includes an AI guardrails pipeline that:

Detects common prompt-injection/jailbreak patterns

Redacts sensitive identifiers such as credit-card numbers and API-key-like strings

Blocks detected prompt-injection attempts

Reports threat and compliance flags through a test endpoint

⚠️ AI Risk Detection

The risk engine analyzes project, weather, and equipment data and returns:

Overall risk level

Risk score

Risk category

Severity

Probability

Risk description

Recommended remedy

Current status

⏱️ AI Delay Prediction

HubAI can analyze:

Project conditions

Weather risk

Equipment availability

Labor capacity

It returns a predicted delay, risk score, primary contributing factor, recommendations, and AI confidence.

💰 AI Project Estimation

The estimation endpoint can generate:

Remaining material estimates

Material quantities and costs

Total cost estimate

Labor-hour estimate

Timeline estimate

Risk assessment

Recommended actions

📄 AI Document & Compliance Analyzer

The platform provides an AI document-analysis workflow for construction documentation, including:

OCR-style document summarization

Compliance status

Key hazards

Revision metadata

Author/date information

Estimated budget impact

🧑‍💼 Executive Briefing Generator

Generates a high-level stakeholder briefing containing:

Overall portfolio health

Key highlights

Financial summary

Required executive action

📡 BIM & Telemetry Architecture

The system specification defines data flows from:

IoT jobsite sensors and cranes

Field engineer tablets

Autodesk BIM 360 / Procore connectors

REST/MQTT API portals

Webhook integrations

📱 Field Engineer Offline Protocol

The architecture includes an offline workflow where field data can be cached locally and synchronized when connectivity is restored. The specification identifies inspection sign-offs, QC checklists, material receipts, and safety flags as examples of queued field transactions.

🔐 Role-Based Access & MFA

The system specification defines five operational roles:

Executive Stakeholder

Project Manager

Site Engineer (Field)

Safety & QC Inspector

API Systems Architect

The specification also describes hardware MFA for protected executive workflows.

🔌 Developer API Sandbox

The backend provides sandbox routes for:

Project retrieval

API/webhook logging

Webhook reception

Health checks

External integration simulation

🦙 Ollama Support

The backend also contains optional Ollama proxy routes for:

Checking an Ollama instance

Sending chat requests to a selected local model

The default Ollama model in the server implementation is llama3.

🧱 Technology Stack

Frontend

React 19

Vite 6

TypeScript

Tailwind CSS 4

@vitejs/plugin-react

Lucide React

Motion

Recharts

Backend

Node.js

Express

TypeScript

TSX

esbuild

dotenv

AI

Google Gemini API through @google/genai

Gemini model used by the backend: gemini-2.5-flash

Optional local Ollama integration

The project's Vite configuration uses both the React and Tailwind Vite plugins, with an @ path alias for the project root.

📁 Project Structure

A typical structure for this project is:

construction-intelligence-hub/
├── src/
│   ├── main.tsx
│   └── ...frontend components...
├── public/
│   └── ...static assets...
├── server.ts
├── index.html
├── package.json
├── package-lock.json
├── vite.config.ts
├── tsconfig.json
├── .env.example
├── .gitignore
├── metadata.json
├── SYSTEM_SPECIFICATION.md
└── README.md

The exact contents of the src/ and public/ directories are not included in the uploaded project files used to prepare this README, so this README does not assume specific component filenames.

🚀 Getting Started

1. Prerequisites

Install:

Node.js 18+ recommended

npm

A Google Gemini API key if you want Gemini-powered features

The project's dependencies include React, Vite, Express, Google GenAI, TypeScript, Tailwind CSS, Recharts, Motion, and related packages.

2. Install Dependencies

npm install

3. Configure Environment Variables

Create a .env file based on .env.example:

GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
APP_URL="http://localhost:3000"

GEMINI_API_KEY is used by the server to initialize the Google GenAI client. If the key is missing, the backend uses its built-in fallback behavior for supported AI workflows.

Never commit real API keys or secrets to GitHub.

4. Run in Development

npm run dev

The package configuration defines the development command as:

tsx server.ts

The Express server defaults to port 3000 unless the PORT environment variable is provided.

Open:

http://localhost:3000

5. Build for Production

npm run build

The build process:

Builds the frontend with Vite.

Bundles server.ts with esbuild.

Produces dist/server.cjs.

6. Start Production Server

npm start

7. Type Check

npm run lint

This runs TypeScript without emitting compiled files.

8. Clean Build Output

npm run clean

🔑 Environment Variables

Variable

Required

Description

GEMINI_API_KEY

Optional for fallback mode / required for Gemini calls

Google Gemini API key

APP_URL

Deployment-dependent

URL where the application is hosted

PORT

Optional

Express server port; defaults to 3000

DISABLE_HMR

Optional

Disables Vite HMR/file watching when set to true

The supplied .env.example documents GEMINI_API_KEY and APP_URL.

🔗 Backend API

Health Check

GET /api/health

Returns the API service status and timestamp.

AI Chat

POST /api/ai/chat

Example request:

{
  "message": "What are the current project risks?",
  "history": []
}

AI Guardrails Test

POST /api/ai/guardrails/test

Example:

{
  "prompt": "Analyze the project safety status."
}

The response includes sanitization results, threat score, security flags, and the action taken.

AI Risk Detection

POST /api/ai/detect-risks

Expected input can include:

projects

weatherData

equipmentData

The AI response is structured JSON containing risk level, score, and risk records.

AI Delay Prediction

POST /api/ai/predict-delay

Expected input:

project

weatherRisk

equipmentStatus

laborCapacity

AI Project Estimation

POST /api/ai/estimate-project

Expected input:

name

code

progress

budget

spent

activeWorkers

AI Document Analysis

POST /api/ai/analyze-document

Expected input:

docTitle

category

notes

Executive Briefing

POST /api/ai/executive-briefing

Expected input:

projectsSummary

timeframe

Ollama Status

POST /api/ai/ollama/status

Optional request body:

{
  "url": "http://localhost:11434"
}

Ollama Chat

POST /api/ai/ollama/chat

Example:

{
  "message": "Summarize current construction risks.",
  "history": [],
  "url": "http://localhost:11434",
  "model": "llama3"
}

Developer API

GET /api/v1/projects
GET /api/v1/logs
POST /api/v1/webhooks/receive

These routes provide a developer sandbox for project data, API logs, and webhook simulation.

🧠 AI Architecture

The server follows a resilient AI pattern:

User / Dashboard
       │
       ▼
   Express API
       │
       ▼
 AI Guardrails
       │
       ├── Prompt injection detected ──► Block
       │
       └── PII / secret detected ─────► Sanitize
                         │
                         ▼
                  Gemini 2.5 Flash
                         │
                         ▼
                    AI Response
                         │
                 Failure / No API Key
                         │
                         ▼
               Offline Fallback Logic

The Gemini client is initialized lazily and only when a GEMINI_API_KEY is available. The backend also contains deterministic fallback responses for several AI workflows.

🏗️ System Architecture

The supplied system specification describes the following high-level flow:

┌───────────────────────────────┐
│ IoT Jobsite Sensors / Cranes  │
└───────────────┬───────────────┘
                │ REST / MQTT
                ▼
┌───────────────────────────────┐
│       Hub Intelligence Core   │
└───────┬─────────┬─────────────┘
        │         │
        │         ├──────────────► AI / Analytics
        │         │                 ├─ Risk Detection
        │         │                 ├─ Delay Prediction
        │         │                 ├─ Estimation
        │         │                 ├─ Document Analysis
        │         │                 └─ Executive Briefing
        │
        ├────────────────────────► BIM / Financial Connectors
        │                           ├─ Autodesk BIM 360
        │                           └─ Procore
        │
        └────────────────────────► Field Engineer Devices
                                    └─ Offline Queue / Sync

🛡️ Security Considerations

The backend implements several application-level protections:

Prompt-injection detection

PII/credential-like string redaction

AI request blocking when injection patterns are detected

Role-based access concepts in the system architecture

MFA requirements described for protected executive workflows

Environment-based secret configuration

No API key should be committed to source control

For production deployment, additional infrastructure security, authentication, authorization, audit logging, secret management, encryption, network controls, and compliance validation should be implemented according to the deployment environment.

📈 Example KPI Model

The system specification defines example portfolio KPIs including:

Total Portfolio Efficiency

Safety Rating

Resource Fleet Load

Budget Variance

The specification's example values are:

Portfolio Efficiency: 92.4%
Safety Rating: 99.8
Resource Fleet Load: 84.1%
Budget Variance: -$4.2k

These are specification/example values and should not be interpreted as live production metrics.

🧪 Development Notes

Gemini unavailable

If GEMINI_API_KEY is not available, supported AI routes can fall back to predefined heuristic responses. This allows the application to continue operating in a sandbox/offline-style mode.

Ollama

For local AI experimentation, run Ollama separately and make sure the selected model is available. The server checks the Ollama /api/tags endpoint and uses /api/chat for conversations.

HMR

The Vite configuration supports DISABLE_HMR=true. This disables HMR and file watching, which is useful in environments where file changes are controlled by an AI development environment.

📦 Available npm Scripts

Command

Purpose

npm run dev

Start development server

npm run build

Build frontend and bundle backend

npm start

Start production server

npm run clean

Remove build output

npm run lint

Type-check the project

🎯 Intended Use Cases

Construction Intelligence Hub is intended as a technology platform/prototype for scenarios such as:

Construction portfolio monitoring

Jobsite safety intelligence

Construction schedule risk analysis

Equipment and resource monitoring

Material procurement intelligence

BIM/document compliance workflows

Executive construction reporting

Field engineering workflows

AI-assisted construction operations

API and webhook integration testing

🔮 Future Enhancements

Potential production-grade extensions include:

Persistent database integration

Full authentication and MFA implementation

Real-time MQTT/IoT ingestion

Production BIM 360 / Procore connectors

Persistent offline synchronization storage

Actual document/PDF upload and OCR pipeline

Advanced computer vision for jobsite safety

Predictive equipment maintenance

Real-time notifications and alerting

Audit trails and enterprise identity integration

Cloud object storage for BIM documents

Automated CI/CD and infrastructure-as-code

Comprehensive unit, integration, and end-to-end testing

📚 Project Documentation

The repository includes SYSTEM_SPECIFICATION.md, which defines the project's Hub Intelligence v4.2 architecture, core architectural pillars, data flow, operational roles, and example KPIs.

👨‍💻 Development

This project uses a React + Vite frontend and an Express/TypeScript backend. The backend integrates Google Gemini through the official @google/genai package and exposes construction-focused AI and developer sandbox APIs.

⚠️ Disclaimer

This project is an AI-enabled construction management platform/prototype. AI-generated recommendations must not replace qualified engineers, safety professionals, project managers, regulatory requirements, or approved construction procedures. Engineering and safety decisions should be validated by appropriately licensed professionals and applicable local standards.

📄 License

No license is specified in the supplied project files. Add an appropriate license before distributing the project publicly.
