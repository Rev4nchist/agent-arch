'use client';

import { useState } from 'react';
import { useAuth } from '@/components/providers/AuthProvider';
import { accessApi, AccessRequestCreate } from '@/lib/access-api';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Send, CheckCircle2, Loader2 } from 'lucide-react';

interface RequestAccessFormProps {
  onSuccess?: () => void;
}

export function RequestAccessForm({ onSuccess }: RequestAccessFormProps) {
  const { user } = useAuth();
  const [reason, setReason] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user?.username || !user?.name) return;

    setIsSubmitting(true);
    setError(null);

    try {
      const request: AccessRequestCreate = {
        email: user.username,
        name: user.name,
        reason: reason || undefined,
      };

      await accessApi.requestAccess(request);
      setIsSubmitted(true);
      onSuccess?.();
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to submit request';
      if (message.includes('already')) {
        setError('You already have a pending access request.');
      } else {
        setError(message);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <div className="text-center py-8">
        <CheckCircle2 className="h-16 w-16 text-green-500 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-gray-900 mb-2">Request Submitted</h3>
        <p className="text-gray-600">
          Your access request has been submitted. An administrator will review your request shortly.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
        <input
          type="text"
          value={user?.name || ''}
          disabled
          className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
        <input
          type="email"
          value={user?.username || ''}
          disabled
          className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-500"
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Reason for Access <span className="text-gray-400">(optional)</span>
        </label>
        <Textarea
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          placeholder="Briefly describe why you need access to this platform..."
          rows={3}
          className="w-full"
        />
      </div>

      {error && (
        <div className="p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">
          {error}
        </div>
      )}

      <Button
        type="submit"
        disabled={isSubmitting}
        className="w-full bg-blue-600 hover:bg-blue-700"
      >
        {isSubmitting ? (
          <>
            <Loader2 className="h-4 w-4 mr-2 animate-spin" />
            Submitting...
          </>
        ) : (
          <>
            <Send className="h-4 w-4 mr-2" />
            Request Access
          </>
        )}
      </Button>
    </form>
  );
}
