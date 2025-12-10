'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { Plus, ThumbsUp, MessageCircle, ArrowUpDown, Bug, Lightbulb, Sparkles, HelpCircle, Settings } from 'lucide-react';
import { api, Submission, SubmissionCategory, SubmissionStatus, SubmissionPriority } from '@/lib/api';
import { MobileFilterBar } from '@/components/MobileFilterBar';

const categoryIcons: Record<SubmissionCategory, typeof Bug> = {
  'Bug Report': Bug,
  'Feature Request': Lightbulb,
  'Improvement Idea': Sparkles,
  'Question': HelpCircle,
};

const categoryColors: Record<SubmissionCategory, string> = {
  'Bug Report': 'bg-red-100 text-red-700',
  'Feature Request': 'bg-blue-100 text-blue-700',
  'Improvement Idea': 'bg-green-100 text-green-700',
  'Question': 'bg-yellow-100 text-yellow-700',
};

const statusColors: Record<SubmissionStatus, string> = {
  'Submitted': 'bg-gray-100 text-gray-700',
  'Under Review': 'bg-yellow-100 text-yellow-700',
  'In Progress': 'bg-blue-100 text-blue-700',
  'Completed': 'bg-green-100 text-green-700',
  'Declined': 'bg-red-100 text-red-700',
};

const priorityColors: Record<SubmissionPriority, string> = {
  'Critical': 'text-red-600',
  'High': 'text-orange-600',
  'Medium': 'text-yellow-600',
  'Low': 'text-gray-600',
};

export default function FeedbackPage() {
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [statusFilter, setStatusFilter] = useState<SubmissionStatus | ''>('');
  const [categoryFilter, setCategoryFilter] = useState<SubmissionCategory | ''>('');
  const [sortBy, setSortBy] = useState<'upvotes' | 'date' | 'priority'>('date');

  useEffect(() => {
    loadSubmissions();
  }, [statusFilter, categoryFilter, sortBy]);

  const loadSubmissions = async () => {
    try {
      setLoading(true);
      const response = await api.submissions.list({
        status: statusFilter || undefined,
        category: categoryFilter || undefined,
        sort_by: sortBy,
      });
      setSubmissions(response.items);
    } catch (err) {
      setError('Failed to load submissions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">Feedback Hub</h1>
              <p className="mt-1 text-sm text-gray-500">
                Submit bug reports, feature requests, and improvement ideas
              </p>
            </div>
        <div className="flex items-center gap-3">
          <Link
            href="/feedback/admin"
            className="inline-flex items-center gap-2 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
          >
            <Settings className="h-4 w-4" />
            Admin
          </Link>
          <Link
            href="/feedback/submit"
            className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            <Plus className="h-4 w-4" />
            Submit New
          </Link>
        </div>
      </div>

      <div className="flex items-center gap-3 rounded-lg bg-white p-4 border border-gray-200">
        <MobileFilterBar
          activeCount={(statusFilter ? 1 : 0) + (categoryFilter ? 1 : 0)}
          title="Filters"
        >
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value as SubmissionStatus | '')}
            className="w-full lg:w-auto rounded-md border border-gray-300 px-3 py-2 lg:py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Status</option>
            <option value="Submitted">Submitted</option>
            <option value="Under Review">Under Review</option>
            <option value="In Progress">In Progress</option>
            <option value="Completed">Completed</option>
            <option value="Declined">Declined</option>
          </select>

          <select
            value={categoryFilter}
            onChange={(e) => setCategoryFilter(e.target.value as SubmissionCategory | '')}
            className="w-full lg:w-auto rounded-md border border-gray-300 px-3 py-2 lg:py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
          >
            <option value="">All Categories</option>
            <option value="Bug Report">Bug Report</option>
            <option value="Feature Request">Feature Request</option>
            <option value="Improvement Idea">Improvement Idea</option>
            <option value="Question">Question</option>
          </select>

          <div className="flex items-center gap-2">
            <ArrowUpDown className="h-4 w-4 text-gray-400" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as 'upvotes' | 'date' | 'priority')}
              className="w-full lg:w-auto rounded-md border border-gray-300 px-3 py-2 lg:py-1.5 text-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
            >
              <option value="date">Most Recent</option>
              <option value="upvotes">Most Upvoted</option>
              <option value="priority">Priority</option>
            </select>
          </div>
        </MobileFilterBar>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-sm text-gray-500">Loading submissions...</p>
        </div>
      ) : error ? (
        <div className="text-center py-12">
          <p className="text-red-600">{error}</p>
          <button onClick={loadSubmissions} className="mt-2 text-blue-600 hover:underline">
            Try again
          </button>
        </div>
      ) : submissions.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg border border-gray-200">
          <MessageCircle className="h-12 w-12 text-gray-300 mx-auto" />
          <h3 className="mt-4 text-lg font-medium text-gray-900">No submissions yet</h3>
          <p className="mt-1 text-sm text-gray-500">
            Be the first to submit feedback or a feature request
          </p>
          <Link
            href="/feedback/submit"
            className="mt-4 inline-flex items-center gap-2 text-blue-600 hover:underline"
          >
            <Plus className="h-4 w-4" />
            Submit your first idea
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {submissions.map((submission) => {
            const CategoryIcon = categoryIcons[submission.category];
            return (
              <Link
                key={submission.id}
                href={`/feedback/view?id=${submission.id}`}
                className="block bg-white rounded-lg border border-gray-200 p-4 hover:border-blue-300 hover:shadow-sm transition-all"
              >
                {/* Mobile: Stack layout, Desktop: Row layout */}
                <div className="flex flex-col lg:flex-row lg:items-start gap-3 lg:gap-4">
                  {/* Upvote - hidden on mobile, shown on desktop */}
                  <div className="hidden lg:flex flex-col items-center gap-1 min-w-[60px]">
                    <button
                      onClick={(e) => e.preventDefault()}
                      className="flex flex-col items-center p-2 rounded-lg hover:bg-gray-100 transition-colors"
                    >
                      <ThumbsUp className="h-5 w-5 text-gray-400" />
                      <span className="text-sm font-semibold text-gray-700">{submission.upvote_count}</span>
                    </button>
                  </div>

                  <div className="flex-1 min-w-0">
                    {/* Badges row */}
                    <div className="flex flex-wrap items-center gap-2 mb-2">
                      <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${categoryColors[submission.category]}`}>
                        <CategoryIcon className="h-3 w-3" />
                        {submission.category}
                      </span>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${statusColors[submission.status]}`}>
                        {submission.status}
                      </span>
                      <span className={`text-xs font-medium ${priorityColors[submission.priority]}`}>
                        {submission.priority}
                      </span>
                    </div>

                    <h3 className="text-base font-medium text-gray-900 line-clamp-2 lg:truncate">
                      {submission.title}
                    </h3>

                    <p className="mt-1 text-sm text-gray-500 line-clamp-2">
                      {submission.description}
                    </p>

                    {/* Meta info - stack on mobile */}
                    <div className="mt-2 flex flex-wrap items-center gap-2 lg:gap-4 text-xs text-gray-500">
                      <span>By {submission.submitted_by}</span>
                      <span>{formatDate(submission.submitted_at)}</span>
                      {submission.comments.length > 0 && (
                        <span className="flex items-center gap-1">
                          <MessageCircle className="h-3 w-3" />
                          {submission.comments.length}
                        </span>
                      )}
                      {submission.assigned_to && (
                        <span className="text-blue-600 hidden lg:inline">Assigned: {submission.assigned_to}</span>
                      )}
                    </div>

                    {/* Mobile: Upvote row at bottom */}
                    <div className="flex lg:hidden items-center justify-between mt-3 pt-3 border-t border-gray-100">
                      <button
                        onClick={(e) => e.preventDefault()}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg hover:bg-gray-100 transition-colors min-h-[44px]"
                      >
                        <ThumbsUp className="h-5 w-5 text-gray-400" />
                        <span className="text-sm font-semibold text-gray-700">{submission.upvote_count}</span>
                      </button>
                      {submission.comments.length > 0 && (
                        <span className="flex items-center gap-1 text-xs text-gray-500">
                          <MessageCircle className="h-4 w-4" />
                          {submission.comments.length} comments
                        </span>
                      )}
                    </div>

                    {submission.tags.length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-1">
                        {submission.tags.slice(0, 3).map((tag) => (
                          <span
                            key={tag}
                            className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs"
                          >
                            {tag}
                          </span>
                        ))}
                        {submission.tags.length > 3 && (
                          <span className="px-2 py-0.5 text-gray-500 text-xs">
                            +{submission.tags.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
        </div>
      </div>
    </div>
  );
}
