import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import { motion } from "framer-motion";
import { useWorkspace } from "../context/WorkspaceContext";
import { Send, Bot, User, CornerDownLeft, Sparkles, Terminal } from "lucide-react";

export const WorkspaceChat = () => {
  const { workspaceId, triggerRefresh } = useWorkspace();
  const [messages, setMessages] = useState([
    { role: "assistant", content: "Hello! I am your AI compliance drafting assistant. You can ask me to query corporate facts, request draft rewrites, or approve section workflow statuses." }
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;
    
    const userMsg = input.trim();
    setInput("");
    
    setMessages(prev => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const res = await axios.post(`/api/workspaces/${workspaceId}/chat`, {
        message: userMsg
      });
      
      if (res.data) {
        setMessages(prev => [...prev, { 
          role: "assistant", 
          content: res.data.agent_response,
          actions: res.data.actions_executed || []
        }]);
        // Trigger a background telemetry refresh in case actions updated statuses/revisions
        triggerRefresh();
      }
    } catch (err) {
      setMessages(prev => [...prev, { 
        role: "assistant", 
        content: "Error interacting with chat agent. Verify backend server is online." 
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-80px)] text-gray-300">
      {/* Header Panel */}
      <div className="flex justify-between items-center mb-6 flex-shrink-0">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">OS AI Assistant</h1>
          <p className="text-gray-400 mt-1">Cursor AI-style workspace terminal helper executing text-to-code database actions.</p>
        </div>
      </div>

      {/* Main chat layout */}
      <div className="flex-1 bg-darkCard border border-gray-800 rounded-xl flex flex-col overflow-hidden shadow-xl min-h-0">
        {/* Messages bubble flow panel */}
        <div className="flex-1 p-6 overflow-y-auto space-y-4 min-h-0 bg-darkBg/10">
          {messages.map((msg, idx) => (
            <div 
              key={idx} 
              className={`flex space-x-3 max-w-3xl ${msg.role === "user" ? "ml-auto flex-row-reverse space-x-reverse" : "mr-auto"}`}
            >
              {/* Avatar Icon */}
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center border flex-shrink-0 ${
                msg.role === "user" 
                  ? "bg-primaryAccent/10 border-primaryAccent/20 text-primaryAccent" 
                  : "bg-purple-500/10 border-purple-500/20 text-purple-400"
              }`}>
                {msg.role === "user" ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
              </div>

              {/* Message content bubble */}
              <div className={`p-4 rounded-xl text-sm border leading-relaxed ${
                msg.role === "user" 
                  ? "bg-primaryAccent/5 border-primaryAccent/20 text-white" 
                  : "bg-darkCard border-gray-850 text-gray-200"
              }`}>
                {/* Custom formatted text parsing helper */}
                <div className="whitespace-pre-wrap font-sans">
                  {msg.content}
                </div>

                {/* System actions logs if any executed */}
                {msg.actions && msg.actions.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-gray-800/85 space-y-2">
                    <span className="text-[10px] font-bold text-gray-500 uppercase tracking-wider flex items-center space-x-1.5">
                      <Terminal className="w-3.5 h-3.5" />
                      <span>System Actions Executed</span>
                    </span>
                    {msg.actions.map((act, aIdx) => (
                      <div key={aIdx} className="text-xs bg-darkBg border border-gray-850 p-2.5 rounded-lg flex items-center justify-between text-gray-400">
                        <span>Action: <span className="font-semibold text-white uppercase">{act.action}</span></span>
                        <span>Section: <span className="font-mono text-primaryAccent">{act.section_slug}</span></span>
                        {act.new_version && <span>Version: <span className="font-bold text-white">v{act.new_version}</span></span>}
                        {act.new_status && <span className="text-green-500 font-bold">{act.new_status}</span>}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {loading && (
            <div className="flex space-x-3 mr-auto">
              <div className="w-8 h-8 rounded-lg flex items-center justify-center bg-purple-500/10 border border-purple-500/20 text-purple-400">
                <Bot className="w-4 h-4" />
              </div>
              <div className="bg-darkCard border border-gray-850 p-4 rounded-xl text-sm text-gray-500 flex items-center space-x-2">
                <Sparkles className="w-4 h-4 animate-spin text-purple-400" />
                <span>AI Agent is drafting revision modifications...</span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Input prompt text bar */}
        <form onSubmit={handleSend} className="p-4 border-t border-gray-800 bg-darkBg/30 flex-shrink-0">
          <div className="relative bg-darkBg border border-gray-850 focus-within:border-primaryAccent focus-within:ring-1 focus-within:ring-primaryAccent rounded-xl p-3 flex items-center transition-all">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === "Enter" && !e.shiftKey) {
                  e.preventDefault();
                  handleSend(e);
                }
              }}
              rows={1}
              placeholder="Ask a question, request a draft rewrite, or approve a section status..."
              className="flex-1 bg-transparent border-0 outline-none text-sm text-white placeholder-gray-500 resize-none font-sans"
            />
            <button
              type="submit"
              disabled={loading || !input.trim()}
              className="ml-3 p-2 bg-primaryAccent hover:bg-blue-650 text-white rounded-lg transition-all disabled:opacity-50 disabled:hover:bg-primaryAccent"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <div className="mt-2 text-[10px] text-gray-500 text-center flex items-center justify-center space-x-2">
            <span>Press Enter to send</span>
            <span>•</span>
            <span>Shift + Enter for new line</span>
          </div>
        </form>
      </div>
    </div>
  );
};
export default WorkspaceChat;
