import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { checkHealth } from "../api/client";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const { email, logout } = useAuth();
  const navigate = useNavigate();
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    checkHealth().then(setOnline);
    const id = setInterval(() => checkHealth().then(setOnline), 15000);
    return () => clearInterval(id);
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <aside className="w-56 min-h-screen bg-slate-900 flex flex-col py-6 px-4 shrink-0">
      <div className="mb-8">
        <h1 className="text-white font-bold text-xl tracking-tight">QueryPilot</h1>
        <p className="text-slate-400 text-xs mt-1">NL → SQL Agent</p>
      </div>

      <nav className="flex flex-col gap-1 flex-1">
        <NavLink
          to="/"
          end
          className={({ isActive }) =>
            `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              isActive
                ? "bg-blue-600 text-white"
                : "text-slate-400 hover:text-white hover:bg-slate-800"
            }`
          }
        >
          Query
        </NavLink>
        <NavLink
          to="/history"
          className={({ isActive }) =>
            `px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
              isActive
                ? "bg-blue-600 text-white"
                : "text-slate-400 hover:text-white hover:bg-slate-800"
            }`
          }
        >
          History
        </NavLink>
      </nav>

      <div className="mt-auto pt-4 border-t border-slate-800 flex flex-col gap-3">
        <div className="flex items-center gap-2">
          <span
            className={`w-2 h-2 rounded-full shrink-0 ${
              online === null ? "bg-slate-500" : online ? "bg-emerald-400" : "bg-red-400"
            }`}
          />
          <span className="text-slate-400 text-xs">
            {online === null ? "Checking..." : online ? "API online" : "API offline"}
          </span>
        </div>

        {email && (
          <div className="flex flex-col gap-1">
            <p className="text-slate-500 text-xs truncate" title={email}>{email}</p>
            <button
              onClick={handleLogout}
              className="text-left text-slate-400 hover:text-white text-xs transition-colors"
            >
              Sign out
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
