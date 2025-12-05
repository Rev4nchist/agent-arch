'use client';

import { useState, useEffect } from 'react';
import { RoleGuard } from '@/components/auth';
import { useAuth } from '@/components/providers/AuthProvider';
import { accessApi, AccessRequest } from '@/lib/access-api';
import { Button } from '@/components/ui/button';
import {
  UserPlus,
  Check,
  X,
  Loader2,
  RefreshCw,
  Clock,
  CheckCircle2,
  XCircle,
  Filter,
} from 'lucide-react';

type FilterStatus = 'all' | 'pending' | 'approved' | 'denied';

export default function AccessRequestsPage() {
  return (
    <RoleGuard requiredRole="admin">
      <AccessRequestsContent />
    </RoleGuard>
  );
}

function AccessRequestsContent() {
  const { user } = useAuth();
  const [requests, setRequests] = useState<AccessRequest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<FilterStatus>('pending');
  const [processingIds, setProcessingIds] = useState<Set<string>>(new Set());

  const loadRequests = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await accessApi.listRequests();
      setRequests(data.items);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load requests');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadRequests();
  }, []);

  const handleApprove = async (requestId: string, role: 'user' | 'admin') => {
    if (!user?.username) return;
    setProcessingIds((prev) => new Set(prev).add(requestId));
    try {
      await accessApi.approveRequest(requestId, user.username, role);
      loadRequests();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to approve request');
    } finally {
      setProcessingIds((prev) => {
        const newSet = new Set(prev);
        newSet.delete(requestId);
        return newSet;
      });
    }
  };

  const handleDeny = async (requestId: string) => {
    if (!user?.username) return;
    setProcessingIds((prev) => new Set(prev).add(requestId));
    try {
      await accessApi.denyRequest(requestId, user.username);
      loadRequests();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to deny request');
    } finally {
      setProcessingIds((prev) => {
        const newSet = new Set(prev);
        newSet.delete(requestId);
        return newSet;
      });
    }
  };

  const filteredRequests = requests.filter((req) => {
    if (filter === 'all') return true;
    return req.status === filter;
  });

  const pendingCount = requests.filter((r) => r.status === 'pending').length;
  const approvedCount = requests.filter((r) => r.status === 'approved').length;
  const deniedCount = requests.filter((r) => r.status === 'denied').length;

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'pending':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
            <Clock className="h-3 w-3" />
            Pending
          </span>
        );
      case 'approved':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
            <CheckCircle2 className="h-3 w-3" />
            Approved
          </span>
        );
      case 'denied':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-red-100 text-red-800">
            <XCircle className="h-3 w-3" />
            Denied
          </span>
        );
      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-6xl mx-auto">
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
              <UserPlus className="h-8 w-8 text-blue-600" />
              Access Requests
            </h1>
            <p className="text-gray-600 mt-1">Review and manage access requests</p>
          </div>
          <Button variant="outline" onClick={loadRequests} disabled={isLoading}>
            <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        <div className="grid grid-cols-4 gap-4 mb-6">
          <button
            onClick={() => setFilter('all')}
            className={`bg-white rounded-xl p-4 border text-left transition-colors ${
              filter === 'all' ? 'border-blue-500 ring-2 ring-blue-100' : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-100 rounded-lg">
                <Filter className="h-5 w-5 text-gray-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{requests.length}</p>
                <p className="text-sm text-gray-500">All Requests</p>
              </div>
            </div>
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`bg-white rounded-xl p-4 border text-left transition-colors ${
              filter === 'pending' ? 'border-yellow-500 ring-2 ring-yellow-100' : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{pendingCount}</p>
                <p className="text-sm text-gray-500">Pending</p>
              </div>
            </div>
          </button>
          <button
            onClick={() => setFilter('approved')}
            className={`bg-white rounded-xl p-4 border text-left transition-colors ${
              filter === 'approved' ? 'border-green-500 ring-2 ring-green-100' : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle2 className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{approvedCount}</p>
                <p className="text-sm text-gray-500">Approved</p>
              </div>
            </div>
          </button>
          <button
            onClick={() => setFilter('denied')}
            className={`bg-white rounded-xl p-4 border text-left transition-colors ${
              filter === 'denied' ? 'border-red-500 ring-2 ring-red-100' : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <XCircle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{deniedCount}</p>
                <p className="text-sm text-gray-500">Denied</p>
              </div>
            </div>
          </button>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
            <button onClick={() => setError(null)} className="ml-2 text-red-500 hover:text-red-700">
              Dismiss
            </button>
          </div>
        )}

        <div className="bg-white rounded-xl border border-gray-200">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
            </div>
          ) : filteredRequests.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              {filter === 'pending' ? 'No pending requests' : `No ${filter} requests found`}
            </div>
          ) : (
            <div className="divide-y divide-gray-200">
              {filteredRequests.map((request) => (
                <div key={request.id} className="p-6 hover:bg-gray-50">
                  <div className="flex items-start justify-between">
                    <div className="flex items-start gap-4">
                      <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center">
                        <span className="text-blue-600 font-medium text-lg">
                          {request.name.charAt(0).toUpperCase()}
                        </span>
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{request.name}</h3>
                        <p className="text-gray-600">{request.email}</p>
                        {request.reason && (
                          <p className="mt-2 text-sm text-gray-500 bg-gray-50 p-2 rounded-lg">
                            &ldquo;{request.reason}&rdquo;
                          </p>
                        )}
                        <p className="mt-2 text-xs text-gray-400">
                          Requested: {request.created_at ? new Date(request.created_at).toLocaleString() : 'N/A'}
                        </p>
                      </div>
                    </div>
                    <div className="flex items-center gap-3">
                      {getStatusBadge(request.status)}
                      {request.status === 'pending' && (
                        <div className="flex items-center gap-2 ml-4">
                          <div className="relative group">
                            <Button
                              size="sm"
                              onClick={() => handleApprove(request.id!, 'user')}
                              disabled={processingIds.has(request.id!)}
                              className="bg-green-600 hover:bg-green-700"
                            >
                              {processingIds.has(request.id!) ? (
                                <Loader2 className="h-4 w-4 animate-spin" />
                              ) : (
                                <>
                                  <Check className="h-4 w-4 mr-1" />
                                  Approve
                                </>
                              )}
                            </Button>
                            <div className="absolute top-full left-0 mt-1 opacity-0 group-hover:opacity-100 transition-opacity z-10">
                              <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-2 flex gap-2">
                                <button
                                  onClick={() => handleApprove(request.id!, 'user')}
                                  className="px-3 py-1 text-sm bg-green-100 text-green-700 rounded hover:bg-green-200"
                                >
                                  As User
                                </button>
                                <button
                                  onClick={() => handleApprove(request.id!, 'admin')}
                                  className="px-3 py-1 text-sm bg-purple-100 text-purple-700 rounded hover:bg-purple-200"
                                >
                                  As Admin
                                </button>
                              </div>
                            </div>
                          </div>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => handleDeny(request.id!)}
                            disabled={processingIds.has(request.id!)}
                            className="text-red-600 border-red-200 hover:bg-red-50"
                          >
                            <X className="h-4 w-4 mr-1" />
                            Deny
                          </Button>
                        </div>
                      )}
                      {request.status !== 'pending' && request.reviewed_by && (
                        <span className="text-xs text-gray-400">
                          by {request.reviewed_by}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
