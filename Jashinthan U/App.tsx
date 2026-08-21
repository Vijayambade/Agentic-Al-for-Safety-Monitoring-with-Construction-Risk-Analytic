import React, { useState, useEffect } from "react";
import { Navbar } from "./components/Navbar";
import { MfaModal } from "./components/MfaModal";
import { PermissionsModal } from "./components/PermissionsModal";
import { ReportGeneratorModal } from "./components/ReportGeneratorModal";
import { RiskDetectionModal } from "./components/RiskDetectionModal";
import { SiteSafetyModal } from "./components/SiteSafetyModal";
import { MaterialEstimationModal } from "./components/MaterialEstimationModal";
import { GuardrailsModal } from "./components/GuardrailsModal";
import { OverviewTab } from "./components/OverviewTab";
import { AnalyticsTab } from "./components/AnalyticsTab";
import { ResourcesTab } from "./components/ResourcesTab";
import { DocumentsTab } from "./components/DocumentsTab";
import { FieldOpsTab } from "./components/FieldOpsTab";
import { ApiPortalTab } from "./components/ApiPortalTab";
import { ChatBotWidget } from "./components/ChatBotWidget";

import { 
  UserRole, 
  PermissionMatrix, 
  Project, 
  ResourceEquipment, 
  ResourceLabor, 
  ResourceMaterial, 
  ConstructionDocument, 
  FieldLog, 
  ApiLog 
} from "./types";
import { 
  DEFAULT_ROLE_PERMISSIONS, 
  INITIAL_PROJECTS, 
  INITIAL_EQUIPMENT, 
  INITIAL_LABOR, 
  INITIAL_MATERIALS, 
  INITIAL_DOCUMENTS, 
  INITIAL_FIELD_LOGS 
} from "./data/mockData";
import { ShieldAlert, Bell, CheckCircle2, WifiOff } from "lucide-react";

export default function App() {
  // Global App States
  const [currentRole, setCurrentRole] = useState<UserRole>("Project Manager");
  const [permissionsMap, setPermissionsMap] = useState<Record<UserRole, PermissionMatrix>>(DEFAULT_ROLE_PERMISSIONS);
  const [activeTab, setActiveTab] = useState<string>("overview");
  const [darkMode, setDarkMode] = useState<boolean>(true);
  const [isOfflineMode, setIsOfflineMode] = useState<boolean>(false);
  const [mfaVerified, setMfaVerified] = useState<boolean>(false);
  const [searchQuery, setSearchQuery] = useState<string>("");

  // Modals
  const [isMfaOpen, setIsMfaOpen] = useState<boolean>(false);
  const [isPermissionsOpen, setIsPermissionsOpen] = useState<boolean>(false);
  const [isReportGeneratorOpen, setIsReportGeneratorOpen] = useState<boolean>(false);
  const [isRiskModalOpen, setIsRiskModalOpen] = useState<boolean>(false);
  const [isSafetyModalOpen, setIsSafetyModalOpen] = useState<boolean>(false);
  const [isMaterialModalOpen, setIsMaterialModalOpen] = useState<boolean>(false);
  const [isGuardrailsModalOpen, setIsGuardrailsModalOpen] = useState<boolean>(false);

  // Live Construction Telemetry Data States
  const [projects, setProjects] = useState<Project[]>(INITIAL_PROJECTS);
  const [equipment, setEquipment] = useState<ResourceEquipment[]>(INITIAL_EQUIPMENT);
  const [labor, setLabor] = useState<ResourceLabor[]>(INITIAL_LABOR);
  const [materials, setMaterials] = useState<ResourceMaterial[]>(INITIAL_MATERIALS);
  const [documents, setDocuments] = useState<ConstructionDocument[]>(INITIAL_DOCUMENTS);
  const [fieldLogs, setFieldLogs] = useState<FieldLog[]>(INITIAL_FIELD_LOGS);
  const [apiLogs, setApiLogs] = useState<ApiLog[]>([
    { id: "LOG-1001", timestamp: new Date(Date.now() - 3600000).toISOString(), method: "POST", endpoint: "/api/v1/projects/PRJ-01/telemetry", status: 200, source: "Autodesk BIM 360 Sync" },
    { id: "LOG-1002", timestamp: new Date(Date.now() - 1800000).toISOString(), method: "GET", endpoint: "/api/v1/projects", status: 200, source: "Procore Connect API" }
  ]);

  // Toast notifications
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  const triggerToast = (msg: string) => {
    setToastMessage(msg);
    setTimeout(() => setToastMessage(null), 3500);
  };

  // Sync dark mode class to HTML root
  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [darkMode]);

  const currentPermissions = permissionsMap[currentRole] || DEFAULT_ROLE_PERMISSIONS["Project Manager"];
  const offlineQueueCount = fieldLogs.filter(l => !l.synced).length;

  // Handlers
  const handleRoleChange = (role: UserRole) => {
    setCurrentRole(role);
    triggerToast(`Switched active workspace role to: ${role}`);
  };

  const handleToggleOfflineMode = () => {
    const newOfflineState = !isOfflineMode;
    setIsOfflineMode(newOfflineState);
    if (newOfflineState) {
      triggerToast("Entered Field Engineer Offline Tablet Mode. New site logs queued locally.");
    } else {
      triggerToast("Reconnected to Cloud BIM Telemetry. Syncing queued logs...");
      // Auto sync all queued
      setTimeout(() => {
        setFieldLogs(prev => prev.map(l => ({ ...l, synced: true })));
      }, 1000);
    }
  };

  const handleSyncQueue = () => {
    setFieldLogs(prev => prev.map(l => ({ ...l, synced: true })));
    triggerToast(`Successfully synced ${offlineQueueCount} field logs to BIM Cloud Server.`);
  };

  const handleDispatchReorder = (matId: string) => {
    setMaterials(prev => prev.map(m => {
      if (m.id === matId) {
        return { ...m, status: "Order Dispatched" };
      }
      return m;
    }));
    triggerToast(`Automated ERP Purchase Order dispatched for item #${matId}`);
  };

  const handleAddDocument = (newDoc: ConstructionDocument) => {
    setDocuments(prev => [newDoc, ...prev]);
    triggerToast(`Uploaded document "${newDoc.title}" with AES-256 Cloud Encryption.`);
  };

  const handleAddFieldLog = (newLog: FieldLog) => {
    setFieldLogs(prev => [newLog, ...prev]);
    if (newLog.synced) {
      triggerToast(`Logged site inspection "${newLog.type}" on live cloud server.`);
    } else {
      triggerToast(`Saved "${newLog.type}" to local offline queue.`);
    }
  };

  const handleAddApiLog = (newLog: ApiLog) => {
    setApiLogs(prev => [newLog, ...prev]);
  };

  const handleSelectProjectForAnalytics = (projectId: string) => {
    setActiveTab("analytics");
    triggerToast(`Filtered portfolio analytics for Project #${projectId}`);
  };

  return (
    <div className={`min-h-screen transition-colors duration-200 font-sans ${
      darkMode ? "bg-slate-950 text-slate-100" : "bg-slate-50 text-slate-900"
    }`}>
      
      {/* Navbar */}
      <Navbar
        currentRole={currentRole}
        onRoleChange={handleRoleChange}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        darkMode={darkMode}
        onToggleDarkMode={() => setDarkMode(!darkMode)}
        isOfflineMode={isOfflineMode}
        onToggleOfflineMode={handleToggleOfflineMode}
        offlineQueueCount={offlineQueueCount}
        onOpenMfa={() => setIsMfaOpen(true)}
        mfaVerified={mfaVerified}
        onOpenPermissions={() => setIsPermissionsOpen(true)}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onOpenReportGenerator={() => setIsReportGeneratorOpen(true)}
        onOpenRiskModal={() => setIsRiskModalOpen(true)}
        onOpenChatBot={() => document.getElementById("hubai-chat-trigger")?.click()}
        onOpenDocsModal={() => {
          setActiveTab("documents");
          setIsReportGeneratorOpen(true);
        }}
        onOpenSafetyModal={() => setIsSafetyModalOpen(true)}
        onOpenMaterialModal={() => setIsMaterialModalOpen(true)}
        onOpenGuardrailsModal={() => setIsGuardrailsModalOpen(true)}
      />

      {/* Floating Alert Bar for Offline Mode or MFA */}
      {(!mfaVerified || isOfflineMode) && (
        <div className={`px-4 py-2 text-xs font-semibold flex items-center justify-between transition-all ${
          isOfflineMode 
            ? "bg-rose-500/20 text-rose-300 border-b border-rose-500/30" 
            : "bg-amber-500/15 text-amber-400 border-b border-amber-500/30"
        }`}>
          <div className="max-w-7xl mx-auto w-full flex items-center justify-between">
            <div className="flex items-center space-x-2">
              {isOfflineMode ? <WifiOff className="w-4 h-4 text-rose-400" /> : <ShieldAlert className="w-4 h-4 text-amber-400" />}
              <span>
                {isOfflineMode 
                  ? `SITE ENGINEER OFFLINE MODE ACTIVE — ${offlineQueueCount} logs stored locally on tablet device.` 
                  : "SECURITY NOTICE — Multi-Factor Authentication (MFA/2FA) not verified. Some executive actions may require 2FA token confirmation."}
              </span>
            </div>
            {!mfaVerified && !isOfflineMode && (
              <button
                onClick={() => setIsMfaOpen(true)}
                className="underline hover:text-white font-bold ml-2"
              >
                Verify MFA Now →
              </button>
            )}
          </div>
        </div>
      )}

      {/* Main Container */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {activeTab === "overview" && (
          <OverviewTab
            projects={projects}
            darkMode={darkMode}
            permissions={currentPermissions}
            onSelectProjectForAnalytics={handleSelectProjectForAnalytics}
          />
        )}

        {activeTab === "analytics" && (
          <AnalyticsTab
            projects={projects}
            darkMode={darkMode}
            permissions={currentPermissions}
            triggerToast={triggerToast}
          />
        )}

        {activeTab === "resources" && (
          <ResourcesTab
            equipment={equipment}
            labor={labor}
            materials={materials}
            darkMode={darkMode}
            onDispatchReorder={handleDispatchReorder}
          />
        )}

        {activeTab === "documents" && (
          <DocumentsTab
            documents={documents}
            darkMode={darkMode}
            permissions={currentPermissions}
            onAddDocument={handleAddDocument}
            onOpenReportGenerator={() => setIsReportGeneratorOpen(true)}
          />
        )}

        {activeTab === "field-ops" && (
          <FieldOpsTab
            logs={fieldLogs}
            projects={projects}
            darkMode={darkMode}
            isOfflineMode={isOfflineMode}
            onToggleOfflineMode={handleToggleOfflineMode}
            onAddLog={handleAddFieldLog}
            onSyncQueue={handleSyncQueue}
          />
        )}

        {activeTab === "api-portal" && (
          <ApiPortalTab
            logs={apiLogs}
            darkMode={darkMode}
            permissions={currentPermissions}
            onAddLog={handleAddApiLog}
          />
        )}
      </main>

      {/* Modals */}
      <MfaModal
        isOpen={isMfaOpen}
        onClose={() => setIsMfaOpen(false)}
        darkMode={darkMode}
        mfaVerified={mfaVerified}
        onVerifySuccess={() => {
          setMfaVerified(true);
          triggerToast("MFA 2FA Hardware Token verified successfully!");
        }}
      />

      <PermissionsModal
        isOpen={isPermissionsOpen}
        onClose={() => setIsPermissionsOpen(false)}
        darkMode={darkMode}
        permissionsMap={permissionsMap}
        onUpdatePermissions={setPermissionsMap}
        currentRole={currentRole}
      />

      <ReportGeneratorModal
        isOpen={isReportGeneratorOpen}
        onClose={() => setIsReportGeneratorOpen(false)}
        projects={projects}
        darkMode={darkMode}
        onSaveToRepository={(newDoc) => {
          handleAddDocument(newDoc);
          triggerToast(`Generated "${newDoc.title}" saved to Cloud Repository!`);
        }}
      />

      {/* Feature Modals accessible from Top Buttons */}
      <RiskDetectionModal
        isOpen={isRiskModalOpen}
        onClose={() => setIsRiskModalOpen(false)}
        projects={projects}
        darkMode={darkMode}
        triggerToast={triggerToast}
      />

      <SiteSafetyModal
        isOpen={isSafetyModalOpen}
        onClose={() => setIsSafetyModalOpen(false)}
        projects={projects}
        darkMode={darkMode}
        triggerToast={triggerToast}
      />

      <MaterialEstimationModal
        isOpen={isMaterialModalOpen}
        onClose={() => setIsMaterialModalOpen(false)}
        projects={projects}
        darkMode={darkMode}
        triggerToast={triggerToast}
      />

      <GuardrailsModal
        isOpen={isGuardrailsModalOpen}
        onClose={() => setIsGuardrailsModalOpen(false)}
        darkMode={darkMode}
        triggerToast={triggerToast}
      />

      {/* Floating AI Chatbot Assistant */}
      <ChatBotWidget darkMode={darkMode} triggerToast={triggerToast} />

      {/* Toast Notification Banner */}
      {toastMessage && (
        <div className="fixed bottom-6 left-6 z-50 animate-fade-in">
          <div className={`px-5 py-3 rounded-2xl shadow-2xl border flex items-center space-x-3 text-xs sm:text-sm font-bold ${
            darkMode ? "bg-slate-900 border-amber-500 text-white" : "bg-slate-900 text-white border-amber-400"
          }`}>
            <CheckCircle2 className="w-5 h-5 text-amber-500 shrink-0" />
            <span>{toastMessage}</span>
          </div>
        </div>
      )}

    </div>
  );
}
