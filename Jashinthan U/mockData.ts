import { Project, ResourceEquipment, ResourceLabor, ResourceMaterial, ConstructionDocument, FieldLog, PermissionMatrix, UserRole } from "../types";

export const DEFAULT_ROLE_PERMISSIONS: Record<UserRole, PermissionMatrix> = {
  "Executive Stakeholder": {
    viewFinancials: true,
    approveChangeOrders: true,
    uploadBlueprints: false,
    logSafetyHazards: false,
    triggerStopWorkOrder: false,
    manageApiKeys: false,
    exportExecutiveReports: true,
  },
  "Project Manager": {
    viewFinancials: true,
    approveChangeOrders: true,
    uploadBlueprints: true,
    logSafetyHazards: true,
    triggerStopWorkOrder: true,
    manageApiKeys: true,
    exportExecutiveReports: true,
  },
  "Site Engineer (Field)": {
    viewFinancials: false,
    approveChangeOrders: false,
    uploadBlueprints: true,
    logSafetyHazards: true,
    triggerStopWorkOrder: true,
    manageApiKeys: false,
    exportExecutiveReports: false,
  },
  "Safety & QC Inspector": {
    viewFinancials: false,
    approveChangeOrders: false,
    uploadBlueprints: false,
    logSafetyHazards: true,
    triggerStopWorkOrder: true,
    manageApiKeys: false,
    exportExecutiveReports: true,
  },
  "API Systems Architect": {
    viewFinancials: true,
    approveChangeOrders: false,
    uploadBlueprints: true,
    logSafetyHazards: false,
    triggerStopWorkOrder: false,
    manageApiKeys: true,
    exportExecutiveReports: true,
  },
};

export const INITIAL_PROJECTS: Project[] = [
  {
    id: "PRJ-01",
    code: "SKY-2026",
    name: "Skyline Financial Tower Phase 2",
    location: "Downtown Financial District, Sector 4",
    manager: "Marcus Vance, P.E.",
    progress: 68,
    status: "Minor Delay",
    budget: 145000000,
    spent: 98600000,
    startDate: "2025-02-15",
    estimatedCompletion: "2026-11-15",
    weatherRisk: "High Rain/Wind Alert",
    activeWorkers: 142,
    openRFIs: 6,
    safetyIncidentsThisMonth: 0,
    milestones: [
      { id: "M1", title: "Deep Foundation & Piling", phase: "Foundation", startDate: "2025-02-15", endDate: "2025-06-30", status: "Completed", completionPercentage: 100 },
      { id: "M2", title: "Steel Superstructure (Levels 1-30)", phase: "Structural Steel", startDate: "2025-07-01", endDate: "2026-03-31", status: "In Progress", completionPercentage: 85 },
      { id: "M3", title: "MEP Rough-In & High-Voltage Busbar", phase: "MEP Rough-in", startDate: "2025-11-15", endDate: "2026-06-15", status: "In Progress", completionPercentage: 42 },
      { id: "M4", title: "Glass Curtain Wall Enclosure", phase: "Exterior Enclosure", startDate: "2026-02-01", endDate: "2026-08-30", status: "Delayed", completionPercentage: 20 },
      { id: "M5", title: "Lobby & Executive Tier Finishes", phase: "Interior Finish", startDate: "2026-07-01", endDate: "2026-11-01", status: "Pending", completionPercentage: 0 }
    ]
  },
  {
    id: "PRJ-02",
    code: "MTR-Underground",
    name: "Metro Hub Underground Terminal",
    location: "Central Station Transit Corridor",
    manager: "Elena Rostova, Eng.D",
    progress: 84,
    status: "Ahead of Schedule",
    budget: 320000000,
    spent: 268800000,
    startDate: "2024-06-01",
    estimatedCompletion: "2026-08-30",
    weatherRisk: "Low",
    activeWorkers: 215,
    openRFIs: 3,
    safetyIncidentsThisMonth: 1,
    milestones: [
      { id: "M6", title: "Slurry Wall & Trench Excavation", phase: "Foundation", startDate: "2024-06-01", endDate: "2025-04-15", status: "Completed", completionPercentage: 100 },
      { id: "M7", title: "Reinforced Concrete Tunnel Arches", phase: "Structural Steel", startDate: "2025-04-16", endDate: "2026-01-20", status: "Completed", completionPercentage: 100 },
      { id: "M8", title: "Tunnel Ventilation & Emergency Power", phase: "MEP Rough-in", startDate: "2025-10-01", endDate: "2026-05-30", status: "In Progress", completionPercentage: 78 }
    ]
  },
  {
    id: "PRJ-03",
    code: "PAC-Bridge",
    name: "Pacific Waterfront Bridge Expansion",
    location: "North Bay Estuary Crossing",
    manager: "Derrick Thorne, CE",
    progress: 41,
    status: "Critical Alert",
    budget: 88000000,
    spent: 39200000,
    startDate: "2025-09-10",
    estimatedCompletion: "2027-04-10",
    weatherRisk: "High Rain/Wind Alert",
    activeWorkers: 64,
    openRFIs: 12,
    safetyIncidentsThisMonth: 0,
    milestones: [
      { id: "M9", title: "Marine Caisson Drilling", phase: "Foundation", startDate: "2025-09-10", endDate: "2026-04-30", status: "Delayed", completionPercentage: 65 },
      { id: "M10", title: "Precast Cantilever Span Girder Lift", phase: "Structural Steel", startDate: "2026-05-01", endDate: "2026-12-15", status: "Pending", completionPercentage: 0 }
    ]
  },
  {
    id: "PRJ-04",
    code: "BIO-RND",
    name: "Biotech Campus R&D Facility",
    location: "Innovation Park, Lot 14",
    manager: "Sophia Chen, AIA",
    progress: 92,
    status: "On Schedule",
    budget: 64000000,
    spent: 58900000,
    startDate: "2024-11-01",
    estimatedCompletion: "2026-07-28",
    weatherRisk: "Low",
    activeWorkers: 86,
    openRFIs: 1,
    safetyIncidentsThisMonth: 0,
    milestones: [
      { id: "M11", title: "BSL-3 Cleanroom Air Handling Validation", phase: "MEP Rough-in", startDate: "2026-01-10", endDate: "2026-06-15", status: "In Progress", completionPercentage: 94 }
    ]
  }
];

export const INITIAL_EQUIPMENT: ResourceEquipment[] = [
  { id: "EQ-101", name: "Liebherr 550 EC-H Tower Crane", type: "Tower Crane", assignedProject: "Skyline Financial Tower Phase 2", status: "Active In-Use", fuelLevel: 88, operatingHours: 1420, nextServiceDate: "2026-07-18", gpsCoordinates: "37.7892° N, 122.4014° W" },
  { id: "EQ-102", name: "Caterpillar 349 Excavator", type: "Excavator", assignedProject: "Metro Hub Underground Terminal", status: "Active In-Use", fuelLevel: 64, operatingHours: 2180, nextServiceDate: "2026-07-10", gpsCoordinates: "37.7749° N, 122.4194° W" },
  { id: "EQ-103", name: "Komatsu D155AX Bulldozer", type: "Bulldozer", assignedProject: "Pacific Waterfront Bridge Expansion", status: "Maintenance Required", fuelLevel: 32, operatingHours: 3410, nextServiceDate: "2026-07-03", gpsCoordinates: "37.8199° N, 122.4783° W" },
  { id: "EQ-104", name: "Putzmeister 56M Concrete Boom Pump", type: "Concrete Pump", assignedProject: "Skyline Financial Tower Phase 2", status: "Active In-Use", fuelLevel: 91, operatingHours: 890, nextServiceDate: "2026-08-14", gpsCoordinates: "37.7895° N, 122.4011° W" },
  { id: "EQ-105", name: "Volvo A45G Articulated Dump Truck", type: "Articulated Dump Truck", assignedProject: "Pacific Waterfront Bridge Expansion", status: "Idle / Standby", fuelLevel: 100, operatingHours: 1650, nextServiceDate: "2026-09-01", gpsCoordinates: "37.8202° N, 122.4780° W" }
];

export const INITIAL_LABOR: ResourceLabor[] = [
  { id: "LBR-01", crewName: "Apex Ironworkers Local 377", trade: "Ironworkers", headcount: 42, attendanceToday: 40, assignedProject: "Skyline Financial Tower Phase 2", shift: "Day (08:00 - 16:30)", productivityRate: 97 },
  { id: "LBR-02", crewName: "SparkPro Commercial Electricians", trade: "Electricians", headcount: 34, attendanceToday: 33, assignedProject: "Metro Hub Underground Terminal", shift: "Morning (06:00 - 14:00)", productivityRate: 94 },
  { id: "LBR-03", crewName: "Pacific Concrete Formwork Masters", trade: "Concrete Formwork", headcount: 28, attendanceToday: 24, assignedProject: "Pacific Waterfront Bridge Expansion", shift: "Day (08:00 - 16:30)", productivityRate: 86 },
  { id: "LBR-04", crewName: "BioTech Clean Piping Specialists", trade: "Plumbing & Pipefitters", headcount: 22, attendanceToday: 22, assignedProject: "Biotech Campus R&D Facility", shift: "Day (08:00 - 16:30)", productivityRate: 99 },
  { id: "LBR-05", crewName: "Skyline General Support Crew B", trade: "General Contractors", headcount: 36, attendanceToday: 35, assignedProject: "Skyline Financial Tower Phase 2", shift: "Overtime Night", productivityRate: 91 }
];

export const INITIAL_MATERIALS: ResourceMaterial[] = [
  { id: "MAT-01", name: "Grade 60 Deformed Rebar (#8 Steel)", unit: "Tons", currentStock: 185, reorderThreshold: 120, status: "Optimal", supplier: "Nucor Steel Western Division", unitCost: 920 },
  { id: "MAT-02", name: "High-Early Strength Concrete C50", unit: "Cubic Yards", currentStock: 45, reorderThreshold: 100, status: "Low Stock Alert", supplier: "Cemex Ready-Mix Solutions", unitCost: 165 },
  { id: "MAT-03", name: "Curtain Wall Glazing Panels (Triple-E)", unit: "Panels", currentStock: 12, reorderThreshold: 40, status: "Order Dispatched", supplier: "Permasteelisa Glass North America", unitCost: 1450 },
  { id: "MAT-04", name: "480V 3-Phase Busway Copper Conductors", unit: "Linear Feet", currentStock: 1400, reorderThreshold: 500, status: "Optimal", supplier: "Eaton Electrical Group", unitCost: 85 },
  { id: "MAT-05", name: "Epoxy Anchor Bolt Sets M24x200mm", unit: "Boxes (50 ct)", currentStock: 18, reorderThreshold: 25, status: "Low Stock Alert", supplier: "Hilti Fastening Systems", unitCost: 310 }
];

export const INITIAL_DOCUMENTS: ConstructionDocument[] = [
  {
    id: "DOC-100",
    title: "Hub Intelligence Master System & Architecture Spec v4.2",
    category: "Submittals & Specs",
    version: "Rev 4.2-Live",
    uploadedBy: "Automated Documentation Engine",
    uploadDate: "2026-07-02",
    size: "1.4 MB",
    status: "Approved",
    tags: ["System Spec", "Architecture", "BIM Telemetry", "Offline Protocol", "RBAC"],
    notes: "Official system documentation generated per user request. Details 5 operational roles, offline tablet syncing protocol, and 24ms live telemetry engine.",
    ocrSummary: "Executive Summary: Hub Intelligence v4.2 validated for 4 active projects ($609M total budget). Confirmed zero-data-loss field tablet sync queue and real-time Procore/BIM 360 connectors."
  },
  {
    id: "DOC-201",
    title: "Structural Frame Blueprint - Level 18 to 30",
    category: "Architectural Blueprints",
    version: "Rev 4.2",
    uploadedBy: "Foster & Partners BIM Lead",
    uploadDate: "2026-06-28",
    size: "48.2 MB",
    status: "Approved",
    tags: ["Structural", "Steel", "Level 18-30", "Skyline Tower"],
    notes: "Approved by Structural Engineer of Record. Incorporates revised outrigger truss joints.",
    ocrSummary: "Extracted 14 column detail tags. Confirmed ASTM A992 structural steel specification throughout Level 24 transfer beam."
  },
  {
    id: "DOC-202",
    title: "MEP vs Structural 3D Clash Detection Report #14",
    category: "3D BIM Models",
    version: "Rev 1.0",
    uploadedBy: "Autodesk Navisworks Auto-Sync",
    uploadDate: "2026-07-01",
    size: "112.5 MB",
    status: "Requires Markup",
    tags: ["BIM Clash", "HVAC", "Structural", "Level 14"],
    notes: "Identified 3 hard collisions between 24-inch supply duct and main steel girders on Level 14 corridor.",
    ocrSummary: "Clash coordinates X:412 Y:88 Z:140. Action assigned to Mechanical Subcontractor to reroute below drop ceiling."
  },
  {
    id: "DOC-203",
    title: "RFI-108: Anchor Bolt Placement Tolerance at Pier 4",
    category: "RFIs & Clarifications",
    version: "Rev 2.1",
    uploadedBy: "Derrick Thorne, CE",
    uploadDate: "2026-06-30",
    size: "4.1 MB",
    status: "Under Review",
    tags: ["RFI", "Foundation", "Bridge", "Pier 4"],
    notes: "Requesting confirmation if +/- 15mm tolerance is acceptable for marine foundation pier caps.",
    ocrSummary: "Engineer response pending. Caltrans bridge specification manual Section 51-1.02 indicates 10mm max tolerance."
  },
  {
    id: "DOC-204",
    title: "OSHA Tower Crane Safety & High-Wind Operation Permit",
    category: "Safety & Environmental Permits",
    version: "Rev 2026-A",
    uploadedBy: "Safety Inspector E. Ramirez",
    uploadDate: "2026-05-12",
    size: "2.8 MB",
    status: "Approved",
    tags: ["Permit", "Safety", "Crane", "OSHA"],
    notes: "Valid through Dec 31, 2026. Mandates crane lockout when continuous anemometer speeds exceed 38 MPH.",
    ocrSummary: "Verified active California DOSH Permit #CR-99421. Emergency contact protocols verified."
  }
];

export const INITIAL_FIELD_LOGS: FieldLog[] = [
  {
    id: "FLG-801",
    timestamp: "2026-07-02 06:45:00",
    author: "Site Engineer J. Miller",
    project: "Skyline Financial Tower Phase 2",
    type: "QC Milestone Signoff",
    description: "Inspected formwork and rebar placement for Level 22 North Slab. Rebar spacing and tie wire density meet structural specification 100%. Ready for concrete pour.",
    locationZone: "North Core, Floor 22",
    priority: "Low",
    synced: true
  },
  {
    id: "FLG-802",
    timestamp: "2026-07-02 07:10:00",
    author: "Safety Inspector E. Ramirez",
    project: "Pacific Waterfront Bridge Expansion",
    type: "Safety Hazard Inspection",
    description: "High wind gusts recorded at Estuary Pier 4 (36 MPH). Issued temporary yellow alert for crane lifting operations above 50 feet. Crews secured loose scaffolding materials.",
    locationZone: "Pier 4 Marine Platform",
    priority: "High Priority Action",
    synced: true
  },
  {
    id: "FLG-803",
    timestamp: "2026-07-02 07:15:00",
    author: "Site Engineer J. Miller",
    project: "Skyline Financial Tower Phase 2",
    type: "Material Delivery Note",
    description: "Received shipment of 18 boxes Hilti Epoxy Anchor Bolts (MAT-05). Inspected lot numbers against purchase order PO-9981.",
    locationZone: "Staging Area Gate 2",
    priority: "Low",
    synced: false // Simulated offline queue item
  }
];

export const MONTHLY_ANALYTICS_DATA = [
  { month: "Jan", budgetPlanned: 12.5, actualSpend: 11.8, productivityIndex: 94, safetyScore: 99 },
  { month: "Feb", budgetPlanned: 18.0, actualSpend: 17.5, productivityIndex: 96, safetyScore: 98 },
  { month: "Mar", budgetPlanned: 24.2, actualSpend: 25.1, productivityIndex: 91, safetyScore: 95 },
  { month: "Apr", budgetPlanned: 31.0, actualSpend: 29.8, productivityIndex: 98, safetyScore: 100 },
  { month: "May", budgetPlanned: 38.5, actualSpend: 37.2, productivityIndex: 97, safetyScore: 100 },
  { month: "Jun", budgetPlanned: 42.0, actualSpend: 40.9, productivityIndex: 95, safetyScore: 99 }
];

export const RESOURCE_UTILIZATION_DATA = [
  { category: "Heavy Equipment Fleet", utilization: 84, target: 85 },
  { category: "Structural Labor Trades", utilization: 94, target: 90 },
  { category: "Subcontractor Crews", utilization: 89, target: 88 },
  { category: "Crane Lift Windows", utilization: 78, target: 82 },
  { category: "Staging Yard Turnover", utilization: 92, target: 85 }
];
