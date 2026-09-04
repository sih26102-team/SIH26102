import { NavLink } from 'react-router-dom';

const LINKS = [
  { to: '/dashboard', label: 'Flagged Works' },
  { to: '/insights', label: 'Insights' },
  { to: '/cases', label: 'Case Management' },
];

export default function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {/* Dark overlay behind drawer on mobile, tap to close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-30 bg-black/50 md:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed inset-y-0 left-0 z-40 flex w-56 flex-shrink-0 flex-col bg-navy-900 text-navy-100
          transition-transform duration-200 ease-in-out
          md:static md:translate-x-0
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}`}
      >
        <div className="flex items-center justify-between gap-2 px-5 py-5">
          <div className="flex items-center gap-2">
            <svg width="26" height="26" viewBox="0 0 32 32" aria-hidden="true">
              <circle cx="16" cy="16" r="14" fill="#0D1B2E" stroke="#3B5D82" strokeWidth="1.5" />
              <circle cx="16" cy="16" r="10" fill="none" stroke="#3B5D82" strokeWidth="2.5" />
              <path d="M16 6 A10 10 0 0 1 24.7 21" fill="none" stroke="#C0392B" strokeWidth="2.5" strokeLinecap="round" />
            </svg>
            <div>
              <p className="font-display text-sm font-semibold text-white leading-tight">MPLADS</p>
              <p className="text-[11px] leading-tight text-navy-100/70">Investigation Console</p>
            </div>
          </div>
          {/* Close button, mobile only */}
          <button onClick={onClose} className="text-navy-100/70 md:hidden" aria-label="Close menu">
            ✕
          </button>
        </div>

        <nav className="flex-1 space-y-1 px-3">
          {LINKS.map((link) => (
            <NavLink
              key={link.to}
              to={link.to}
              onClick={onClose}
              className={({ isActive }) =>
                `block rounded px-3 py-2 text-sm font-medium transition ${
                  isActive ? 'bg-navy-700 text-white' : 'text-navy-100/80 hover:bg-navy-700/60 hover:text-white'
                }`
              }
            >
              {link.label}
            </NavLink>
          ))}
        </nav>

        <div className="border-t border-navy-700 px-5 py-4 text-[11px] leading-relaxed text-navy-100/60">
          SIH26102 · Decision support only.
          <br />
          Flags are signals for review, not findings.
        </div>
      </aside>
    </>
  );
}
