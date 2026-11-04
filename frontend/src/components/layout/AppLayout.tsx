import { NavLink, Outlet } from "react-router-dom";
import { FileText, MessageSquare } from "lucide-react";

const navItems = [
  { to: "/", label: "Documents", icon: FileText },
  { to: "/chat", label: "Chat", icon: MessageSquare },
];

export default function AppLayout() {
  return (
    <div className="flex h-screen flex-col bg-gray-50 text-gray-900">
      {/* ── Top bar ── */}
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-gray-200 bg-white px-6">
        <span className="text-lg font-semibold tracking-tight text-indigo-700">
          DocuMind AI
        </span>

        <nav className="flex gap-1">
          {navItems.map(({ to, label, icon: Icon }) => (
            <NavLink
              key={to}
              to={to}
              end={to === "/"}
              className={({ isActive }) =>
                `inline-flex items-center gap-2 rounded-md px-3 py-1.5 text-sm font-medium transition-colors ${
                  isActive
                    ? "bg-indigo-50 text-indigo-700"
                    : "text-gray-600 hover:bg-gray-100 hover:text-gray-900"
                }`
              }
            >
              <Icon className="h-4 w-4" />
              {label}
            </NavLink>
          ))}
        </nav>
      </header>

      {/* ── Main content ── */}
      <main className="flex-1 overflow-y-auto">
        <Outlet />
      </main>
    </div>
  );
}

