'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useMobile, useSwipeGesture } from '@/hooks/useMobile';

interface NavItem {
  label: string;
  href: string;
  icon?: React.ReactNode;
}

interface MobileNavProps {
  items: NavItem[];
  logo?: React.ReactNode;
}

export default function MobileNav({ items, logo }: MobileNavProps) {
  const [isOpen, setIsOpen] = useState(false);
  const { isMobile } = useMobile();

  const swipeHandlers = useSwipeGesture(
    () => setIsOpen(false), // swipe left to close
    () => setIsOpen(true),  // swipe right to open
  );

  if (!isMobile) return null;

  return (
    <>
      {/* Mobile Header */}
      <header className="fixed top-0 left-0 right-0 h-16 bg-gray-900 border-b border-gray-800 flex items-center justify-between px-4 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="p-2 hover:bg-gray-800 rounded"
          aria-label="Toggle menu"
        >
          <svg
            className="w-6 h-6 text-white"
            fill="none"
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth="2"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            {isOpen ? (
              <path d="M6 18L18 6M6 6l12 12" />
            ) : (
              <path d="M4 6h16M4 12h16M4 18h16" />
            )}
          </svg>
        </button>

        <div className="flex-1 flex justify-center">
          {logo || <span className="text-white font-bold">IKODIO</span>}
        </div>

        <div className="w-10" /> {/* Spacer for centering */}
      </header>

      {/* Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}

      {/* Slide-out Menu */}
      <nav
        {...swipeHandlers}
        className={`
          fixed top-0 left-0 h-full w-64 bg-gray-900 border-r border-gray-800 z-50
          transform transition-transform duration-300 ease-in-out
          ${isOpen ? 'translate-x-0' : '-translate-x-full'}
        `}
      >
        <div className="p-4 border-b border-gray-800">
          {logo || <span className="text-white font-bold text-xl">IKODIO</span>}
        </div>

        <ul className="py-4">
          {items.map((item, index) => (
            <li key={index}>
              <Link
                href={item.href}
                onClick={() => setIsOpen(false)}
                className="flex items-center px-4 py-3 text-gray-300 hover:bg-gray-800 hover:text-white transition-colors"
              >
                {item.icon && <span className="mr-3">{item.icon}</span>}
                <span>{item.label}</span>
              </Link>
            </li>
          ))}
        </ul>
      </nav>

      {/* Spacer for fixed header */}
      <div className="h-16" />
    </>
  );
}
