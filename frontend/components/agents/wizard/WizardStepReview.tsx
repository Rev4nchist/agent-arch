'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import {
  ENTERPRISE_CONNECTORS,
  DATA_CLASSIFICATIONS,
  type WizardData,
} from '@/lib/agent-factory-types';
import {
  User,
  Building2,
  FileText,
  Search,
  Code2,
  Plug,
  BookOpen,
  Shield,
  CheckCircle,
  XCircle,
} from 'lucide-react';

interface WizardStepReviewProps {
  data: WizardData;
  onEditStep: (step: number) => void;
}

export function WizardStepReview({ data, onEditStep }: WizardStepReviewProps) {
  const classificationInfo = DATA_CLASSIFICATIONS.find(
    (c) => c.id === data.governance.classification
  );

  const selectedConnectors = ENTERPRISE_CONNECTORS.filter((c) =>
    data.tools.connectors.includes(c.id)
  );

  const hasKnowledge = data.knowledge.files.length > 0;
  const hasTools = data.tools.fileSearch || data.tools.codeInterpreter || data.tools.connectors.length > 0;

  return (
    <div className="space-y-6">
      <div className="text-center mb-8">
        <h3 className="text-lg font-semibold mb-2">Review Your Agent</h3>
        <p className="text-muted-foreground">
          Please review the configuration before provisioning. Click any section to edit.
        </p>
      </div>

      <Card
        className="cursor-pointer hover:border-primary/50 transition-colors"
        onClick={() => onEditStep(1)}
      >
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <User className="h-4 w-4" />
            Basic Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-xs text-muted-foreground">Name</p>
              <p className="font-medium">{data.basicInfo.name || '—'}</p>
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Owner</p>
              <p className="font-medium">{data.basicInfo.owner || '—'}</p>
            </div>
          </div>
          <div>
            <p className="text-xs text-muted-foreground">Description</p>
            <p className="text-sm line-clamp-2">{data.basicInfo.description || '—'}</p>
          </div>
          {data.basicInfo.department && (
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <Building2 className="h-3.5 w-3.5" />
              {data.basicInfo.department}
            </div>
          )}
        </CardContent>
      </Card>

      <Card
        className="cursor-pointer hover:border-primary/50 transition-colors"
        onClick={() => onEditStep(2)}
      >
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Instructions
          </CardTitle>
        </CardHeader>
        <CardContent>
          {data.instructions.systemPrompt ? (
            <div className="bg-muted/50 rounded-md p-3 text-sm font-mono max-h-32 overflow-y-auto">
              {data.instructions.systemPrompt.slice(0, 500)}
              {data.instructions.systemPrompt.length > 500 && '...'}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">No instructions set</p>
          )}
        </CardContent>
      </Card>

      <Card
        className="cursor-pointer hover:border-primary/50 transition-colors"
        onClick={() => onEditStep(3)}
      >
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Plug className="h-4 w-4" />
            Tools & Capabilities
          </CardTitle>
        </CardHeader>
        <CardContent>
          {hasTools ? (
            <div className="space-y-3">
              <div className="flex flex-wrap gap-2">
                {data.tools.fileSearch && (
                  <Badge variant="secondary" className="gap-1">
                    <Search className="h-3 w-3" />
                    File Search
                  </Badge>
                )}
                {data.tools.codeInterpreter && (
                  <Badge variant="secondary" className="gap-1">
                    <Code2 className="h-3 w-3" />
                    Code Interpreter
                  </Badge>
                )}
              </div>
              {selectedConnectors.length > 0 && (
                <div>
                  <p className="text-xs text-muted-foreground mb-2">Enterprise Connectors:</p>
                  <div className="flex flex-wrap gap-2">
                    {selectedConnectors.map((c) => (
                      <Badge key={c.id} variant="outline" className="text-xs">
                        {c.name}
                      </Badge>
                    ))}
                  </div>
                </div>
              )}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">No tools selected</p>
          )}
        </CardContent>
      </Card>

      <Card
        className="cursor-pointer hover:border-primary/50 transition-colors"
        onClick={() => onEditStep(4)}
      >
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <BookOpen className="h-4 w-4" />
            Knowledge Base
          </CardTitle>
        </CardHeader>
        <CardContent>
          {hasKnowledge ? (
            <div>
              <p className="text-sm font-medium mb-2">
                {data.knowledge.files.length} file{data.knowledge.files.length !== 1 && 's'} to be indexed
              </p>
              <ul className="text-sm text-muted-foreground space-y-1">
                {data.knowledge.files.slice(0, 3).map((file, idx) => (
                  <li key={idx} className="truncate">
                    {file.name}
                  </li>
                ))}
                {data.knowledge.files.length > 3 && (
                  <li>+{data.knowledge.files.length - 3} more</li>
                )}
              </ul>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground italic">No documents uploaded</p>
          )}
        </CardContent>
      </Card>

      <Card
        className="cursor-pointer hover:border-primary/50 transition-colors"
        onClick={() => onEditStep(5)}
      >
        <CardHeader className="pb-2">
          <CardTitle className="text-sm flex items-center gap-2">
            <Shield className="h-4 w-4" />
            Governance
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center gap-2">
              <Badge
                variant="outline"
                className={cn(
                  data.governance.classification === 'Public' && 'border-green-300 bg-green-50 text-green-700',
                  data.governance.classification === 'Internal' && 'border-blue-300 bg-blue-50 text-blue-700',
                  data.governance.classification === 'Confidential' && 'border-yellow-300 bg-yellow-50 text-yellow-700',
                  data.governance.classification === 'Restricted' && 'border-red-300 bg-red-50 text-red-700'
                )}
              >
                {classificationInfo?.name || data.governance.classification}
              </Badge>
              {data.governance.costCenter && (
                <span className="text-sm text-muted-foreground">
                  Cost Center: {data.governance.costCenter}
                </span>
              )}
            </div>
            <div className="flex items-center gap-2 text-sm">
              {data.governance.requiresApproval ? (
                <>
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Manager approval required</span>
                </>
              ) : (
                <>
                  <XCircle className="h-4 w-4 text-muted-foreground" />
                  <span className="text-muted-foreground">No approval required</span>
                </>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
