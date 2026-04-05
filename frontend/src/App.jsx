import { Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import UserScan from "./pages/UserScan";
import AdminDashboard from "./pages/AdminDashboard";

function ProtectedRoute({ children }) {
  const token = localStorage.getItem("phish_token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}

function App() {
  const handleLogout = () => {
    localStorage.removeItem("phish_token");
    window.location.href = "/login";
  };

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />

      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <UserScan onLogout={handleLogout} />
          </ProtectedRoute>
        }
      />

      {/* 
        For now, treating root as Dashboard. 
        Later we can have a landing page. 
      */}
      <Route path="/" element={<Navigate to="/dashboard" replace />} />

      {/* Admin Route - simplified for now */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute>
            <AdminDashboard onLogout={handleLogout} />
          </ProtectedRoute>
        }
      />

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}

export default App;