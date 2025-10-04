import { Link, NavLink } from "react-router-dom";
import { ReactNode } from "react";

const nav = [
  { to: "/admin/dashboard", label: "Overview" },
  { to: "/admin/videos", label: "Videos" },
  { to: "/admin/automation", label: "Automation" },
  { to: "/admin/social", label: "Social" },
  { to: "/admin/financial", label: "Financial" },
  { to: "/admin/leads", label: "Leads" },
];

export default function AdminLayout({
  children,
  onLogout,
}: { children: ReactNode; onLogout?: () => void }) {
  return (
    <div className="min-h-screen grid grid-cols-[240px_1fr]">
      <aside className="border-r bg-white">
        <div className="p-4 border-b">
          <Link to="/" className="font-bold">AutoPro Daune</Link>
          <div className="text-xs text-muted-foreground">Admin</div>
        </div>
        <nav className="p-2 space-y-1">
          {nav.map((i) => (
            <NavLink
              key={i.to}
              to={i.to}
              className={({ isActive }) =>
                `block rounded px-3 py-2 text-sm ${isActive ? "bg-gray-100 font-medium" : "hover:bg-gray-50"}`
              }
            >
              {i.label}
            </NavLink>
          ))}
        </nav>
        <div className="p-4 mt-auto">
          <button
            onClick={onLogout}
            className="w-full text-left text-sm text-red-600 hover:underline"
          >
            Logout
          </button>
        </div>
      </aside>
      <main className="p-6 bg-gray-50">{children}</main>
    </div>
  );
}