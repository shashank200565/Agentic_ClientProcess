import { NavLink, Outlet } from "react-router-dom";

const navigation = [
  { to: "/", label: "Upload", end: true },
  { to: "/dashboard", label: "Portfolio" },
];

export function AppShell() {
  return (
    <div className="min-h-screen bg-cloud text-ink">
      <header className="sticky top-0 z-40 border-b border-white/20 bg-brand-radial text-white shadow-[0_10px_30px_rgba(13,63,222,0.16)]">
        <div className="mx-auto flex max-w-[1600px] flex-wrap items-center gap-4 px-5 py-4 lg:px-10">
          <div className="flex min-w-fit items-center gap-3">
            <span className="grid h-10 w-10 place-items-center rounded-full bg-white font-display text-xl font-bold text-brand ring-4 ring-white/20">M</span>
            <div>
              <p className="font-display text-lg font-semibold tracking-tight">Mastikhors</p>
              <p className="text-[10px] uppercase tracking-[0.2em] text-blue-100">Workflow studio</p>
            </div>
          </div>
          <nav className="order-3 flex w-full gap-2 overflow-x-auto lg:order-none lg:ml-8 lg:w-auto">
          {navigation.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) => `flex items-center justify-between rounded-full px-4 py-3 text-sm transition ${isActive ? "bg-white text-ink shadow-lg" : "text-blue-100 hover:bg-white/15 hover:text-white"}`}
            >
              {item.label}
            </NavLink>
          ))}
          </nav>
          <div className="ml-auto hidden items-center gap-3 rounded-full border border-white/20 bg-white/10 px-4 py-2 backdrop-blur sm:flex">
            <span className="grid h-7 w-7 place-items-center rounded-full bg-white/20 text-xs font-bold text-white">IM</span>
            <div><p className="text-[10px] font-bold uppercase tracking-[0.14em] text-blue-100">Investment management</p><p className="text-xs text-white/75">Depth over generic advice</p></div>
          </div>
          <span className="ml-auto rounded-full bg-white px-3 py-1.5 text-xs font-semibold text-brand sm:ml-0">Demo workspace</span>
        </div>
      </header>
      <main className="min-h-screen">
        <div className="mx-auto max-w-[1600px] px-5 py-5 lg:px-10 lg:py-7">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
