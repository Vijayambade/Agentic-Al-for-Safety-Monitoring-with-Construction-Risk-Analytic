import React, { useState } from "react";
import { 
  X, 
  Coins, 
  Calculator, 
  Download, 
  Printer, 
  CheckCircle2, 
  Layers, 
  Hammer, 
  TrendingUp, 
  AlertTriangle,
  Send,
  RefreshCw
} from "lucide-react";
import { Project } from "../types";

interface MaterialEstimationModalProps {
  isOpen: boolean;
  onClose: () => void;
  projects: Project[];
  darkMode: boolean;
  triggerToast: (msg: string) => void;
}

export const MaterialEstimationModal: React.FC<MaterialEstimationModalProps> = ({
  isOpen,
  onClose,
  projects,
  darkMode,
  triggerToast,
}) => {
  const [selectedProjectId, setSelectedProjectId] = useState<string>("PRJ-01");

  // Material item list with interactive unit sliders/quantities
  const [materialsList, setMaterialsList] = useState([
    { id: "MAT-01", name: "Structural Steel (Grade A992)", category: "Structural", unit: "Tons", qtyNeeded: 14800, qtyPlaced: 11250, unitPrice: 1150, wastePct: 1.8, status: "Optimal" },
    { id: "MAT-02", name: "Ready-Mix Concrete (Grade C40)", category: "Foundation", unit: "Cubic Yards", qtyNeeded: 68000, qtyPlaced: 52100, unitPrice: 145, wastePct: 2.4, status: "Order Dispatched" },
    { id: "MAT-03", name: "Double-Glazed Curtain Wall Glass", category: "Facade", unit: "Sq Ft", qtyNeeded: 245000, qtyPlaced: 115000, unitPrice: 48.5, wastePct: 0.9, status: "Optimal" },
    { id: "MAT-04", name: "Galvanized Copper Pipe (Type L)", category: "MEP", unit: "Linear Ft", qtyNeeded: 185000, qtyPlaced: 142000, unitPrice: 12.8, wastePct: 3.1, status: "Low Stock Alert" },
    { id: "MAT-05", name: "Fire-Rated Type-X Drywall (5/8\")", category: "Finishes", unit: "Sheets", qtyNeeded: 310000, qtyPlaced: 85000, unitPrice: 18.2, wastePct: 4.2, status: "Optimal" },
  ]);

  if (!isOpen) return null;

  const handleQtyChange = (id: string, delta: number) => {
    setMaterialsList(prev => prev.map(m => {
      if (m.id === id) {
        const newNeeded = Math.max(100, m.qtyNeeded + delta);
        return { ...m, qtyNeeded: newNeeded };
      }
      return m;
    }));
    triggerToast("Recalculated material estimation & procurement budget variance.");
  };

  const handleReorder = (name: string) => {
    triggerToast(`Automated ERP Purchase Order created for ${name}. Transmitted to vendor gateway.`);
  };

  const totalEstimateCost = materialsList.reduce((acc, m) => acc + (m.qtyNeeded * m.unitPrice), 0);
  const totalSpentCost = materialsList.reduce((acc, m) => acc + (m.qtyPlaced * m.unitPrice), 0);
  const remainingCost = totalEstimateCost - totalSpentCost;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className={`w-full max-w-5xl rounded-2xl border shadow-2xl overflow-hidden flex flex-col max-h-[90vh] ${
        darkMode ? "bg-slate-950 border-slate-800 text-slate-100" : "bg-white border-slate-200 text-slate-900"
      }`}>
        {/* Header */}
        <div className={`p-5 border-b flex items-center justify-between shrink-0 ${
          darkMode ? "bg-slate-900 border-slate-800" : "bg-slate-100 border-slate-200"
        }`}>
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-amber-500 rounded-xl text-slate-950 font-bold shadow-lg shadow-amber-500/20">
              <Coins className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-extrabold tracking-tight">Material Estimation & Bill of Quantities (BOQ)</h2>
                <span className="px-2 py-0.5 text-[10px] uppercase font-mono font-bold rounded bg-amber-500/10 text-amber-500 border border-amber-500/30">
                  ERP Live Sync
                </span>
              </div>
              <p className="text-xs opacity-75">Interactive material breakdown, unit pricing, procurement forecasting, and waste factors.</p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          
          {/* KPI Summary Banner */}
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div className={`p-4 rounded-xl border ${
              darkMode ? "bg-slate-900/60 border-slate-800" : "bg-amber-50/50 border-amber-200"
            }`}>
              <span className="text-[10px] font-bold uppercase tracking-wider opacity-60">Total Budgeted Estimation</span>
              <div className="text-2xl font-extrabold text-amber-500 font-mono">
                {new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(totalEstimateCost)}
              </div>
              <span className="text-[10px] opacity-70">Calculated across 5 Core Trades</span>
            </div>

            <div className={`p-4 rounded-xl border ${
              darkMode ? "bg-slate-900/60 border-slate-800" : "bg-emerald-50/50 border-emerald-200"
            }`}>
              <span className="text-[10px] font-bold uppercase tracking-wider opacity-60">Placed Material Value</span>
              <div className="text-2xl font-extrabold text-emerald-500 font-mono">
                {new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(totalSpentCost)}
              </div>
              <span className="text-[10px] text-emerald-600 dark:text-emerald-400 font-bold">
                {((totalSpentCost / totalEstimateCost) * 100).toFixed(1)}% Installed
              </span>
            </div>

            <div className={`p-4 rounded-xl border ${
              darkMode ? "bg-slate-900/60 border-slate-800" : "bg-blue-50/50 border-blue-200"
            }`}>
              <span className="text-[10px] font-bold uppercase tracking-wider opacity-60">Remaining Requisition</span>
              <div className="text-2xl font-extrabold text-blue-500 font-mono">
                {new Intl.NumberFormat("en-US", { style: "currency", currency: "USD", notation: "compact" }).format(remainingCost)}
              </div>
              <span className="text-[10px] opacity-70">Pro-rated for completion phase</span>
            </div>
          </div>

          {/* Interactive Material Estimation Table */}
          <div className="space-y-3">
            <h3 className="text-xs font-extrabold uppercase tracking-wider opacity-70 flex items-center gap-1.5">
              <Calculator className="w-4 h-4 text-amber-500" /> Interactive Bill of Materials (BOQ)
            </h3>

            <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-slate-800">
              <table className="w-full text-xs text-left">
                <thead className={`text-[10px] font-bold uppercase tracking-wider border-b ${
                  darkMode ? "bg-slate-900/90 border-slate-800 opacity-70" : "bg-slate-100 border-slate-200 text-slate-700"
                }`}>
                  <tr>
                    <th className="p-3">Material Name & Category</th>
                    <th className="p-3">Est. Needed</th>
                    <th className="p-3">Installed</th>
                    <th className="p-3">Unit Price</th>
                    <th className="p-3">Total Value</th>
                    <th className="p-3">Procurement Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-200 dark:divide-slate-800 font-mono">
                  {materialsList.map((m) => {
                    const rowValue = m.qtyNeeded * m.unitPrice;
                    return (
                      <tr key={m.id} className={darkMode ? "hover:bg-slate-900/40" : "hover:bg-slate-50"}>
                        <td className="p-3 font-sans">
                          <div className="font-extrabold text-xs">{m.name}</div>
                          <span className="text-[10px] opacity-60 font-mono">{m.category} | Waste Factor: {m.wastePct}%</span>
                        </td>
                        <td className="p-3">
                          <div className="flex items-center space-x-1.5">
                            <span className="font-bold">{m.qtyNeeded.toLocaleString()} {m.unit}</span>
                            <div className="flex flex-col">
                              <button onClick={() => handleQtyChange(m.id, 500)} className="text-[9px] hover:text-amber-500">▲</button>
                              <button onClick={() => handleQtyChange(m.id, -500)} className="text-[9px] hover:text-amber-500">▼</button>
                            </div>
                          </div>
                        </td>
                        <td className="p-3">
                          <span className="text-emerald-500 font-bold">{m.qtyPlaced.toLocaleString()} {m.unit}</span>
                        </td>
                        <td className="p-3 opacity-80">
                          ${m.unitPrice.toFixed(2)} / {m.unit}
                        </td>
                        <td className="p-3 font-bold text-amber-500">
                          ${rowValue.toLocaleString()}
                        </td>
                        <td className="p-3 font-sans">
                          <button
                            onClick={() => handleReorder(m.name)}
                            className="px-2.5 py-1 bg-amber-500 hover:bg-amber-400 text-slate-950 font-extrabold text-[10px] rounded transition-all flex items-center space-x-1 cursor-pointer"
                          >
                            <Send className="w-3 h-3" />
                            <span>ERP Reorder</span>
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>

          {/* Environmental & Carbon Footprint Note */}
          <div className={`p-4 rounded-xl border flex flex-col sm:flex-row items-center justify-between gap-3 ${
            darkMode ? "bg-slate-900/50 border-slate-800" : "bg-slate-50 border-slate-200"
          }`}>
            <div className="space-y-1">
              <h4 className="text-xs font-bold text-emerald-500 flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4" /> Green BIM Material Sustainability Rating
              </h4>
              <p className="text-[11px] opacity-75">
                Low waste ratio (2.14%) mitigates approximately <strong>142.5 Metric Tons</strong> of CO2e carbon footprint across raw material transport.
              </p>
            </div>

            <button
              onClick={() => window.print()}
              className="px-4 py-2 bg-slate-900 text-white dark:bg-white dark:text-slate-950 hover:opacity-90 rounded-xl text-xs font-bold transition-all flex items-center space-x-1.5 shrink-0 cursor-pointer"
            >
              <Printer className="w-3.5 h-3.5" />
              <span>Export BOQ Report</span>
            </button>
          </div>

        </div>
      </div>
    </div>
  );
};
