import { useState } from "react";
import Sidebar from "../components/Sidebar";
import Logs from "./Logs";
import Analytics from "./Analytics";

function AdminDashboard({ onLogout }) {
  const [active, setActive] = useState("dashboard");

  return (
    <div className="flex bg-gray-900 text-white">
      {/* Sidebar */}
      <Sidebar active={active} setActive={setActive} onLogout={onLogout} />

      {/* Main Content */}
      <div className="flex-1 p-6">
        {active === "dashboard" && <Analytics />}
        {active === "logs" && <Logs />}
        {active === "analytics" && <Analytics />}
      </div>
    </div>
  );
}

export default AdminDashboard;