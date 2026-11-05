export default function Header() {
  return (
    <header className="site-header">
      <div className="brand">
        <svg viewBox="0 0 64 64" aria-hidden="true">
          <rect width="64" height="64" rx="12" fill="#121a15" />
          <path
            d="M32 6c6 10-6 12-6 20a10 10 0 0 0 20 0c0-4-2-7-4-9 1 6-3 8-5 6 3-6-1-12-5-17z"
            fill="#e37f7f"
          />
          <path
            d="M27 34a7 7 0 0 0 14 0c0-2-1-4-2-5 0 4-2 5-3 4 1-3-1-6-3-8-2 3-6 5-6 9z"
            fill="#e3d57f"
          />
        </svg>
        FireGuard AI
      </div>
      <nav>
        <a href="#monitoring">Monitoring</a>
        <a href="#detection">Detection</a>
        <a href="#risk">Risk</a>
        <a href="#alerts">Alerts</a>
      </nav>
    </header>
  );
}
