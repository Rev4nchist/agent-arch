'use client';

import { SidebarContent } from './SidebarContent';

export default function Sidebar() {
  return (
    <div className="hidden lg:block">
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200">
        <SidebarContent />
      </div>
    </div>
  );
}
