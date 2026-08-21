import React, { useState, useRef, useEffect } from "react";
import { 
  MessageSquare, 
  X, 
  Send, 
  Sparkles, 
  Bot, 
  User, 
  Zap, 
  ArrowRight,
  ShieldCheck,
  Sliders,
  Database,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";

interface ChatMessage {
  id: string;
  role: "user" | "model";
  content: string;
  timestamp: Date;
}

interface ChatBotWidgetProps {
  darkMode: boolean;
  triggerToast: (msg: string) => void;
}

export const ChatBotWidget: React.FC<ChatBotWidgetProps> = ({
  darkMode,
  triggerToast,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [message, setMessage] = useState("");
  const [history, setHistory] = useState<ChatMessage[]>([
    {
      id: "init",
      role: "model",
      content: "Hello! I am **HubAI**, your construction telemetry and schedule integrity assistant. I can scan your projects for delay vectors, analyze blueprint compliance, or audit safety/mitigation logs. How can I help you optimize your jobsite today?",
      timestamp: new Date()
    }
  ]);
  const [loading, setLoading] = useState(false);

  // Ollama Settings State (Sync with LocalStorage)
  const [aiProvider, setAiProvider] = useState<"gemini" | "ollama">(() => {
    return (localStorage.getItem("ai_provider") as "gemini" | "ollama") || "gemini";
  });
  const [ollamaUrl, setOllamaUrl] = useState(() => {
    return localStorage.getItem("ollama_url") || "http://localhost:11434";
  });
  const [ollamaModel, setOllamaModel] = useState(() => {
    return localStorage.getItem("ollama_model") || "llama3";
  });
  const [ollamaRouting, setOllamaRouting] = useState<"client" | "server">(() => {
    return (localStorage.getItem("ollama_routing") as "client" | "server") || "server";
  });
  const [showSettings, setShowSettings] = useState(false);
  const [testingOllama, setTestingOllama] = useState(false);
  const [ollamaStatusMsg, setOllamaStatusMsg] = useState<{ type: "success" | "error"; text: string } | null>(null);

  useEffect(() => {
    localStorage.setItem("ai_provider", aiProvider);
    localStorage.setItem("ollama_url", ollamaUrl);
    localStorage.setItem("ollama_model", ollamaModel);
    localStorage.setItem("ollama_routing", ollamaRouting);
  }, [aiProvider, ollamaUrl, ollamaModel, ollamaRouting]);
  
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Quick Action chips
  const suggestedPrompts = [
    "Scan active project risks",
    "Identify materials in low stock",
    "Explain safety compliance index",
    "What is our budget status?"
  ];

  // Auto scroll to bottom
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [history, loading, isOpen, showSettings]);

  const handleTestOllama = async () => {
    setTestingOllama(true);
    setOllamaStatusMsg(null);
    try {
      if (ollamaRouting === "client") {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 4000);
        const res = await fetch(`${ollamaUrl}/api/tags`, { signal: controller.signal });
        clearTimeout(timeoutId);
        if (res.ok) {
          const data = await res.json();
          const modelsList = data.models ? data.models.map((m: any) => m.name).join(", ") : "none";
          setOllamaStatusMsg({
            type: "success",
            text: `Connected (Client Direct)! Models: [${modelsList}]`
          });
          triggerToast("Ollama connection verified client-side!");
        } else {
          setOllamaStatusMsg({
            type: "error",
            text: `Ollama returned status ${res.status}`
          });
        }
      } else {
        // server-side proxy
        const res = await fetch("/api/ai/ollama/status", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: ollamaUrl })
        });
        const data = await res.json();
        if (data.success) {
          const modelsList = data.models ? data.models.map((m: any) => m.name).join(", ") : "none";
          setOllamaStatusMsg({
            type: "success",
            text: `Connected (Server Proxy)! Models: [${modelsList}]`
          });
          triggerToast("Ollama connection verified server-side!");
        } else {
          setOllamaStatusMsg({
            type: "error",
            text: data.message || "Failed to reach Ollama from server."
          });
        }
      }
    } catch (err: any) {
      setOllamaStatusMsg({
        type: "error",
        text: `Error connecting: ${err.message}. ${
          ollamaRouting === "client" ? "Ensure Ollama is running and started with OLLAMA_ORIGINS=\"*\" to prevent CORS blocking." : ""
        }`
      });
    } finally {
      setTestingOllama(false);
    }
  };

  const handleSendMessage = async (textToSend?: string) => {
    const activeText = textToSend || message;
    if (!activeText.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: "user",
      content: activeText,
      timestamp: new Date()
    };

    setHistory(prev => [...prev, userMsg]);
    if (!textToSend) setMessage("");
    setLoading(true);

    try {
      if (aiProvider === "ollama") {
        if (ollamaRouting === "client") {
          const systemInstruction = `You are "HubAI", an elite, professional AI Construction Intelligence Assistant. Keep a professional, helpful, and engineering-focused tone. Answer accurately. Use bulleted lists, bold terms, and provide clear mitigation recommendations.`;
          const ollamaMessages = [
            { role: "system", content: systemInstruction }
          ];

          for (const h of history) {
            if (h.id === "init") continue;
            ollamaMessages.push({
              role: h.role === "user" ? "user" : "assistant",
              content: h.content
            });
          }
          ollamaMessages.push({
            role: "user",
            content: activeText
          });

          const response = await fetch(`${ollamaUrl}/api/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              model: ollamaModel,
              messages: ollamaMessages,
              stream: false
            })
          });

          if (!response.ok) {
            throw new Error(`Ollama returned status ${response.status}. Ensure CORS is enabled (OLLAMA_ORIGINS="*" ollama serve).`);
          }

          const data = await response.json();
          const botText = data.message?.content || "";

          const botMsg: ChatMessage = {
            id: `bot-${Date.now()}`,
            role: "model",
            content: botText || "No response received from local Ollama model.",
            timestamp: new Date()
          };
          setHistory(prev => [...prev, botMsg]);
        } else {
          // Server-side proxy
          const response = await fetch("/api/ai/ollama/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              message: activeText,
              url: ollamaUrl,
              model: ollamaModel,
              history: history.filter(h => h.id !== "init").map(h => ({
                role: h.role,
                content: h.content
              }))
            })
          });

          const data = await response.json();
          const botMsg: ChatMessage = {
            id: `bot-${Date.now()}`,
            role: "model",
            content: data.text || "No response returned from Ollama Server Proxy.",
            timestamp: new Date()
          };
          setHistory(prev => [...prev, botMsg]);
        }
      } else {
        // Standard Gemini
        const response = await fetch("/api/ai/chat", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            message: activeText,
            history: history.filter(h => h.id !== "init").map(h => ({
              role: h.role,
              content: h.content
            }))
          })
        });

        const data = await response.json();
        
        const botMsg: ChatMessage = {
          id: `bot-${Date.now()}`,
          role: "model",
          content: data.text || "I am processing telemetry, but I did not receive a response string. Please check the BIM cloud gateway.",
          timestamp: new Date()
        };
        setHistory(prev => [...prev, botMsg]);
      }
    } catch (e: any) {
      console.error(e);
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        role: "model",
        content: `Connection error: ${e.message || "Failed to reach AI service."}\n\n*Suggestions for Ollama:* \n1. Ensure Ollama is running locally.\n2. In Client-Side mode, run: \`OLLAMA_ORIGINS="*" ollama serve\`\n3. Pull the model: \`ollama pull ${ollamaModel}\``,
        timestamp: new Date()
      };
      setHistory(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const formatMarkdown = (text: string) => {
    if (!text) return null;
    const lines = text.split("\n");
    return lines.map((line, lineIdx) => {
      const trimmed = line.trim();
      const isBullet = trimmed.startsWith("- ") || trimmed.startsWith("* ") || trimmed.startsWith("• ");
      const lineContent = isBullet ? trimmed.replace(/^[-*•]\s+/, "") : line;

      const boldRegex = /\*\*(.*?)\*\*/g;
      const parts = lineContent.split(boldRegex);
      const formattedParts = parts.map((part, partIdx) => {
        if (partIdx % 2 === 1) {
          return <strong key={partIdx} className="font-extrabold text-amber-500">{part}</strong>;
        }
        return part;
      });

      if (isBullet) {
        return (
          <div key={lineIdx} className="flex items-start space-x-2 my-1 pl-1">
            <span className="text-amber-500 font-black shrink-0">•</span>
            <span className="flex-1">{formattedParts}</span>
          </div>
        );
      }

      return (
        <span key={lineIdx} className="block min-h-[1.1em] leading-relaxed">
          {formattedParts}
        </span>
      );
    });
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 flex flex-col items-end">
      {/* Expanded Chat Box */}
      {isOpen && (
        <div className={`w-[360px] sm:w-[400px] h-[520px] rounded-2xl border flex flex-col overflow-hidden shadow-2xl transition-all duration-300 transform translate-y-0 opacity-100 mb-4 ${
          darkMode 
            ? "bg-slate-950/95 border-slate-800 text-slate-100 shadow-slate-950/80 backdrop-blur-md" 
            : "bg-white border-slate-200 text-slate-800 shadow-slate-300/80"
        }`}>
          
          {/* Header Banner */}
          <div className="p-4 bg-gradient-to-r from-amber-500 to-amber-600 text-slate-950 flex items-center justify-between font-bold shadow-md">
            <div className="flex items-center space-x-2.5">
              <div className="p-1.5 bg-slate-950 text-amber-500 rounded-lg shadow-inner">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <h4 className="text-sm font-black leading-tight tracking-tight">HubAI Telemetry Assistant</h4>
                <div className="flex items-center space-x-1.5 text-[10px] opacity-90">
                  <span className="flex items-center gap-1">
                    <ShieldCheck className="w-3 h-3 text-slate-900" /> {aiProvider === "gemini" ? "Ollama Local" : `Ollama (${ollamaModel})`}
                  </span>
                  <span>•</span>
                  <span className="bg-slate-950/20 px-1.5 py-0.2 rounded font-mono font-bold text-[9px]">
                    🛡️ Guardrails Active
                  </span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center space-x-1">
              <button
                onClick={() => {
                  setShowSettings(!showSettings);
                  setOllamaStatusMsg(null);
                }}
                className={`p-1.5 rounded-lg hover:bg-slate-950/10 transition-colors ${
                  showSettings ? "bg-slate-950/20 text-slate-950" : ""
                }`}
                title="AI Connection Settings"
              >
                <Sliders className="w-4 h-4" />
              </button>
              <button 
                onClick={() => setIsOpen(false)}
                className="p-1.5 rounded-lg hover:bg-slate-950/10 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Settings Screen Overlay */}
          {showSettings ? (
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-slate-50 dark:bg-slate-900/40">
              <div className="flex items-center justify-between border-b border-slate-200 dark:border-slate-800/80 pb-2">
                <h5 className="font-bold text-xs flex items-center gap-1.5 uppercase tracking-wider opacity-80">
                  <Database className="w-3.5 h-3.5 text-amber-500" /> Model Configuration
                </h5>
                <button
                  onClick={() => setShowSettings(false)}
                  className="text-xs font-bold text-amber-500 hover:opacity-80 transition-opacity"
                >
                  Exit Settings
                </button>
              </div>

              {/* Provider Selection */}
              <div className="space-y-1.5">
                <label className="text-[10px] font-extrabold uppercase tracking-wider opacity-60">Active Intelligence Engine</label>
                <div className="grid grid-cols-2 gap-2">
                  <button
                    onClick={() => setAiProvider("gemini")}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      aiProvider === "gemini"
                        ? "bg-amber-500/10 border-amber-500 text-amber-500 font-bold"
                        : "bg-white dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-xs opacity-75"
                    }`}
                  >
                    <div className="flex items-center gap-1">
                      <Sparkles className="w-3.5 h-3.5" />
                      <span className="text-xs">Gemini Cloud</span>
                    </div>
                    <span className="text-[9px] opacity-60 block mt-0.5 font-normal">Fast, secure cloud model</span>
                  </button>

                  <button
                    onClick={() => setAiProvider("ollama")}
                    className={`p-3 rounded-xl border text-left transition-all ${
                      aiProvider === "ollama"
                        ? "bg-amber-500/10 border-amber-500 text-amber-500 font-bold"
                        : "bg-white dark:bg-slate-950 border-slate-200 dark:border-slate-800 text-xs opacity-75"
                    }`}
                  >
                    <div className="flex items-center gap-1">
                      <Zap className="w-3.5 h-3.5" />
                      <span className="text-xs">Ollama Local</span>
                    </div>
                    <span className="text-[9px] opacity-60 block mt-0.5 font-normal">Offline-first local models</span>
                  </button>
                </div>
              </div>

              {aiProvider === "ollama" && (
                <div className="space-y-3 border-t border-slate-200 dark:border-slate-800/80 pt-3">
                  {/* Ollama Host URL */}
                  <div className="space-y-1">
                    <label className="text-[10px] font-extrabold uppercase tracking-wider opacity-60">Ollama API Endpoint</label>
                    <input
                      type="text"
                      value={ollamaUrl}
                      onChange={(e) => setOllamaUrl(e.target.value)}
                      placeholder="e.g., http://localhost:11434"
                      className="w-full px-3 py-2 text-xs rounded-lg bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500 font-mono text-xs"
                    />
                  </div>

                  {/* Ollama Model Name */}
                  <div className="space-y-1">
                    <label className="text-[10px] font-extrabold uppercase tracking-wider opacity-60">Target Model Name</label>
                    <input
                      type="text"
                      value={ollamaModel}
                      onChange={(e) => setOllamaModel(e.target.value)}
                      placeholder="e.g., llama3, mistral, gemma"
                      className="w-full px-3 py-2 text-xs rounded-lg bg-white dark:bg-slate-950 border border-slate-200 dark:border-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500 font-mono text-xs"
                    />
                  </div>

                  {/* Request Routing Mode */}
                  <div className="space-y-1">
                    <label className="text-[10px] font-extrabold uppercase tracking-wider opacity-60">Network Routing Layer</label>
                    <div className="grid grid-cols-2 gap-2">
                      <button
                        type="button"
                        onClick={() => setOllamaRouting("client")}
                        className={`p-2 rounded-lg border text-left text-xs transition-all ${
                          ollamaRouting === "client"
                            ? "bg-amber-500/10 border-amber-500 text-amber-500 font-bold"
                            : "bg-white dark:bg-slate-950 border-slate-200 dark:border-slate-800 opacity-75"
                        }`}
                      >
                        <div className="font-bold text-[11px]">Client Direct</div>
                        <span className="text-[9px] opacity-60 block mt-0.5 font-normal">Browser direct fetch</span>
                      </button>

                      <button
                        type="button"
                        onClick={() => setOllamaRouting("server")}
                        className={`p-2 rounded-lg border text-left text-xs transition-all ${
                          ollamaRouting === "server"
                            ? "bg-amber-500/10 border-amber-500 text-amber-500 font-bold"
                            : "bg-white dark:bg-slate-950 border-slate-200 dark:border-slate-800 opacity-75"
                        }`}
                      >
                        <div className="font-bold text-[11px]">Server Proxy</div>
                        <span className="text-[9px] opacity-60 block mt-0.5 font-normal">Express container tunnel</span>
                      </button>
                    </div>
                    {ollamaRouting === "client" ? (
                      <p className="text-[9px] text-amber-600/80 dark:text-amber-500/70 mt-1 leading-normal">
                        ⚠️ Requires starting Ollama with CORS origins enabled: <code className="font-mono bg-slate-200 dark:bg-slate-800 px-1 rounded text-[8px]">OLLAMA_ORIGINS="*" ollama serve</code>
                      </p>
                    ) : (
                      <p className="text-[9px] text-slate-500/70 mt-1 leading-normal">
                        Perfect for public hostings/tunnels. Backend container will resolve connection requests.
                      </p>
                    )}
                  </div>

                  {/* Test Connection Button */}
                  <div className="space-y-2 pt-1">
                    <button
                      type="button"
                      onClick={handleTestOllama}
                      disabled={testingOllama}
                      className="w-full py-2 bg-slate-900 text-white dark:bg-white dark:text-slate-950 hover:opacity-90 rounded-lg text-xs font-bold transition-all flex items-center justify-center gap-1.5"
                    >
                      {testingOllama ? "Pinging endpoint..." : "Test Connection Status"}
                    </button>

                    {ollamaStatusMsg && (
                      <div className={`p-2.5 rounded-lg text-[10px] flex items-start gap-1.5 leading-normal ${
                        ollamaStatusMsg.type === "success" 
                          ? "bg-emerald-500/10 border border-emerald-500/20 text-emerald-500" 
                          : "bg-rose-500/10 border border-rose-500/20 text-rose-500"
                      }`}>
                        {ollamaStatusMsg.type === "success" ? (
                          <CheckCircle2 className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                        ) : (
                          <AlertTriangle className="w-3.5 h-3.5 shrink-0 mt-0.5" />
                        )}
                        <span>{ollamaStatusMsg.text}</span>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <>
              {/* Conversation Logs */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {history.map((msg) => (
                  <div 
                    key={msg.id}
                    className={`flex gap-2.5 max-w-[85%] ${
                      msg.role === "user" ? "ml-auto flex-row-reverse" : "mr-auto"
                    }`}
                  >
                    {/* Avatar */}
                    <div className={`w-8 h-8 rounded-xl flex items-center justify-center shrink-0 border shadow-sm ${
                      msg.role === "user"
                        ? "bg-slate-900 dark:bg-white text-white dark:text-slate-900 border-slate-700"
                        : "bg-amber-500/10 text-amber-500 border-amber-500/20"
                    }`}>
                      {msg.role === "user" ? <User className="w-4.5 h-4.5" /> : <Bot className="w-4.5 h-4.5" />}
                    </div>

                    {/* Message Bubble */}
                    <div className={`p-3 rounded-2xl text-xs leading-relaxed ${
                      msg.role === "user"
                        ? "bg-slate-900 text-white dark:bg-white dark:text-slate-950 rounded-tr-none font-medium"
                        : darkMode 
                          ? "bg-slate-900/60 border border-slate-800 rounded-tl-none text-slate-200" 
                          : "bg-slate-100 rounded-tl-none border border-slate-200 text-slate-800"
                    }`}>
                      <div className="whitespace-pre-line">{formatMarkdown(msg.content)}</div>
                      {msg.id.startsWith("err-") && aiProvider === "ollama" && (
                        <button
                          onClick={() => {
                            setAiProvider("gemini");
                            triggerToast("Switched active provider to Gemini Cloud Core!");
                          }}
                          className="mt-2.5 px-3 py-1.5 bg-amber-500 text-slate-950 font-bold rounded-lg text-[10px] flex items-center space-x-1 hover:bg-amber-400 transition-all cursor-pointer shadow-sm"
                        >
                          <Sparkles className="w-3 h-3" />
                          <span>Switch to Gemini Cloud Engine</span>
                        </button>
                      )}
                      <span className={`block text-[8px] mt-1.5 text-right opacity-50`}>
                        {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                  </div>
                ))}

                {/* AI Typing Indicator */}
                {loading && (
                  <div className="flex gap-2.5 max-w-[85%] mr-auto items-center">
                    <div className="w-8 h-8 rounded-xl bg-amber-500/10 text-amber-500 border border-amber-500/20 flex items-center justify-center shrink-0 shadow-sm animate-pulse">
                      <Bot className="w-4.5 h-4.5" />
                    </div>
                    <div className={`p-3 rounded-2xl rounded-tl-none text-xs flex items-center space-x-1.5 ${
                      darkMode ? "bg-slate-900/60 border border-slate-800" : "bg-slate-100 border border-slate-200"
                    }`}>
                      <span className="w-2 h-2 rounded-full bg-amber-500 animate-bounce" style={{ animationDelay: "0ms" }}></span>
                      <span className="w-2 h-2 rounded-full bg-amber-500 animate-bounce" style={{ animationDelay: "150ms" }}></span>
                      <span className="w-2 h-2 rounded-full bg-amber-500 animate-bounce" style={{ animationDelay: "300ms" }}></span>
                    </div>
                  </div>
                )}
                
                <div ref={chatEndRef} />
              </div>

              {/* Prompt suggestions / chips */}
              <div className="px-4 py-2 border-t border-slate-200 dark:border-slate-800/80 overflow-x-auto flex gap-2 whitespace-nowrap scrollbar-none">
                {suggestedPrompts.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(p)}
                    disabled={loading}
                    className={`px-3 py-1.5 rounded-full text-[10px] font-bold border transition-colors flex items-center space-x-1 ${
                      darkMode
                        ? "bg-slate-900/50 hover:bg-slate-800 border-slate-800 text-amber-500"
                        : "bg-amber-50/50 hover:bg-amber-100 border-amber-200 text-amber-700"
                    }`}
                  >
                    <span>{p}</span>
                    <ArrowRight className="w-2.5 h-2.5" />
                  </button>
                ))}
              </div>
            </>
          )}

          {/* Text Input Footer */}
          <div className="p-3 border-t border-slate-200 dark:border-slate-800/80 flex items-center space-x-2 bg-slate-50/50 dark:bg-slate-950/40">
            <input
              type="text"
              placeholder={aiProvider === "gemini" ? "Query timelines, materials or risks..." : `Query local Ollama model (${ollamaModel})...`}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              disabled={loading}
              className={`flex-1 px-3 py-2 text-xs rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500 ${
                darkMode
                  ? "bg-slate-900 border-slate-800 text-white placeholder-slate-500"
                  : "bg-white border-slate-300 text-slate-900 placeholder-slate-400"
              }`}
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!message.trim() || loading}
              className={`p-2.5 rounded-xl transition-all shadow-lg ${
                message.trim() && !loading
                  ? "bg-amber-500 hover:bg-amber-400 text-slate-950 shadow-amber-500/10"
                  : "bg-slate-200 text-slate-400 dark:bg-slate-900 dark:text-slate-600 shadow-none cursor-not-allowed"
              }`}
            >
              <Send className="w-3.5 h-3.5" />
            </button>
          </div>

        </div>
      )}

      {/* Floating Toggle Icon */}
      <button
        id="hubai-chat-trigger"
        onClick={() => {
          setIsOpen(!isOpen);
          if (!isOpen) {
            triggerToast(
              aiProvider === "gemini" 
                ? "Consulting HubAI Assistant - Live Gemini Core online." 
                : `Consulting HubAI Assistant - Local Ollama model "${ollamaModel}" ready.`
            );
          }
        }}
        className="group relative flex items-center justify-center w-14 h-14 bg-amber-500 hover:bg-amber-400 text-slate-950 rounded-2xl shadow-xl shadow-amber-500/25 transition-all duration-300 transform hover:scale-105 active:scale-95 border-2 border-amber-400 dark:border-amber-600"
      >
        {isOpen ? (
          <X className="w-6 h-6 stroke-[2.5]" />
        ) : (
          <>
            {/* Animated outer notification pulse */}
            <span className="absolute -top-1 -right-1 flex h-3 w-3">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500"></span>
            </span>
            <MessageSquare className="w-6 h-6 group-hover:rotate-6 transition-transform" />
          </>
        )}
      </button>
    </div>
  );
};
