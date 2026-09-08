import { NavLink, Outlet } from "react-router-dom";

const navigation = [
  { to: "/", label: "Upload", end: true },
  { to: "/dashboard", label: "Portfolio" },
  { to: "/resume", label: "Resume session" },
];

export function AppShell() {
  return (
    <div className="min-h-screen bg-[#f6f7f2] text-slate-900">
      <aside className="fixed inset-y-0 left-0 hidden w-72 flex-col border-r border-slate-200 bg-[#102a2c] px-7 py-8 text-white lg:flex">
        <div className="mb-16">
          <div className="mb-4 flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-[#f2c14e] font-display text-xl font-bold text-[#102a2c]">M</span>
            <div>
              <p className="font-display text-lg font-semibold tracking-tight">Mastikhors</p>
              <p className="text-[11px] uppercase tracking-[0.2em] text-teal-200">Workflow studio</p>
            </div>
          </div>
          <p className="max-w-[190px] text-sm leading-6 text-slate-300">A sharper way to decide what deserves automation.</p>
        </div>
        <nav className="space-y-2">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `flex items-center justify-between rounded-xl px-4 py-3 text-sm transition ${isActive ? "bg-white/12 text-white" : "text-slate-400 hover:bg-white/6 hover:text-white"}`}
            >
              {item.label}
              {item.label === "Resume session" && <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px]">soon</span>}
            </NavLink>
          ))}
        </nav>
        <div className="mt-auto rounded-2xl border border-white/10 bg-white/6 p-4">
          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.16em] text-[#f2c14e]">Investment management</p>
          <p className="text-sm leading-5 text-slate-300">Depth over generic workflow advice.</p>
        </div>
      </aside>
      <main className="min-h-screen lg:pl-72">
        <header className="flex items-center justify-between border-b border-slate-200 bg-[#f6f7f2]/90 px-6 py-5 backdrop-blur lg:px-12">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-teal-700">Diagnostic workspace</p>
            <p className="mt-1 font-display text-sm text-slate-500">From workflow friction to a defensible next move.</p>
          </div>
          <div className="rounded-full border border-slate-200 bg-white px-3 py-1.5 text-xs font-medium text-slate-500">Demo workspace</div>
        </header>
        <div className="px-6 py-8 lg:px-12 lg:py-12">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
