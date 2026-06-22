import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { checkHealth } from "../api/client";
import { useAuth } from "../context/AuthContext";

const NAV_ITEMS = [
  { to: "/", label: "Query", icon: "⚡", end: true },
  { to: "/history", label: "History", icon: "🕓", end: false },
];

export default function Navbar() {
  const { email, logout } = useAuth();
  const navigate = useNavigate();
  const [online, setOnline] = useState<boolean | null>(null);

  useEffect(() => {
    checkHealth().then(setOnline);
    const id = setInterval(() => checkHealth().then(setOnline), 15000);
    return () => clearInterval(id);
  }, []);

  const handleLogout = () => { logout(); navigate("/login"); };

  return (
    <aside className="w-60 min-h-screen bg-slate-950 flex flex-col py-5 shrink-0 border-r border-slate-800">
      {/* Logo */}
      <div className="flex items-center gap-2.5 px-5 mb-8">
        <div className="w-7 h-7 rounded-lg bg-blue-500 flex items-center justify-center text-white font-bold text-xs shrink-0">Q</div>
        <div>
          <p className="text-white font-semibold text-sm leading-none">QueryPilot</p>
          <p className="text-slate-500 text-[10px] mt-0.5">NL → SQL Agent</p>
        </div>
      </div>

      {/* Nav */}
      <nav className="flex flex-col gap-0.5 px-3 flex-1">
        <p className="text-slate-600 text-[10px] font-semibold uppercase tracking-widest px-2 mb-2">Navigation</p>
        {NAV_ITEMS.map(({ to, label, icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              `flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-150 ${
                isActive
                  ? "bg-blue-600 text-white shadow-md shadow-blue-900/40"
                  : "text-slate-400 hover:text-slate-100 hover:bg-slate-800/60"
              }`
            }
          >
            <span className="text-base leading-none">{icon}</span>
            {label}
          </NavLink>
        ))}
      </nav>

      {/* Footer */}
      <div className="px-3 pt-4 border-t border-slate-800 mt-4">
        {/* Status */}
        <div className="flex items-center gap-2 px-3 py-2 mb-2">
          <span className={`w-1.5 h-1.5 rounded-full shrink-0 ${
            online === null ? "bg-slate-600" : online ? "bg-emerald-400" : "bg-red-400"
          }`} />
          <span className="text-slate-500 text-xs">
            {online === null ? "Connecting..." : online ? "API connected" : "API offline"}
          </span>
        </div>

        {/* User */}
        {email && (
          <div className="flex items-center gap-2.5 px-3 py-2 rounded-lg hover:bg-slate-800/60 transition-colors group cursor-default">
            <div className="w-6 h-6 rounded-full bg-blue-600 flex items-center justify-center text-white text-[10px] font-bold shrink-0">
              {email[0].toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-slate-300 text-xs font-medium truncate">{email}</p>
            </div>
            <button
              onClick={handleLogout}
              title="Sign out"
              className="text-slate-600 hover:text-slate-300 transition-colors opacity-0 group-hover:opacity-100"
            >
              <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a2 2 0 01-2 2H5a2 2 0 01-2-2V7a2 2 0 012-2h6a2 2 0 012 2v1" />
              </svg>
            </button>
          </div>
        )}
      </div>
    </aside>
  );
}
