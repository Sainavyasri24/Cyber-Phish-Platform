import React from "react";

function Sidebar({ active, setActive, onLogout }) {
  const menu = [
    { id: "scan", label: "Scanner", icon: "🔍" },
    { id: "dashboard", label: "SOC Dashboard", icon: "📊" },
    { id: "logs", label: "Threat Logs", icon: "🛡" },
    { id: "analytics", label: "Analytics", icon: "📈" }
  ];

  return (
    <div className="w-64 min-h-screen bg-cyber-secondary border-r border-gray-800 text-white p-4 flex flex-col">
      <div className="mb-10 text-center pt-4">
        <h2 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-neon-blue to-neon-green font-mono">
          CYBER SENTRY
        </h2>
        <div className="h-0.5 w-16 bg-neon-blue mx-auto mt-2 rounded-full shadow-neon-blue"></div>
      </div>

      <ul className="space-y-4 flex-1">
        {menu.map((item) => (
          <li
            key={item.id}
            onClick={() => setActive(item.id)}
            className={`cursor-pointer p-3 rounded-lg flex items-center gap-3 transition-all duration-300 font-mono text-sm border border-transparent
              ${active === item.id
                ? "bg-neon-blue/10 text-neon-blue border-neon-blue/30 shadow-neon-blue"
                : "text-gray-400 hover:text-white hover:bg-white/5"}`}
          >
            <span className="text-lg">{item.icon}</span>
            {item.label}
          </li>
        ))}
      </ul>

      <div className="mt-auto border-t border-gray-800 pt-4 text-center">
        <div className="flex flex-col items-center justify-center gap-2 text-xs text-gray-500 font-mono">
          <button
            onClick={onLogout}
            className="text-gray-400 hover:text-white mb-2 text-sm font-medium transition-colors border border-gray-700 px-3 py-1 rounded hover:bg-gray-800"
          >
            Logout
          </button>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-neon-green rounded-full animate-pulse"></div>
            SYSTEM SECURE
          </div>
        </div>
      </div>
    </div>
  );
}

export default Sidebar;