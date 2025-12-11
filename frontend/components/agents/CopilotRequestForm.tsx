'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Workflow, ArrowLeft, Send, CheckCircle } from 'lucide-react';
import { api } from '@/lib/api';
import type { CopilotRequest } from '@/lib/agent-factory-types';

interface CopilotRequestFormProps {
  onBack: () => void;
  onSuccess?: () => void;
  defaultRequestor?: string;
}

export function CopilotRequestForm({
  onBack,
  onSuccess,
  defaultRequestor = '',
}: CopilotRequestFormProps) {
  const [formData, setFormData] = useState<Omit<CopilotRequest, 'attachments'>>({
    workflow_name: '',
    department: '',
    requestor: defaultRequestor,
    business_justification: '',
    estimated_users: '',
    target_timeline: '',
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isSubmitted, setIsSubmitted] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleChange = (field: keyof typeof formData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
    setError(null);
  };

  const isValid =
    formData.workflow_name.trim() &&
    formData.department.trim() &&
    formData.requestor.trim() &&
    formData.business_justification.trim();

  const handleSubmit = async () => {
    if (!isValid) return;

    setIsSubmitting(true);
    setError(null);

    try {
      await api.submissions.create({
        title: `Copilot Studio Request: ${formData.workflow_name}`,
        category: 'Feature Request',
        priority: 'Medium',
        description: `
**Workflow Name:** ${formData.workflow_name}
**Department:** ${formData.department}
**Requestor:** ${formData.requestor}
**Estimated Users:** ${formData.estimated_users || 'Not specified'}
**Target Timeline:** ${formData.target_timeline || 'Not specified'}

**Business Justification:**
${formData.business_justification}

---
*This request was submitted through the Agent Factory intake process.*
        `.trim(),
        submitted_by: formData.requestor,
        tags: ['copilot-studio-request', 'agent-factory'],
      });

      setIsSubmitted(true);
      onSuccess?.();
    } catch (err) {
      console.error('Failed to submit request:', err);
      setError('Failed to submit request. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isSubmitted) {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardContent className="p-12 text-center">
          <div className="mx-auto mb-6 p-4 rounded-full bg-green-100 w-fit">
            <CheckCircle className="h-12 w-12 text-green-600" />
          </div>
          <h3 className="text-2xl font-semibold text-gray-900 mb-2">
            Request Submitted!
          </h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Your Copilot Studio environment request has been submitted. Our team
            will review it and reach out to discuss next steps.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button variant="outline" onClick={onBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to Agent Factory
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to assessment
        </Button>
      </div>

      <Card>
        <CardHeader className="text-center pb-4">
          <div className="mx-auto mb-4 p-4 rounded-full bg-blue-500/10">
            <Workflow className="h-8 w-8 text-blue-500" />
          </div>
          <CardTitle className="text-xl">Request Copilot Studio Environment</CardTitle>
          <p className="text-sm text-muted-foreground mt-2">
            Submit a request for a structured workflow using Copilot Studio. Our
            team will review and provision the environment.
          </p>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <Label htmlFor="workflow_name">Workflow Name *</Label>
            <Input
              id="workflow_name"
              placeholder="e.g., Leave Request Approval Bot"
              value={formData.workflow_name}
              onChange={(e) => handleChange('workflow_name', e.target.value)}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="department">Department *</Label>
              <Select
                value={formData.department}
                onValueChange={(value) => handleChange('department', value)}
              >
                <SelectTrigger id="department">
                  <SelectValue placeholder="Select department" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="HR">Human Resources</SelectItem>
                  <SelectItem value="Finance">Finance</SelectItem>
                  <SelectItem value="IT">IT</SelectItem>
                  <SelectItem value="Operations">Operations</SelectItem>
                  <SelectItem value="Sales">Sales</SelectItem>
                  <SelectItem value="Marketing">Marketing</SelectItem>
                  <SelectItem value="Customer Success">Customer Success</SelectItem>
                  <SelectItem value="Other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="requestor">Requestor *</Label>
              <Input
                id="requestor"
                placeholder="Your name"
                value={formData.requestor}
                onChange={(e) => handleChange('requestor', e.target.value)}
              />
            </div>
          </div>

          <div className="space-y-2">
            <Label htmlFor="business_justification">Business Justification *</Label>
            <Textarea
              id="business_justification"
              placeholder="Describe the business problem this workflow will solve and expected benefits..."
              value={formData.business_justification}
              onChange={(e) => handleChange('business_justification', e.target.value)}
              rows={4}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="estimated_users">Estimated Users</Label>
              <Input
                id="estimated_users"
                placeholder="e.g., 50-100 employees"
                value={formData.estimated_users}
                onChange={(e) => handleChange('estimated_users', e.target.value)}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="target_timeline">Target Timeline</Label>
              <Select
                value={formData.target_timeline}
                onValueChange={(value) => handleChange('target_timeline', value)}
              >
                <SelectTrigger id="target_timeline">
                  <SelectValue placeholder="When do you need this?" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="ASAP">As soon as possible</SelectItem>
                  <SelectItem value="1-2 weeks">1-2 weeks</SelectItem>
                  <SelectItem value="1 month">Within 1 month</SelectItem>
                  <SelectItem value="This quarter">This quarter</SelectItem>
                  <SelectItem value="No rush">No specific deadline</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          {error && (
            <div className="text-sm text-destructive bg-destructive/10 p-3 rounded-md">
              {error}
            </div>
          )}

          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <Button variant="outline" className="flex-1" onClick={onBack}>
              Cancel
            </Button>
            <Button
              className="flex-1 bg-blue-500 hover:bg-blue-600"
              onClick={handleSubmit}
              disabled={!isValid || isSubmitting}
            >
              {isSubmitting ? (
                'Submitting...'
              ) : (
                <>
                  <Send className="h-4 w-4 mr-2" />
                  Submit Request
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
