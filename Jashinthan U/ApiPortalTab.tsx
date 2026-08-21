import React, { useState } from "react";
import { 
  Code, 
  Terminal, 
  Send, 
  Copy, 
  Check, 
  Key, 
  RefreshCw, 
  Database, 
  Webhook, 
  Layers, 
  ExternalLink,
  ShieldAlert
} from "lucide-react";
import { ApiLog, PermissionMatrix } from "../types";

interface ApiPortalTabProps {
  logs: ApiLog[];
  darkMode: boolean;
  permissions: PermissionMatrix;
  onAddLog: (log: ApiLog) => void;
}

export const ApiPortalTab: React.FC<ApiPortalTabProps> = ({
  logs,
  darkMode,
  permissions,
  onAddLog,
}) => {
  const [apiKey, setApiKey] = useState("cih_live_9948201a88f4b29c018a");
  const [copied, setCopied] = useState(false);

  // REST Endpoint Tester state
  const [method, setMethod] = useState<"GET" | "POST">("GET");
  const [endpoint, setEndpoint] = useState("/api/v1/projects");
  const [payload, setPayload] = useState('{\n  "source": "Procore Sandbox Simulator",\n  "projectCode": "SKY-2026",\n  "statusUpdate": "Pour completed for Level 22"\n}');
  const [testing, setTesting] = useState(false);
  const [testResponse, setTestResponse] = useState<any | null>(null);

  // Ollama playground state
  const [playgroundUrl, setPlaygroundUrl] = useState("http://localhost:11434");
  const [playgroundModel, setPlaygroundModel] = useState("llama3");
  const [playgroundSys, setPlaygroundSys] = useState("You are HubAI Construction Assistant.");
  const [playgroundPrompt, setPlaygroundPrompt] = useState("Generate a 3-bullet point safety check list for a high-rise crane lifting operation.");
  const [testingPlayground, setTestingPlayground] = useState(false);
  const [playgroundStatus, setPlaygroundStatus] = useState<{ success: boolean; message: string } | null>(null);
  const [queryingPlayground, setQueryingPlayground] = useState(false);
  const [playgroundResponse, setPlaygroundResponse] = useState("");

  const integrations = [
    { name: "Procore Construction ERP", type: "Bidirectional Webhook", status: "Active Connected", latency: "42ms", callsToday: "1,420" },
    { name: "Autodesk BIM 360 / Navisworks", type: "Clash Detection Sync", status: "Active Connected", latency: "88ms", callsToday: "650" },
    { name: "Caterpillar GPS Fleet Telemetry", type: "IoT Telemetry Stream", status: "Active Connected", latency: "18ms", callsToday: "8,920" },
    { name: "SAP S/4HANA Financial Cloud", type: "Pay Application Bridge", status: "Standby / Hourly", latency: "115ms", callsToday: "24" },
  ];

  const handleCopyKey = () => {
    navigator.clipboard.writeText(apiKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleRegenerateKey = () => {
    if (!permissions.manageApiKeys) {
      alert("Permission denied. Ask an API Systems Architect or Project Manager to regenerate keys.");
      return;
    }
    const chars = "abcdef0123456789";
    let rand = "";
    for (let i = 0; i < 20; i++) rand += chars[Math.floor(Math.random() * chars.length)];
    setApiKey(`cih_live_${rand}`);
  };

  const handleExecuteRequest = async () => {
    setTesting(true);
    setTestResponse(null);
    try {
      const options: RequestInit = {
        method,
        headers: {
          "Content-Type": "application/json",
          "X-API-Client": "CIH Interactive Developer Sandbox"
        }
      };
      if (method === "POST") {
        options.body = payload;
      }

      const res = await fetch(endpoint, options);
      const data = await res.json();
      setTestResponse({ status: res.status, statusText: res.statusText, body: data });

      // Add log
      onAddLog({
        id: `LOG-${1000 + logs.length + 1}`,
        timestamp: new Date().toISOString(),
        method,
        endpoint,
        status: res.status,
        source: "Developer Console Tester"
      });
    } catch (err: any) {
      setTestResponse({
        status: 500,
        statusText: "Network Error / Simulation Fallback",
        body: { error: err.message || "Failed to execute API request" }
      });
    } finally {
      setTesting(false);
    }
  };

  const handleTestPlayground = async () => {
    setTestingPlayground(true);
    setPlaygroundStatus(null);
    try {
      const res = await fetch("/api/ai/ollama/status", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: playgroundUrl })
      });
      const data = await res.json();
      if (data.success) {
        const modelsList = data.models && data.models.length > 0 
          ? data.models.map((m: any) => m.name).join(", ") 
          : "none (try pulling a model)";
        setPlaygroundStatus({ success: true, message: `✅ Successfully connected! Installed models: [${modelsList}]` });
      } else {
        setPlaygroundStatus({ success: false, message: `❌ Connection failed: ${data.message}` });
      }
    } catch (err: any) {
      setPlaygroundStatus({ success: false, message: `❌ Connection error: ${err.message}` });
    } finally {
      setTestingPlayground(false);
    }
  };

  const handleRunPlaygroundQuery = async () => {
    setQueryingPlayground(true);
    setPlaygroundResponse("");
    try {
      const res = await fetch("/api/ai/ollama/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: playgroundPrompt,
          url: playgroundUrl,
          model: playgroundModel,
          history: []
        })
      });
      const data = await res.json();
      setPlaygroundResponse(data.text || "No response generated.");
    } catch (err: any) {
      setPlaygroundResponse(`❌ Failed to query Ollama node: ${err.message}`);
    } finally {
      setQueryingPlayground(false);
    }
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Top Header */}
      <div className={`p-6 rounded-2xl border flex flex-col md:flex-row md:items-center justify-between gap-4 ${
        darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
      }`}>
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="font-extrabold text-lg sm:text-xl">Developer API Sandbox & Third-Party Integrations Portal</h2>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/20 text-amber-500 border border-amber-500/30">
              REST v2.4 / Webhooks
            </span>
          </div>
          <p className="text-xs opacity-70 mt-1">
            Seamlessly synchronize project telemetry, BIM submittals, and GPS fleet statuses with Procore, Autodesk, and corporate ERPs.
          </p>
        </div>

        {/* API Key Box */}
        <div className="flex items-center space-x-2">
          <div className={`flex items-center space-x-2 px-3 py-2 rounded-xl border text-xs font-mono ${
            darkMode ? "bg-slate-800 border-slate-700" : "bg-slate-100 border-slate-300"
          }`}>
            <Key className="w-3.5 h-3.5 text-amber-500" />
            <span className="max-w-[150px] sm:max-w-none truncate">{apiKey}</span>
            <button onClick={handleCopyKey} title="Copy Key" className="hover:opacity-100 opacity-70">
              {copied ? <Check className="w-4 h-4 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
            </button>
          </div>
          {permissions.manageApiKeys && (
            <button
              onClick={handleRegenerateKey}
              title="Regenerate API Key"
              className="p-2 rounded-xl bg-amber-500 text-slate-950 hover:bg-amber-400 font-bold text-xs"
            >
              <RefreshCw className="w-4 h-4" />
            </button>
          )}
        </div>
      </div>

      {/* Third-Party Integrations Grid */}
      <div>
        <h3 className="text-xs font-bold uppercase tracking-wider opacity-70 mb-3">Pre-Configured Enterprise Connectors</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {integrations.map((intg, i) => (
            <div key={i} className={`p-4 rounded-2xl border transition-all ${
              darkMode ? "bg-slate-900/60 border-slate-800" : "bg-white border-slate-200 shadow-sm"
            }`}>
              <div className="flex items-center justify-between">
                <Webhook className="w-5 h-5 text-amber-500" />
                <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-emerald-500/15 text-emerald-500 border border-emerald-500/30">
                  {intg.status}
                </span>
              </div>
              <h4 className="font-bold text-sm mt-3">{intg.name}</h4>
              <p className="text-xs opacity-70">{intg.type}</p>
              
              <div className="mt-4 pt-3 border-t border-slate-200/20 dark:border-slate-800 flex items-center justify-between text-[11px] font-mono opacity-80">
                <span>Latency: {intg.latency}</span>
                <span>{intg.callsToday} req/day</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Interactive API Sandbox / REST Endpoint Tester */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Request Tester Form */}
        <div className={`p-6 rounded-2xl border transition-all space-y-4 ${
          darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
        }`}>
          <div className="flex items-center space-x-2 pb-3 border-b border-slate-200 dark:border-slate-800">
            <Terminal className="w-5 h-5 text-amber-500" />
            <h3 className="font-extrabold text-base">Interactive REST Endpoint Console</h3>
          </div>

          <div className="flex items-center space-x-2">
            <select
              value={method}
              onChange={(e) => {
                const m = e.target.value as "GET" | "POST";
                setMethod(m);
                if (m === "POST") setEndpoint("/api/v1/webhooks/receive");
                else setEndpoint("/api/v1/projects");
              }}
              className="px-3 py-2 rounded-xl text-xs font-bold bg-amber-500 text-slate-950 focus:outline-none"
            >
              <option value="GET">GET</option>
              <option value="POST">POST</option>
            </select>

            <input
              type="text"
              value={endpoint}
              onChange={(e) => setEndpoint(e.target.value)}
              className={`flex-1 px-3.5 py-2 text-xs font-mono rounded-xl border ${
                darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"
              }`}
            />
          </div>

          {method === "POST" && (
            <div>
              <label className="block text-xs font-bold uppercase mb-1 opacity-70">JSON Payload Body</label>
              <textarea
                rows={5}
                value={payload}
                onChange={(e) => setPayload(e.target.value)}
                className={`w-full p-3 font-mono text-xs rounded-xl border ${
                  darkMode ? "bg-slate-950 border-slate-800 text-amber-400" : "bg-slate-900 border-slate-800 text-emerald-400"
                }`}
              />
            </div>
          )}

          <button
            onClick={handleExecuteRequest}
            disabled={testing}
            className="w-full py-2.5 px-4 rounded-xl font-bold text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/20 transition-all flex items-center justify-center space-x-2"
          >
            {testing ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
            <span>Execute Live Request to Sandbox</span>
          </button>

          {/* Response Box */}
          {testResponse && (
            <div className="mt-4 pt-4 border-t border-slate-200 dark:border-slate-800 space-y-2 animate-fade-in">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold uppercase tracking-wider opacity-70">Response Output</span>
                <span className={`px-2 py-0.5 rounded text-[10px] font-mono font-bold ${
                  testResponse.status < 300 ? "bg-emerald-500/20 text-emerald-500" : "bg-rose-500/20 text-rose-500"
                }`}>
                  Status: {testResponse.status} {testResponse.statusText}
                </span>
              </div>

              <pre className={`p-4 rounded-xl font-mono text-[11px] overflow-x-auto max-h-60 ${
                darkMode ? "bg-slate-950 text-slate-300 border border-slate-800" : "bg-slate-900 text-slate-100"
              }`}>
                {JSON.stringify(testResponse.body, null, 2)}
              </pre>
            </div>
          )}
        </div>

        {/* Live API Audit Logs */}
        <div className={`p-6 rounded-2xl border transition-all space-y-4 ${
          darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
        }`}>
          <div className="flex items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center space-x-2">
              <Database className="w-5 h-5 text-blue-500" />
              <h3 className="font-extrabold text-base">Live API Request Stream & Webhooks</h3>
            </div>
            <span className="text-xs font-mono text-emerald-500">Real-Time Polling</span>
          </div>

          <div className="space-y-2.5 max-h-[480px] overflow-y-auto pr-1">
            {logs.map((lg) => (
              <div key={lg.id} className={`p-3.5 rounded-xl border font-mono text-xs transition-all ${
                darkMode ? "bg-slate-800/40 border-slate-800" : "bg-slate-50 border-slate-200"
              }`}>
                <div className="flex items-center justify-between mb-1.5">
                  <div className="flex items-center space-x-2">
                    <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                      lg.method === "POST" ? "bg-amber-500/20 text-amber-500" : "bg-blue-500/20 text-blue-500"
                    }`}>
                      {lg.method}
                    </span>
                    <span className="font-bold truncate max-w-[180px]">{lg.endpoint}</span>
                  </div>
                  <span className={`px-1.5 py-0.2 rounded text-[10px] font-bold ${
                    lg.status < 300 ? "text-emerald-500 bg-emerald-500/10" : "text-rose-500 bg-rose-500/10"
                  }`}>
                    {lg.status}
                  </span>
                </div>
                <div className="flex items-center justify-between text-[11px] opacity-60">
                  <span>Client: {lg.source}</span>
                  <span>{new Date(lg.timestamp).toLocaleTimeString()}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>

      {/* Local AI Integration Node: Ollama Console */}
      <div className={`p-6 rounded-2xl border transition-all space-y-4 ${
        darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
      }`}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-3 border-b border-slate-200 dark:border-slate-800 gap-2">
          <div className="flex items-center space-x-2">
            <Layers className="w-5 h-5 text-amber-500" />
            <div>
              <h3 className="font-extrabold text-base">Ollama Node Playground & Diagnostics</h3>
              <p className="text-xs opacity-70">Query and debug your local or remote Ollama models directly within the Developer Hub.</p>
            </div>
          </div>
          <span className="px-2.5 py-1 rounded-full text-[10px] font-bold bg-amber-500/10 text-amber-500 border border-amber-500/20 w-fit">
            AI Engine Connector
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Settings Column */}
          <div className="space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider opacity-60 font-mono">Connection Parameters</h4>
            
            <div className="space-y-1">
              <label className="text-[10px] font-bold opacity-70">Ollama API URL</label>
              <input
                type="text"
                value={playgroundUrl}
                onChange={(e) => setPlaygroundUrl(e.target.value)}
                placeholder="e.g. http://localhost:11434"
                className={`w-full px-3 py-2 text-xs font-mono rounded-lg border ${
                  darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"
                }`}
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-bold opacity-70">Model Tag</label>
              <input
                type="text"
                value={playgroundModel}
                onChange={(e) => setPlaygroundModel(e.target.value)}
                placeholder="e.g. llama3"
                className={`w-full px-3 py-2 text-xs font-mono rounded-lg border ${
                  darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"
                }`}
              />
            </div>

            <button
              onClick={handleTestPlayground}
              disabled={testingPlayground}
              className="w-full py-2 bg-slate-950 text-white dark:bg-white dark:text-slate-950 hover:opacity-90 rounded-lg text-xs font-bold transition-all cursor-pointer"
            >
              {testingPlayground ? "Testing Node..." : "Test Local Node Connection"}
            </button>

            {playgroundStatus && (
              <div className={`p-3 rounded-xl text-xs font-mono ${
                playgroundStatus.success ? "bg-emerald-500/10 text-emerald-500 border border-emerald-500/20" : "bg-rose-500/10 text-rose-500 border border-rose-500/20"
              }`}>
                {playgroundStatus.message}
              </div>
            )}
          </div>

          {/* Prompt / Query Column */}
          <div className="md:col-span-2 space-y-4">
            <h4 className="text-xs font-bold uppercase tracking-wider opacity-60 font-mono">Sandbox AI Direct Query</h4>
            
            <div className="space-y-1">
              <label className="text-[10px] font-bold opacity-70">System Context Instruction</label>
              <input
                type="text"
                value={playgroundSys}
                onChange={(e) => setPlaygroundSys(e.target.value)}
                className={`w-full px-3 py-2 text-xs rounded-lg border ${
                  darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"
                }`}
              />
            </div>

            <div className="space-y-1">
              <label className="text-[10px] font-bold opacity-70">Input Query Text</label>
              <textarea
                rows={3}
                value={playgroundPrompt}
                onChange={(e) => setPlaygroundPrompt(e.target.value)}
                placeholder="Type anything to query the active model..."
                className={`w-full p-3 text-xs rounded-lg border ${
                  darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"
                }`}
              />
            </div>

            <div className="flex gap-2">
              <button
                onClick={handleRunPlaygroundQuery}
                disabled={queryingPlayground || !playgroundPrompt.trim()}
                className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-lg text-xs font-bold transition-all flex items-center gap-1 cursor-pointer"
              >
                {queryingPlayground ? "Generating..." : "Execute Query"}
              </button>
              <button
                onClick={() => setPlaygroundResponse("")}
                className="px-3 py-2 border border-slate-200 dark:border-slate-800 hover:opacity-80 rounded-lg text-xs cursor-pointer"
              >
                Clear
              </button>
            </div>

            {playgroundResponse && (
              <div className="space-y-1.5 animate-fade-in">
                <label className="text-[10px] font-bold uppercase tracking-wider opacity-60 font-mono">Engine Output</label>
                <div className={`p-4 rounded-xl border max-h-60 overflow-y-auto whitespace-pre-wrap text-xs leading-relaxed font-mono ${
                  darkMode ? "bg-slate-950 text-slate-200 border-slate-800" : "bg-slate-50 text-slate-800 border-slate-200"
                }`}>
                  {playgroundResponse}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

    </div>
  );
};
