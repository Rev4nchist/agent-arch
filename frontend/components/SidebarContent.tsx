'use client';

import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { useEffect, useState } from 'react';
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
  Users,
  UserPlus,
  Settings,
  Brain,
  Newspaper,
} from 'lucide-react';
import { UserProfile } from './UserProfile';
import { useAuth } from './providers/AuthProvider';
import { accessApi } from '@/lib/access-api';

interface NavItem {
  name: string;
  href: string;
  icon: React.ComponentType<{ className?: string }>;
  adminOnly?: boolean;
}

const allNavigation: NavItem[] = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard, adminOnly: true },
  { name: 'Proposals & Decisions', href: '/decisions', icon: Lightbulb, adminOnly: true },
  { name: 'Meetings Hub', href: '/meetings', icon: Calendar, adminOnly: true },
  { name: 'Tasks', href: '/tasks', icon: CheckSquare, adminOnly: true },
  { name: 'Agents', href: '/agents', icon: Bot },
  { name: 'Governance', href: '/governance', icon: FileText },
  { name: 'Budget & Licensing', href: '/budget', icon: DollarSign, adminOnly: true },
  { name: 'Resources Library', href: '/resources', icon: FolderOpen, adminOnly: true },
  { name: 'Tech Radar', href: '/tech-radar', icon: Radar },
  { name: 'Architecture Lab', href: '/architecture', icon: BookOpen, adminOnly: true },
  { name: 'Feedback Hub', href: '/feedback', icon: MessageCircle },
  { name: 'Audit Trail', href: '/audit', icon: Shield, adminOnly: true },
  { name: 'Fourth AI Guide', href: '/guide', icon: MessageSquare },
  { name: 'User Memories', href: '/memories', icon: Brain },
  { name: 'Feature Updates', href: '/updates', icon: Newspaper },
];

const adminNavigation: NavItem[] = [
  { name: 'User Management', href: '/admin/users', icon: Users, adminOnly: true },
  { name: 'Access Requests', href: '/admin/access-requests', icon: UserPlus, adminOnly: true },
];

interface SidebarContentProps {
  onNavigate?: () => void;
}

export function SidebarContent({ onNavigate }: SidebarContentProps) {
  const pathname = usePathname();
  const { userRole, isAuthorized } = useAuth();
  const [pendingCount, setPendingCount] = useState(0);
  const isAdmin = userRole === 'admin';

  useEffect(() => {
    if (isAdmin && isAuthorized) {
      accessApi.getPendingCount().then(res => setPendingCount(res.count)).catch(() => {});
    }
  }, [isAdmin, isAuthorized]);

  const navigation = allNavigation.filter(item => !item.adminOnly || isAdmin);

  const renderNavItem = (item: NavItem) => {
    const isActive = item.href === '/'
      ? pathname === '/'
      : pathname === item.href || pathname.startsWith(`${item.href}/`);
    const Icon = item.icon;
    const showBadge = item.href === '/admin/access-requests' && pendingCount > 0;

    return (
      <Link
        key={item.name}
        href={item.href}
        onClick={onNavigate}
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
        <span className="flex-1">{item.name}</span>
        {showBadge && (
          <span className="inline-flex items-center justify-center px-2 py-0.5 text-xs font-medium bg-red-100 text-red-700 rounded-full">
            {pendingCount}
          </span>
        )}
      </Link>
    );
  };

  return (
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
        {navigation.map(renderNavItem)}

        {isAdmin && (
          <>
            <div className="pt-4 pb-2">
              <div className="flex items-center gap-2 px-3">
                <Settings className="h-4 w-4 text-gray-400" />
                <span className="text-xs font-semibold text-gray-400 uppercase tracking-wider">
                  Admin
                </span>
              </div>
            </div>
            {adminNavigation.map(renderNavItem)}
          </>
        )}
      </nav>

      <div className="border-t border-gray-200 p-3">
        <UserProfile />
      </div>
      <div className="border-t border-gray-200 p-4 pt-2">
        <p className="text-xs text-gray-500">
          MSFT Agent Framework Guide
        </p>
      </div>
    </div>
  );
}
