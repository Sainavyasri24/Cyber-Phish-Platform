import { useState, useEffect } from "react";
import { scanURL } from "../services/api";
import RiskCard from "../components/RiskCard";
import Logs from "./Logs";
import Settings from "../components/Settings";
import Reports from "../components/Reports";
import Help from "../components/Help";

function UserScan({ onLogout }) {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [currentTime, setCurrentTime] = useState("");
  const [activeTab, setActiveTab] = useState("Dashboard");

  // Live IST clock
  useEffect(() => {
    const timer = setInterval(() => {
      const now = new Date();
      const timeString = now.toLocaleString("en-IN", {
        weekday: "long",
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "numeric",
        minute: "numeric",
        second: "numeric",
        timeZone: "Asia/Kolkata",
      });
      setCurrentTime(`${timeString} IST`);
    }, 1000);
    return () => clearInterval(timer);
  }, []);

  const handleScan = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setResult(null);
    setError("");

    try {
      const res = await scanURL(url);
      setResult(res.data);
    } catch (err) {
      console.error(err);
      setError("Scan failed. Please check that the backend is running and try again.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleScan();
  };

  const navItems = ["Dashboard", "Logs", "Settings", "Reports", "Help"];

  const renderContent = () => {
    switch (activeTab) {
      case "Dashboard":
        return (
          <div className="max-w-4xl animate-fade-in">
            <h2 className="text-2xl font-bold mb-6 text-white font-serif">
              URL Scanner
            </h2>

            {/* Input Row */}
            <div className="mb-6">
              <p className="mb-2 text-sm font-medium text-gray-400 uppercase tracking-wider">
                Enter a URL to scan
              </p>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="https://example.com"
                  className="border border-gray-700 p-2.5 flex-1 max-w-xl rounded bg-[#111] text-white placeholder-gray-600 focus:outline-none focus:border-blue-500 transition-colors"
                />
                <button
                  onClick={handleScan}
                  disabled={loading}
                  className={`px-6 py-2.5 rounded font-semibold transition-all shadow-sm text-white
                    ${loading
                      ? "bg-blue-800 cursor-not-allowed"
                      : "bg-[#1976d2] hover:bg-[#1565c0] active:scale-95"
                    }`}
                >
                  {loading ? (
                    <span className="flex items-center gap-2">
                      <span className="animate-scan-pulse">●</span>
                      Scanning…
                    </span>
                  ) : (
                    "Scan"
                  )}
                </button>
              </div>

              {/* Inline error */}
              {error && (
                <div className="mt-3 flex items-center gap-2 text-sm text-red-400 bg-red-900/20 border border-red-800 rounded px-4 py-2.5 animate-fade-in">
                  <span>⚠️</span>
                  <span>{error}</span>
                </div>
              )}
            </div>

            {/* Results Area */}
            {result ? (
              <div className="animate-fade-in">
                <RiskCard data={result} />
              </div>
            ) : (
              !loading && !error && (
                <div className="h-48 flex flex-col items-center justify-center text-gray-700 border border-dashed border-gray-800 rounded gap-3">
                  <span className="text-4xl">🔍</span>
                  <p className="text-sm">Enter a URL above and click Scan</p>
                </div>
              )
            )}

            {/* Footer clock */}
            <div className="mt-10 text-xs text-gray-600">
              <p>{currentTime}</p>
            </div>
          </div>
        );
      case "Logs":
        return <Logs />;
      case "Settings":
        return <Settings />;
      case "Reports":
        return <Reports />;
      case "Help":
        return <Help />;
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen flex flex-col font-sans text-sm bg-black text-white">
      {/* Header */}
      <div className="bg-black px-6 py-4 flex justify-between items-center border-b border-gray-800">
        <div className="flex items-center gap-3">
          <span className="text-2xl">🛡️</span>
          <h1 className="text-2xl font-bold text-white tracking-tight font-serif">
            Secure Web Gateway
          </h1>
        </div>
        <button
          onClick={onLogout}
          className="text-gray-400 hover:text-white text-sm font-medium transition-colors border border-gray-700 px-3 py-1 rounded hover:bg-gray-800"
        >
          Logout
        </button>
      </div>

      {/* Tab Nav */}
      <div className="bg-[#0a0a0a] px-6 flex items-center border-b border-gray-900">
        <div className="flex space-x-0">
          {navItems.map((item) => (
            <button
              key={item}
              onClick={() => setActiveTab(item)}
              className={`px-4 py-3 text-sm font-medium transition-colors border-b-2
                ${activeTab === item
                  ? "text-white border-[#1976d2]"
                  : "text-gray-500 border-transparent hover:text-gray-300 hover:border-gray-700"
                }`}
            >
              {item}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 p-8 bg-black">
        {renderContent()}
      </div>
    </div>
  );
}

export default UserScan;