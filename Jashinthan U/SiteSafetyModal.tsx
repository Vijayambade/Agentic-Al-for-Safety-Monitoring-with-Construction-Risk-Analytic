import React, { useState } from "react";
import { 
  X, 
  ShieldCheck, 
  CheckCircle2, 
  AlertTriangle, 
  HardHat, 
  Wind, 
  Flame, 
  Zap, 
  FileCheck2, 
  UserCheck, 
  ClipboardCheck,
  Sparkles
} from "lucide-react";
import { Project } from "../types";

interface SiteSafetyModalProps {
  isOpen: boolean;
  onClose: () => void;
  projects: Project[];
  darkMode: boolean;
  triggerToast: (msg: string) => void;
}

export const SiteSafetyModal: React.FC<SiteSafetyModalProps> = ({
  isOpen,
  onClose,
  projects,
  darkMode,
  triggerToast,
}) => {
  const [safetyScore, setSafetyScore] = useState<number>(99.4);
  const [checklist, setChecklist] = useState([
    { id: "SFT-01", title: "Personal Protective Equipment (PPE) Mandate", category: "Personnel Safety", status: true, detail: "100% hardhat, safety glasses, high-vis vests and steel-toe boots verified at site entry gates." },
    { id: "SFT-02", title: "High-Altitude Steel Rigging Double-Lanyard Harnesses", category: "Fall Protection", status: true, detail: "Inspected 42 safety lifelines on Levels 18-30. Self-retracting lanyards certified." },
    { id: "SFT-03", title: "Tower Crane Wind Limit Anemometers", category: "Heavy Equipment", status: true, detail: "Automated shutoff calibrated at 38.0 MPH. Current gust readings: 14.2 MPH." },
    { id: "SFT-04", title: "Lock-out / Tag-out (LOTO) Electrical Busbar Isolation", category: "Electrical Safety", status: true, detail: "Main switchgear Level 12 padlocked and tagged with certified electrician logs." },
    { id: "SFT-05", title: "Subterranean Trench Shoring & Retaining Wall Piles", category: "Geotechnical", status: true, detail: "Slurry wall pressure sensors stable at Level B4. Hydrostatic pumps tested." },
    { id: "SFT-06", title: "Combustible Gas & Oxygen Level Atmospheric Sensors", category: "Hazardous Materials", status: true, detail: "Enclosed space gas detectors in basement utility vaults report 20.9% O2." },
  ]);

  const [inspectorName, setInspectorName] = useState("Marcus Vance (CSO)");
  const [signOffComplete, setSignOffComplete] = useState(false);

  if (!isOpen) return null;

  const toggleCheck = (id: string) => {
    setChecklist(prev => prev.map(item => {
      if (item.id === id) {
        const nextStatus = !item.status;
        triggerToast(`Updated safety status for "${item.title}": ${nextStatus ? "COMPLIANT" : "FLAGGED FOR REVIEW"}`);
        return { ...item, status: nextStatus };
      }
      return item;
    }));
  };

  const totalIncidents = projects.reduce((acc, p) => acc + p.safetyIncidentsThisMonth, 0);

  const handleSignOff = () => {
    setSignOffComplete(true);
    triggerToast(`Official OSHA Safety & QC Audit signed off by ${inspectorName}. Certificate logged to Cloud Vault.`);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className={`w-full max-w-4xl rounded-2xl border shadow-2xl overflow-hidden flex flex-col max-h-[90vh] ${
        darkMode ? "bg-slate-950 border-slate-800 text-slate-100" : "bg-white border-slate-200 text-slate-900"
      }`}>
        {/* Header */}
        <div className={`p-5 border-b flex items-center justify-between shrink-0 ${
          darkMode ? "bg-slate-900 border-slate-800" : "bg-slate-100 border-slate-200"
        }`}>
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-emerald-500 rounded-xl text-slate-950 font-bold shadow-lg shadow-emerald-500/20">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-extrabold tracking-tight">OSHA & QC Jobsite Safety Suite</h2>
                <span className="px-2 py-0.5 text-[10px] uppercase font-mono font-bold rounded bg-emerald-500/10 text-emerald-500 border border-emerald-500/30">
                  Site Audit Active
                </span>
              </div>
              <p className="text-xs opacity-75">Field hazard verification, PPE inspection checklists, and environmental compliance sign-off.</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Content */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Top KPI Cards */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className={`p-4 rounded-xl border flex items-center space-x-3 ${
              darkMode ? "bg-slate-900/60 border-slate-800" : "bg-emerald-50/50 border-emerald-200"
            }`}>
              <div className="p-3 bg-emerald-500/10 text-emerald-500 rounded-xl border border-emerald-500/20">
                <ClipboardCheck className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider opacity-60">Safety Index</span>
                <div className="text-xl font-extrabold text-emerald-500 font-mono">{safetyScore}%</div>
                <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold">100% OSHA Compliant</span>
              </div>
            </div>

            <div className={`p-4 rounded-xl border flex items-center space-x-3 ${
              darkMode ? "bg-slate-900/60 border-slate-800" : "bg-amber-50/50 border-amber-200"
            }`}>
              <div className="p-3 bg-amber-500/10 text-amber-500 rounded-xl border border-amber-500/20">
                <HardHat className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider opacity-60">Active Personnel</span>
                <div className="text-xl font-extrabold font-mono">
                  {projects.reduce((acc, p) => acc + p.activeWorkers, 0)}
                </div>
                <span className="text-[10px] opacity-70">Across {projects.length} Active Sites</span>
              </div>
            </div>

            <div className={`p-4 rounded-xl border flex items-center space-x-3 ${
              darkMode ? "bg-slate-900/60 border-slate-800" : "bg-rose-50/50 border-rose-200"
            }`}>
              <div className="p-3 bg-rose-500/10 text-rose-500 rounded-xl border border-rose-500/20">
                <AlertTriangle className="w-6 h-6" />
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold tracking-wider opacity-60">Monthly Incidents</span>
                <div className="text-xl font-extrabold font-mono text-rose-500">{totalIncidents}</div>
                <span className="text-[10px] opacity-70">Zero Lost-Time Workdays</span>
              </div>
            </div>
          </div>

          {/* Interactive Checklist Table */}
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-extrabold uppercase tracking-wider opacity-70 flex items-center gap-1.5">
                <FileCheck2 className="w-4 h-4 text-emerald-500" /> Site Inspector Compliance Checklist
              </h3>
              <span className="text-[11px] font-mono text-emerald-500 font-bold">
                {checklist.filter(c => c.status).length} / {checklist.length} Passed
              </span>
            </div>

            <div className="space-y-2">
              {checklist.map((item) => (
                <div 
                  key={item.id}
                  onClick={() => toggleCheck(item.id)}
                  className={`p-4 rounded-xl border transition-all cursor-pointer flex items-start justify-between gap-3 ${
                    item.status
                      ? darkMode 
                        ? "bg-slate-900/40 border-slate-800 hover:border-emerald-500/50" 
                        : "bg-slate-50 border-slate-200 hover:border-emerald-400"
                      : "bg-rose-500/10 border-rose-500/30 text-rose-300"
                  }`}
                >
                  <div className="flex items-start space-x-3">
                    <input
                      type="checkbox"
                      checked={item.status}
                      onChange={() => {}}
                      className="mt-1 w-4 h-4 text-emerald-500 rounded border-slate-700 focus:ring-emerald-500 cursor-pointer"
                    />
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-[9px] font-mono font-bold uppercase px-1.5 py-0.5 rounded bg-slate-200 dark:bg-slate-800 opacity-80">
                          {item.category}
                        </span>
                        <strong className="text-xs font-bold">{item.title}</strong>
                      </div>
                      <p className="text-[11px] opacity-75 mt-1 leading-relaxed">{item.detail}</p>
                    </div>
                  </div>

                  <span className={`px-2.5 py-1 rounded text-[10px] font-extrabold uppercase font-mono shrink-0 ${
                    item.status ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30" : "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                  }`}>
                    {item.status ? "PASSED" : "REVIEW"}
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Inspector Sign-off Box */}
          <div className={`p-4 rounded-xl border space-y-3 ${
            darkMode ? "bg-slate-900/80 border-slate-800" : "bg-slate-50 border-slate-200"
          }`}>
            <h4 className="text-xs font-bold uppercase tracking-wider opacity-70 flex items-center gap-1.5">
              <UserCheck className="w-4 h-4 text-emerald-500" /> Digital Safety Sign-off Certification
            </h4>

            <div className="flex flex-col sm:flex-row items-center justify-between gap-3">
              <div className="w-full sm:w-auto flex-1">
                <label className="text-[10px] font-bold opacity-60 block mb-1">Chief Safety Officer (CSO) Name</label>
                <input
                  type="text"
                  value={inspectorName}
                  onChange={(e) => setInspectorName(e.target.value)}
                  className={`w-full px-3 py-1.5 text-xs rounded-lg border ${
                    darkMode ? "bg-slate-950 border-slate-800 text-white" : "bg-white border-slate-300 text-slate-900"
                  }`}
                />
              </div>

              <button
                onClick={handleSignOff}
                disabled={signOffComplete}
                className={`w-full sm:w-auto px-5 py-2.5 rounded-xl font-bold text-xs transition-all flex items-center justify-center space-x-2 cursor-pointer ${
                  signOffComplete
                    ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                    : "bg-emerald-500 hover:bg-emerald-400 text-slate-950 shadow-lg shadow-emerald-500/20"
                }`}
              >
                <CheckCircle2 className="w-4 h-4" />
                <span>{signOffComplete ? "Certified & Digitally Signed" : "Digitally Sign & Lock Safety Audit"}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
