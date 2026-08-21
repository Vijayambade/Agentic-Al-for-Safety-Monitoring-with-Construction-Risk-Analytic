export type UserRole = 
  | "Executive Stakeholder"
  | "Project Manager"
  | "Site Engineer (Field)"
  | "Safety & QC Inspector"
  | "API Systems Architect";

export interface PermissionMatrix {
  viewFinancials: boolean;
  approveChangeOrders: boolean;
  uploadBlueprints: boolean;
  logSafetyHazards: boolean;
  triggerStopWorkOrder: boolean;
  manageApiKeys: boolean;
  exportExecutiveReports: boolean;
}

export interface Project {
  id: string;
  code: string;
  name: string;
  location: string;
  manager: string;
  progress: number;
  status: "On Schedule" | "Minor Delay" | "Critical Alert" | "Ahead of Schedule";
  budget: number;
  spent: number;
  startDate: string;
  estimatedCompletion: string;
  weatherRisk: "Low" | "Moderate" | "High Rain/Wind Alert";
  activeWorkers: number;
  openRFIs: number;
  safetyIncidentsThisMonth: number;
  milestones: Milestone[];
}

export interface Milestone {
  id: string;
  title: string;
  phase: "Foundation" | "Structural Steel" | "MEP Rough-in" | "Exterior Enclosure" | "Interior Finish";
  startDate: string;
  endDate: string;
  status: "Completed" | "In Progress" | "Pending" | "Delayed";
  completionPercentage: number;
}

export interface ResourceEquipment {
  id: string;
  name: string;
  type: "Excavator" | "Tower Crane" | "Bulldozer" | "Concrete Pump" | "Articulated Dump Truck";
  assignedProject: string;
  status: "Active In-Use" | "Idle / Standby" | "Maintenance Required" | "In Transit";
  fuelLevel: number;
  operatingHours: number;
  nextServiceDate: string;
  gpsCoordinates: string;
}

export interface ResourceLabor {
  id: string;
  crewName: string;
  trade: "Ironworkers" | "Electricians" | "Concrete Formwork" | "Plumbing & Pipefitters" | "General Contractors";
  headcount: number;
  attendanceToday: number;
  assignedProject: string;
  shift: "Morning (06:00 - 14:00)" | "Day (08:00 - 16:30)" | "Overtime Night";
  productivityRate: number; // e.g. 96%
}

export interface ResourceMaterial {
  id: string;
  name: string;
  unit: string;
  currentStock: number;
  reorderThreshold: number;
  status: "Optimal" | "Low Stock Alert" | "Order Dispatched";
  supplier: string;
  unitCost: number;
}

export interface ConstructionDocument {
  id: string;
  title: string;
  category: "Architectural Blueprints" | "3D BIM Models" | "RFIs & Clarifications" | "Submittals & Specs" | "Safety & Environmental Permits";
  version: string;
  uploadedBy: string;
  uploadDate: string;
  size: string;
  status: "Approved" | "Under Review" | "Requires Markup";
  tags: string[];
  notes?: string;
  ocrSummary?: string;
}

export interface FieldLog {
  id: string;
  timestamp: string;
  author: string;
  project: string;
  type: "Safety Hazard Inspection" | "QC Milestone Signoff" | "Material Delivery Note" | "Weather Stop Log";
  description: string;
  locationZone: string;
  priority: "Low" | "Medium" | "High Priority Action";
  synced: boolean;
  photoUrl?: string;
}

export interface ApiLog {
  id: string;
  timestamp: string;
  method: string;
  endpoint: string;
  status: number;
  source: string;
}
