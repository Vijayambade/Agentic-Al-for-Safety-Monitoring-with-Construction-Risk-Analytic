import React from "react";
import { 
  Building2, 
  ShieldCheck, 
  Wifi, 
  WifiOff, 
  Sun, 
  Moon, 
  Search, 
  KeyRound, 
  UserCheck,
  ChevronDown,
  FileText,
  ShieldAlert,
  MessageSquare,
  Coins,
  Sparkles,
  Calculator
} from "lucide-react";
import { UserRole } from "../types";

interface NavbarProps {
  currentRole: UserRole;
  onRoleChange: (role: UserRole) => void;
  activeTab: string;
  onTabChange: (tab: string) => void;
  darkMode: boolean;
  onToggleDarkMode: () => void;
  isOfflineMode: boolean;
  onToggleOfflineMode: () => void;
  offlineQueueCount: number;
  onOpenMfa: () => void;
  mfaVerified: boolean;
  onOpenPermissions: () => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  onOpenReportGenerator?: () => void;
  onOpenRiskModal?: () => void;
  onOpenChatBot?: () => void;
  onOpenDocsModal?: () => void;
  onOpenSafetyModal?: () => void;
  onOpenMaterialModal?: () => void;
  onOpenGuardrailsModal?: () => void;
}

export const Navbar: React.FC<NavbarProps> = ({
  currentRole,
  onRoleChange,
  activeTab,
  onTabChange,
  darkMode,
  onToggleDarkMode,
  isOfflineMode,
  onToggleOfflineMode,
  offlineQueueCount,
  onOpenMfa,
  mfaVerified,
  onOpenPermissions,
  searchQuery,
  onSearchChange,
  onOpenReportGenerator,
  onOpenRiskModal,
  onOpenChatBot,
  onOpenDocsModal,
  onOpenSafetyModal,
  onOpenMaterialModal,
  onOpenGuardrailsModal,
}) => {
  const roles: UserRole[] = [
    "Executive Stakeholder",
    "Project Manager",
    "Site Engineer (Field)",
    "Safety & QC Inspector",
    "API Systems Architect"
  ];

  const navItems = [
    { id: "overview", label: "Real-Time Tracking & Gantt" },
    { id: "analytics", label: "AI Analytics & Reports" },
    { id: "resources", label: "Resource Management" },
    { id: "documents", label: "Cloud BIM Repository" },
    { id: "field-ops", label: "Field Engineer Suite (Mobile)" },
    { id: "api-portal", label: "API & Integrations" },
  ];

  return (
    <header className={`sticky top-0 z-40 border-b transition-colors duration-200 ${
      darkMode ? "bg-slate-900/95 border-slate-800 text-slate-100" : "bg-white/95 border-slate-200 text-slate-800"
    } backdrop-blur-md shadow-sm`}>
      {/* Top Banner Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          
          {/* Logo & Title */}
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-amber-500 rounded-xl text-slate-950 font-bold shadow-lg shadow-amber-500/20 flex items-center justify-center">
              <Building2 className="w-6 h-6 stroke-[2.5]" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-extrabold text-lg sm:text-xl tracking-tight">Construction Intelligence Hub</span>
                <span className="px-2 py-0.5 text-[10px] uppercase font-mono font-bold rounded bg-amber-500/10 text-amber-500 border border-amber-500/30">
                  BIM 4.0 Live
                </span>
              </div>
              <p className="text-xs opacity-75 hidden sm:block">AI-Driven Real-Time Telemetry & Resource Synchronization</p>
            </div>
          </div>

          {/* Universal Omni-Search Bar */}
          <div className="flex-1 max-w-md mx-auto md:mx-4 w-full">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 w-4 h-4 opacity-50" />
              <input
                type="text"
                placeholder="Search projects, RFIs, equipment GPS, drawings, API logs..."
                value={searchQuery}
                onChange={(e) => onSearchChange(e.target.value)}
                className={`w-full pl-9 pr-4 py-1.5 text-xs sm:text-sm rounded-lg border focus:outline-none focus:ring-2 focus:ring-amber-500 transition-all ${
                  darkMode 
                    ? "bg-slate-800 border-slate-700 placeholder-slate-400 text-white" 
                    : "bg-slate-100 border-slate-300 placeholder-slate-500 text-slate-900"
                }`}
              />
              {searchQuery && (
                <button 
                  onClick={() => onSearchChange("")}
                  className="absolute right-2.5 top-2 text-xs opacity-50 hover:opacity-100"
                >
                  Clear
                </button>
              )}
            </div>
          </div>

          {/* Security, Role & System Controls */}
          <div className="flex items-center flex-wrap justify-end gap-2 sm:gap-3">
            
            {/* Offline Site Engineer Mode Toggle */}
            <button
              onClick={onToggleOfflineMode}
              title="Toggle Field Tablet Offline Mode"
              className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold border transition-all ${
                isOfflineMode
                  ? "bg-rose-500/15 border-rose-500/50 text-rose-400 animate-pulse"
                  : darkMode
                    ? "bg-slate-800 border-slate-700 hover:bg-slate-700 text-emerald-400"
                    : "bg-emerald-50 border-emerald-200 hover:bg-emerald-100 text-emerald-700"
              }`}
            >
              {isOfflineMode ? (
                <>
                  <WifiOff className="w-3.5 h-3.5" />
                  <span>Offline Field Mode ({offlineQueueCount})</span>
                </>
              ) : (
                <>
                  <Wifi className="w-3.5 h-3.5" />
                  <span className="hidden lg:inline">Online Sync Active</span>
                  <span className="lg:hidden">Online</span>
                </>
              )}
            </button>

            {/* MFA Shield */}
            <button
              onClick={onOpenMfa}
              className={`flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-medium border transition-all ${
                mfaVerified
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-500"
                  : "bg-amber-500/15 border-amber-500/40 text-amber-500"
              }`}
            >
              <ShieldCheck className="w-4 h-4" />
              <span className="hidden xl:inline">{mfaVerified ? "MFA Verified (2FA)" : "Verify MFA"}</span>
            </button>

            {/* Role Switcher Dropdown */}
            <div className="relative group">
              <select
                value={currentRole}
                onChange={(e) => onRoleChange(e.target.value as UserRole)}
                className={`appearance-none pl-8 pr-7 py-1.5 rounded-lg text-xs font-semibold border cursor-pointer focus:outline-none focus:ring-2 focus:ring-amber-500 ${
                  darkMode
                    ? "bg-slate-800 border-slate-700 text-amber-400 hover:bg-slate-700"
                    : "bg-amber-50 border-amber-200 text-amber-900 hover:bg-amber-100"
                }`}
              >
                {roles.map((r) => (
                  <option key={r} value={r} className={darkMode ? "bg-slate-900 text-white" : "bg-white text-slate-900"}>
                    Role: {r}
                  </option>
                ))}
              </select>
              <UserCheck className="absolute left-2.5 top-2 w-3.5 h-3.5 text-amber-500 pointer-events-none" />
              <ChevronDown className="absolute right-2 top-2.5 w-3 h-3 opacity-60 pointer-events-none" />
            </div>

            {/* Role Permission Matrix Button */}
            <button
              onClick={onOpenPermissions}
              title="Configure Role Permissions Matrix"
              className={`p-1.5 rounded-lg border transition-all ${
                darkMode ? "border-slate-700 hover:bg-slate-800 text-slate-300" : "border-slate-300 hover:bg-slate-100 text-slate-700"
              }`}
            >
              <KeyRound className="w-4 h-4" />
            </button>

            {/* Export Report / Generate Doc Button */}
            {onOpenReportGenerator && (
              <button
                onClick={onOpenReportGenerator}
                className="bg-amber-500 hover:brightness-110 text-slate-950 font-bold text-[10px] sm:text-xs px-3 py-1.5 rounded uppercase tracking-wider transition-all flex items-center space-x-1 shadow-md shadow-amber-500/20 shrink-0"
              >
                <FileText className="w-3.5 h-3.5" />
                <span>Export Report</span>
              </button>
            )}

            {/* Dark Mode Toggle */}
            <button
              onClick={onToggleDarkMode}
              title={darkMode ? "Switch to Modern Blueprint Light" : "Switch to Slate Construction Dark"}
              className={`p-1.5 rounded-lg border transition-all ${
                darkMode
                  ? "bg-slate-800 border-slate-700 text-amber-400 hover:bg-slate-700"
                  : "bg-slate-100 border-slate-300 text-slate-700 hover:bg-slate-200"
              }`}
            >
              {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
            </button>

          </div>
        </div>
      </div>

      {/* Top Feature Shortcut Buttons Bar */}
      <div className={`px-4 sm:px-6 lg:px-8 py-2 border-t flex items-center justify-between gap-2 overflow-x-auto scrollbar-none ${
        darkMode ? "bg-slate-900/90 border-slate-800" : "bg-slate-100/90 border-slate-200"
      }`}>
        <div className="flex items-center space-x-2 min-w-max text-xs font-bold">
          <span className="text-[10px] uppercase font-mono tracking-wider opacity-60 mr-1 flex items-center gap-1">
            <Sparkles className="w-3 h-3 text-amber-500" /> Key Features:
          </span>

          {/* 1. Risk Detection Button */}
          {onOpenRiskModal && (
            <button
              onClick={onOpenRiskModal}
              className="px-3 py-1.5 rounded-lg bg-rose-500/10 hover:bg-rose-500/20 text-rose-500 border border-rose-500/30 transition-all flex items-center space-x-1.5 shadow-sm cursor-pointer"
            >
              <ShieldAlert className="w-3.5 h-3.5" />
              <span>Risk Detection</span>
            </button>
          )}

          {/* 2. AI ChatBot Assistant Button */}
          {onOpenChatBot && (
            <button
              onClick={onOpenChatBot}
              className="px-3 py-1.5 rounded-lg bg-amber-500/10 hover:bg-amber-500/20 text-amber-500 border border-amber-500/30 transition-all flex items-center space-x-1.5 shadow-sm cursor-pointer"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>AI ChatBot</span>
            </button>
          )}

          {/* 3. Construction Documents Button */}
          {onOpenDocsModal && (
            <button
              onClick={onOpenDocsModal}
              className="px-3 py-1.5 rounded-lg bg-sky-500/10 hover:bg-sky-500/20 text-sky-500 border border-sky-500/30 transition-all flex items-center space-x-1.5 shadow-sm cursor-pointer"
            >
              <FileText className="w-3.5 h-3.5" />
              <span>Construction Docs</span>
            </button>
          )}

          {/* 4. Site Safety Button */}
          {onOpenSafetyModal && (
            <button
              onClick={onOpenSafetyModal}
              className="px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-500 border border-emerald-500/30 transition-all flex items-center space-x-1.5 shadow-sm cursor-pointer"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>Site Safety & QC</span>
            </button>
          )}

          {/* 5. Material Estimation & Reports Button */}
          {onOpenMaterialModal && (
            <button
              onClick={onOpenMaterialModal}
              className="px-3 py-1.5 rounded-lg bg-purple-500/10 hover:bg-purple-500/20 text-purple-400 border border-purple-500/30 transition-all flex items-center space-x-1.5 shadow-sm cursor-pointer"
            >
              <Coins className="w-3.5 h-3.5" />
              <span>Material Estimation Details & Reports</span>
            </button>
          )}

          {/* 6. AI Guardrails Shield Button */}
          {onOpenGuardrailsModal && (
            <button
              onClick={onOpenGuardrailsModal}
              className="px-3 py-1.5 rounded-lg bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 transition-all flex items-center space-x-1.5 shadow-sm cursor-pointer"
            >
              <ShieldCheck className="w-3.5 h-3.5" />
              <span>AI Guardrails Shield</span>
            </button>
          )}
        </div>
      </div>

      {/* Navigation Tabs Bar */}
      <div className={`px-4 sm:px-6 lg:px-8 border-t overflow-x-auto scrollbar-none ${
        darkMode ? "border-slate-800 bg-slate-950/60" : "border-slate-200 bg-slate-50/70"
      }`}>
        <nav className="flex space-x-1 sm:space-x-4 min-w-max py-1.5">
          {navItems.map((tab) => {
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                onClick={() => onTabChange(tab.id)}
                className={`px-3 py-2 rounded-lg text-xs sm:text-sm font-semibold transition-all flex items-center space-x-1.5 ${
                  isActive
                    ? "bg-amber-500 text-slate-950 shadow-md shadow-amber-500/20"
                    : darkMode
                      ? "text-slate-400 hover:text-white hover:bg-slate-800/80"
                      : "text-slate-600 hover:text-slate-950 hover:bg-slate-200/60"
                }`}
              >
                <span>{tab.label}</span>
                {tab.id === "field-ops" && offlineQueueCount > 0 && (
                  <span className="px-1.5 py-0.2 bg-rose-500 text-white rounded-full text-[10px] font-bold">
                    {offlineQueueCount}
                  </span>
                )}
              </button>
            );
          })}
        </nav>
      </div>
    </header>
  );
};
