'use client';

import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Checkbox } from '@/components/ui/checkbox';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Card } from '@/components/ui/card';
import { cn } from '@/lib/utils';
import {
  DATA_CLASSIFICATIONS,
  type WizardGovernance,
  type DataClassification,
} from '@/lib/agent-factory-types';
import { Shield, AlertTriangle } from 'lucide-react';

interface WizardStepGovernanceProps {
  data: WizardGovernance;
  onChange: (data: Partial<WizardGovernance>) => void;
}

export function WizardStepGovernance({ data, onChange }: WizardStepGovernanceProps) {
  const getClassificationColor = (classification: DataClassification) => {
    switch (classification) {
      case 'Public':
        return 'border-green-300 bg-green-50';
      case 'Internal':
        return 'border-blue-300 bg-blue-50';
      case 'Confidential':
        return 'border-yellow-300 bg-yellow-50';
      case 'Restricted':
        return 'border-red-300 bg-red-50';
    }
  };

  return (
    <div className="space-y-6">
      <Card className="p-4 bg-muted/50">
        <div className="flex gap-3">
          <Shield className="h-5 w-5 text-primary flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-medium mb-1">Security & Compliance</p>
            <p className="text-muted-foreground">
              Configure governance settings to ensure your agent complies with
              organizational policies. These settings affect data handling and audit
              requirements.
            </p>
          </div>
        </div>
      </Card>

      <div className="space-y-2">
        <Label>Data Classification</Label>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {DATA_CLASSIFICATIONS.map((classification) => {
            const isSelected = data.classification === classification.id;
            return (
              <Card
                key={classification.id}
                className={cn(
                  'p-3 cursor-pointer transition-all',
                  isSelected
                    ? getClassificationColor(classification.id)
                    : 'hover:border-primary/50'
                )}
                onClick={() => onChange({ classification: classification.id })}
              >
                <div className="flex items-start gap-2">
                  <div
                    className={cn(
                      'w-4 h-4 rounded-full border-2 flex-shrink-0 mt-0.5',
                      isSelected ? 'border-primary bg-primary' : 'border-muted-foreground/30'
                    )}
                  >
                    {isSelected && (
                      <div className="w-full h-full rounded-full bg-primary-foreground scale-50" />
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-sm">{classification.name}</p>
                    <p className="text-xs text-muted-foreground">
                      {classification.description}
                    </p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>

      {(data.classification === 'Confidential' || data.classification === 'Restricted') && (
        <Card className="p-4 border-yellow-300 bg-yellow-50">
          <div className="flex gap-3">
            <AlertTriangle className="h-5 w-5 text-yellow-600 flex-shrink-0" />
            <div className="text-sm">
              <p className="font-medium text-yellow-800 mb-1">Additional Review Required</p>
              <p className="text-yellow-700">
                Agents handling {data.classification.toLowerCase()} data require additional
                security review before deployment. Your request will be reviewed by the
                security team.
              </p>
            </div>
          </div>
        </Card>
      )}

      <div className="space-y-2">
        <Label htmlFor="costCenter">Cost Center</Label>
        <Input
          id="costCenter"
          placeholder="e.g., CC-12345"
          value={data.costCenter}
          onChange={(e) => onChange({ costCenter: e.target.value })}
        />
        <p className="text-xs text-muted-foreground">
          The cost center for billing and resource allocation
        </p>
      </div>

      <Card
        className={cn(
          'p-4 cursor-pointer transition-all',
          data.requiresApproval && 'border-primary bg-primary/5'
        )}
        onClick={() => onChange({ requiresApproval: !data.requiresApproval })}
      >
        <div className="flex items-start gap-3">
          <Checkbox
            checked={data.requiresApproval}
            onCheckedChange={(checked) => onChange({ requiresApproval: !!checked })}
            className="mt-1"
          />
          <div>
            <Label className="font-medium cursor-pointer">
              Require Manager Approval
            </Label>
            <p className="text-sm text-muted-foreground mt-1">
              If enabled, the agent must be approved by a manager before it can be
              deployed to production. Recommended for enterprise-tier agents.
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
