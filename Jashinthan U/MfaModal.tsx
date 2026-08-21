import React, { useState } from "react";
import { ShieldCheck, Lock, Smartphone, X, CheckCircle2, AlertTriangle, Key } from "lucide-react";

interface MfaModalProps {
  isOpen: boolean;
  onClose: () => void;
  darkMode: boolean;
  mfaVerified: boolean;
  onVerifySuccess: () => void;
}

export const MfaModal: React.FC<MfaModalProps> = ({
  isOpen,
  onClose,
  darkMode,
  mfaVerified,
  onVerifySuccess,
}) => {
  const [code, setCode] = useState("849201");
  const [verifying, setVerifying] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleVerify = (e: React.FormEvent) => {
    e.preventDefault();
    setVerifying(true);
    setError("");
    setTimeout(() => {
      if (code.length === 6) {
        setVerifying(false);
        onVerifySuccess();
        onClose();
      } else {
        setVerifying(false);
        setError("Please enter a valid 6-digit verification code.");
      }
    }, 800);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm animate-fade-in">
      <div className={`w-full max-w-md rounded-2xl border shadow-2xl overflow-hidden transition-all ${
        darkMode ? "bg-slate-900 border-slate-800 text-white" : "bg-white border-slate-200 text-slate-900"
      }`}>
        
        {/* Modal Header */}
        <div className="p-6 border-b flex items-center justify-between bg-gradient-to-r from-amber-500/10 to-transparent">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-amber-500/20 text-amber-500 rounded-xl">
              <ShieldCheck className="w-6 h-6" />
            </div>
            <div>
              <h3 className="font-bold text-lg">Multi-Factor Authentication (MFA)</h3>
              <p className="text-xs opacity-70">2FA High-Security Construction Suite</p>
            </div>
          </div>
          <button onClick={onClose} className="p-1.5 rounded-lg hover:bg-slate-500/10 opacity-70 hover:opacity-100">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4">
          {mfaVerified ? (
            <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-start space-x-3 text-emerald-500">
              <CheckCircle2 className="w-6 h-6 shrink-0 mt-0.5" />
              <div>
                <p className="font-semibold text-sm">Hardware Token & Biometric Auth Verified</p>
                <p className="text-xs opacity-90 mt-1">
                  Your session is authenticated with AES-256 cloud encryption. You have full access to BIM financial submittals and executive override endpoints.
                </p>
              </div>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/30 flex items-start space-x-3 text-amber-500">
              <AlertTriangle className="w-5 h-5 shrink-0 mt-0.5" />
              <p className="text-xs">
                For security compliance across cloud BIM blueprints and contractor change orders, please authenticate via your Google Authenticator or SMS token.
              </p>
            </div>
          )}

          <form onSubmit={handleVerify} className="space-y-4">
            <div>
              <label className="block text-xs font-bold uppercase tracking-wider mb-2 opacity-80">
                Authentication Code (Simulated Token: 849201)
              </label>
              <div className="relative">
                <Key className="absolute left-3 top-3.5 w-4 h-4 opacity-50" />
                <input
                  type="text"
                  maxLength={6}
                  value={code}
                  onChange={(e) => setCode(e.target.value.replace(/\D/g, ""))}
                  placeholder="000000"
                  className={`w-full pl-10 pr-4 py-3 font-mono text-center text-lg tracking-widest rounded-xl border focus:outline-none focus:ring-2 focus:ring-amber-500 ${
                    darkMode ? "bg-slate-800 border-slate-700 text-white" : "bg-slate-50 border-slate-300 text-slate-900"
                  }`}
                />
              </div>
              {error && <p className="text-xs text-rose-500 mt-1.5">{error}</p>}
            </div>

            <div className={`p-3 rounded-xl border text-xs space-y-1.5 ${
              darkMode ? "bg-slate-800/50 border-slate-700/80" : "bg-slate-50 border-slate-200"
            }`}>
              <div className="flex items-center justify-between">
                <span className="opacity-70 flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5 text-amber-500" /> Session Encryption:
                </span>
                <span className="font-mono font-semibold text-emerald-500">TLS 1.3 / End-to-End</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="opacity-70 flex items-center gap-1.5">
                  <Smartphone className="w-3.5 h-3.5 text-blue-500" /> Hardware Key:
                </span>
                <span className="font-mono font-semibold">YubiKey / Passkey Active</span>
              </div>
            </div>

            <div className="pt-2 flex items-center justify-end space-x-3">
              <button
                type="button"
                onClick={onClose}
                className={`px-4 py-2 rounded-xl text-xs font-semibold border ${
                  darkMode ? "border-slate-700 hover:bg-slate-800" : "border-slate-300 hover:bg-slate-100"
                }`}
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={verifying}
                className="px-5 py-2.5 rounded-xl text-xs font-bold bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-lg shadow-amber-500/25 transition-all flex items-center space-x-2"
              >
                {verifying ? <span>Verifying Token...</span> : <span>Confirm & Authenticate</span>}
              </button>
            </div>
          </form>
        </div>

      </div>
    </div>
  );
};
