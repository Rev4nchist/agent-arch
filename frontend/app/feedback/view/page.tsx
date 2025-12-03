'use client';

import { useState, useEffect, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  ThumbsUp,
  MessageCircle,
  Send,
  Trash2,
  ExternalLink,
  Bug,
  Lightbulb,
  Sparkles,
  HelpCircle,
  CheckCircle,
  Clock,
  XCircle,
  ArrowRight,
  User,
} from 'lucide-react';
import { api, Submission, SubmissionCategory, SubmissionStatus, SubmissionPriority } from '@/lib/api';

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

const statusIcons: Record<SubmissionStatus, typeof Clock> = {
  'Submitted': Clock,
  'Under Review': Clock,
  'In Progress': ArrowRight,
  'Completed': CheckCircle,
  'Declined': XCircle,
};

const priorityColors: Record<SubmissionPriority, string> = {
  'Critical': 'text-red-600 bg-red-50',
  'High': 'text-orange-600 bg-orange-50',
  'Medium': 'text-yellow-600 bg-yellow-50',
  'Low': 'text-gray-600 bg-gray-50',
};

function SubmissionDetailContent() {
  const searchParams = useSearchParams();
  const id = searchParams.get('id');

  const [submission, setSubmission] = useState<Submission | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [upvoting, setUpvoting] = useState(false);
  const [commentText, setCommentText] = useState('');
  const [commentUser, setCommentUser] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  const [currentUser] = useState('Anonymous User');

  useEffect(() => {
    if (id) {
      loadSubmission();
    } else {
      setLoading(false);
      setError('No submission ID provided');
    }
  }, [id]);

  const loadSubmission = async () => {
    if (!id) return;
    try {
      setLoading(true);
      const data = await api.submissions.get(id);
      setSubmission(data);
    } catch (err) {
      setError('Failed to load submission');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleUpvote = async () => {
    if (!submission || upvoting || !id) return;

    try {
      setUpvoting(true);
      const updated = await api.submissions.upvote(id, currentUser);
      setSubmission(updated);
    } catch (err) {
      console.error('Failed to upvote:', err);
    } finally {
      setUpvoting(false);
    }
  };

  const handleAddComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!commentText.trim() || !commentUser.trim() || submittingComment || !id) return;

    try {
      setSubmittingComment(true);
      const updated = await api.submissions.addComment(id, commentUser.trim(), commentText.trim());
      setSubmission(updated);
      setCommentText('');
    } catch (err) {
      console.error('Failed to add comment:', err);
    } finally {
      setSubmittingComment(false);
    }
  };

  const handleDeleteComment = async (commentId: string) => {
    if (!submission || !id) return;

    try {
      const updated = await api.submissions.deleteComment(id, commentId);
      setSubmission(updated);
    } catch (err) {
      console.error('Failed to delete comment:', err);
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-GB', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !submission) {
    return (
      <div className="text-center py-12">
        <p className="text-red-600">{error || 'Submission not found'}</p>
        <Link href="/feedback" className="mt-4 inline-flex items-center gap-2 text-blue-600 hover:underline">
          <ArrowLeft className="h-4 w-4" />
          Back to Feedback Hub
        </Link>
      </div>
    );
  }

  const CategoryIcon = categoryIcons[submission.category];
  const StatusIcon = statusIcons[submission.status];
  const hasUpvoted = submission.upvotes.includes(currentUser);

  return (
    <div className="max-w-3xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Link
          href="/feedback"
          className="p-2 rounded-lg hover:bg-gray-100 transition-colors"
        >
          <ArrowLeft className="h-5 w-5 text-gray-600" />
        </Link>
        <div className="flex items-center gap-2 text-sm text-gray-500">
          <Link href="/feedback" className="hover:text-gray-700">Feedback Hub</Link>
          <span>/</span>
          <span className="text-gray-900">{submission.title}</span>
        </div>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
        <div className="p-6">
          <div className="flex items-start gap-6">
            <div className="flex flex-col items-center">
              <button
                onClick={handleUpvote}
                disabled={upvoting}
                className={`flex flex-col items-center p-3 rounded-lg transition-colors ${
                  hasUpvoted
                    ? 'bg-blue-100 text-blue-600'
                    : 'hover:bg-gray-100 text-gray-400'
                }`}
              >
                <ThumbsUp className={`h-6 w-6 ${hasUpvoted ? 'fill-current' : ''}`} />
                <span className="text-lg font-bold mt-1">{submission.upvote_count}</span>
              </button>
              <span className="text-xs text-gray-500 mt-1">upvotes</span>
            </div>

            <div className="flex-1">
              <div className="flex flex-wrap items-center gap-2 mb-3">
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium ${categoryColors[submission.category]}`}>
                  <CategoryIcon className="h-4 w-4" />
                  {submission.category}
                </span>
                <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-sm font-medium ${statusColors[submission.status]}`}>
                  <StatusIcon className="h-4 w-4" />
                  {submission.status}
                </span>
                <span className={`px-2.5 py-1 rounded-full text-sm font-medium ${priorityColors[submission.priority]}`}>
                  {submission.priority} Priority
                </span>
              </div>

              <h1 className="text-2xl font-semibold text-gray-900">
                {submission.title}
              </h1>

              <div className="flex items-center gap-4 mt-3 text-sm text-gray-500">
                <span className="flex items-center gap-1">
                  <User className="h-4 w-4" />
                  {submission.submitted_by}
                </span>
                <span>{formatDate(submission.submitted_at)}</span>
                {submission.assigned_to && (
                  <span className="text-blue-600">
                    Assigned to: {submission.assigned_to}
                  </span>
                )}
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t border-gray-200">
            <h2 className="text-sm font-medium text-gray-900 mb-2">Description</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{submission.description}</p>
          </div>

          {submission.tags.length > 0 && (
            <div className="mt-4 flex flex-wrap gap-2">
              {submission.tags.map((tag) => (
                <span
                  key={tag}
                  className="px-2.5 py-1 bg-gray-100 text-gray-600 rounded-full text-sm"
                >
                  {tag}
                </span>
              ))}
            </div>
          )}

          {submission.linked_task_id && (
            <div className="mt-6 p-4 bg-green-50 border border-green-200 rounded-lg">
              <div className="flex items-center gap-2 text-green-700">
                <CheckCircle className="h-5 w-5" />
                <span className="font-medium">Converted to Task</span>
              </div>
              <Link
                href={`/tasks?id=${submission.linked_task_id}`}
                className="mt-2 inline-flex items-center gap-1 text-sm text-green-600 hover:underline"
              >
                View Task
                <ExternalLink className="h-3 w-3" />
              </Link>
            </div>
          )}

          {submission.resolution_notes && (
            <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
              <h3 className="text-sm font-medium text-gray-900 mb-1">Resolution Notes</h3>
              <p className="text-gray-700 text-sm">{submission.resolution_notes}</p>
            </div>
          )}
        </div>

        <div className="border-t border-gray-200 bg-gray-50 p-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
            <MessageCircle className="h-5 w-5" />
            Comments ({submission.comments.length})
          </h2>

          {submission.comments.length > 0 ? (
            <div className="space-y-4 mb-6">
              {submission.comments.map((comment) => (
                <div key={comment.id} className="bg-white rounded-lg border border-gray-200 p-4">
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2 text-sm">
                      <span className="font-medium text-gray-900">{comment.user}</span>
                      <span className="text-gray-400">{formatDate(comment.created_at)}</span>
                      {comment.updated_at && (
                        <span className="text-gray-400 text-xs">(edited)</span>
                      )}
                    </div>
                    <button
                      onClick={() => handleDeleteComment(comment.id)}
                      className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                      title="Delete comment"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                  <p className="mt-2 text-gray-700">{comment.content}</p>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-gray-500 text-sm mb-6">No comments yet. Be the first to comment!</p>
          )}

          <form onSubmit={handleAddComment} className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="grid grid-cols-4 gap-3 mb-3">
              <input
                type="text"
                value={commentUser}
                onChange={(e) => setCommentUser(e.target.value)}
                placeholder="Your name"
                className="col-span-1 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none"
                required
              />
              <textarea
                value={commentText}
                onChange={(e) => setCommentText(e.target.value)}
                placeholder="Write a comment..."
                rows={2}
                className="col-span-3 px-3 py-2 border border-gray-300 rounded-lg text-sm focus:border-blue-500 focus:ring-1 focus:ring-blue-500 outline-none resize-none"
                required
              />
            </div>
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={submittingComment || !commentText.trim() || !commentUser.trim()}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {submittingComment ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
                    Posting...
                  </>
                ) : (
                  <>
                    <Send className="h-4 w-4" />
                    Post Comment
                  </>
                )}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}

export default function SubmissionDetailPage() {
  return (
    <Suspense fallback={
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    }>
      <SubmissionDetailContent />
    </Suspense>
  );
}
