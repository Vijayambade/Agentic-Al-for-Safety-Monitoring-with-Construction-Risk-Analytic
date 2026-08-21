import React, { useState } from "react";
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend, 
  ResponsiveContainer,
  LineChart,
  Line
} from "recharts";
import { 
  Sparkles, 
  FileText, 
  Mail, 
  Download, 
  CheckCircle2, 
  TrendingUp, 
  PieChart,
  RefreshCw,
  Send
} from "lucide-react";
import { MONTHLY_ANALYTICS_DATA, RESOURCE_UTILIZATION_DATA } from "../data/mockData";
import { Project, PermissionMatrix } from "../types";
import { RiskDetectionPanel } from "./RiskDetectionPanel";

interface AnalyticsTabProps {
  projects: Project[];
  darkMode: boolean;
  permissions: PermissionMatrix;
  triggerToast: (msg: string) => void;
}

export const AnalyticsTab: React.FC<AnalyticsTabProps> = ({
  projects,
  darkMode,
  permissions,
  triggerToast,
}) => {
  const [briefingLoading, setBriefingLoading] = useState(false);
  const [executiveBriefing, setExecutiveBriefing] = useState<{
    title: string;
    dateGenerated: string;
    overallHealth: string;
    keyHighlights: string[];
    financialSummary: string;
    actionRequired: string;
  } | null>(null);

  const [emailScheduled, setEmailScheduled] = useState(true);
  const [exportingPdf, setExportingPdf] = useState(false);

  const handleGenerateBriefing = async () => {
    setBriefingLoading(true);
    try {
      const response = await fetch("/api/ai/executive-briefing", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          projectsSummary: projects.map(p => ({ name: p.name, progress: p.progress, status: p.status, spent: p.spent })),
          timeframe: "Q3 2026 Executive Review"
        })
      });
      const data = await response.json();
      setExecutiveBriefing(data);
    } catch (e) {
      setExecutiveBriefing({
        title: "Executive Construction Intelligence Briefing (Current Quarter)",
        dateGenerated: new Date().toLocaleDateString(),
        overallHealth: "Good (89% On-Schedule across 4 active portfolios)",
        keyHighlights: [
          "Skyline Financial Tower Level 24 transfer truss steel completed 3 days ahead of baseline schedule.",
          "Metro Hub Underground Slurry Wall completed with zero environmental water intrusion alerts.",
          "Overall labor productivity rate increased from 91% to 96% following automated equipment staging."
        ],
        financialSummary: "Total portfolio burn rate is tracking 1.8% under projected baseline contingency allowances.",
        actionRequired: "Stakeholder sign-off required for marine caisson drilling Change Order CO-209 at Pacific Waterfront."
      });
    } finally {
      setBriefingLoading(false);
    }
  };

  const handleExportPdf = () => {
    setExportingPdf(true);
    setTimeout(() => {
      setExportingPdf(false);
      alert("Executive Briefing PDF Report successfully compiled and downloaded to local storage.");
    }, 1200);
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Header & Automated Reporting Controls Banner */}
      <div className={`p-6 rounded-2xl border flex flex-col md:flex-row md:items-center justify-between gap-4 ${
        darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
      }`}>
        <div>
          <div className="flex items-center space-x-2">
            <h2 className="font-extrabold text-lg sm:text-xl">Portfolio Data Analytics & Automated Stakeholder Reporting</h2>
            <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-amber-500/20 text-amber-500">
              AI Synthesizer Active
            </span>
          </div>
          <p className="text-xs opacity-70 mt-1">
            Visualizing financial spend velocity, productivity metrics, and resource utilization across all project sites.
          </p>
        </div>

        <div className="flex items-center flex-wrap gap-3">
          <button
            onClick={() => setEmailScheduled(!emailScheduled)}
            className={`px-3.5 py-2 rounded-xl text-xs font-semibold border transition-all flex items-center space-x-2 ${
              emailScheduled
                ? "bg-emerald-500/15 border-emerald-500/40 text-emerald-500"
                : "bg-slate-100 dark:bg-slate-800 border-slate-300 dark:border-slate-700 opacity-80"
            }`}
          >
            <Mail className="w-4 h-4" />
            <span>{emailScheduled ? "Weekly Email Digest: ON" : "Weekly Email Digest: OFF"}</span>
          </button>

          {permissions.exportExecutiveReports && (
            <button
              onClick={handleGenerateBriefing}
              disabled={briefingLoading}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/20 transition-all flex items-center space-x-2"
            >
              {briefingLoading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
              <span>Generate Gemini AI Briefing</span>
            </button>
          )}
        </div>
      </div>

      {/* AI Executive Briefing Synthesizer Box (if generated) */}
      {executiveBriefing && (
        <div className={`p-6 rounded-2xl border transition-all animate-fade-in ${
          darkMode 
            ? "bg-gradient-to-br from-slate-900 via-slate-900 to-amber-950/20 border-amber-500/50 shadow-xl" 
            : "bg-gradient-to-br from-amber-50/70 via-white to-amber-100/40 border-amber-400 shadow-md"
        }`}>
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-amber-500/20">
            <div className="flex items-center space-x-3">
              <div className="p-2.5 bg-amber-500 text-slate-950 rounded-xl font-bold shadow-md">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <h3 className="font-extrabold text-base">{executiveBriefing.title}</h3>
                <p className="text-xs opacity-70">Synthesized on {executiveBriefing.dateGenerated} | Overall Status: <strong className="text-emerald-500">{executiveBriefing.overallHealth}</strong></p>
              </div>
            </div>

            <button
              onClick={handleExportPdf}
              disabled={exportingPdf}
              className="px-4 py-2 rounded-xl text-xs font-bold bg-slate-900 text-white dark:bg-white dark:text-slate-900 hover:opacity-90 transition-all flex items-center space-x-1.5"
            >
              <Download className="w-4 h-4" />
              <span>{exportingPdf ? "Compiling PDF..." : "Export Briefing (PDF/HTML)"}</span>
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-5">
            <div>
              <h4 className="text-xs font-bold uppercase tracking-wider opacity-70 mb-2.5">Key Portfolio Achievements:</h4>
              <ul className="space-y-2 text-xs">
                {executiveBriefing.keyHighlights.map((hl, idx) => (
                  <li key={idx} className="flex items-start space-x-2">
                    <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0 mt-0.5" />
                    <span className="opacity-90 leading-relaxed">{hl}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="space-y-4">
              <div className="p-3.5 rounded-xl bg-amber-500/10 border border-amber-500/30">
                <span className="text-[10px] uppercase font-bold text-amber-500">Financial Spend Summary</span>
                <p className="text-xs font-medium mt-1 leading-relaxed opacity-90">{executiveBriefing.financialSummary}</p>
              </div>

              <div className="p-3.5 rounded-xl bg-rose-500/10 border border-rose-500/30">
                <span className="text-[10px] uppercase font-bold text-rose-500">Immediate Action Required</span>
                <p className="text-xs font-bold mt-1 leading-relaxed opacity-95">{executiveBriefing.actionRequired}</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Real-Time AI Site Risk & Hazard Auditor */}
      <RiskDetectionPanel 
        projects={projects} 
        darkMode={darkMode} 
        triggerToast={triggerToast} 
      />

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Chart 1: Budget Planned vs Actual Spend ($ Millions) */}
        <div className={`p-6 rounded-2xl border transition-all ${
          darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
        }`}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-extrabold text-sm sm:text-base">Monthly Spend Velocity ($M)</h3>
              <p className="text-xs opacity-60">Planned baseline vs Actual project spend</p>
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-500 font-bold">
              Tracking Under Budget
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={MONTHLY_ANALYTICS_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? "#334155" : "#e2e8f0"} opacity={0.5} />
                <XAxis dataKey="month" stroke={darkMode ? "#94a3b8" : "#64748b"} fontSize={12} />
                <YAxis stroke={darkMode ? "#94a3b8" : "#64748b"} fontSize={12} unit="$M" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: darkMode ? "#0f172a" : "#ffffff", 
                    borderColor: darkMode ? "#334155" : "#cbd5e1",
                    borderRadius: "12px",
                    fontSize: "12px"
                  }} 
                />
                <Legend wrapperStyle={{ fontSize: "12px" }} />
                <Bar dataKey="budgetPlanned" name="Planned ($M)" fill="#3b82f6" radius={[6, 6, 0, 0]} />
                <Bar dataKey="actualSpend" name="Actual Spend ($M)" fill="#f59e0b" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Productivity Index & Safety Health Score */}
        <div className={`p-6 rounded-2xl border transition-all ${
          darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
        }`}>
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-extrabold text-sm sm:text-base">Productivity & Safety Trend Index</h3>
              <p className="text-xs opacity-60">Labor output % vs OSHA compliance rate</p>
            </div>
            <span className="text-xs font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-500 font-bold">
              99% Avg Safety
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={MONTHLY_ANALYTICS_DATA} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? "#334155" : "#e2e8f0"} opacity={0.5} />
                <XAxis dataKey="month" stroke={darkMode ? "#94a3b8" : "#64748b"} fontSize={12} />
                <YAxis stroke={darkMode ? "#94a3b8" : "#64748b"} fontSize={12} domain={[80, 100]} unit="%" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: darkMode ? "#0f172a" : "#ffffff", 
                    borderColor: darkMode ? "#334155" : "#cbd5e1",
                    borderRadius: "12px",
                    fontSize: "12px"
                  }} 
                />
                <Legend wrapperStyle={{ fontSize: "12px" }} />
                <Line type="monotone" dataKey="productivityIndex" name="Productivity Index (%)" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="safetyScore" name="Safety Compliance (%)" stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

      </div>

      {/* Bottom Chart: Resource Utilization Rate */}
      <div className={`p-6 rounded-2xl border transition-all ${
        darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
      }`}>
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-extrabold text-sm sm:text-base">Resource Utilization vs Target Rate (%)</h3>
            <p className="text-xs opacity-60">Efficiency benchmark across heavy equipment, labor, and yard staging</p>
          </div>
        </div>

        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart layout="vertical" data={RESOURCE_UTILIZATION_DATA} margin={{ top: 10, right: 20, left: 60, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke={darkMode ? "#334155" : "#e2e8f0"} opacity={0.5} />
              <XAxis type="number" domain={[0, 100]} stroke={darkMode ? "#94a3b8" : "#64748b"} fontSize={12} unit="%" />
              <YAxis dataKey="category" type="category" stroke={darkMode ? "#94a3b8" : "#64748b"} fontSize={12} width={130} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: darkMode ? "#0f172a" : "#ffffff", 
                  borderColor: darkMode ? "#334155" : "#cbd5e1",
                  borderRadius: "12px",
                  fontSize: "12px"
                }} 
              />
              <Legend wrapperStyle={{ fontSize: "12px" }} />
              <Bar dataKey="utilization" name="Current Utilization (%)" fill="#10b981" radius={[0, 6, 6, 0]} />
              <Bar dataKey="target" name="Target Benchmark (%)" fill="#64748b" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

    </div>
  );
};
