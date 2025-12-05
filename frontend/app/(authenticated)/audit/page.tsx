'use client';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  api,
  AuditLog,
  AuditAction,
  AuditEntityType,
  AuditSummary,
} from '@/lib/api';
import {
  Shield,
  Search,
  RefreshCw,
  Eye,
  Plus,
  Pencil,
  Trash2,
  MessageSquare,
  User,
  Clock,
  Filter,
  BarChart3,
  ChevronLeft,
  ChevronRight,
  Camera,
  AlertTriangle,
} from 'lucide-react';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from '@/components/ui/alert-dialog';

const ACTION_ICONS: Record<AuditAction, typeof Eye> = {
  view: Eye,
  create: Plus,
  update: Pencil,
  delete: Trash2,
  query: MessageSquare,
};

const ACTION_COLORS: Record<AuditAction, string> = {
  view: 'bg-blue-100 text-blue-800',
  create: 'bg-green-100 text-green-800',
  update: 'bg-yellow-100 text-yellow-800',
  delete: 'bg-red-100 text-red-800',
  query: 'bg-purple-100 text-purple-800',
};

const ENTITY_COLORS: Record<AuditEntityType, string> = {
  task: 'bg-orange-100 text-orange-800',
  agent: 'bg-cyan-100 text-cyan-800',
  meeting: 'bg-indigo-100 text-indigo-800',
  decision: 'bg-pink-100 text-pink-800',
  proposal: 'bg-teal-100 text-teal-800',
  resource: 'bg-lime-100 text-lime-800',
  tech_radar: 'bg-amber-100 text-amber-800',
  code_pattern: 'bg-violet-100 text-violet-800',
};

interface SnapshotInfo {
  count: number;
  latest?: string;
}

export default function AuditPage() {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [summary, setSummary] = useState<AuditSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(0);
  const [limit] = useState(25);

  const [filterUser, setFilterUser] = useState<string>('all');
  const [filterEntity, setFilterEntity] = useState<string>('all');
  const [filterAction, setFilterAction] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const [snapshotInfo, setSnapshotInfo] = useState<SnapshotInfo>({ count: 0 });
  const [clearingSnapshots, setClearingSnapshots] = useState(false);

  useEffect(() => {
    loadAuditLogs();
    loadSummary();
    loadSnapshotInfo();
  }, [page, filterUser, filterEntity, filterAction]);

  async function loadAuditLogs() {
    try {
      setLoading(true);
      const params: {
        limit: number;
        offset: number;
        user_id?: string;
        entity_type?: AuditEntityType;
        action?: AuditAction;
      } = {
        limit,
        offset: page * limit,
      };

      if (filterUser !== 'all') params.user_id = filterUser;
      if (filterEntity !== 'all') params.entity_type = filterEntity as AuditEntityType;
      if (filterAction !== 'all') params.action = filterAction as AuditAction;

      const response = await api.audit.list(params);
      setLogs(response.items);
      setTotal(response.total);
    } catch (error) {
      console.error('Failed to load audit logs:', error);
    } finally {
      setLoading(false);
    }
  }

  async function loadSummary() {
    try {
      const data = await api.audit.getSummary();
      setSummary(data);
    } catch (error) {
      console.error('Failed to load summary:', error);
    }
  }

  async function loadSnapshotInfo() {
    try {
      const response = await fetch('/api/snapshots', {
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY || 'dev-test-key-123'}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setSnapshotInfo({
          count: data.count || 0,
          latest: data.snapshots?.[0]?.date,
        });
      }
    } catch (error) {
      console.error('Failed to load snapshot info:', error);
    }
  }

  async function handleClearSnapshots() {
    try {
      setClearingSnapshots(true);
      const response = await fetch('/api/snapshots', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${process.env.NEXT_PUBLIC_API_KEY || 'dev-test-key-123'}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        alert(`Successfully cleared ${data.deleted_count} snapshots`);
        loadSnapshotInfo();
      } else {
        throw new Error('Failed to clear snapshots');
      }
    } catch (error) {
      console.error('Failed to clear snapshots:', error);
      alert('Failed to clear snapshots. Please try again.');
    } finally {
      setClearingSnapshots(false);
    }
  }

  function formatTimestamp(timestamp: string): string {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString();
  }

  const filteredLogs = logs.filter((log) => {
    if (!searchQuery) return true;
    const query = searchQuery.toLowerCase();
    return (
      log.entity_id.toLowerCase().includes(query) ||
      log.entity_title?.toLowerCase().includes(query) ||
      log.user_id.toLowerCase().includes(query) ||
      log.user_name?.toLowerCase().includes(query)
    );
  });

  const uniqueUsers = summary
    ? Object.keys(summary.by_user)
    : [];

  const totalPages = Math.ceil(total / limit);

  if (loading && logs.length === 0) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading audit trail...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <div className="flex items-center gap-3">
            <Shield className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Audit Trail</h1>
              <p className="mt-1 text-gray-600">
                Track all user actions and system changes
              </p>
            </div>
          </div>
        </div>

        {summary && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Total Actions</p>
                    <p className="text-2xl font-bold">{summary.total_logs}</p>
                  </div>
                  <BarChart3 className="h-8 w-8 text-gray-400" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Creates</p>
                    <p className="text-2xl font-bold text-green-600">
                      {summary.by_action.create || 0}
                    </p>
                  </div>
                  <Plus className="h-8 w-8 text-green-400" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Updates</p>
                    <p className="text-2xl font-bold text-yellow-600">
                      {summary.by_action.update || 0}
                    </p>
                  </div>
                  <Pencil className="h-8 w-8 text-yellow-400" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-500">Active Users</p>
                    <p className="text-2xl font-bold text-blue-600">
                      {Object.keys(summary.by_user).length}
                    </p>
                  </div>
                  <User className="h-8 w-8 text-blue-400" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Snapshots Management Section */}
        <Card className="mb-6">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <Camera className="h-5 w-5" />
              Historical Snapshots
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
              <div className="flex-1">
                <p className="text-sm text-gray-600 mb-2">
                  Snapshots capture daily metrics (tasks, agents, decisions, meetings) to enable
                  historical trend analysis and comparison queries in the AI Guide.
                </p>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-gray-500">
                    <strong>{snapshotInfo.count}</strong> snapshots stored
                  </span>
                  {snapshotInfo.latest && (
                    <span className="text-gray-500">
                      Latest: {new Date(snapshotInfo.latest).toLocaleDateString()}
                    </span>
                  )}
                </div>
              </div>
              <AlertDialog>
                <AlertDialogTrigger asChild>
                  <Button
                    variant="destructive"
                    size="sm"
                    disabled={clearingSnapshots || snapshotInfo.count === 0}
                  >
                    <Trash2 className="h-4 w-4 mr-2" />
                    Clear All Snapshots
                  </Button>
                </AlertDialogTrigger>
                <AlertDialogContent>
                  <AlertDialogHeader>
                    <AlertDialogTitle className="flex items-center gap-2">
                      <AlertTriangle className="h-5 w-5 text-yellow-500" />
                      Clear All Snapshots?
                    </AlertDialogTitle>
                    <AlertDialogDescription asChild>
                      <div className="text-sm text-muted-foreground">
                        <p>
                          This will permanently delete all {snapshotInfo.count} historical snapshots.
                          This action cannot be undone.
                        </p>
                        <p className="mt-3 font-medium">When to clear snapshots:</p>
                        <ul className="list-disc list-inside mt-2 space-y-1">
                          <li>Transitioning from test data to production</li>
                          <li>Resetting after significant data cleanup</li>
                          <li>Starting fresh metrics tracking</li>
                        </ul>
                      </div>
                    </AlertDialogDescription>
                  </AlertDialogHeader>
                  <AlertDialogFooter>
                    <AlertDialogCancel>Cancel</AlertDialogCancel>
                    <AlertDialogAction
                      onClick={handleClearSnapshots}
                      className="bg-red-600 hover:bg-red-700"
                    >
                      {clearingSnapshots ? 'Clearing...' : 'Yes, Clear All Snapshots'}
                    </AlertDialogAction>
                  </AlertDialogFooter>
                </AlertDialogContent>
              </AlertDialog>
            </div>
          </CardContent>
        </Card>

        <Card className="mb-6">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg flex items-center gap-2">
              <Filter className="h-5 w-5" />
              Filters
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex flex-col sm:flex-row gap-4">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search by entity ID, title, or user..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>

              <Select value={filterAction} onValueChange={(v) => { setFilterAction(v); setPage(0); }}>
                <SelectTrigger className="w-full sm:w-[160px]">
                  <SelectValue placeholder="Action" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Actions</SelectItem>
                  <SelectItem value="view">View</SelectItem>
                  <SelectItem value="create">Create</SelectItem>
                  <SelectItem value="update">Update</SelectItem>
                  <SelectItem value="delete">Delete</SelectItem>
                  <SelectItem value="query">Query</SelectItem>
                </SelectContent>
              </Select>

              <Select value={filterEntity} onValueChange={(v) => { setFilterEntity(v); setPage(0); }}>
                <SelectTrigger className="w-full sm:w-[160px]">
                  <SelectValue placeholder="Entity" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Entities</SelectItem>
                  <SelectItem value="task">Tasks</SelectItem>
                  <SelectItem value="agent">Agents</SelectItem>
                  <SelectItem value="meeting">Meetings</SelectItem>
                  <SelectItem value="decision">Decisions</SelectItem>
                  <SelectItem value="proposal">Proposals</SelectItem>
                  <SelectItem value="resource">Resources</SelectItem>
                  <SelectItem value="tech_radar">Tech Radar</SelectItem>
                  <SelectItem value="code_pattern">Code Patterns</SelectItem>
                </SelectContent>
              </Select>

              <Select value={filterUser} onValueChange={(v) => { setFilterUser(v); setPage(0); }}>
                <SelectTrigger className="w-full sm:w-[160px]">
                  <SelectValue placeholder="User" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Users</SelectItem>
                  {uniqueUsers.map((user) => (
                    <SelectItem key={user} value={user}>
                      {user}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              <Button
                variant="outline"
                onClick={() => {
                  loadAuditLogs();
                  loadSummary();
                }}
              >
                <RefreshCw className="h-4 w-4 mr-2" />
                Refresh
              </Button>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-4">
            <div className="flex items-center justify-between">
              <CardTitle className="text-lg">Activity Log</CardTitle>
              <span className="text-sm text-gray-500">
                {total} total entries
              </span>
            </div>
          </CardHeader>
          <CardContent>
            {filteredLogs.length === 0 ? (
              <div className="text-center py-12">
                <Shield className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No audit logs found
                </h3>
                <p className="text-gray-600">
                  {searchQuery || filterAction !== 'all' || filterEntity !== 'all' || filterUser !== 'all'
                    ? 'Try adjusting your filters'
                    : 'Actions will appear here as users interact with the system'}
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {filteredLogs.map((log) => {
                  const ActionIcon = ACTION_ICONS[log.action];
                  return (
                    <div
                      key={log.id}
                      className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <div className={`p-2 rounded-full ${ACTION_COLORS[log.action]}`}>
                        <ActionIcon className="h-4 w-4" />
                      </div>

                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 flex-wrap">
                          <span className="font-medium text-gray-900">
                            {log.user_name || log.user_id}
                          </span>
                          <Badge className={ACTION_COLORS[log.action]} variant="secondary">
                            {log.action.toUpperCase()}
                          </Badge>
                          <Badge className={ENTITY_COLORS[log.entity_type]} variant="secondary">
                            {log.entity_type.replace('_', ' ')}
                          </Badge>
                        </div>

                        <p className="text-sm text-gray-600 mt-1">
                          {log.entity_title || log.entity_id}
                          {log.entity_title && (
                            <span className="text-gray-400 ml-2">({log.entity_id})</span>
                          )}
                        </p>

                        {log.details && (
                          <p className="text-xs text-gray-500 mt-1">
                            {log.details.path ? `Path: ${String(log.details.path)}` : null}
                            {log.details.status_code ? ` • Status: ${String(log.details.status_code)}` : null}
                          </p>
                        )}
                      </div>

                      <div className="text-right shrink-0">
                        <div className="flex items-center gap-1 text-sm text-gray-500">
                          <Clock className="h-3 w-3" />
                          {formatTimestamp(log.timestamp)}
                        </div>
                        {log.ip_address && (
                          <p className="text-xs text-gray-400 mt-1">
                            {log.ip_address}
                          </p>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}

            {totalPages > 1 && (
              <div className="flex items-center justify-between mt-6 pt-4 border-t">
                <p className="text-sm text-gray-500">
                  Showing {page * limit + 1} - {Math.min((page + 1) * limit, total)} of {total}
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(Math.max(0, page - 1))}
                    disabled={page === 0}
                  >
                    <ChevronLeft className="h-4 w-4" />
                    Previous
                  </Button>
                  <span className="text-sm text-gray-600">
                    Page {page + 1} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setPage(Math.min(totalPages - 1, page + 1))}
                    disabled={page >= totalPages - 1}
                  >
                    Next
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
