import React from "react";
import { X, ShieldAlert } from "lucide-react";
import { Project } from "../types";
import { RiskDetectionPanel } from "./RiskDetectionPanel";

interface RiskDetectionModalProps {
  isOpen: boolean;
  onClose: () => void;
  projects: Project[];
  darkMode: boolean;
  triggerToast: (msg: string) => void;
}

export const RiskDetectionModal: React.FC<RiskDetectionModalProps> = ({
  isOpen,
  onClose,
  projects,
  darkMode,
  triggerToast,
}) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className={`w-full max-w-5xl rounded-2xl border shadow-2xl overflow-hidden flex flex-col max-h-[90vh] ${
        darkMode ? "bg-slate-950 border-slate-800 text-slate-100" : "bg-white border-slate-200 text-slate-900"
      }`}>
        {/* Modal Header */}
        <div className={`p-5 border-b flex items-center justify-between shrink-0 ${
          darkMode ? "bg-slate-900 border-slate-800" : "bg-slate-100 border-slate-200"
        }`}>
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-amber-500 rounded-xl text-slate-950 font-bold shadow-lg shadow-amber-500/20">
              <ShieldAlert className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-extrabold tracking-tight">AI Site Risk & Hazard Auditor</h2>
                <span className="px-2 py-0.5 text-[10px] uppercase font-mono font-bold rounded bg-amber-500/10 text-amber-500 border border-amber-500/30">
                  Live BIM Telemetry
                </span>
              </div>
              <p className="text-xs opacity-75">Real-time threat vectors, environmental risk scores, and automated mitigation plans.</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="flex-1 overflow-y-auto p-6">
          <RiskDetectionPanel
            projects={projects}
            darkMode={darkMode}
            triggerToast={triggerToast}
          />
        </div>
      </div>
    </div>
  );
};
