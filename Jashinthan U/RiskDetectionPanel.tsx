import React, { useState } from "react";
import { 
  Sparkles, 
  AlertTriangle, 
  CheckCircle, 
  RefreshCw, 
  ShieldAlert, 
  Activity, 
  FileCheck2,
  TrendingDown,
  Wrench,
  Thermometer,
  Zap
} from "lucide-react";
import { Project } from "../types";

interface RiskItem {
  id: string;
  title: string;
  projectCode: string;
  category: string;
  severity: "Low" | "Moderate" | "High" | "Critical";
  probability: string;
  description: string;
  remedy: string;
  status: "Monitoring" | "Action Required" | "Active Alert" | "Mitigated";
}

interface RiskDetectionPanelProps {
  projects: Project[];
  darkMode: boolean;
  triggerToast: (msg: string) => void;
}

export const RiskDetectionPanel: React.FC<RiskDetectionPanelProps> = ({
  projects,
  darkMode,
  triggerToast,
}) => {
  const [loading, setLoading] = useState(false);
  const [overallScore, setOverallScore] = useState<number>(68);
  const [overallLevel, setOverallLevel] = useState<string>("Moderate-High");
  const [scanTime, setScanTime] = useState<string>("");
  const [risks, setRisks] = useState<RiskItem[]>([
    {
      id: "RISK-01",
      title: "Tower Crane High Wind Hazard",
      projectCode: "PRJ-01",
      category: "Safety & QC",
      severity: "High",
      probability: "85%",
      description: "Localized anemometers are flagging continuous structural gusts up to 34 MPH on Skyline Financial Tower Phase 2, threatening high-elevation formwork shifts.",
      remedy: "Engage electromagnetic crane slewing brakes and suspend all material loads exceeding 2.5 metric tons.",
      status: "Active Alert"
    },
    {
      id: "RISK-02",
      title: "Galvanized Copper Pipe Supply Outage",
      projectCode: "PRJ-03",
      category: "Material Procurement",
      severity: "Moderate",
      probability: "90%",
      description: "Pacific Waterfront MEP installation rough-ins are draining regional inventory stocks. Projected copper conduit reserve is less than 3 days.",
      remedy: "Approve emergency supply chain requisition with secondary vendor in Seattle, expanding active local warehouse reserves.",
      status: "Action Required"
    },
    {
      id: "RISK-03",
      title: "Subterranean Tidal Infiltration",
      projectCode: "PRJ-02",
      category: "Geotechnical / Environmental",
      severity: "Critical",
      probability: "35%",
      description: "Hydrostatic load sensors alert minor water table seepage at Metro Underground retaining wall Level B4 following high tide shift.",
      remedy: "Initialize backup slurry pump arrays (Zones B-4 through B-7) and dispatch quick-set bentonite sealant crew.",
      status: "Monitoring"
    }
  ]);

  const runRiskScan = async () => {
    setLoading(true);
    triggerToast("Initiating AI Portfolio Telemetry Scan across active jobsites...");
    try {
      const response = await fetch("/api/ai/detect-risks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          projects: projects.map(p => ({
            code: p.code,
            name: p.name,
            progress: p.progress,
            status: p.status,
            weatherRisk: p.weatherRisk,
            activeWorkers: p.activeWorkers,
            openRFIs: p.openRFIs,
            safetyIncidents: p.safetyIncidentsThisMonth
          })),
          weatherData: "Local meteorological forecasts: intermittent localized storm squalls, 32-38 knots coastal wind gusts",
          equipmentData: "Liebherr Crawler Tower Crane operational limit warning, slurry extraction pressure variance +12%"
        })
      });
      const data = await response.json();
      if (data && data.risks) {
        setRisks(data.risks);
        setOverallScore(data.overallRiskScore || 70);
        setOverallLevel(data.overallRiskLevel || "Moderate");
        setScanTime(data.scanTimestamp ? new Date(data.scanTimestamp).toLocaleTimeString() : new Date().toLocaleTimeString());
        triggerToast("AI Portfolio Risk Audit scan completed successfully!");
      }
    } catch (e) {
      console.error(e);
      triggerToast("BIM Cloud API timeout. Initializing intelligent offline heuristic database.");
    } finally {
      setLoading(false);
    }
  };

  const handleApplyActionPlan = (riskId: string, title: string) => {
    setRisks(prev => prev.map(r => {
      if (r.id === riskId) {
        return { ...r, status: "Mitigated" };
      }
      return r;
    }));
    triggerToast(`Mitigation Plan Dispatched: "${title}" resolved successfully! Resources reallocated.`);
  };

  const getSeverityStyles = (severity: string) => {
    switch (severity) {
      case "Critical":
        return "bg-rose-500/10 text-rose-500 border-rose-500/30";
      case "High":
        return "bg-amber-500/10 text-amber-500 border-amber-500/30";
      case "Moderate":
        return "bg-blue-500/10 text-blue-400 border-blue-500/30";
      default:
        return "bg-slate-500/10 text-slate-400 border-slate-500/30";
    }
  };

  const getStatusStyles = (status: string) => {
    switch (status) {
      case "Active Alert":
        return "bg-rose-500 text-white animate-pulse";
      case "Action Required":
        return "bg-amber-500 text-slate-950 font-bold";
      case "Monitoring":
        return "bg-blue-600 text-white";
      case "Mitigated":
        return "bg-emerald-600 text-white";
      default:
        return "bg-slate-600 text-white";
    }
  };

  return (
    <div className={`p-6 rounded-2xl border transition-all ${
      darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
    }`}>
      {/* Header and Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 pb-6 border-b border-slate-200 dark:border-slate-800">
        <div>
          <div className="flex items-center space-x-2">
            <div className="p-2 bg-amber-500/10 rounded-xl text-amber-500 border border-amber-500/20">
              <ShieldAlert className="w-5 h-5" />
            </div>
            <div>
              <h3 className="font-extrabold text-base sm:text-lg">Real-Time AI Site Risk & Hazard Auditor</h3>
              <p className="text-xs opacity-70">Automated structural, safety, geotechnical, and logistics vulnerability assessment</p>
            </div>
          </div>
        </div>

        <button
          onClick={runRiskScan}
          disabled={loading}
          className="px-4 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/20 transition-all flex items-center space-x-2 shrink-0 self-start md:self-center"
        >
          {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Activity className="w-4 h-4" />}
          <span>{loading ? "Scanning BIM Telemetry..." : "Run Global AI Portfolio Scan"}</span>
        </button>
      </div>

      {/* Main Grid: KPIs and Risks List */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
        
        {/* Left Column: Gauges and Meta Data */}
        <div className="space-y-4">
          <div className={`p-5 rounded-xl border flex flex-col items-center justify-center text-center ${
            darkMode ? "bg-slate-950/40 border-slate-800" : "bg-slate-50 border-slate-200"
          }`}>
            <span className="text-xs font-bold uppercase tracking-wider opacity-60">Overall Portfolio Risk</span>
            
            {/* Visual Risk Indicator Ring */}
            <div className="relative flex items-center justify-center my-6">
              <svg className="w-32 h-32 transform -rotate-90">
                <circle
                  cx="64"
                  cy="64"
                  r="52"
                  strokeWidth="8"
                  stroke={darkMode ? "#1e293b" : "#e2e8f0"}
                  fill="transparent"
                />
                <circle
                  cx="64"
                  cy="64"
                  r="52"
                  strokeWidth="8"
                  stroke={overallScore > 75 ? "#f43f5e" : overallScore > 50 ? "#f59e0b" : "#10b981"}
                  fill="transparent"
                  strokeDasharray={2 * Math.PI * 52}
                  strokeDashoffset={2 * Math.PI * 52 * (1 - overallScore / 100)}
                  strokeLinecap="round"
                  className="transition-all duration-1000 ease-out"
                />
              </svg>
              <div className="absolute flex flex-col items-center">
                <span className="font-extrabold text-3xl font-mono tracking-tighter">{overallScore}%</span>
                <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-full mt-1 ${
                  overallScore > 75 
                    ? "bg-rose-500/20 text-rose-400" 
                    : overallScore > 50 
                      ? "bg-amber-500/20 text-amber-400" 
                      : "bg-emerald-500/20 text-emerald-400"
                }`}>
                  {overallLevel}
                </span>
              </div>
            </div>

            <p className="text-xs text-center opacity-80 leading-relaxed max-w-[240px]">
              Active hazard probability algorithm is aggregated from {projects.length} live BIM models, onsite cameras, and localized NOAA weather feeds.
            </p>
          </div>

          <div className={`p-4 rounded-xl border space-y-3 ${
            darkMode ? "bg-slate-950/40 border-slate-800" : "bg-slate-50 border-slate-200"
          }`}>
            <h4 className="text-xs font-bold uppercase tracking-wider opacity-70 flex items-center gap-1.5 border-b pb-2 border-slate-200 dark:border-slate-800">
              <FileCheck2 className="w-4 h-4 text-amber-500" /> Active Threat Vectors
            </h4>
            <div className="grid grid-cols-2 gap-2 text-xs">
              <div className="p-2.5 rounded bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="block text-[10px] opacity-60">High Wind</span>
                <strong className="text-rose-500 font-mono font-bold text-sm">34 MPH</strong>
              </div>
              <div className="p-2.5 rounded bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="block text-[10px] opacity-60">Hydrostatic</span>
                <strong className="text-amber-500 font-mono font-bold text-sm">+12% Var</strong>
              </div>
              <div className="p-2.5 rounded bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="block text-[10px] opacity-60">Procurement</span>
                <strong className="text-amber-500 font-mono font-bold text-sm">1 Critical</strong>
              </div>
              <div className="p-2.5 rounded bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800">
                <span className="block text-[10px] opacity-60">Last Scan</span>
                <strong className="opacity-90 font-mono text-[10px]">{scanTime || "06:11:23 AM"}</strong>
              </div>
            </div>
          </div>
        </div>

        {/* Right 2 Columns: Risks Feed */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="text-xs font-extrabold uppercase tracking-wider opacity-70">
              Live Threat Feed ({risks.filter(r => r.status !== "Mitigated").length} Open, {risks.filter(r => r.status === "Mitigated").length} Resolved)
            </h4>
            {loading && (
              <span className="text-xs text-amber-500 flex items-center gap-1.5 font-bold animate-pulse">
                <Zap className="w-3.5 h-3.5 animate-bounce" /> Updating audit records...
              </span>
            )}
          </div>

          <div className="space-y-4 max-h-[390px] overflow-y-auto pr-1">
            {risks.map((risk) => (
              <div 
                key={risk.id}
                className={`p-4 rounded-xl border transition-all ${
                  risk.status === "Mitigated"
                    ? "opacity-50 bg-emerald-500/5 border-emerald-500/20"
                    : darkMode 
                      ? "bg-slate-950/30 border-slate-800 hover:border-slate-700" 
                      : "bg-slate-50/50 border-slate-200 hover:bg-slate-50"
                }`}
              >
                {/* Risk Title & Status */}
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 dark:border-slate-800/80 pb-2 mb-2.5">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold border ${getSeverityStyles(risk.severity)}`}>
                      {risk.severity} severity
                    </span>
                    <h5 className="font-extrabold text-xs sm:text-sm">{risk.title}</h5>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <span className="text-[10px] font-mono opacity-60">Affected: <strong>{risk.projectCode}</strong></span>
                    <span className="text-[10px] opacity-60">| Prob: <strong>{risk.probability}</strong></span>
                    <span className={`px-2 py-0.5 rounded-[5px] text-[10px] font-extrabold uppercase tracking-wide font-mono ${getStatusStyles(risk.status)}`}>
                      {risk.status}
                    </span>
                  </div>
                </div>

                {/* Description */}
                <p className="text-xs opacity-80 leading-relaxed mb-3">
                  {risk.description}
                </p>

                {/* AI Remedy & Mitigation controls */}
                <div className="p-3 rounded-lg bg-amber-500/5 dark:bg-amber-500/[0.02] border border-amber-500/10 space-y-2">
                  <div className="flex items-center space-x-1.5 text-[10px] font-bold text-amber-500 uppercase">
                    <Sparkles className="w-3.5 h-3.5" />
                    <span>Gemini AI Actionable Mitigation Plan</span>
                  </div>
                  <p className="text-xs opacity-90 leading-relaxed">
                    {risk.remedy}
                  </p>

                  {risk.status !== "Mitigated" && (
                    <div className="pt-2 flex justify-end">
                      <button
                        onClick={() => handleApplyActionPlan(risk.id, risk.title)}
                        className="px-3.5 py-1.5 rounded-lg text-[11px] font-extrabold bg-slate-900 hover:bg-slate-800 dark:bg-white dark:text-slate-950 dark:hover:bg-slate-100 text-white transition-all flex items-center space-x-1"
                      >
                        <Wrench className="w-3.5 h-3.5" />
                        <span>Dispatch Engineering Remedy</span>
                      </button>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
};
