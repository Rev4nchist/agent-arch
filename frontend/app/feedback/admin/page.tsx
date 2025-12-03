'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  BarChart2,
  ThumbsUp,
  Clock,
  CheckCircle,
  XCircle,
  Bug,
  Lightbulb,
  Sparkles,
  HelpCircle,
  RefreshCw,
  ExternalLink,
} from 'lucide-react';
import { api, Submission, SubmissionStats, SubmissionStatus, SubmissionCategory } from '@/lib/api';

const categoryIcons: Record<SubmissionCategory, typeof Bug> = {
  'Bug Report': Bug,
  'Feature Request': Lightbulb,
  'Improvement Idea': Sparkles,
  'Question': HelpCircle,
};

const statusColors: Record<SubmissionStatus, string> = {
  'Submitted': 'bg-gray-100 text-gray-700 border-gray-200',
  'Under Review': 'bg-yellow-100 text-yellow-700 border-yellow-200',
  'In Progress': 'bg-blue-100 text-blue-700 border-blue-200',
  'Completed': 'bg-green-100 text-green-700 border-green-200',
  'Declined': 'bg-red-100 text-red-700 border-red-200',
};

const teamMembers = [
  'David Hayes',
  'Martin Brady',
  'Stephen Allen',
  'Leanne McCourt',
  'Lisa Ann Kelly',
  'Kieran Smyth',
];

const taskCategories = ['Governance', 'Technical', 'Agent', 'Licensing', 'AI Architect'];

export default function FeedbackAdminPage() {
  const [stats, setStats] = useState<SubmissionStats | null>(null);
  const [triageQueue, setTriageQueue] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [converting, setConverting] = useState<string | null>(null);
  const [updatingStatus, setUpdatingStatus] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [statsData, submissionsData] = await Promise.all([
        api.submissions.getStats(),
        api.submissions.list({ status: 'Submitted', sort_by: 'upvotes' }),
      ]);
      setStats(statsData);
      setTriageQueue(submissionsData.items);
    } catch (err) {
      console.error('Failed to load admin data:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleStatusChange = async (id: string, newStatus: SubmissionStatus) => {
    try {
      setUpdatingStatus(id);
      await api.submissions.update(id, { status: newStatus });
      await loadData();
    } catch (err) {
      console.error('Failed to update status:', err);
    } finally {
      setUpdatingStatus(null);
    }
  };

  const handleAssign = async (id: string, assignee: string) => {
    try {
      setUpdatingStatus(id);
      await api.submissions.update(id, {
        assigned_to: assignee,
        status: 'Under Review',
      });
      await loadData();
    } catch (err) {
      console.error('Failed to assign:', err);
    } finally {
      setUpdatingStatus(null);
    }
  };

  const handleConvertToTask = async (id: string, category: string) => {
    try {
      setConverting(id);
      await api.submissions.convertToTask(id, category);
      await loadData();
    } catch (err) {
      console.error('Failed to convert to task:', err);
    } finally {
      setConverting(null);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Link
            href="/feedback"
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ArrowLeft className="h-5 w-5 text-gray-600" />
          </Link>
          <div>
            <h1 className="text-2xl font-semibold text-gray-900">Feedback Admin</h1>
            <p className="text-sm text-gray-500">Manage and triage submissions</p>
          </div>
        </div>
        <button
          onClick={loadData}
          className="inline-flex items-center gap-2 px-3 py-2 text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
        >
          <RefreshCw className="h-4 w-4" />
          Refresh
        </button>
      </div>

      {stats && (
        <div className="grid grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BarChart2 className="h-5 w-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">{stats.total}</p>
                <p className="text-sm text-gray-500">Total Submissions</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-yellow-100 rounded-lg">
                <Clock className="h-5 w-5 text-yellow-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {(stats.by_status['Submitted'] || 0) + (stats.by_status['Under Review'] || 0)}
                </p>
                <p className="text-sm text-gray-500">Pending Review</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <CheckCircle className="h-5 w-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.by_status['Completed'] || 0}
                </p>
                <p className="text-sm text-gray-500">Completed</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-red-100 rounded-lg">
                <XCircle className="h-5 w-5 text-red-600" />
              </div>
              <div>
                <p className="text-2xl font-bold text-gray-900">
                  {stats.by_status['Declined'] || 0}
                </p>
                <p className="text-sm text-gray-500">Declined</p>
              </div>
            </div>
          </div>
        </div>
      )}

      {stats && (
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">By Category</h3>
            <div className="space-y-2">
              {Object.entries(stats.by_category).map(([category, count]) => {
                const Icon = categoryIcons[category as SubmissionCategory] || Lightbulb;
                return (
                  <div key={category} className="flex items-center justify-between">
                    <span className="flex items-center gap-2 text-sm text-gray-600">
                      <Icon className="h-4 w-4" />
                      {category}
                    </span>
                    <span className="text-sm font-medium text-gray-900">{count}</span>
                  </div>
                );
              })}
            </div>
          </div>

          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="text-sm font-medium text-gray-900 mb-3">By Status</h3>
            <div className="space-y-2">
              {Object.entries(stats.by_status).map(([status, count]) => (
                <div key={status} className="flex items-center justify-between">
                  <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[status as SubmissionStatus] || 'bg-gray-100 text-gray-700'}`}>
                    {status}
                  </span>
                  <span className="text-sm font-medium text-gray-900">{count}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      <div className="bg-white rounded-lg border border-gray-200">
        <div className="px-4 py-3 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900 flex items-center gap-2">
            <Clock className="h-5 w-5 text-yellow-500" />
            Triage Queue ({triageQueue.length})
          </h2>
          <p className="text-sm text-gray-500">Submissions awaiting review, sorted by upvotes</p>
        </div>

        {triageQueue.length === 0 ? (
          <div className="p-8 text-center">
            <CheckCircle className="h-12 w-12 text-green-300 mx-auto" />
            <p className="mt-2 text-gray-500">All submissions have been triaged!</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {triageQueue.map((submission) => {
              const CategoryIcon = categoryIcons[submission.category];
              const isProcessing = updatingStatus === submission.id || converting === submission.id;

              return (
                <div key={submission.id} className="p-4">
                  <div className="flex items-start gap-4">
                    <div className="flex flex-col items-center text-center">
                      <ThumbsUp className="h-5 w-5 text-gray-400" />
                      <span className="text-lg font-bold text-gray-700">{submission.upvote_count}</span>
                    </div>

                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <CategoryIcon className="h-4 w-4 text-gray-400" />
                        <span className="text-xs text-gray-500">{submission.category}</span>
                        <span className="text-xs px-1.5 py-0.5 bg-orange-100 text-orange-700 rounded">
                          {submission.priority}
                        </span>
                      </div>

                      <Link
                        href={`/feedback/view?id=${submission.id}`}
                        className="text-base font-medium text-gray-900 hover:text-blue-600 flex items-center gap-1"
                      >
                        {submission.title}
                        <ExternalLink className="h-3 w-3" />
                      </Link>

                      <p className="mt-1 text-sm text-gray-500 line-clamp-1">
                        {submission.description}
                      </p>

                      <div className="mt-1 text-xs text-gray-400">
                        By {submission.submitted_by} on {formatDate(submission.submitted_at)}
                      </div>
                    </div>

                    <div className="flex items-center gap-2">
                      <select
                        onChange={(e) => e.target.value && handleAssign(submission.id, e.target.value)}
                        disabled={isProcessing}
                        className="text-xs border border-gray-300 rounded px-2 py-1 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        defaultValue=""
                      >
                        <option value="">Assign to...</option>
                        {teamMembers.map((member) => (
                          <option key={member} value={member}>{member}</option>
                        ))}
                      </select>

                      <select
                        onChange={(e) => {
                          if (e.target.value) {
                            handleConvertToTask(submission.id, e.target.value);
                          }
                        }}
                        disabled={isProcessing}
                        className="text-xs border border-blue-300 bg-blue-50 text-blue-700 rounded px-2 py-1 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
                        defaultValue=""
                      >
                        <option value="">Convert to Task...</option>
                        {taskCategories.map((cat) => (
                          <option key={cat} value={cat}>{cat}</option>
                        ))}
                      </select>

                      <button
                        onClick={() => handleStatusChange(submission.id, 'Declined')}
                        disabled={isProcessing}
                        className="p-1.5 text-red-600 hover:bg-red-50 rounded transition-colors disabled:opacity-50"
                        title="Decline"
                      >
                        <XCircle className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
        </div>
      </div>
    </div>
  );
}
