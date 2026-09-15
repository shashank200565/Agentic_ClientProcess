import { NavLink, Outlet } from "react-router-dom";

const navigation = [
  { to: "/", label: "Upload", end: true },
  { to: "/dashboard", label: "Portfolio" },
  { to: "/resume", label: "Resume session" },
];

export function AppShell() {
  return (
    <div className="min-h-screen bg-cloud text-ink">
      <aside className="fixed inset-y-0 left-0 hidden w-72 flex-col bg-brand-radial px-7 py-8 text-white lg:flex">
        <div className="mb-16">
          <div className="mb-4 flex items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-full bg-white font-display text-xl font-bold text-brand ring-4 ring-white/20">M</span>
            <div>
              <p className="font-display text-lg font-semibold tracking-tight">Mastikhors</p>
              <p className="text-[11px] uppercase tracking-[0.2em] text-blue-100">Workflow studio</p>
            </div>
          </div>
          <p className="max-w-[190px] text-sm leading-6 text-blue-100">A sharper way to decide what deserves automation.</p>
        </div>
        <nav className="space-y-2">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `flex items-center justify-between rounded-full px-4 py-3 text-sm transition ${isActive ? "bg-white text-ink shadow-lg" : "text-blue-100 hover:bg-white/15 hover:text-white"}`}
            >
              {item.label}
              {item.label === "Resume session" && <span className="rounded-full bg-white/10 px-2 py-0.5 text-[10px]">soon</span>}
            </NavLink>
          ))}
        </nav>
          <div className="mt-auto rounded-3xl border border-white/20 bg-white/10 p-4 backdrop-blur">
          <p className="mb-1 text-xs font-semibold uppercase tracking-[0.16em] text-blue-100">Investment management</p>
          <p className="text-sm leading-5 text-white/75">Depth over generic workflow advice.</p>
        </div>
      </aside>
      <main className="min-h-screen lg:pl-72">
        <header className="flex items-center justify-between border-b border-blue-100/70 bg-white/75 px-6 py-5 backdrop-blur lg:px-12">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-brand">Diagnostic workspace</p>
            <p className="mt-1 font-display text-sm text-slate-500">From workflow friction to a defensible next move.</p>
          </div>
          <div className="rounded-full border border-blue-100 bg-white px-4 py-2 text-xs font-medium text-slate-500 shadow-sm">Demo workspace</div>
        </header>
        <div className="px-6 py-8 lg:px-12 lg:py-12">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
