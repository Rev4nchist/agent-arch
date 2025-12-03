'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import {
  LayoutDashboard,
  Calendar,
  CheckSquare,
  Bot,
  FileText,
  DollarSign,
  FolderOpen,
  Radar,
  BookOpen,
  MessageSquare,
  Lightbulb,
  Shield,
  MessageCircle,
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Proposals & Decisions', href: '/decisions', icon: Lightbulb },
  { name: 'Meetings Hub', href: '/meetings', icon: Calendar },
  { name: 'Tasks', href: '/tasks', icon: CheckSquare },
  { name: 'Agents', href: '/agents', icon: Bot },
  { name: 'Governance', href: '/governance', icon: FileText },
  { name: 'Budget & Licensing', href: '/budget', icon: DollarSign },
  { name: 'Resources Library', href: '/resources', icon: FolderOpen },
  { name: 'Tech Radar', href: '/tech-radar', icon: Radar },
  { name: 'Architecture Lab', href: '/architecture', icon: BookOpen },
  { name: 'Feedback Hub', href: '/feedback', icon: MessageCircle },
  { name: 'Audit Trail', href: '/audit', icon: Shield },
  { name: 'Fourth AI Guide', href: '/guide', icon: MessageSquare },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200">
      <div className="flex h-full flex-col">
        <div className="flex h-16 shrink-0 items-center gap-3 px-6 border-b border-gray-200">
          <Image
            src="/Fourth_icon.png"
            alt="Fourth Logo"
            width={32}
            height={32}
            className="flex-shrink-0"
          />
          <h1 className="text-xl font-bold text-gray-900">
            Fourth AI Architecture
          </h1>
        </div>

        <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
          {navigation.map((item) => {
            const isActive = item.href === '/'
              ? pathname === '/'
              : pathname === item.href || pathname.startsWith(`${item.href}/`);
            const Icon = item.icon;

            return (
              <Link
                key={item.name}
                href={item.href}
                className={`
                  relative flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition-colors
                  ${
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-700 hover:bg-gray-100 hover:text-gray-900'
                  }
                `}
              >
                {isActive && (
                  <span className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-6 bg-blue-600 rounded-r-full" />
                )}
                <Icon className={`h-5 w-5 ${isActive ? 'text-blue-600' : ''}`} />
                {item.name}
              </Link>
            );
          })}
        </nav>

        <div className="border-t border-gray-200 p-4">
          <p className="text-xs text-gray-500">
            MSFT Agent Framework Guide
          </p>
        </div>
      </div>
    </div>
  );
}
