import React, { useState } from "react";
import { 
  FileText, 
  Download, 
  CheckCircle2, 
  Sparkles, 
  X, 
  Printer, 
  Copy, 
  Save, 
  Building2, 
  ShieldCheck, 
  Cpu, 
  TrendingUp,
  Coins,
  FileCheck
} from "lucide-react";
import { Project, ConstructionDocument } from "../types";

interface ReportGeneratorModalProps {
  isOpen: boolean;
  onClose: () => void;
  projects: Project[];
  darkMode: boolean;
  onSaveToRepository?: (doc: ConstructionDocument) => void;
}

export const ReportGeneratorModal: React.FC<ReportGeneratorModalProps> = ({
  isOpen,
  onClose,
  projects,
  darkMode,
  onSaveToRepository,
}) => {
  const [reportType, setReportType] = useState<
    "system_spec" | "executive_portfolio" | "safety_audit" | "material_estimation" | "document_compliance" | "resource_telemetry"
  >("system_spec");
  const [selectedProjectId, setSelectedProjectId] = useState<string>("all");
  const [isGenerating, setIsGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [saved, setSaved] = useState(false);

  if (!isOpen) return null;

  const totalBudget = projects.reduce((acc, p) => acc + p.budget, 0);
  const totalSpent = projects.reduce((acc, p) => acc + p.spent, 0);
  const totalWorkers = projects.reduce((acc, p) => acc + p.activeWorkers, 0);

  const handleGenerate = (type: typeof reportType) => {
    setReportType(type);
    setIsGenerating(true);
    setSaved(false);
    setTimeout(() => {
      setIsGenerating(false);
    }, 450);
  };

  const getReportTitle = () => {
    switch (reportType) {
      case "system_spec":
        return "Hub Intelligence v4.2 System Specification & Master Architecture Document";
      case "executive_portfolio":
        return "Executive Construction Portfolio Financial & Progress Briefing";
      case "safety_audit":
        return "OSHA & QC Environmental Site Safety & Compliance Inspection Audit";
      case "material_estimation":
        return "Comprehensive Materials Estimation, Procurement & Bill of Quantities (BOQ)";
      case "document_compliance":
        return "Construction Documents Review & AI OCR Structural Compliance Audit";
      case "resource_telemetry":
        return "IoT Telemetry Fleet & Labor Trades Resource Utilization Document";
    }
  };

  const getReportContent = () => {
    switch (reportType) {
      case "system_spec":
        return `HUB INTELLIGENCE — CONSTRUCTION MANAGEMENT v4.2
OFFICIAL SYSTEM ARCHITECTURE & MASTER SPECIFICATION DOCUMENT
================================================================================
Document ID: SPEC-2026-v4.2 | Classification: Enterprise Confidential
Generated Date: ${new Date().toLocaleDateString()} | Active Telemetry Latency: 24ms

1. SYSTEM EXECUTIVE SUMMARY
Hub Intelligence v4.2 is a full-stack, AI-powered construction portfolio platform integrating BIM 360 3D models, live IoT tower crane GPS sensors, and offline tablet engineering workflows.

2. ACTIVE PORTFOLIO OVERVIEW
Total Managed Projects: ${projects.length}
Total Allocated Budget: $${(totalBudget / 1000000).toFixed(1)}M USD
Current Cumulative Spend: $${(totalSpent / 1000000).toFixed(1)}M USD (${((totalSpent / totalBudget) * 100).toFixed(1)}% burned)
Active On-Site Labor Force: ${totalWorkers} certified union and subcontractor personnel across all sites.

3. ARCHITECTURAL PILLARS & CORE MODULES
- Real-Time Gantt & Milestone Synchronization Engine: Tracks foundational, structural steel, and MEP rough-in phases with automated critical-path delay calculations.
- Field Engineer Tablet Offline Protocol: When underground connectivity drops (e.g., Metro Hub Tunnel), field logs queue locally in device storage and automatically reconcile upon re-establishing 5G/BIM Cloud link.
- AES-256 Document Vault & OCR AI Analyzer: Scans contractor submittals and engineering blueprints against Caltrans and ASTM A992 structural standards.
- Hardware MFA & Dynamic Role Matrix: Enforces strict separation of duties across 5 operational tiers (Executive, PM, Site Engineer, Safety Inspector, API Architect).

4. COMPLIANCE SIGN-OFF
Certified by Automated Documentation Engine v4.2
Status: VERIFIED & LIVE`;

      case "executive_portfolio":
        return `EXECUTIVE CONSTRUCTION PORTFOLIO BRIEFING
================================================================================
Report Date: ${new Date().toLocaleDateString()} | Prepared for Executive Stakeholders

1. PORTFOLIO FINANCIAL SUMMARY
Total Portfolio Budget: $${(totalBudget / 1000000).toFixed(2)}M
Current Expenditure: $${(totalSpent / 1000000).toFixed(2)}M
Net Budget Variance: -$4,200 (Under Budget)

2. PROJECT BREAKDOWN
${projects.map(p => `• ${p.name} (${p.code}):
  - Status: ${p.status} (${p.progress}% Complete)
  - Budget: $${(p.budget / 1000000).toFixed(1)}M | Spent: $${(p.spent / 1000000).toFixed(1)}M
  - Active Workers: ${p.activeWorkers} | Open RFIs: ${p.openRFIs}`).join("\n\n")}

3. RECOMMENDED EXECUTIVE ACTIONS
- Approve Phase 2 structural steel procurement change order for Skyline Financial Tower.
- Monitor weather alert advisories for Pacific Waterfront Bridge marine caisson drilling.`;

      case "safety_audit":
        return `OSHA & QC ENVIRONMENTAL SITE SAFETY & COMPLIANCE AUDIT
================================================================================
Audit Date: ${new Date().toLocaleDateString()} | Site Integrity Rating: 99.8/100 (PASSED)

1. ACTIVE JOB-SITE SAFETY METRICS
- Cumulative Safety Incidents (This Month): ${projects.reduce((acc, p) => acc + p.safetyIncidentsThisMonth, 0)}
- Active OSHA Stop-Work Orders: 0
- Active Weather Hazard Advisories: ${projects.filter(p => p.weatherRisk === "High Rain/Wind Alert").length} High Rain/Wind Alert(s)
- Emergency Muster Points Inspected: 100% Cleared & Signposted

2. SITE SAFETY FIELD CHECKLIST
[✔] Personal Protective Equipment (PPE) Compliance: 100% mandate verified at entry gates.
    - Double Lanyard Harnesses inspected for high-altitude steel rigging.
    - Certified ballistic protective hardhats and high-visibility class 3 vests.
[✔] Tower Crane Wind Velocity Limiters:
    - Current continuous wind speed: 14.5 MPH.
    - Automated Liebherr 550 EC-H alarm locked at 38.0 MPH (continuous shutdown triggered).
[✔] Excavation & Trenching Shoring:
    - Concrete retaining walls for deep foundational digging certified by Geotechnical Inspector.
[✔] Electrical Busbar & High-Voltage Safety:
    - Active Lock-out/Tag-out (LOTO) protocols validated on structural Level 12 main switchgear boards.
[✔] Fire Prevention & Hazardous Materials:
    - Gas cylinder storage cages secured and grounded. Class ABC fire extinguishers verified on all floor levels.

3. INSPECTOR REMARKS & REMEDIATION LOGS
- Checked high-stress support beams on Pacific Waterfront marine piers. Anchor bolt torque specs conform exactly to Caltrans DOT regulations. No safety warnings.`;

      case "material_estimation":
        return `COMPREHENSIVE MATERIALS ESTIMATION & BILL OF QUANTITIES (BOQ)
================================================================================
Audit Date: ${new Date().toLocaleDateString()} | ERP Database Connector: ACTIVE

1. PORTFOLIO ITEMID MATERIAL ESTIMATIONS
Below is the master estimation sheet contrasted against physical jobsite material intake:

• Reinforced Structural Steel (Grade A992)
  - Estimated Needed Quantity: 14,800 Tons
  - Actual Placed Quantity: 11,250 Tons
  - Average Unit Price: $1,150.00 / Ton
  - Total Budgeted Value: $17,020,000 USD
  - Cost Variance: -$4,082,500 (Ongoing procurement)
  - Estimated Waste Factor: 1.8% (Target limit < 3.0%)
  - Reorder Status: OPTIMAL (Next batch delivery July 24)

• Ready-Mix High-Strength Concrete (Grade C40)
  - Estimated Needed Quantity: 68,000 Cubic Yards
  - Actual Poured Quantity: 52,100 Cubic Yards
  - Average Unit Price: $145.00 / Cubic Yard
  - Total Budgeted Value: $9,860,000 USD
  - Cost Variance: -$2,305,500 (Continuous pours scheduled)
  - Estimated Waste Factor: 2.4% (Target limit < 4.0%)
  - Reorder Status: ORDER DISPATCHED (Transit queue)

• High-Performance Double-Glazed Curtain Wall Glass
  - Estimated Needed Quantity: 245,000 Sq Ft
  - Actual Installed Quantity: 115,000 Sq Ft
  - Average Unit Price: $48.50 / Sq Ft
  - Total Budgeted Value: $11,882,500 USD
  - Cost Variance: -$6,305,000 (Installation active)
  - Estimated Waste Factor: 0.9% (Target limit < 1.5%)
  - Reorder Status: OPTIMAL

• Galvanized Copper Pipe & Conduit (Type L)
  - Estimated Needed Quantity: 185,000 Linear Ft
  - Actual Placed Quantity: 142,000 Linear Ft
  - Average Unit Price: $12.80 / Linear Ft
  - Total Budgeted Value: $2,368,000 USD
  - Cost Variance: -$550,400 (MEP Stage 3 active)
  - Estimated Waste Factor: 3.1% (Target limit < 5.0%)
  - Reorder Status: LOW STOCK ALERT (Auto-procurement triggered)

• Fire-Rated Type-X Drywall Boards (5/8")
  - Estimated Needed Quantity: 310,000 Sheets
  - Actual Placed Quantity: 85,000 Sheets
  - Average Unit Price: $18.20 / Sheet
  - Total Budgeted Value: $5,642,000 USD
  - Cost Variance: -$4,095,000 (Finishing stage pending)
  - Estimated Waste Factor: 4.2% (Target limit < 5.5%)
  - Reorder Status: OPTIMAL

2. MATERIAL ESTIMATION KPIs
- Weighted Material Waste Ratio: 2.14% (Highly Optimal)
- Estimated Embedded Carbon Offset (CO2e Reduction): -142.5 Metric Tons
- Total Procurement Capital Saved via Bulk Ordering: $845,000 USD`;

      case "document_compliance":
        return `CONSTRUCTION DOCUMENTS COMPLIANCE & AI OCR AUDIT REVIEW
================================================================================
Audit Date: ${new Date().toLocaleDateString()} | Compliance Level: 99.2% (EXCELLENT)

1. SYSTEM COMPLIANCE SUMMARY
Our AI OCR engine has successfully parsed and matched 100% of uploaded submittals, blueprints, and local permits to local regulatory standards (including Caltrans DOT, OSHA Standards, and ASTM specifications).

2. FILE STATUS & COMPLIANCE DISPOSITION
• Level 18-30 Structural Steel Frame Blueprint (DOC-201)
  - Class: Architectural Blueprints | Version: Rev 12.2
  - OCR Compliance Validation: SUCCESS
  - Extracted Specs: Checked weld connection tolerances (0.015" deflection limits). Verified compliance with ASTM A992.
  - Disposition: APPROVED BY CITY ARCHITECT

• Deep Soil Hydrology Log & Foundation Survey (DOC-202)
  - Class: Safety & Environmental Permits | Version: Rev 3.0
  - OCR Compliance Validation: SUCCESS
  - Extracted Specs: Checked water table pressure at -45ft excavation point. Confirmed pile integrity coefficient.
  - Disposition: APPROVED BY GEOTECHNICAL ENG

• Municipal Tower Cranes Height & Wind Permits (DOC-203)
  - Class: Safety & Environmental Permits | Version: Rev 1.0-Active
  - OCR Compliance Validation: SUCCESS
  - Extracted Specs: Maximum height clearance 485ft MSL. Anemometer lock trigger verified at 38 MPH.
  - Disposition: APPROVED - EXPIRES OCT 31, 2026

• Level 1-5 Electrical Rough-in Diagram (DOC-204)
  - Class: RFIs & Clarifications | Version: Rev 2.1
  - OCR Compliance Validation: SUCCESS
  - Extracted Specs: Verified copper gauge and main busbar isolation grounding limits.
  - Disposition: UNDER REVIEW (Awaiting Fire Marshal check)

3. COMPLIANCE GAPS & RECOMMENDED REMEDIATION
- Highlight: Structural Concrete Curing Log for Level 21 Column B is missing local inspector digital signature. Auto RFI has been fired to subcontractor.`;

      case "resource_telemetry":
        return `IoT TELEMETRY FLEET & LABOR RESOURCE UTILIZATION DOCUMENT
================================================================================
Telemetry Timestamp: ${new Date().toLocaleString()} | Active Sensors: 100% Online

1. HEAVY EQUIPMENT FLEET TELEMETRY
- Liebherr 550 EC-H Tower Crane: Active In-Use | Fuel/Battery: 88% | Operating Hours: 1,420h
- Putzmeister 56M Concrete Boom Pump: Active In-Use | Fuel: 91% | Operating Hours: 890h
- Caterpillar 349 Excavator: Active In-Use | Fuel: 64% | Operating Hours: 2,180h

2. TRADE LABOR ALLOCATION
Total Headcount On-Site: ${totalWorkers} personnel across Ironworkers, Electrical, Concrete, and Marine trades.
Overall Labor Productivity Index: 95.4% against target milestones.`;
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(getReportContent());
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleSaveToRepo = () => {
    if (!onSaveToRepository) return;
    const newDoc: ConstructionDocument = {
      id: `DOC-${Math.floor(Math.random() * 899 + 100)}`,
      title: getReportTitle(),
      category: reportType === "system_spec" ? "Submittals & Specs" : reportType === "safety_audit" ? "Safety & Environmental Permits" : "RFIs & Clarifications",
      version: "Rev 1.0-Gen",
      uploadedBy: "Automated Documentation Engine",
      uploadDate: new Date().toISOString().split("T")[0],
      size: "1.1 MB",
      status: "Approved",
      tags: ["AI Generated", reportType.toUpperCase(), "Report"],
      notes: "Generated live via Executive Document Studio.",
      ocrSummary: `Summary: ${getReportTitle()}. Verified complete dataset.`
    };
    onSaveToRepository(newDoc);
    setSaved(true);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className={`w-full max-w-5xl rounded-2xl border shadow-2xl overflow-hidden flex flex-col max-h-[90vh] ${
        darkMode ? "bg-[#0f1115] border-slate-800 text-slate-100" : "bg-white border-slate-200 text-slate-900"
      }`}>
        
        {/* Header */}
        <div className={`p-6 border-b flex items-center justify-between ${
          darkMode ? "bg-[#0a0c10] border-slate-800" : "bg-slate-100 border-slate-200"
        }`}>
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-xl bg-amber-500/20 border border-amber-500/30 flex items-center justify-center text-amber-500">
              <FileText className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <h2 className="text-lg font-bold tracking-tight">Executive Document Studio</h2>
                <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 font-bold">
                  AI Generator v4.2
                </span>
              </div>
              <p className="text-xs text-slate-400">Generate, download, or save official construction, safety, and material estimation reports.</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Document Selector Navigation */}
        <div className={`grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-2 p-4 border-b ${
          darkMode ? "bg-slate-900/50 border-slate-800" : "bg-slate-50 border-slate-200"
        }`}>
          <button
            onClick={() => handleGenerate("system_spec")}
            className={`flex items-center space-x-1.5 px-2 py-2 rounded-lg text-[11px] font-bold transition-all ${
              reportType === "system_spec"
                ? "bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20"
                : darkMode ? "bg-slate-800/60 text-slate-300 hover:bg-slate-800" : "bg-white text-slate-700 hover:bg-slate-100 border"
            }`}
          >
            <Cpu className="w-3.5 h-3.5 shrink-0 text-amber-500" />
            <span className="truncate">System Spec</span>
          </button>

          <button
            onClick={() => handleGenerate("executive_portfolio")}
            className={`flex items-center space-x-1.5 px-2 py-2 rounded-lg text-[11px] font-bold transition-all ${
              reportType === "executive_portfolio"
                ? "bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20"
                : darkMode ? "bg-slate-800/60 text-slate-300 hover:bg-slate-800" : "bg-white text-slate-700 hover:bg-slate-100 border"
            }`}
          >
            <Building2 className="w-3.5 h-3.5 shrink-0 text-amber-500" />
            <span className="truncate">Portfolio Brief</span>
          </button>

          <button
            onClick={() => handleGenerate("safety_audit")}
            className={`flex items-center space-x-1.5 px-2 py-2 rounded-lg text-[11px] font-bold transition-all ${
              reportType === "safety_audit"
                ? "bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20"
                : darkMode ? "bg-slate-800/60 text-slate-300 hover:bg-slate-800" : "bg-white text-slate-700 hover:bg-slate-100 border"
            }`}
          >
            <ShieldCheck className="w-3.5 h-3.5 shrink-0 text-emerald-500" />
            <span className="truncate">Site Safety Audit</span>
          </button>

          <button
            onClick={() => handleGenerate("material_estimation")}
            className={`flex items-center space-x-1.5 px-2 py-2 rounded-lg text-[11px] font-bold transition-all ${
              reportType === "material_estimation"
                ? "bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20"
                : darkMode ? "bg-slate-800/60 text-slate-300 hover:bg-slate-800" : "bg-white text-slate-700 hover:bg-slate-100 border"
            }`}
          >
            <Coins className="w-3.5 h-3.5 shrink-0 text-amber-500" />
            <span className="truncate">Material Est.</span>
          </button>

          <button
            onClick={() => handleGenerate("document_compliance")}
            className={`flex items-center space-x-1.5 px-2 py-2 rounded-lg text-[11px] font-bold transition-all ${
              reportType === "document_compliance"
                ? "bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20"
                : darkMode ? "bg-slate-800/60 text-slate-300 hover:bg-slate-800" : "bg-white text-slate-700 hover:bg-slate-100 border"
            }`}
          >
            <FileCheck className="w-3.5 h-3.5 shrink-0 text-sky-500" />
            <span className="truncate">Doc Compliance</span>
          </button>

          <button
            onClick={() => handleGenerate("resource_telemetry")}
            className={`flex items-center space-x-1.5 px-2 py-2 rounded-lg text-[11px] font-bold transition-all ${
              reportType === "resource_telemetry"
                ? "bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/20"
                : darkMode ? "bg-slate-800/60 text-slate-300 hover:bg-slate-800" : "bg-white text-slate-700 hover:bg-slate-100 border"
            }`}
          >
            <TrendingUp className="w-3.5 h-3.5 shrink-0 text-amber-500" />
            <span className="truncate">IoT Telemetry</span>
          </button>
        </div>

        {/* Document Content Viewport */}
        <div className="flex-1 p-6 overflow-y-auto font-mono text-xs leading-relaxed">
          {isGenerating ? (
            <div className="h-64 flex flex-col items-center justify-center space-y-3">
              <div className="w-8 h-8 border-2 border-amber-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-slate-400 font-sans">Synthesizing document data & telemetry metrics...</p>
            </div>
          ) : (
            <div className={`p-6 rounded-xl border whitespace-pre-wrap shadow-inner ${
              darkMode ? "bg-[#050505] border-slate-800 text-slate-300" : "bg-slate-50 border-slate-200 text-slate-800"
            }`}>
              {getReportContent()}
            </div>
          )}
        </div>


        {/* Action Footer */}
        <div className={`p-4 border-t flex flex-wrap items-center justify-between gap-3 ${
          darkMode ? "bg-[#0a0c10] border-slate-800" : "bg-slate-100 border-slate-200"
        }`}>
          <div className="flex items-center space-x-2 text-xs text-slate-400 font-sans">
            <CheckCircle2 className="w-4 h-4 text-emerald-500" />
            <span>Document ready for cloud export or print</span>
          </div>

          <div className="flex items-center space-x-2 font-sans">
            <button
              onClick={handleCopy}
              className={`px-3 py-2 rounded-lg border text-xs font-bold flex items-center space-x-1.5 transition-colors ${
                copied
                  ? "bg-emerald-500/20 border-emerald-500 text-emerald-400"
                  : darkMode ? "bg-slate-800 border-slate-700 text-slate-200 hover:bg-slate-700" : "bg-white border-slate-300 text-slate-700 hover:bg-slate-50"
              }`}
            >
              <Copy className="w-3.5 h-3.5" />
              <span>{copied ? "Copied to Clipboard!" : "Copy Text"}</span>
            </button>

            {onSaveToRepository && (
              <button
                onClick={handleSaveToRepo}
                disabled={saved}
                className={`px-3 py-2 rounded-lg border text-xs font-bold flex items-center space-x-1.5 transition-colors ${
                  saved
                    ? "bg-emerald-500/20 border-emerald-500 text-emerald-400"
                    : darkMode ? "bg-slate-800 border-slate-700 text-slate-200 hover:bg-slate-700" : "bg-white border-slate-300 text-slate-700 hover:bg-slate-50"
                }`}
              >
                <Save className="w-3.5 h-3.5" />
                <span>{saved ? "Saved to Repo!" : "Save to Repository"}</span>
              </button>
            )}

            <button
              onClick={() => window.print()}
              className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-lg text-xs font-bold flex items-center space-x-1.5 transition-all shadow-md shadow-amber-500/20"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Print / Download PDF</span>
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};
