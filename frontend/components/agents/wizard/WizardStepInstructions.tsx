'use client';

import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { INSTRUCTION_TEMPLATES, type WizardInstructions } from '@/lib/agent-factory-types';
import { Lightbulb } from 'lucide-react';

interface WizardStepInstructionsProps {
  data: WizardInstructions;
  onChange: (data: Partial<WizardInstructions>) => void;
}

export function WizardStepInstructions({ data, onChange }: WizardStepInstructionsProps) {
  const handleTemplateChange = (templateId: string) => {
    const template = INSTRUCTION_TEMPLATES.find((t) => t.id === templateId);
    if (template) {
      onChange({
        templateId,
        systemPrompt: template.prompt,
      });
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-4 bg-blue-50/50 border-blue-200">
        <div className="flex gap-3">
          <Lightbulb className="h-5 w-5 text-blue-500 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-medium text-blue-900 mb-1">Writing Good Instructions</p>
            <p className="text-blue-700">
              Clear instructions help your agent understand its role and boundaries. Include
              the agent&apos;s purpose, tone, what it should and shouldn&apos;t do, and how
              to handle edge cases.
            </p>
          </div>
        </div>
      </Card>

      <div className="space-y-2">
        <Label htmlFor="template">Start from a Template</Label>
        <Select value={data.templateId || ''} onValueChange={handleTemplateChange}>
          <SelectTrigger id="template">
            <SelectValue placeholder="Choose a template (optional)" />
          </SelectTrigger>
          <SelectContent>
            {INSTRUCTION_TEMPLATES.map((template) => (
              <SelectItem key={template.id} value={template.id}>
                {template.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-xs text-muted-foreground">
          Select a template to get started quickly, or write your own instructions below
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="systemPrompt">
          System Instructions <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id="systemPrompt"
          placeholder="You are a helpful assistant that..."
          value={data.systemPrompt}
          onChange={(e) => onChange({ systemPrompt: e.target.value })}
          rows={10}
          className="font-mono text-sm"
        />
        <div className="flex justify-between text-xs text-muted-foreground">
          <span>
            Define the agent&apos;s personality, capabilities, and guidelines
          </span>
          <span>{data.systemPrompt.length} characters</span>
        </div>
      </div>
    </div>
  );
}
