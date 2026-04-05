import { useEffect, useState } from "react";
import { fetchLogs } from "../services/api";

function Logs() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadLogs();
  }, []);

  const loadLogs = async () => {
    setLoading(true);
    setError("");
    try {
      const res = await fetchLogs();
      setLogs(res.data);
    } catch (err) {
      console.error(err);
      setError("Failed to load logs. Make sure you are logged in and the backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const riskColor = (level) => {
    if (level === "High")   return "text-red-400 bg-red-900/20";
    if (level === "Medium") return "text-yellow-400 bg-yellow-900/20";
    return "text-green-400 bg-green-900/10";
  };

  const riskBadge = (level) => {
    if (level === "High")   return "bg-red-900/40 text-red-400 border border-red-800";
    if (level === "Medium") return "bg-yellow-900/40 text-yellow-400 border border-yellow-800";
    return "bg-green-900/30 text-green-400 border border-green-800";
  };

  return (
    <div className="max-w-5xl animate-fade-in">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white font-serif">Threat Logs</h2>
        <button
          onClick={loadLogs}
          className="text-xs text-gray-500 hover:text-gray-300 border border-gray-800 hover:border-gray-600 px-3 py-1.5 rounded transition-colors"
        >
          ↻ Refresh
        </button>
      </div>

      {/* Loading */}
      {loading && (
        <div className="flex items-center gap-3 text-gray-500 py-16 justify-center">
          <span className="animate-scan-pulse text-2xl">🔄</span>
          <span className="text-sm">Loading logs…</span>
        </div>
      )}

      {/* Error */}
      {error && !loading && (
        <div className="flex items-center gap-2 text-sm text-red-400 bg-red-900/20 border border-red-800 rounded px-4 py-3">
          <span>⚠️</span> {error}
        </div>
      )}

      {/* Empty state */}
      {!loading && !error && logs.length === 0 && (
        <div className="flex flex-col items-center justify-center py-20 text-gray-700 border border-dashed border-gray-800 rounded gap-3">
          <span className="text-4xl">📋</span>
          <p className="text-sm">No scan logs yet. Scan a URL to get started.</p>
        </div>
      )}

      {/* Table */}
      {!loading && !error && logs.length > 0 && (
        <div className="overflow-x-auto rounded border border-gray-800">
          <table className="w-full text-xs">
            <thead>
              <tr className="bg-[#111] text-gray-500 uppercase tracking-wider">
                <th className="text-left px-4 py-3 font-medium">URL</th>
                <th className="text-left px-4 py-3 font-medium w-24">Risk</th>
                <th className="text-left px-4 py-3 font-medium w-16">Score</th>
                <th className="text-left px-4 py-3 font-medium w-36">Action</th>
                <th className="text-left px-4 py-3 font-medium w-40">Model</th>
                <th className="text-left px-4 py-3 font-medium w-44">Time</th>
              </tr>
            </thead>
            <tbody>
              {logs.map((log, i) => (
                <tr
                  key={log.id ?? i}
                  className={`border-t border-gray-900 transition-colors hover:bg-white/5 ${riskColor(log.risk_level)}`}
                >
                  <td className="px-4 py-3 max-w-xs">
                    <span className="block truncate text-white" title={log.url}>
                      {log.url}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${riskBadge(log.risk_level)}`}>
                      {log.risk_level}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-gray-300">
                    {Math.round((log.threat_score ?? 0) * 100)}%
                  </td>
                  <td className="px-4 py-3 text-gray-300">{log.action}</td>
                  <td className="px-4 py-3 text-gray-500">{log.model_used}</td>
                  <td className="px-4 py-3 text-gray-600 text-xs">
                    {log.timestamp ? new Date(log.timestamp).toLocaleString("en-IN", { timeZone: "Asia/Kolkata" }) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <div className="px-4 py-2 text-right text-xs text-gray-700 border-t border-gray-900">
            {logs.length} record{logs.length !== 1 ? "s" : ""}
          </div>
        </div>
      )}
    </div>
  );
}

export default Logs;