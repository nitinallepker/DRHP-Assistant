import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { 
  Home, 
  Folder, 
  Brain, 
  FileText, 
  Search, 
  Sparkles, 
  Palette, 
  Download, 
  MessageSquare,
  ChevronLeft,
  ChevronRight,
  Briefcase
} from "lucide-react";
import { useWorkspace } from "../context/WorkspaceContext";

export const Sidebar = ({ onCollapse }) => {
  const { workspaceName, workspaceStatus } = useWorkspace();
  const [collapsed, setCollapsed] = useState(false);

  const toggleCollapse = (val) => {
    setCollapsed(val);
    if (onCollapse) onCollapse(val);
  };

  const navItems = [
    { to: "/", icon: <Home className="w-5 h-5" />, label: "Dashboard", activeColor: "text-blue-500" },
    { to: "/workspace", icon: <Folder className="w-5 h-5" />, label: "Workspace", activeColor: "text-green-500" },
    { to: "/repository", icon: <Brain className="w-5 h-5" />, label: "Knowledge", activeColor: "text-purple-500" },
    { to: "/drhp", icon: <FileText className="w-5 h-5" />, label: "DRHP Page", activeColor: "text-amber-500" },
    { to: "/review", icon: <Search className="w-5 h-5" />, label: "Review", activeColor: "text-red-500" },
    { to: "/improvement", icon: <Sparkles className="w-5 h-5" />, label: "Improvement", activeColor: "text-indigo-500" },
    { to: "/transformation", icon: <Palette className="w-5 h-5" />, label: "Transformation", activeColor: "text-pink-500" },
    { to: "/export", icon: <Download className="w-5 h-5" />, label: "Export", activeColor: "text-teal-500" },
    { to: "/chat", icon: <MessageSquare className="w-5 h-5" />, label: "Workspace Chat", activeColor: "text-cyan-500" },
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case "READY":
        return "bg-green-500";
      case "PROCESSING":
        return "bg-yellow-500 animate-pulse";
      case "FAILED":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  return (
    <aside 
      className={`bg-darkCard border-r border-gray-800/80 flex flex-col h-screen fixed left-0 top-0 text-gray-300 transition-all duration-300 z-30 ${
        collapsed ? "w-20" : "w-64"
      }`}
    >
      {/* Brand Header */}
      <div className="p-5 border-b border-gray-800 flex items-center justify-between overflow-hidden">
        {!collapsed && (
          <div>
            <h1 className="text-sm font-bold text-white tracking-wider flex items-center space-x-2">
              <Briefcase className="w-4 h-4 text-primaryAccent" />
              <span>DRHP Assistant</span>
            </h1>
            <p className="text-[10px] text-gray-400 font-semibold normal-case mt-1 leading-tight">Companies can make your DRHP at ease for IPO</p>
          </div>
        )}
        {collapsed && (
          <div className="mx-auto text-primaryAccent">
            <Briefcase className="w-6 h-6" />
          </div>
        )}
        
        {/* Toggle Collapse Button */}
        {!collapsed && (
          <button 
            onClick={() => toggleCollapse(true)}
            className="p-1 hover:bg-gray-800 rounded text-gray-500 hover:text-white transition-colors"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
        )}
      </div>

      {/* Expanded Workspace indicator card */}
      {!collapsed && (
        <div className="p-4 mx-4 my-4 bg-darkBg/60 border border-gray-800 rounded-xl">
          <div className="flex items-center space-x-2">
            <span className={`w-2 h-2 rounded-full ${getStatusColor(workspaceStatus)}`} />
            <span className="text-[9px] uppercase font-bold text-gray-500 tracking-wider">IPO PROJECT STATUS</span>
          </div>
          <h2 className="text-xs font-bold text-white mt-1.5 truncate" title={workspaceName}>
            {workspaceName}
          </h2>
          <p className="text-[10px] text-gray-400 mt-0.5 uppercase font-mono">{workspaceStatus}</p>
        </div>
      )}

      {/* Navigation menu */}
      <nav className="flex-1 px-3 space-y-1 overflow-y-auto py-2">
        {navItems.map((item, idx) => (
          <NavLink
            key={idx}
            to={item.to}
            className={({ isActive }) =>
              `flex items-center rounded-lg text-xs font-semibold transition-all ${
                collapsed ? "justify-center p-3" : "space-x-3 px-4 py-3"
              } ${
                isActive
                  ? "bg-darkBg border border-gray-800 text-white shadow-xl"
                  : "hover:bg-gray-800/40 text-gray-400 hover:text-white"
              }`
            }
            title={collapsed ? item.label : ""}
          >
            {({ isActive }) => (
              <>
                <span className={isActive ? item.activeColor : "text-gray-500"}>
                  {item.icon}
                </span>
                {!collapsed && <span>{item.label}</span>}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Collapse Trigger for Collapsed Sidebar */}
      {collapsed && (
        <button 
          onClick={() => toggleCollapse(false)}
          className="p-3 hover:bg-gray-800 text-gray-500 hover:text-white mx-auto my-3 rounded-lg border border-gray-800/80 transition-colors"
          title="Expand Navigation"
        >
          <ChevronRight className="w-4 h-4" />
        </button>
      )}

      {/* Sidebar Footer */}
      {!collapsed && (
        <div className="p-4 border-t border-gray-800/60 text-[9px] text-gray-600 text-center font-bold tracking-wide uppercase">
          DRHP Assistant v1.0
        </div>
      )}
    </aside>
  );
};
export default Sidebar;
