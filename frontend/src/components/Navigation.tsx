'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Navigation() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: '🏠 Dashboard' },
    { href: '/agents', label: '🤖 Agents' },
    { href: '/projects', label: '📦 Projects' },
    { href: '/evolution', label: '🧬 Evolution' },
    { href: '/metrics', label: '📊 Metrics' },
  ];

  return (
    <nav className="bg-gray-900 text-white p-4 shadow-lg">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <h1 className="text-xl font-bold">T-Developer</h1>
          <div className="flex space-x-1">
            {links.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`px-4 py-2 rounded-lg transition-colors ${
                  pathname === link.href
                    ? 'bg-blue-600 text-white'
                    : 'hover:bg-gray-800'
                }`}
              >
                {link.label}
              </Link>
            ))}
          </div>
        </div>
        <div className="text-sm text-gray-400">
          Phase 3 • Day 45 • v40.0.0
        </div>
      </div>
    </nav>
  );
}
