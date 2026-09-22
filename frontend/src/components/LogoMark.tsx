export function LogoMark() {
  return (
    <svg
      aria-hidden="true"
      className="h-7 w-7"
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <defs>
        <linearGradient id="reflow-logo-gradient" x1="5" y1="25" x2="27" y2="7" gradientUnits="userSpaceOnUse">
          <stop stopColor="var(--color-brand-deep)" />
          <stop offset="0.55" stopColor="var(--color-brand)" />
          <stop offset="1" stopColor="var(--color-brand-soft)" />
        </linearGradient>
      </defs>
      <path d="M8 22C12 22 12.5 10 17 10C21 10 20 19 25 19" stroke="url(#reflow-logo-gradient)" strokeWidth="2.5" strokeLinecap="round" />
      <circle cx="7" cy="22" r="3.5" fill="var(--color-brand-deep)" />
      <circle cx="25" cy="19" r="3.5" fill="var(--color-brand)" />
    </svg>
  );
}
