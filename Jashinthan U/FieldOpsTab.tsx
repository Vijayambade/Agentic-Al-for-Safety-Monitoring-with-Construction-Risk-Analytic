import React, { useState } from "react";
import { 
  Smartphone, 
  WifiOff, 
  Wifi, 
  Camera, 
  MapPin, 
  AlertTriangle, 
  CheckCircle2, 
  Clock, 
  Plus, 
  Send, 
  HardHat, 
  RefreshCw,
  FileSpreadsheet
} from "lucide-react";
import { FieldLog, Project } from "../types";

interface FieldOpsTabProps {
  logs: FieldLog[];
  projects: Project[];
  darkMode: boolean;
  isOfflineMode: boolean;
  onToggleOfflineMode: () => void;
  onAddLog: (log: FieldLog) => void;
  onSyncQueue: () => void;
}

export const FieldOpsTab: React.FC<FieldOpsTabProps> = ({
  logs,
  projects,
  darkMode,
  isOfflineMode,
  onToggleOfflineMode,
  onAddLog,
  onSyncQueue,
}) => {
  const [logType, setLogType] = useState<FieldLog["type"]>("Safety Hazard Inspection");
  const [project, setProject] = useState<string>(projects[0]?.name || "Skyline Financial Tower Phase 2");
  const [locationZone, setLocationZone] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState<FieldLog["priority"]>("Medium");

  const [gpsCheckedIn, setGpsCheckedIn] = useState(true);

  const unsyncedCount = logs.filter(l => !l.synced).length;

  const handleSubmitLog = (e: React.FormEvent) => {
    e.preventDefault();
    if (!description || !locationZone) return;

    const newLog: FieldLog = {
      id: `FLG-${800 + logs.length + 1}`,
      timestamp: new Date().toISOString().replace("T", " ").substring(0, 19),
      author: "Field Engineer J. Miller (Tablet ID #T-449)",
      project,
      type: logType,
      description,
      locationZone,
      priority,
      synced: !isOfflineMode
    };

    onAddLog(newLog);
    setDescription("");
    setLocationZone("");
  };

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Tablet Header Banner */}
      <div className={`p-6 rounded-2xl border transition-all flex flex-col md:flex-row md:items-center justify-between gap-4 ${
        isOfflineMode 
          ? "bg-rose-500/10 border-rose-500/40" 
          : darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
      }`}>
        <div className="flex items-center space-x-3">
          <div className={`p-3 rounded-xl ${
            isOfflineMode ? "bg-rose-500 text-white animate-pulse" : "bg-emerald-500 text-slate-950"
          }`}>
            <Smartphone className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="font-extrabold text-lg sm:text-xl">On-Site Field Engineer Suite (Mobile Tablet Mode)</h2>
              <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                isOfflineMode ? "bg-rose-500/20 text-rose-400" : "bg-emerald-500/20 text-emerald-500"
              }`}>
                {isOfflineMode ? "Offline Queue Active" : "Live Cloud Syncing"}
              </span>
            </div>
            <p className="text-xs opacity-70 mt-0.5">
              Optimized for high-contrast touch targets, low-latency data entry, and automatic local caching in basement zones.
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={onToggleOfflineMode}
            className={`px-4 py-2.5 rounded-xl text-xs font-bold border transition-all flex items-center space-x-2 ${
              isOfflineMode
                ? "bg-rose-500 hover:bg-rose-400 text-white border-rose-400 shadow-lg shadow-rose-500/20"
                : darkMode ? "bg-slate-800 border-slate-700 hover:bg-slate-700 text-slate-200" : "bg-slate-100 border-slate-300 text-slate-800"
            }`}
          >
            {isOfflineMode ? <WifiOff className="w-4 h-4" /> : <Wifi className="w-4 h-4 text-emerald-500" />}
            <span>{isOfflineMode ? `Simulate Reconnect & Sync (${unsyncedCount})` : "Simulate Offline Basement Mode"}</span>
          </button>

          {unsyncedCount > 0 && !isOfflineMode && (
            <button
              onClick={onSyncQueue}
              className="px-4 py-2.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/20 transition-all flex items-center space-x-1.5"
            >
              <RefreshCw className="w-4 h-4" />
              <span>Push {unsyncedCount} Queued Logs</span>
            </button>
          )}
        </div>
      </div>

      {/* Grid: Quick Field Form (Left) + Site Logs History (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Quick Log Form */}
        <div className={`p-6 rounded-2xl border transition-all ${
          darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
        }`}>
          <div className="flex items-center justify-between pb-4 border-b border-slate-200 dark:border-slate-800">
            <div className="flex items-center space-x-2">
              <HardHat className="w-5 h-5 text-amber-500" />
              <h3 className="font-extrabold text-base">Quick Site Inspection Logger</h3>
            </div>
            {gpsCheckedIn && (
              <span className="text-[10px] font-mono text-emerald-500 flex items-center gap-1">
                <MapPin className="w-3 h-3" /> GPS Zone Verified
              </span>
            )}
          </div>

          <form onSubmit={handleSubmitLog} className="mt-4 space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase mb-1.5">Project Site</label>
              <select
                value={project}
                onChange={(e) => setProject(e.target.value)}
                className={`w-full px-3.5 py-2.5 text-xs font-semibold rounded-xl border ${
                  darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"
                }`}
              >
                {projects.map(p => (
                  <option key={p.id} value={p.name}>{p.name}</option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="block text-xs font-bold uppercase mb-1.5">Log Type</label>
                <select
                  value={logType}
                  onChange={(e) => setLogType(e.target.value as any)}
                  className={`w-full px-3 py-2.5 text-xs rounded-xl border ${
                    darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"
                  }`}
                >
                  <option value="Safety Hazard Inspection">Safety Hazard</option>
                  <option value="QC Milestone Signoff">QC Signoff</option>
                  <option value="Material Delivery Note">Material Delivery</option>
                  <option value="Weather Stop Log">Weather Stop</option>
                </select>
              </div>

              <div>
                <label className="block text-xs font-bold uppercase mb-1.5">Priority</label>
                <select
                  value={priority}
                  onChange={(e) => setPriority(e.target.value as any)}
                  className={`w-full px-3 py-2.5 text-xs rounded-xl border font-bold ${
                    priority === "High Priority Action" ? "text-rose-500" : ""
                  } ${darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"}`}
                >
                  <option value="Low">Low / Standard</option>
                  <option value="Medium">Medium Priority</option>
                  <option value="High Priority Action">High Priority Action</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-xs font-bold uppercase mb-1.5">Zone / Coordinates</label>
              <input
                type="text"
                required
                placeholder="e.g. Sector 4, Floor 22 Column Bay E"
                value={locationZone}
                onChange={(e) => setLocationZone(e.target.value)}
                className={`w-full px-3.5 py-2.5 text-xs rounded-xl border ${
                  darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"
                }`}
              />
            </div>

            <div>
              <label className="block text-xs font-bold uppercase mb-1.5">Observation / Hazard Description</label>
              <textarea
                rows={3}
                required
                placeholder="Detailed field notes, compliance observations, or rebar tag verifications..."
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className={`w-full px-3.5 py-2.5 text-xs rounded-xl border ${
                  darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"
                }`}
              />
            </div>

            <div className="flex items-center justify-between pt-2">
              <button
                type="button"
                onClick={() => alert("Simulating field tablet camera capture... Photo timestamped and geo-tagged!")}
                className="px-3.5 py-2 rounded-xl border text-xs font-semibold flex items-center space-x-1.5 opacity-80 hover:opacity-100"
              >
                <Camera className="w-4 h-4 text-amber-500" />
                <span>Attach Photo</span>
              </button>

              <button
                type="submit"
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/25 transition-all flex items-center space-x-2"
              >
                <Plus className="w-4 h-4" />
                <span>{isOfflineMode ? "Queue Offline Log" : "Submit Site Log"}</span>
              </button>
            </div>
          </form>
        </div>

        {/* Recent Site Inspection Logs */}
        <div className={`lg:col-span-2 p-6 rounded-2xl border transition-all space-y-4 ${
          darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
        }`}>
          <div className="flex items-center justify-between">
            <div>
              <h3 className="font-extrabold text-base">Live Field Engineer Log Feed</h3>
              <p className="text-xs opacity-70">Timestamped field inspections, safety hazard tags, and QC signoffs</p>
            </div>
            {unsyncedCount > 0 && (
              <span className="px-2.5 py-1 rounded-lg text-xs font-bold bg-rose-500/20 text-rose-400 border border-rose-500/30">
                {unsyncedCount} Queued Offline
              </span>
            )}
          </div>

          <div className="space-y-3 max-h-[500px] overflow-y-auto pr-1">
            {logs.map((lg) => {
              const typeColors = {
                "Safety Hazard Inspection": "bg-rose-500/15 text-rose-500 border-rose-500/30",
                "QC Milestone Signoff": "bg-emerald-500/15 text-emerald-500 border-emerald-500/30",
                "Material Delivery Note": "bg-blue-500/15 text-blue-500 border-blue-500/30",
                "Weather Stop Log": "bg-amber-500/15 text-amber-500 border-amber-500/30",
              }[lg.type];

              return (
                <div key={lg.id} className={`p-4 rounded-2xl border transition-all ${
                  !lg.synced
                    ? darkMode ? "bg-rose-950/20 border-rose-500/40 ring-1 ring-rose-500/30" : "bg-rose-50/70 border-rose-300"
                    : darkMode ? "bg-slate-800/40 border-slate-800" : "bg-slate-50 border-slate-200"
                }`}>
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs font-bold opacity-60">{lg.id}</span>
                      <span className={`px-2 py-0.5 rounded text-[10px] font-extrabold border ${typeColors}`}>
                        {lg.type}
                      </span>
                      {lg.priority === "High Priority Action" && (
                        <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-rose-500 text-white animate-pulse">
                          High Priority
                        </span>
                      )}
                    </div>

                    <div className="flex items-center space-x-3">
                      <span className="text-xs font-mono opacity-70 flex items-center gap-1">
                        <Clock className="w-3 h-3" /> {lg.timestamp}
                      </span>
                      {lg.synced ? (
                        <span className="flex items-center gap-1 text-[11px] font-semibold text-emerald-500">
                          <CheckCircle2 className="w-3.5 h-3.5" /> Synced
                        </span>
                      ) : (
                        <span className="flex items-center gap-1 text-[11px] font-semibold text-rose-400 animate-pulse">
                          <WifiOff className="w-3.5 h-3.5" /> Queued (Offline)
                        </span>
                      )}
                    </div>
                  </div>

                  <p className="font-medium text-xs sm:text-sm mt-2 leading-relaxed">{lg.description}</p>
                  
                  <div className="mt-3 pt-2.5 border-t border-slate-200/30 dark:border-slate-700/50 flex flex-wrap items-center justify-between text-xs opacity-75 gap-2">
                    <span className="flex items-center gap-1 font-semibold text-amber-500">
                      <MapPin className="w-3.5 h-3.5" /> {lg.locationZone} ({lg.project})
                    </span>
                    <span>Logged by: {lg.author}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>

      </div>

    </div>
  );
};
