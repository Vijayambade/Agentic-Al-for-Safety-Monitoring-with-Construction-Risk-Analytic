import React, { useState, useEffect } from "react";
import { 
  Building2, 
  AlertTriangle, 
  Calendar, 
  Users, 
  DollarSign, 
  CheckCircle2, 
  Sparkles, 
  CloudRain, 
  ArrowRight, 
  BarChart2,
  Clock,
  MapPin,
  RefreshCw,
  Calculator,
  Coins,
  Hammer,
  Sliders,
  Layers
} from "lucide-react";
import { Project, PermissionMatrix } from "../types";

interface OverviewTabProps {
  projects: Project[];
  darkMode: boolean;
  permissions: PermissionMatrix;
  onSelectProjectForAnalytics: (projectId: string) => void;
}

export const OverviewTab: React.FC<OverviewTabProps> = ({
  projects,
  darkMode,
  permissions,
  onSelectProjectForAnalytics,
}) => {
  const [selectedProjectId, setSelectedProjectId] = useState<string>(projects[0]?.id || "PRJ-01");
  const [aiPredicting, setAiPredicting] = useState(false);
  const [aiPredictionResult, setAiPredictionResult] = useState<{
    riskScore: number;
    riskLevel: string;
    predictedDelayDays: number;
    primaryFactor: string;
    recommendations: string[];
    aiConfidence: string;
  } | null>(null);

  // Ollama & AI configuration states synced with localStorage
  const [aiProvider, setAiProvider] = useState<"gemini" | "ollama">("gemini");
  const [ollamaUrl, setOllamaUrl] = useState("http://localhost:11434");
  const [ollamaModel, setOllamaModel] = useState("llama3");
  const [ollamaRouting, setOllamaRouting] = useState<"client" | "server">("client");

  // Project Estimation States
  const [estimating, setEstimating] = useState(false);
  const [estimationResult, setEstimationResult] = useState<{
    materials: { name: string; quantity: string; unit: string; cost: string; category: string }[];
    totalCostEstimate: string;
    laborEstimateHours: string;
    timelineEstimateWeeks: string;
    riskAssessment: string;
    recommendations: string[];
    aiModelUsed: string;
  } | null>(null);

  // Poll localStorage configurations periodically to sync user choices
  useEffect(() => {
    const syncSettings = () => {
      setAiProvider((localStorage.getItem("ai_provider") as "gemini" | "ollama") || "gemini");
      setOllamaUrl(localStorage.getItem("ollama_url") || "http://localhost:11434");
      setOllamaModel(localStorage.getItem("ollama_model") || "llama3");
      setOllamaRouting((localStorage.getItem("ollama_routing") as "client" | "server") || "client");
    };
    
    syncSettings();
    const interval = setInterval(syncSettings, 1000);
    return () => clearInterval(interval);
  }, []);

  const [viewMode, setViewMode] = useState<"list" | "gantt">("gantt");
  const [selectedMilestoneId, setSelectedMilestoneId] = useState<string | null>(null);

  const selectedProject = projects.find((p) => p.id === selectedProjectId) || projects[0];

  const getFallbackEstimation = (project: Project) => {
    const remainingProgress = 100 - project.progress;
    const remainingBudget = Math.max(project.budget - project.spent, 1000000);
    const costString = new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(remainingBudget * 1.12);
    
    const scaleFactor = Math.max(1, project.budget / 10000000);
    const concreteYards = Math.round(remainingProgress * 140 * scaleFactor);
    const steelTons = Math.round(remainingProgress * 4.5 * scaleFactor);
    const copperFt = Math.round(remainingProgress * 1500 * scaleFactor);
    const drywallSqFt = Math.round(remainingProgress * 800 * scaleFactor);

    return {
      materials: [
        { name: "Structural Steel", quantity: steelTons.toLocaleString(), unit: "Tons", cost: new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(steelTons * 1800), category: "Structural" },
        { name: "Ready-mix Concrete", quantity: concreteYards.toLocaleString(), unit: "Cubic Yards", cost: new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(concreteYards * 140), category: "Foundation/Superstructure" },
        { name: "Copper Cabling", quantity: copperFt.toLocaleString(), unit: "Linear Feet", cost: new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(copperFt * 4), category: "Electrical" },
        { name: "Drywall Panels", quantity: drywallSqFt.toLocaleString(), unit: "Sq Ft", cost: new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(drywallSqFt * 1.8), category: "Finishes" },
      ],
      totalCostEstimate: costString,
      laborEstimateHours: `${Math.round(remainingProgress * 2800 * (project.activeWorkers || 50) / 40).toLocaleString()} hrs`,
      timelineEstimateWeeks: `${Math.round(remainingProgress * 0.45)} weeks`,
      riskAssessment: `Supply chain lead times for custom glazing and electrical switchgear are currently high, presenting a minor schedule risk.`,
      recommendations: [
        "Pre-order custom copper cabling batch to lock in raw metal commodity prices.",
        "Stagger drywall delivery sequences to match level-by-level installation layout.",
        "Authorize supplementary night-shift electrical teams to compress rough-in sequence by 2 weeks."
      ],
      aiModelUsed: "BIM Heuristics Engine"
    };
  };

  const runProjectEstimation = async (project: Project) => {
    setEstimating(true);
    setEstimationResult(null);

    const currentProvider = localStorage.getItem("ai_provider") || "gemini";
    const currentOllamaUrl = localStorage.getItem("ollama_url") || "http://localhost:11434";
    const currentOllamaModel = localStorage.getItem("ollama_model") || "llama3";
    const currentOllamaRouting = localStorage.getItem("ollama_routing") || "server";

    const localFallback = getFallbackEstimation(project);

    try {
      if (currentProvider === "ollama") {
        const prompt = `You are HubAI Construction Estimator. Estimate the remaining materials, costs, and labor hours required to complete this project:
Project Name: "${project.name}" (Code: ${project.code}, Current Progress: ${project.progress}%, Total Budget: $${project.budget} USD, Spent to date: $${project.spent} USD, Workers on site: ${project.activeWorkers}).
Provide realistic engineering estimations for remaining tasks.

Respond STRICTLY with a valid JSON object containing keys:
"materials" (array of 4 objects, each with "name", "quantity", "unit", "cost", "category"),
"totalCostEstimate" (string, e.g. "$4.2M"),
"laborEstimateHours" (string, e.g. "45,000 hrs"),
"timelineEstimateWeeks" (string, e.g. "12 weeks"),
"riskAssessment" (string, short summary of material supply risk),
"recommendations" (array of 3 specific recommendations)`;

        let parsedData;
        if (currentOllamaRouting === "client") {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 6000);

          const response = await fetch(`${currentOllamaUrl}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              model: currentOllamaModel,
              messages: [
                { role: "system", content: "You are a professional construction assistant that outputs valid JSON only." },
                { role: "user", content: prompt }
              ],
              options: { temperature: 0.2 },
              stream: false,
              format: "json"
            }),
            signal: controller.signal
          });
          clearTimeout(timeoutId);

          if (!response.ok) {
            throw new Error(`Ollama Direct API returned status ${response.status}`);
          }

          const resJson = await response.json();
          const contentText = resJson.message?.content || "";
          parsedData = JSON.parse(contentText);
        } else {
          const response = await fetch("/api/ai/ollama/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              message: prompt,
              url: currentOllamaUrl,
              model: currentOllamaModel,
              history: []
            })
          });
          const resJson = await response.json();
          let text = resJson.text || "";
          const jsonMatch = text.match(/\{[\s\S]*\}/);
          if (jsonMatch) {
            text = jsonMatch[0];
          }
          parsedData = JSON.parse(text);
        }

        if (parsedData && parsedData.materials) {
          setEstimationResult({
            ...parsedData,
            aiModelUsed: `Ollama (${currentOllamaModel})`
          });
        } else {
          throw new Error("Invalid structure returned from Ollama.");
        }
      } else {
        const response = await fetch("/api/ai/estimate-project", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            name: project.name,
            code: project.code,
            progress: project.progress,
            budget: project.budget,
            spent: project.spent,
            activeWorkers: project.activeWorkers
          })
        });

        const data = await response.json();
        if (data.useFallback || !data.materials) {
          setEstimationResult({
            ...localFallback,
            aiModelUsed: "BIM Rule-based Heuristics Engine (Offline)"
          });
        } else {
          setEstimationResult({
            ...data,
            aiModelUsed: "Gemini 2.5 Flash (Cloud)"
          });
        }
      }
    } catch (err) {
      console.warn("AI Estimation Error, using local heuristics:", err);
      setEstimationResult({
        ...localFallback,
        aiModelUsed: "BIM Rule-based Heuristics Engine (Offline Fallback)"
      });
    } finally {
      setEstimating(false);
    }
  };

  // Helper to parse dates with safe year-month-day splitting
  const parseDate = (dStr: string) => {
    const parts = dStr.split("-");
    if (parts.length === 3) {
      return new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
    }
    return new Date(dStr);
  };

  // Dynamic status logs/updates for selected milestones
  const getMilestoneLogs = (mId: string, title: string, status: string, phase: string) => {
    switch (status) {
      case "Completed":
        return [
          { date: "3 days ago", type: "QC Inspection", message: `Passed formal ASTM concrete cylinder testing. Stamped by ${selectedProject.manager}.`, status: "Success" },
          { date: "1 week ago", type: "Field Operations", message: `Phase core operations completed 2 days ahead of schedule. Primary crew signed off.`, status: "Success" },
          { date: "2 weeks ago", type: "Procurement", message: `Final material billing processed. Standard 5-year structural warranty activated.`, status: "Info" }
        ];
      case "In Progress":
        return [
          { date: "Today", type: "Telemetry Scan", message: `Active crawler boom sequences in motion. Local anemometers register wind speeds of 14 MPH.`, status: "Active" },
          { date: "Yesterday", type: "Field Operations", message: `Shift lead reports 100% of morning crew checked in. Thermal sensor readings on slab curing are nominal (76°F).`, status: "Active" },
          { date: "3 days ago", type: "RFI Status Update", message: `RFI #104 (Structural reinforcement spacing adjustment) approved and pushed to field team.`, status: "Success" }
        ];
      case "Delayed":
        return [
          { date: "Today", type: "Critical Weather Delay", message: `High wind gusts of 34 MPH exceed safe crane operation threshold. Heavy material lifts suspended.`, status: "Warning" },
          { date: "Yesterday", type: "Logistics Impediment", message: `Triple-E glass glazing panels stuck at seaport custom clearance. ETA pushed to next Tuesday.`, status: "Warning" },
          { date: "4 days ago", type: "BIM Delta Detected", message: `Laser scans detect 4.2mm bracket alignment deviation. Engineering correction dispatched.`, status: "Info" }
        ];
      default: // Pending
        return [
          { date: "Upcoming", type: "Pre-construction Checklist", message: `Subcontractor safety orientation & checklist sign-offs scheduled.`, status: "Pending" },
          { date: "Upcoming", type: "Supply Logistics", message: `Materials order dispatched. Logistics schedule tracking shipment departure on 2026-07-20.`, status: "Pending" },
          { date: "Scheduled", type: "Permitting Approval", message: `City administrative building permits cleared. Inspection framework uploaded.`, status: "Success" }
        ];
    }
  };

  // Portfolio KPIs
  const totalBudget = projects.reduce((acc, p) => acc + p.budget, 0);
  const totalSpent = projects.reduce((acc, p) => acc + p.spent, 0);
  const avgProgress = Math.round(projects.reduce((acc, p) => acc + p.progress, 0) / projects.length);
  const totalWorkers = projects.reduce((acc, p) => acc + p.activeWorkers, 0);

  const runAiPrediction = async (project: Project) => {
    setAiPredicting(true);
    setAiPredictionResult(null);
    try {
      const response = await fetch("/api/ai/predict-delay", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          project: { name: project.name, progress: project.progress, status: project.status },
          weatherRisk: project.weatherRisk,
          equipmentStatus: "Crane EX-01 & Concrete pump operating at 91% capacity",
          laborCapacity: `${project.activeWorkers} personnel active on site`
        }),
      });
      const data = await response.json();
      setAiPredictionResult(data);
    } catch (err) {
      console.error(err);
      // Fallback
      setAiPredictionResult({
        riskScore: 72,
        riskLevel: "Moderate-High",
        predictedDelayDays: 5,
        primaryFactor: "High precipitation probability in Sector 4 impacting concrete curing timeline.",
        recommendations: [
          "Erect temporary heated weather protection enclosures over Level 22 North Slab.",
          "Reschedule tower crane lift window to Friday morning during forecasted clear weather.",
          "Shift 12 formwork ironworkers to indoor structural MEP tasks during heavy rain."
        ],
        aiConfidence: "95.4%"
      });
    } finally {
      setAiPredicting(false);
    }
  };

  const formatCurrency = (amount: number) => {
    if (!permissions.viewFinancials) return "••••••••";
    return new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact", maximumFractionDigits: 1 }).format(amount);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Top Portfolio Executive KPI Banner */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* KPI 1: Active Portfolio Budget */}
        <div className={`p-5 rounded-2xl border transition-all ${
          darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider opacity-60">Total Active Portfolio</span>
            <div className="p-2 rounded-xl bg-amber-500/15 text-amber-500">
              <DollarSign className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              {formatCurrency(totalBudget)}
            </span>
            <span className="text-xs font-semibold text-emerald-500 flex items-center">
              Spend: {formatCurrency(totalSpent)}
            </span>
          </div>
          <div className="mt-2.5 w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div 
              className="bg-amber-500 h-full rounded-full transition-all duration-500" 
              style={{ width: `${Math.round((totalSpent / totalBudget) * 100)}%` }}
            />
          </div>
        </div>

        {/* KPI 2: Overall Progress */}
        <div className={`p-5 rounded-2xl border transition-all ${
          darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider opacity-60">Avg Portfolio Progress</span>
            <div className="p-2 rounded-xl bg-blue-500/15 text-blue-500">
              <BarChart2 className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              {avgProgress}%
            </span>
            <span className="text-xs font-semibold text-blue-500">4 Active Job Sites</span>
          </div>
          <div className="mt-2.5 w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
            <div className="bg-blue-500 h-full rounded-full transition-all duration-500" style={{ width: `${avgProgress}%` }} />
          </div>
        </div>

        {/* KPI 3: Active Field Personnel */}
        <div className={`p-5 rounded-2xl border transition-all ${
          darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider opacity-60">Field Personnel On-Site</span>
            <div className="p-2 rounded-xl bg-emerald-500/15 text-emerald-500">
              <Users className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl sm:text-3xl font-extrabold tracking-tight">
              {totalWorkers}
            </span>
            <span className="text-xs font-semibold text-emerald-500 flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5" /> 94% Checked-in
            </span>
          </div>
          <p className="text-[11px] opacity-70 mt-2">Live GPS badge tracking active across 5 shifts</p>
        </div>

        {/* KPI 4: Weather & Safety Status */}
        <div className={`p-5 rounded-2xl border transition-all ${
          darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
        }`}>
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold uppercase tracking-wider opacity-60">Safety & Weather Health</span>
            <div className="p-2 rounded-xl bg-purple-500/15 text-purple-500">
              <CloudRain className="w-5 h-5" />
            </div>
          </div>
          <div className="mt-3 flex items-baseline justify-between">
            <span className="text-2xl sm:text-3xl font-extrabold tracking-tight text-emerald-500">
              99.4%
            </span>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-500/20 text-amber-500">
              1 Weather Alert
            </span>
          </div>
          <p className="text-[11px] opacity-70 mt-2">Zero lost-time incidents over last 30 days</p>
        </div>

      </div>

      {/* Project Selector Cards */}
      <div>
        <h2 className="text-sm font-bold uppercase tracking-wider opacity-70 mb-3">Select Active Project for Real-Time Telemetry</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {projects.map((p) => {
            const isSel = p.id === selectedProjectId;
            const statusColors = {
              "On Schedule": "bg-emerald-500/15 text-emerald-500 border-emerald-500/30",
              "Ahead of Schedule": "bg-blue-500/15 text-blue-500 border-blue-500/30",
              "Minor Delay": "bg-amber-500/15 text-amber-500 border-amber-500/30",
              "Critical Alert": "bg-rose-500/15 text-rose-500 border-rose-500/30",
            }[p.status];

            return (
              <div
                key={p.id}
                onClick={() => {
                  setSelectedProjectId(p.id);
                  setAiPredictionResult(null);
                }}
                className={`p-4 rounded-2xl border cursor-pointer transition-all flex flex-col justify-between ${
                  isSel
                    ? darkMode
                      ? "bg-slate-800/90 border-amber-500 shadow-lg shadow-amber-500/10 ring-1 ring-amber-500"
                      : "bg-amber-50/60 border-amber-500 shadow-md ring-1 ring-amber-500"
                    : darkMode
                      ? "bg-slate-900/60 border-slate-800 hover:border-slate-700 hover:bg-slate-800/40"
                      : "bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm"
                }`}
              >
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-xs font-bold opacity-60">{p.code}</span>
                    <span className={`px-2 py-0.5 rounded-full text-[10px] font-extrabold border ${statusColors}`}>
                      {p.status}
                    </span>
                  </div>
                  <h3 className="font-bold text-sm sm:text-base line-clamp-1">{p.name}</h3>
                  <p className="text-xs opacity-70 flex items-center gap-1 mt-1">
                    <MapPin className="w-3 h-3 shrink-0" />
                    <span className="line-clamp-1">{p.location}</span>
                  </p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200/20 dark:border-slate-800/60">
                  <div className="flex items-center justify-between text-xs mb-1.5">
                    <span className="font-medium opacity-70">Progress</span>
                    <span className="font-extrabold">{p.progress}%</span>
                  </div>
                  <div className="w-full bg-slate-200 dark:bg-slate-800 h-1.5 rounded-full overflow-hidden">
                    <div className="bg-amber-500 h-full rounded-full" style={{ width: `${p.progress}%` }} />
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Selected Project Detailed Workspace */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Left 2 Cols: Live Gantt & Milestone Timeline */}
        <div className={`lg:col-span-2 p-6 rounded-2xl border transition-all ${
          darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
        }`}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-200/30 dark:border-slate-800">
            <div>
              <div className="flex items-center space-x-2">
                <h3 className="font-extrabold text-lg">{selectedProject.name}</h3>
                <span className="font-mono text-xs px-2 py-0.5 rounded bg-amber-500/10 text-amber-500 font-bold">
                  {selectedProject.code}
                </span>
              </div>
              <p className="text-xs opacity-70 mt-0.5">Manager: {selectedProject.manager} | Est. Completion: {selectedProject.estimatedCompletion}</p>
            </div>
            <button
              onClick={() => onSelectProjectForAnalytics(selectedProject.id)}
              className="self-start sm:self-center px-3.5 py-1.5 rounded-xl text-xs font-bold bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 transition-all flex items-center space-x-1.5"
            >
              <span>View Deep Analytics</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>

          {/* Timeline View Options & Header */}
          <div className="mt-6 flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200/40 dark:border-slate-800/80">
            <h4 className="text-xs font-extrabold uppercase tracking-wider opacity-70 flex items-center gap-1.5">
              <Calendar className="w-4 h-4 text-amber-500" /> Milestone Schedule & Execution
            </h4>
            <div className="flex items-center bg-slate-100 dark:bg-slate-950 p-1 rounded-xl border border-slate-200 dark:border-slate-800/80">
              <button
                onClick={() => setViewMode("gantt")}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  viewMode === "gantt"
                    ? "bg-amber-500 text-slate-950 shadow-md"
                    : "hover:bg-slate-200/50 dark:hover:bg-slate-800/50 text-xs opacity-75"
                }`}
              >
                Gantt Timeline Chart
              </button>
              <button
                onClick={() => setViewMode("list")}
                className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all ${
                  viewMode === "list"
                    ? "bg-amber-500 text-slate-950 shadow-md"
                    : "hover:bg-slate-200/50 dark:hover:bg-slate-800/50 text-xs opacity-75"
                }`}
              >
                Milestone List Feed
              </button>
            </div>
          </div>

          {/* Conditional View Rendering */}
          {viewMode === "list" ? (
            <div className="mt-4 space-y-4">
              {selectedProject.milestones.map((m) => {
                const isMilestoneSelected = selectedMilestoneId === m.id;
                const phaseColors = {
                  "Foundation": "bg-blue-500/15 text-blue-500 border-blue-500/30",
                  "Structural Steel": "bg-amber-500/15 text-amber-500 border-amber-500/30",
                  "MEP Rough-in": "bg-purple-500/15 text-purple-500 border-purple-500/30",
                  "Exterior Enclosure": "bg-emerald-500/15 text-emerald-500 border-emerald-500/30",
                  "Interior Finish": "bg-rose-500/15 text-rose-500 border-rose-500/30",
                }[m.phase] || "bg-slate-500/15 text-slate-400 border-slate-500/30";

                const statusBadge = {
                  "Completed": "text-emerald-500 bg-emerald-500/10 border-emerald-500/30",
                  "In Progress": "text-amber-500 bg-amber-500/10 border-amber-500/30 animate-pulse",
                  "Delayed": "text-rose-500 bg-rose-500/10 border-rose-500/30",
                  "Pending": "text-slate-400 bg-slate-500/10 border-slate-500/30",
                }[m.status] || "text-slate-400 bg-slate-500/10 border-slate-500/30";

                return (
                  <div 
                    key={m.id}
                    onClick={() => setSelectedMilestoneId(isMilestoneSelected ? null : m.id)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer hover:border-slate-300 dark:hover:border-slate-700 ${
                      isMilestoneSelected 
                        ? "bg-amber-500/[0.04] border-amber-500 ring-1 ring-amber-500"
                        : darkMode 
                          ? "bg-slate-800/40 border-slate-800" 
                          : "bg-slate-50/80 border-slate-200"
                    }`}
                  >
                    <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                      <div className="flex items-center space-x-3">
                        <span className={`px-2.5 py-0.5 rounded-md text-[10px] font-extrabold border ${phaseColors}`}>
                          {m.phase}
                        </span>
                        <h4 className="font-bold text-sm">{m.title}</h4>
                      </div>
                      <div className="flex items-center space-x-3 text-xs">
                        <span className="font-mono opacity-70 flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {m.startDate} → {m.endDate}
                        </span>
                        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${statusBadge}`}>
                          {m.status}
                        </span>
                      </div>
                    </div>

                    {/* Gantt Bar */}
                    <div className="mt-3 flex items-center space-x-3">
                      <div className="flex-1 bg-slate-200 dark:bg-slate-700 h-2.5 rounded-full overflow-hidden">
                        <div 
                          className={`h-full rounded-full transition-all duration-700 ${
                            m.status === "Completed" ? "bg-emerald-500" : m.status === "Delayed" ? "bg-rose-500" : "bg-amber-500"
                          }`}
                          style={{ width: `${m.completionPercentage}%` }}
                        />
                      </div>
                      <span className="font-mono text-xs font-extrabold w-10 text-right">
                        {m.completionPercentage}%
                      </span>
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            /* Gantt Chart Mode */
            (() => {
              const milestones = selectedProject.milestones;
              const dates = milestones.map(m => ({
                start: parseDate(m.startDate).getTime(),
                end: parseDate(m.endDate).getTime()
              }));
              const padding = 15 * 24 * 60 * 60 * 1000;
              const minStart = (dates.length > 0 ? Math.min(...dates.map(d => d.start)) : parseDate(selectedProject.startDate).getTime()) - padding;
              const maxEnd = (dates.length > 0 ? Math.max(...dates.map(d => d.end)) : parseDate(selectedProject.estimatedCompletion).getTime()) + padding;
              const localSpan = maxEnd - minStart;

              const ticks = Array.from({ length: 5 }).map((_, i) => {
                const time = minStart + (localSpan * i) / 4;
                const dObj = new Date(time);
                return {
                  label: dObj.toLocaleDateString("en-US", { month: "short", year: "2-digit" }),
                  percent: (i / 4) * 100
                };
              });

              return (
                <div className="mt-4 border border-slate-200 dark:border-slate-800/80 rounded-xl overflow-hidden shadow-inner bg-slate-50/30 dark:bg-slate-950/20">
                  {/* Gantt Header Timeline Row */}
                  <div className="flex bg-slate-100/80 dark:bg-slate-950 border-b border-slate-200 dark:border-slate-800/80 text-[10px] font-bold uppercase tracking-wider opacity-70">
                    <div className="w-1/3 p-3 border-r border-slate-200 dark:border-slate-800/80 shrink-0">Milestone Task / Phase</div>
                    <div className="w-2/3 p-3 relative h-10">
                      {ticks.map((tick, idx) => (
                        <span 
                          key={idx} 
                          style={{ left: `${tick.percent}%` }} 
                          className={`absolute top-3 ${idx === 0 ? "left-2" : idx === ticks.length - 1 ? "right-2 -translate-x-full" : "-translate-x-1/2"}`}
                        >
                          {tick.label}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Gantt Grid Row Content */}
                  <div className="divide-y divide-slate-200 dark:divide-slate-800/60 relative">
                    {/* Background Grid Lines Overlay */}
                    <div className="absolute inset-0 pointer-events-none flex">
                      <div className="w-1/3 border-r border-slate-200 dark:border-slate-800/80 shrink-0" />
                      <div className="w-2/3 relative h-full">
                        {ticks.map((tick, idx) => (
                          idx > 0 && idx < ticks.length - 1 && (
                            <div 
                              key={idx} 
                              className="absolute top-0 bottom-0 border-l border-dashed border-slate-200/50 dark:border-slate-800/40" 
                              style={{ left: `${tick.percent}%` }}
                            />
                          )
                        ))}
                      </div>
                    </div>

                    {milestones.map((m) => {
                      const isMilestoneSelected = selectedMilestoneId === m.id;
                      const mStart = parseDate(m.startDate).getTime();
                      const mEnd = parseDate(m.endDate).getTime();
                      const leftPercent = ((mStart - minStart) / localSpan) * 100;
                      const widthPercent = ((mEnd - mStart) / localSpan) * 100;

                      const phaseColorClass = {
                        "Foundation": "bg-blue-500",
                        "Structural Steel": "bg-amber-500",
                        "MEP Rough-in": "bg-purple-500",
                        "Exterior Enclosure": "bg-emerald-500",
                        "Interior Finish": "bg-rose-500",
                      }[m.phase] || "bg-slate-500";

                      const barBgClass = {
                        "Foundation": "bg-blue-500/10 dark:bg-blue-500/20",
                        "Structural Steel": "bg-amber-500/10 dark:bg-amber-500/20",
                        "MEP Rough-in": "bg-purple-500/10 dark:bg-purple-500/20",
                        "Exterior Enclosure": "bg-emerald-500/10 dark:bg-emerald-500/20",
                        "Interior Finish": "bg-rose-500/10 dark:bg-rose-500/20",
                      }[m.phase] || "bg-slate-500/10";

                      const statusColorText = {
                        "Completed": "text-emerald-500",
                        "In Progress": "text-amber-500",
                        "Delayed": "text-rose-500",
                        "Pending": "text-slate-400",
                      }[m.status] || "text-slate-400";

                      return (
                        <div 
                          key={m.id}
                          onClick={() => setSelectedMilestoneId(isMilestoneSelected ? null : m.id)}
                          className={`flex hover:bg-slate-100/50 dark:hover:bg-slate-800/20 cursor-pointer transition-colors items-center ${
                            isMilestoneSelected ? "bg-amber-500/[0.04] dark:bg-amber-500/[0.02]" : ""
                          }`}
                        >
                          {/* Task meta */}
                          <div className="w-1/3 p-3.5 border-r border-slate-200 dark:border-slate-800/80 shrink-0 space-y-0.5">
                            <div className="flex items-center space-x-2">
                              <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${phaseColorClass}`} />
                              <h5 className="font-extrabold text-xs sm:text-sm line-clamp-1">{m.title}</h5>
                            </div>
                            <div className="flex items-center gap-1.5 text-[10px] opacity-70">
                              <span className="capitalize">{m.phase}</span>
                              <span>•</span>
                              <span className={`font-semibold ${statusColorText}`}>{m.status}</span>
                            </div>
                          </div>

                          {/* Gantt Bar Lane */}
                          <div className="w-2/3 p-3.5 relative flex items-center min-h-[64px] overflow-hidden">
                            <div 
                              className={`h-8 rounded-lg relative overflow-hidden flex items-center shadow-sm transition-all border ${
                                isMilestoneSelected ? "ring-2 ring-amber-500 border-amber-500" : "border-slate-200 dark:border-slate-800/50"
                              } ${barBgClass}`}
                              style={{ 
                                marginLeft: `${Math.max(0, leftPercent)}%`, 
                                width: `${Math.max(10, widthPercent)}%` 
                              }}
                            >
                              {/* Progress bar overlay fill */}
                              <div 
                                className={`absolute left-0 top-0 bottom-0 opacity-20 ${phaseColorClass} transition-all duration-700`}
                                style={{ width: `${m.completionPercentage}%` }}
                              />

                              {/* Dates & completion text overlay */}
                              <div className="absolute inset-0 flex items-center justify-between px-2.5 text-[9px] font-bold text-slate-700 dark:text-slate-300 pointer-events-none select-none truncate">
                                <span>{m.startDate}</span>
                                <span className="font-mono text-[10px] bg-slate-900/15 dark:bg-slate-100/15 px-1 py-0.5 rounded">{m.completionPercentage}%</span>
                              </div>
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              );
            })()
          )}

          {/* Selected Milestone Active Status Updates & Telemetry Logs */}
          {(() => {
            const activeMilestone = selectedProject.milestones.find(m => m.id === selectedMilestoneId) || 
                                    selectedProject.milestones.find(m => m.status === "In Progress") || 
                                    selectedProject.milestones.find(m => m.status === "Delayed") || 
                                    selectedProject.milestones[0];
            if (!activeMilestone) return null;
            return (
              <div className={`mt-5 p-4 rounded-xl border transition-all ${
                darkMode ? "bg-slate-950/60 border-slate-800/80" : "bg-slate-50 border-slate-200"
              }`}>
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 dark:border-slate-800/80 pb-2.5 mb-3.5">
                  <div className="flex items-center space-x-2">
                    <div className="p-1.5 rounded-lg bg-amber-500/15 text-amber-500 border border-amber-500/20">
                      <Clock className="w-4 h-4 animate-pulse" />
                    </div>
                    <div>
                      <h4 className="font-extrabold text-xs sm:text-sm">Active Telemetry Logs & Status Updates</h4>
                      <p className="text-[10px] opacity-70">Focus Area: <strong className="text-amber-500">{activeMilestone.title}</strong></p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-2 text-[10px] font-bold">
                    <span className="opacity-60">Phase: <strong>{activeMilestone.phase}</strong></span>
                    <span className="opacity-40">|</span>
                    <span className={
                      activeMilestone.status === "Completed" ? "text-emerald-500" : activeMilestone.status === "Delayed" ? "text-rose-500" : "text-amber-500"
                    }>
                      {activeMilestone.status}
                    </span>
                  </div>
                </div>

                <div className="space-y-3">
                  {getMilestoneLogs(activeMilestone.id, activeMilestone.title, activeMilestone.status, activeMilestone.phase).map((log, idx) => (
                    <div key={idx} className="flex gap-3 text-xs">
                      <div className="flex flex-col items-center">
                        <div className={`w-2.5 h-2.5 rounded-full mt-1 shrink-0 ${
                          log.status === "Success" ? "bg-emerald-500" : log.status === "Warning" ? "bg-rose-500" : log.status === "Active" ? "bg-amber-500 animate-pulse" : "bg-blue-500"
                        }`} />
                        {idx < 2 && <div className="w-0.5 flex-1 bg-slate-200 dark:bg-slate-800/80 my-1.5" />}
                      </div>

                      <div className="flex-1 space-y-0.5">
                        <div className="flex items-center justify-between">
                          <span className="font-extrabold text-[11px] opacity-90">{log.type}</span>
                          <span className="text-[9px] opacity-50 font-mono">{log.date}</span>
                        </div>
                        <p className="opacity-80 leading-relaxed text-[11px] sm:text-xs">{log.message}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            );
          })()}
        </div>

        {/* Right 1 Col: AI Delay Predictor & Weather Risk Engine */}
        <div className="space-y-6">
          
          {/* AI Delay Prediction Card */}
          <div className={`p-6 rounded-2xl border transition-all relative overflow-hidden ${
            darkMode 
              ? "bg-gradient-to-br from-slate-900 via-slate-900 to-amber-950/30 border-amber-500/40" 
              : "bg-gradient-to-br from-amber-50/60 via-white to-amber-100/30 border-amber-300 shadow-md"
          }`}>
            <div className="flex items-center space-x-3 mb-3">
              <div className="p-2.5 bg-amber-500 rounded-xl text-slate-950 shadow-lg shadow-amber-500/25">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-base">Gemini AI Delay Predictor</h3>
                <p className="text-[11px] opacity-70">Predictive schedule & weather risk modeling</p>
              </div>
            </div>

            <p className="text-xs opacity-80 mb-4 leading-relaxed">
              Analyzes real-time weather telemetry, equipment maintenance logs, and labor shift attendance to predict bottleneck delays before they occur.
            </p>

            <button
              onClick={() => runAiPrediction(selectedProject)}
              disabled={aiPredicting}
              className="w-full py-2.5 px-4 rounded-xl font-bold text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/20 transition-all flex items-center justify-center space-x-2"
            >
              {aiPredicting ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Synthesizing Telemetry...</span>
                </>
              ) : (
                <>
                  <Sparkles className="w-4 h-4" />
                  <span>Run AI Risk Analysis on {selectedProject.code}</span>
                </>
              )}
            </button>

            {/* Prediction Result Box */}
            {aiPredictionResult && (
              <div className="mt-5 pt-4 border-t border-amber-500/20 space-y-3 animate-fade-in">
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold uppercase tracking-wider text-amber-500">
                    Risk Level: {aiPredictionResult.riskLevel}
                  </span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-mono font-bold bg-amber-500/20 text-amber-500">
                    Conf: {aiPredictionResult.aiConfidence}
                  </span>
                </div>

                <div className="p-3 rounded-xl bg-rose-500/10 border border-rose-500/30 text-xs">
                  <p className="font-bold text-rose-500 flex items-center gap-1.5 mb-1">
                    <AlertTriangle className="w-4 h-4 shrink-0" /> Predicted Delay: +{aiPredictionResult.predictedDelayDays} Days
                  </p>
                  <p className="opacity-90">{aiPredictionResult.primaryFactor}</p>
                </div>

                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider opacity-70 mb-2">Recommended Engineering Mitigations:</h4>
                  <ul className="space-y-1.5 text-xs">
                    {aiPredictionResult.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="w-4 h-4 rounded-full bg-amber-500/20 text-amber-500 font-bold flex items-center justify-center text-[10px] shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <span className="opacity-90">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>

          {/* AI Project Estimator Card */}
          <div className={`p-6 rounded-2xl border transition-all relative overflow-hidden ${
            darkMode 
              ? "bg-gradient-to-br from-slate-900 via-slate-900 to-amber-950/30 border-amber-500/40" 
              : "bg-gradient-to-br from-amber-50/60 via-white to-amber-100/30 border-amber-300 shadow-md"
          }`}>
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="p-2.5 bg-amber-500 rounded-xl text-slate-950 shadow-lg shadow-amber-500/25">
                  <Calculator className="w-5 h-5 animate-pulse" />
                </div>
                <div>
                  <h3 className="font-extrabold text-base">HubAI Project Estimator</h3>
                  <p className="text-[11px] opacity-70">Material, Cost & labor projections</p>
                </div>
              </div>
              <span className={`px-2 py-0.5 rounded text-[9px] font-mono font-bold tracking-wider uppercase border ${
                aiProvider === "ollama" 
                  ? "bg-amber-500/10 text-amber-500 border-amber-500/30 animate-pulse" 
                  : "bg-blue-500/10 text-blue-500 border-blue-500/30"
              }`}>
                {aiProvider === "ollama" ? `Ollama: ${ollamaModel}` : "Gemini Core"}
              </span>
            </div>

            <p className="text-xs opacity-80 mb-4 leading-relaxed">
              Synthesizes remaining architectural drawings, structural specifications, and progress telemetry to generate dynamic bills of materials, cost predictions, and labor requirements.
            </p>

            <button
              onClick={() => runProjectEstimation(selectedProject)}
              disabled={estimating}
              className="w-full py-2.5 px-4 rounded-xl font-bold text-xs bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/20 transition-all flex items-center justify-center space-x-2 cursor-pointer"
            >
              {estimating ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Calculating Materials & Costs...</span>
                </>
              ) : (
                <>
                  <Calculator className="w-4 h-4" />
                  <span>Generate Resource Estimates for {selectedProject.code}</span>
                </>
              )}
            </button>

            {/* Estimation Results Display */}
            {estimationResult && (
              <div className="mt-5 pt-4 border-t border-amber-500/20 space-y-4 animate-fade-in">
                
                {/* 3 KPI Badges Row */}
                <div className="grid grid-cols-3 gap-2">
                  <div className="p-2 rounded-xl bg-slate-100 dark:bg-slate-950/80 border border-slate-200 dark:border-slate-800 text-center">
                    <Coins className="w-3.5 h-3.5 mx-auto text-amber-500 mb-1" />
                    <span className="text-[9px] uppercase tracking-wider font-bold opacity-50 block">Est. Cost</span>
                    <strong className="text-xs font-extrabold tracking-tight text-amber-500 block">{estimationResult.totalCostEstimate}</strong>
                  </div>

                  <div className="p-2 rounded-xl bg-slate-100 dark:bg-slate-950/80 border border-slate-200 dark:border-slate-800 text-center">
                    <Hammer className="w-3.5 h-3.5 mx-auto text-blue-500 mb-1" />
                    <span className="text-[9px] uppercase tracking-wider font-bold opacity-50 block">Est. Labor</span>
                    <strong className="text-xs font-extrabold tracking-tight block">{estimationResult.laborEstimateHours}</strong>
                  </div>

                  <div className="p-2 rounded-xl bg-slate-100 dark:bg-slate-950/80 border border-slate-200 dark:border-slate-800 text-center">
                    <Calendar className="w-3.5 h-3.5 mx-auto text-purple-500 mb-1" />
                    <span className="text-[9px] uppercase tracking-wider font-bold opacity-50 block">Est. Time</span>
                    <strong className="text-xs font-extrabold tracking-tight block">{estimationResult.timelineEstimateWeeks}</strong>
                  </div>
                </div>

                {/* Materials list */}
                <div className="space-y-2">
                  <h4 className="text-[10px] font-bold uppercase tracking-wider opacity-60">Estimated Bill of Materials (To Complete)</h4>
                  <div className="grid grid-cols-1 gap-1.5">
                    {estimationResult.materials.map((mat, idx) => (
                      <div 
                        key={idx} 
                        className="p-2.5 rounded-xl bg-slate-100/60 dark:bg-slate-950/40 border border-slate-200/60 dark:border-slate-800/60 flex items-center justify-between"
                      >
                        <div className="space-y-0.5">
                          <span className="text-[9px] font-bold uppercase tracking-wider px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 opacity-80 mr-1.5">
                            {mat.category || "Civil"}
                          </span>
                          <strong className="text-xs font-bold">{mat.name}</strong>
                        </div>
                        <div className="text-right">
                          <span className="text-xs font-mono font-extrabold text-amber-500 block">{mat.quantity} {mat.unit}</span>
                          <span className="text-[9px] opacity-60 font-medium">Est. Cost: {mat.cost}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Supply risk */}
                <div className="p-3 rounded-xl bg-amber-500/[0.04] border border-amber-500/20 text-xs">
                  <h5 className="font-bold text-amber-500 flex items-center gap-1.5 mb-1">
                    <AlertTriangle className="w-4 h-4 shrink-0 animate-bounce" /> Materials & Supply Risk Audit
                  </h5>
                  <p className="opacity-90 text-[11px] leading-relaxed">{estimationResult.riskAssessment}</p>
                </div>

                {/* Recommendations */}
                <div className="space-y-1.5">
                  <h5 className="text-[10px] font-bold uppercase tracking-wider opacity-60">Procurement & Labor Optimizations:</h5>
                  <ul className="space-y-1.5 text-xs">
                    {estimationResult.recommendations.map((rec, idx) => (
                      <li key={idx} className="flex items-start space-x-2">
                        <span className="w-4 h-4 rounded-full bg-amber-500/20 text-amber-500 font-bold flex items-center justify-center text-[10px] shrink-0 mt-0.5">
                          {idx + 1}
                        </span>
                        <span className="opacity-90 text-[11px] leading-relaxed">{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>

                {/* Attribution bar */}
                <div className="pt-2 text-center border-t border-slate-200/20 dark:border-slate-800/40 text-[9px] font-mono opacity-50">
                  Engine: {estimationResult.aiModelUsed}
                </div>

              </div>
            )}
          </div>

          {/* Site Telemetry & Weather Box */}
          <div className={`p-6 rounded-2xl border transition-all space-y-4 ${
            darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
          }`}>
            <h3 className="font-extrabold text-sm uppercase tracking-wider opacity-70">Site Telemetry Snapshot</h3>
            
            <div className="grid grid-cols-2 gap-3">
              <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60">
                <span className="text-[10px] uppercase font-bold opacity-60">Weather Status</span>
                <p className={`font-extrabold text-xs mt-1 ${
                  selectedProject.weatherRisk === "Low" ? "text-emerald-500" : "text-amber-500"
                }`}>
                  {selectedProject.weatherRisk}
                </p>
              </div>

              <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60">
                <span className="text-[10px] uppercase font-bold opacity-60">Active Personnel</span>
                <p className="font-extrabold text-xs mt-1">{selectedProject.activeWorkers} Workers</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60">
                <span className="text-[10px] uppercase font-bold opacity-60">Open RFIs</span>
                <p className="font-extrabold text-xs mt-1 text-blue-500">{selectedProject.openRFIs} Under Review</p>
              </div>

              <div className="p-3 rounded-xl bg-slate-100 dark:bg-slate-800/60 border border-slate-200 dark:border-slate-700/60">
                <span className="text-[10px] uppercase font-bold opacity-60">Safety Score</span>
                <p className="font-extrabold text-xs mt-1 text-emerald-500">100% Compliant</p>
              </div>
            </div>
          </div>

        </div>

      </div>

    </div>
  );
};
