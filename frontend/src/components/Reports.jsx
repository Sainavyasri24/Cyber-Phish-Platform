import { useState, useEffect } from "react";
import { fetchLogs } from "../services/api";

function Reports() {
    const [stats, setStats] = useState({ total: 0, high: 0, medium: 0, safe: 0 });
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        loadStats();
    }, []);

    const loadStats = async () => {
        try {
            const res = await fetchLogs();
            const logs = res.data;

            const high = logs.filter(l => l.risk_level === "High").length;
            const medium = logs.filter(l => l.risk_level === "Medium").length;
            const safe = logs.filter(l => l.risk_level === "Low").length;

            setStats({
                total: logs.length,
                high,
                medium,
                safe
            });
        } catch (err) {
            console.error("Failed to load reports data", err);
        }
    };

    const downloadCSV = async () => {
        setLoading(true);
        try {
            const res = await fetchLogs();
            const logs = res.data;

            if (logs.length === 0) {
                alert("No logs available to download.");
                setLoading(false);
                return;
            }

            // Convert JSON to CSV
            const headers = Object.keys(logs[0]).join(",");
            const rows = logs.map(row =>
                Object.values(row).map(value => {
                    if (typeof value === 'object') return `"${JSON.stringify(value).replace(/"/g, '""')}"`;
                    return `"${String(value).replace(/"/g, '""')}"`;
                }).join(",")
            );

            const csvContent = "data:text/csv;charset=utf-8," + [headers, ...rows].join("\n");
            const encodedUri = encodeURI(csvContent);

            // Create hidden link to download
            const link = document.createElement("a");
            link.setAttribute("href", encodedUri);
            link.setAttribute("download", `scan_reports_${new Date().toISOString().slice(0, 10)}.csv`);
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);

        } catch (err) {
            console.error("Download failed", err);
            alert("Failed to generate report.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-4xl text-white animate-fade-in">
            <h2 className="text-2xl font-bold mb-6 font-serif">Reports & Analytics</h2>

            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8">
                <StatCard label="Total Scans" value={stats.total} color="bg-gray-800" />
                <StatCard label="Malicious" value={stats.high} color="bg-red-900/50 border-red-800" />
                <StatCard label="Suspicious" value={stats.medium} color="bg-yellow-900/50 border-yellow-800" />
                <StatCard label="Safe" value={stats.safe} color="bg-green-900/50 border-green-800" />
            </div>

            <div className="bg-[#1a1a1a] p-6 rounded-sm border border-gray-800">
                <h3 className="text-lg font-semibold mb-4 text-blue-400">Export Data</h3>
                <p className="text-sm text-gray-400 mb-6">
                    Download the complete scan history in CSV format for offline analysis or compliance auditing.
                </p>

                <button
                    onClick={downloadCSV}
                    disabled={loading}
                    className={`px-6 py-3 rounded-sm font-semibold text-white flex items-center gap-2 transition-colors ${loading ? "bg-gray-600 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700"
                        }`}
                >
                    {loading ? (
                        <span>Generating...</span>
                    ) : (
                        <>
                            <span>Download CSV Report</span>
                            <span className="text-xl">⬇️</span>
                        </>
                    )}
                </button>
            </div>
        </div>
    );
}

function StatCard({ label, value, color }) {
    return (
        <div className={`${color} p-4 rounded-sm border border-transparent`}>
            <p className="text-gray-400 text-sm uppercase tracking-wider">{label}</p>
            <p className="text-3xl font-bold mt-1">{value}</p>
        </div>
    );
}

export default Reports;
