'use client';

import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { TeamMemberSelect } from '@/components/ui/team-member-select';
import type { WizardBasicInfo } from '@/lib/agent-factory-types';

interface WizardStepBasicInfoProps {
  data: WizardBasicInfo;
  onChange: (data: Partial<WizardBasicInfo>) => void;
}

export function WizardStepBasicInfo({ data, onChange }: WizardStepBasicInfoProps) {
  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="name">
          Agent Name <span className="text-destructive">*</span>
        </Label>
        <Input
          id="name"
          placeholder="e.g., Customer Support Assistant"
          value={data.name}
          onChange={(e) => onChange({ name: e.target.value })}
        />
        <p className="text-xs text-muted-foreground">
          Choose a clear, descriptive name that reflects the agent&apos;s purpose
        </p>
      </div>

      <div className="space-y-2">
        <Label htmlFor="description">
          Description <span className="text-destructive">*</span>
        </Label>
        <Textarea
          id="description"
          placeholder="Describe what this agent does and its primary function..."
          value={data.description}
          onChange={(e) => onChange({ description: e.target.value })}
          rows={3}
        />
        <p className="text-xs text-muted-foreground">
          Provide a brief summary of the agent&apos;s capabilities and use case
        </p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div className="space-y-2">
          <Label htmlFor="owner">
            Owner <span className="text-destructive">*</span>
          </Label>
          <TeamMemberSelect
            value={data.owner}
            onValueChange={(value) => onChange({ owner: value })}
            placeholder="Select owner"
          />
          <p className="text-xs text-muted-foreground">
            The person responsible for this agent
          </p>
        </div>

        <div className="space-y-2">
          <Label htmlFor="department">Department</Label>
          <Input
            id="department"
            placeholder="e.g., Customer Success"
            value={data.department}
            onChange={(e) => onChange({ department: e.target.value })}
          />
          <p className="text-xs text-muted-foreground">
            The team or department using this agent
          </p>
        </div>
      </div>
    </div>
  );
}
