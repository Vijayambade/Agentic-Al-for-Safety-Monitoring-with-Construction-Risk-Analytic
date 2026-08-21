import React, { useState } from "react";
import { 
  Truck, 
  Users, 
  Package, 
  MapPin, 
  Wrench, 
  Fuel, 
  Clock, 
  AlertTriangle, 
  CheckCircle2, 
  ShoppingCart,
  Search,
  Filter
} from "lucide-react";
import { ResourceEquipment, ResourceLabor, ResourceMaterial } from "../types";

interface ResourcesTabProps {
  equipment: ResourceEquipment[];
  labor: ResourceLabor[];
  materials: ResourceMaterial[];
  darkMode: boolean;
  onDispatchReorder: (materialId: string) => void;
}

export const ResourcesTab: React.FC<ResourcesTabProps> = ({
  equipment,
  labor,
  materials,
  darkMode,
  onDispatchReorder,
}) => {
  const [activeSubTab, setActiveSubTab] = useState<"equipment" | "labor" | "materials">("equipment");
  const [filterQuery, setFilterQuery] = useState("");

  return (
    <div className="space-y-6 animate-fade-in">
      
      {/* Top Selector Banner */}
      <div className={`p-4 rounded-2xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
        darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
      }`}>
        <div className="flex space-x-2 overflow-x-auto">
          <button
            onClick={() => setActiveSubTab("equipment")}
            className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center space-x-2 ${
              activeSubTab === "equipment"
                ? "bg-amber-500 text-slate-950 shadow-md"
                : darkMode ? "bg-slate-800 text-slate-300 hover:bg-slate-700" : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            }`}
          >
            <Truck className="w-4 h-4" />
            <span>Heavy Machinery & Fleet ({equipment.length})</span>
          </button>

          <button
            onClick={() => setActiveSubTab("labor")}
            className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center space-x-2 ${
              activeSubTab === "labor"
                ? "bg-amber-500 text-slate-950 shadow-md"
                : darkMode ? "bg-slate-800 text-slate-300 hover:bg-slate-700" : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            }`}
          >
            <Users className="w-4 h-4" />
            <span>Workforce & Contractor Crews ({labor.length})</span>
          </button>

          <button
            onClick={() => setActiveSubTab("materials")}
            className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-bold transition-all flex items-center space-x-2 ${
              activeSubTab === "materials"
                ? "bg-amber-500 text-slate-950 shadow-md"
                : darkMode ? "bg-slate-800 text-slate-300 hover:bg-slate-700" : "bg-slate-100 text-slate-700 hover:bg-slate-200"
            }`}
          >
            <Package className="w-4 h-4" />
            <span>Material Inventory & Reorder ({materials.length})</span>
          </button>
        </div>

        <div className="relative max-w-xs w-full">
          <Search className="absolute left-3 top-2.5 w-4 h-4 opacity-50" />
          <input
            type="text"
            placeholder="Filter resources..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            className={`w-full pl-9 pr-4 py-1.5 text-xs rounded-xl border focus:outline-none focus:ring-2 focus:ring-amber-500 ${
              darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"
            }`}
          />
        </div>
      </div>

      {/* SUB-TAB 1: EQUIPMENT & HEAVY MACHINERY */}
      {activeSubTab === "equipment" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {equipment
            .filter(e => e.name.toLowerCase().includes(filterQuery.toLowerCase()) || e.assignedProject.toLowerCase().includes(filterQuery.toLowerCase()))
            .map((eq) => {
              const statusColors = {
                "Active In-Use": "bg-emerald-500/15 text-emerald-500 border-emerald-500/30",
                "Idle / Standby": "bg-blue-500/15 text-blue-500 border-blue-500/30",
                "Maintenance Required": "bg-rose-500/15 text-rose-500 border-rose-500/30 animate-pulse",
                "In Transit": "bg-amber-500/15 text-amber-500 border-amber-500/30",
              }[eq.status];

              return (
                <div key={eq.id} className={`p-5 rounded-2xl border transition-all flex flex-col justify-between ${
                  darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
                }`}>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-xs font-bold opacity-60">{eq.id}</span>
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border ${statusColors}`}>
                        {eq.status}
                      </span>
                    </div>
                    <h3 className="font-bold text-base">{eq.name}</h3>
                    <p className="text-xs opacity-70 mt-0.5">{eq.type} | Assigned: {eq.assignedProject}</p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-200/20 dark:border-slate-800 space-y-2.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="opacity-70 flex items-center gap-1.5">
                        <Fuel className="w-3.5 h-3.5 text-amber-500" /> Fuel Level
                      </span>
                      <div className="flex items-center space-x-2">
                        <div className="w-20 bg-slate-200 dark:bg-slate-700 h-1.5 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${eq.fuelLevel < 40 ? "bg-rose-500" : "bg-emerald-500"}`} style={{ width: `${eq.fuelLevel}%` }} />
                        </div>
                        <span className="font-mono font-bold">{eq.fuelLevel}%</span>
                      </div>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="opacity-70 flex items-center gap-1.5">
                        <Clock className="w-3.5 h-3.5 text-blue-500" /> Operating Hours
                      </span>
                      <span className="font-mono font-bold">{eq.operatingHours} hrs</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="opacity-70 flex items-center gap-1.5">
                        <Wrench className="w-3.5 h-3.5 text-purple-500" /> Next Service Date
                      </span>
                      <span className="font-mono font-bold">{eq.nextServiceDate}</span>
                    </div>

                    <div className="flex items-center justify-between pt-1 text-[11px] opacity-60">
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3 h-3 text-amber-500" /> GPS Coordinates:
                      </span>
                      <span className="font-mono">{eq.gpsCoordinates}</span>
                    </div>
                  </div>
                </div>
              );
            })}
        </div>
      )}

      {/* SUB-TAB 2: WORKFORCE & CONTRACTOR CREWS */}
      {activeSubTab === "labor" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {labor
            .filter(l => l.crewName.toLowerCase().includes(filterQuery.toLowerCase()) || l.trade.toLowerCase().includes(filterQuery.toLowerCase()))
            .map((lb) => (
              <div key={lb.id} className={`p-5 rounded-2xl border transition-all flex flex-col justify-between ${
                darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
              }`}>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="font-mono text-xs font-bold opacity-60">{lb.id}</span>
                    <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-blue-500/15 text-blue-500 border border-blue-500/30">
                      {lb.trade}
                    </span>
                  </div>
                  <h3 className="font-bold text-base">{lb.crewName}</h3>
                  <p className="text-xs opacity-70 mt-0.5">Assigned: {lb.assignedProject}</p>
                </div>

                <div className="mt-4 pt-3 border-t border-slate-200/20 dark:border-slate-800 space-y-2.5 text-xs">
                  <div className="flex items-center justify-between">
                    <span className="opacity-70">Shift Schedule</span>
                    <span className="font-semibold">{lb.shift}</span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="opacity-70">Attendance Today</span>
                    <span className="font-bold text-emerald-500">
                      {lb.attendanceToday} / {lb.headcount} Personnel ({Math.round((lb.attendanceToday / lb.headcount) * 100)}%)
                    </span>
                  </div>

                  <div className="flex items-center justify-between">
                    <span className="opacity-70">Productivity Rate</span>
                    <span className="font-bold text-amber-500">{lb.productivityRate}% Benchmark</span>
                  </div>
                </div>
              </div>
            ))}
        </div>
      )}

      {/* SUB-TAB 3: MATERIAL INVENTORY & STOCK ALERTS */}
      {activeSubTab === "materials" && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {materials
            .filter(m => m.name.toLowerCase().includes(filterQuery.toLowerCase()) || m.supplier.toLowerCase().includes(filterQuery.toLowerCase()))
            .map((mat) => {
              const statusColors = {
                "Optimal": "bg-emerald-500/15 text-emerald-500 border-emerald-500/30",
                "Low Stock Alert": "bg-rose-500/15 text-rose-500 border-rose-500/30 animate-pulse",
                "Order Dispatched": "bg-blue-500/15 text-blue-500 border-blue-500/30",
              }[mat.status];

              return (
                <div key={mat.id} className={`p-5 rounded-2xl border transition-all flex flex-col justify-between ${
                  darkMode ? "bg-slate-900/90 border-slate-800" : "bg-white border-slate-200 shadow-sm"
                }`}>
                  <div>
                    <div className="flex items-center justify-between mb-2">
                      <span className="font-mono text-xs font-bold opacity-60">{mat.id}</span>
                      <span className={`px-2.5 py-0.5 rounded-full text-[10px] font-extrabold border ${statusColors}`}>
                        {mat.status}
                      </span>
                    </div>
                    <h3 className="font-bold text-base">{mat.name}</h3>
                    <p className="text-xs opacity-70 mt-0.5">Supplier: {mat.supplier}</p>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-200/20 dark:border-slate-800 space-y-2.5 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="opacity-70">Current Stock</span>
                      <span className="font-bold text-sm">
                        {mat.currentStock} {mat.unit}
                      </span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="opacity-70">Reorder Trigger Threshold</span>
                      <span className="font-mono opacity-80">{mat.reorderThreshold} {mat.unit}</span>
                    </div>

                    <div className="flex items-center justify-between">
                      <span className="opacity-70">Unit Cost</span>
                      <span className="font-mono font-bold">${mat.unitCost} / {mat.unit}</span>
                    </div>

                    {mat.status === "Low Stock Alert" && (
                      <div className="pt-2">
                        <button
                          onClick={() => onDispatchReorder(mat.id)}
                          className="w-full py-2 px-3 rounded-xl font-bold text-xs bg-rose-500 hover:bg-rose-400 text-white shadow-md shadow-rose-500/20 transition-all flex items-center justify-center space-x-1.5"
                        >
                          <ShoppingCart className="w-3.5 h-3.5" />
                          <span>Dispatch Automated ERP PO Reorder</span>
                        </button>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
        </div>
      )}

    </div>
  );
};
