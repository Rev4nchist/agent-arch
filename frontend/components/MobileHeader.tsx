'use client';

import Image from 'next/image';
import { Menu } from 'lucide-react';

interface MobileHeaderProps {
  onMenuClick: () => void;
}

export function MobileHeader({ onMenuClick }: MobileHeaderProps) {
  return (
    <header className="fixed top-0 left-0 right-0 h-14 bg-white border-b border-gray-200 lg:hidden z-50">
      <div className="flex items-center justify-between h-full px-4">
        <button
          onClick={onMenuClick}
          className="flex items-center justify-center w-11 h-11 -ml-2 rounded-lg hover:bg-gray-100 active:bg-gray-200 transition-colors"
          aria-label="Open menu"
        >
          <Menu className="h-6 w-6 text-gray-700" />
        </button>

        <div className="flex items-center gap-2">
          <Image
            src="/Fourth_icon.png"
            alt="Fourth Logo"
            width={28}
            height={28}
            className="flex-shrink-0"
          />
          <span className="text-lg font-semibold text-gray-900">Fourth AI</span>
        </div>

        <div className="w-11" />
      </div>
    </header>
  );
}
