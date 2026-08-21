import React, { useState } from "react";
import { KeyRound, Shield, Check, X, UserCheck, AlertCircle } from "lucide-react";
import { UserRole, PermissionMatrix } from "../types";

interface PermissionsModalProps {
  isOpen: boolean;
  onClose: () => void;
  darkMode: boolean;
  permissionsMap: Record<UserRole, PermissionMatrix>;
  onUpdatePermissions: (newMap: Record<UserRole, PermissionMatrix>) => void;
  currentRole: UserRole;
}

export const PermissionsModal: React.FC<PermissionsModalProps> = ({
  isOpen,
  onClose,
  darkMode,
  permissionsMap,
  onUpdatePermissions,
  currentRole,
}) => {
  const [selectedRole, setSelectedRole] = useState<UserRole>(currentRole);
  const [localMap, setLocalMap] = useState<Record<UserRole, PermissionMatrix>>(permissionsMap);
  const [savedMessage, setSavedMessage] = useState(false);

  if (!isOpen) return null;

  const roles: UserRole[] = [
    "Executive Stakeholder",
    "Project Manager",
    "Site Engineer (Field)",
    "Safety & QC Inspector",
    "API Systems Architect"
  ];

  const permissionLabels: Array<{ key: keyof PermissionMatrix; label: string; desc: string }> = [
    { key: "viewFinancials", label: "View Portfolio Financials", desc: "Access budget burn rates, spend analytics, and contractor pay applications." },
    { key: "approveChangeOrders", label: "Approve Change Orders", desc: "Authorize budget or schedule modifications up to $250,000 threshold." },
    { key: "uploadBlueprints", label: "Upload & Revise BIM Blueprints", desc: "Commit structural revisions, 3D clash files, and specification markups." },
    { key: "logSafetyHazards", label: "Log Safety Hazards & Inspections", desc: "Submit on-site safety incident logs and OSHA compliance signoffs." },
    { key: "triggerStopWorkOrder", label: "Trigger Emergency Stop Work Order", desc: "Immediately halt cranes or site pouring during high wind or critical hazards." },
    { key: "manageApiKeys", label: "Manage API Keys & Webhooks", desc: "Configure Procore, Autodesk BIM 360, and ERP REST integration webhooks." },
    { key: "exportExecutiveReports", label: "Generate AI Executive Briefings", desc: "Synthesize portfolio status reports with Gemini AI and export PDF/Emails." },
  ];

  const handleToggle = (permKey: keyof PermissionMatrix) => {
    setLocalMap((prev) => ({
      ...prev,
      [selectedRole]: {
        ...prev[selectedRole],
        [permKey]: !prev[selectedRole][permKey]
      }
    }));
  };

  const handleSave = () => {
    onUpdatePermissions(localMap);
    setSavedMessage(true);
    setTimeout(() => {
      setSavedMessage(false);
      onClose();
    }, 1000);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className={`w-full max-w-2xl rounded-2xl border shadow-2xl overflow-hidden transition-all flex flex-col max-h-[90vh] ${
        darkMode ? "bg-slate-900 border-slate-800 text-white" : "bg-white border-slate-200 text-slate-900"
      }`}>
        
        {/* Header */}
        <div className="p-6 border-b flex items-center justify-between bg-gradient-to-r from-amber-500/10 to-transparent">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-amber-500/20 text-amber-500 rounded-xl">
              <KeyRound className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-lg">Granular Role Permissions Matrix</h3>
              <p className="text-xs opacity-70">Customize functional access rights across Construction Intelligence Hub</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-slate-500/10 opacity-70 hover:opacity-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Role Selector Tabs */}
        <div className={`p-3 border-b flex flex-wrap gap-2 overflow-x-auto ${
          darkMode ? "bg-slate-950/40 border-slate-800" : "bg-slate-50 border-slate-200"
        }`}>
          {roles.map((r) => {
            const isSel = selectedRole === r;
            return (
              <button
                key={r}
                onClick={() => setSelectedRole(r)}
                className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all flex items-center space-x-1.5 ${
                  isSel
                    ? "bg-amber-500 text-slate-950 shadow-md"
                    : darkMode ? "bg-slate-800 text-slate-300 hover:bg-slate-700" : "bg-white border text-slate-700 hover:bg-slate-100"
                }`}
              >
                <UserCheck className="w-3.5 h-3.5" />
                <span>{r}</span>
              </button>
            );
          })}
        </div>

        {/* Matrix List */}
        <div className="p-6 overflow-y-auto space-y-3 flex-1">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-bold uppercase tracking-wider opacity-60">
              Configuring access for: <strong className="text-amber-500">{selectedRole}</strong>
            </span>
            <span className="text-xs font-mono opacity-60">Click toggle to edit</span>
          </div>

          {permissionLabels.map(({ key, label, desc }) => {
            const isEnabled = localMap[selectedRole]?.[key];
            return (
              <div
                key={key}
                onClick={() => handleToggle(key)}
                className={`p-3.5 rounded-xl border flex items-center justify-between cursor-pointer transition-all ${
                  isEnabled
                    ? darkMode
                      ? "bg-amber-500/10 border-amber-500/40 hover:bg-amber-500/15"
                      : "bg-amber-50 border-amber-300 hover:bg-amber-100/70"
                    : darkMode
                      ? "bg-slate-800/40 border-slate-800 hover:bg-slate-800"
                      : "bg-slate-50 border-slate-200 hover:bg-slate-100"
                }`}
              >
                <div className="pr-4">
                  <div className="flex items-center space-x-2">
                    <span className={`font-bold text-sm ${isEnabled ? "text-amber-500" : "opacity-80"}`}>
                      {label}
                    </span>
                    {isEnabled ? (
                      <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-bold bg-emerald-500/20 text-emerald-500">
                        Granted
                      </span>
                    ) : (
                      <span className="px-1.5 py-0.5 rounded text-[10px] uppercase font-bold bg-slate-500/20 text-slate-400">
                        Restricted
                      </span>
                    )}
                  </div>
                  <p className="text-xs opacity-70 mt-1">{desc}</p>
                </div>

                <div className={`w-11 h-6 rounded-full transition-colors flex items-center p-1 ${
                  isEnabled ? "bg-amber-500 justify-end" : darkMode ? "bg-slate-700 justify-start" : "bg-slate-300 justify-start"
                }`}>
                  <div className="w-4 h-4 rounded-full bg-white shadow-md flex items-center justify-center text-slate-950">
                    {isEnabled ? <Check className="w-2.5 h-2.5 stroke-[3]" /> : <X className="w-2.5 h-2.5 stroke-[3]" />}
                  </div>
                </div>
              </div>
            );
          })}
        </div>

        {/* Footer */}
        <div className={`p-4 border-t flex items-center justify-between ${
          darkMode ? "bg-slate-950/40 border-slate-800" : "bg-slate-50 border-slate-200"
        }`}>
          <div className="flex items-center space-x-2 text-xs opacity-70">
            <AlertCircle className="w-4 h-4 text-amber-500" />
            <span>Changes take effect immediately across dashboards</span>
          </div>
          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className={`px-4 py-2 rounded-xl text-xs font-semibold border ${
                darkMode ? "border-slate-700 hover:bg-slate-800" : "border-slate-300 hover:bg-slate-100"
              }`}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              className="px-5 py-2.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/20 transition-all"
            >
              {savedMessage ? "Saved Matrix!" : "Apply Custom Permissions"}
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
