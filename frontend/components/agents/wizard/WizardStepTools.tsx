'use client';

import { Checkbox } from '@/components/ui/checkbox';
import { Label } from '@/components/ui/label';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import {
  ENTERPRISE_CONNECTORS,
  type WizardTools,
  type EnterpriseConnector,
} from '@/lib/agent-factory-types';
import { Search, Code2, Plug, Check } from 'lucide-react';

interface WizardStepToolsProps {
  data: WizardTools;
  onChange: (data: Partial<WizardTools>) => void;
}

export function WizardStepTools({ data, onChange }: WizardStepToolsProps) {
  const toggleConnector = (connectorId: EnterpriseConnector) => {
    const current = data.connectors;
    const updated = current.includes(connectorId)
      ? current.filter((c) => c !== connectorId)
      : [...current, connectorId];
    onChange({ connectors: updated });
  };

  return (
    <div className="space-y-8">
      <div>
        <h3 className="text-lg font-medium mb-1">Built-in Tools</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Select the core capabilities for your agent
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <Card
            className={cn(
              'p-4 cursor-pointer transition-all hover:border-primary/50',
              data.fileSearch && 'border-primary bg-primary/5'
            )}
            onClick={() => onChange({ fileSearch: !data.fileSearch })}
          >
            <div className="flex items-start gap-3">
              <Checkbox
                checked={data.fileSearch}
                onCheckedChange={(checked) => onChange({ fileSearch: !!checked })}
                className="mt-1"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Search className="h-4 w-4 text-primary" />
                  <Label className="font-medium cursor-pointer">File Search</Label>
                </div>
                <p className="text-sm text-muted-foreground">
                  Search through uploaded documents using semantic similarity
                </p>
              </div>
            </div>
          </Card>

          <Card
            className={cn(
              'p-4 cursor-pointer transition-all hover:border-primary/50',
              data.codeInterpreter && 'border-primary bg-primary/5'
            )}
            onClick={() => onChange({ codeInterpreter: !data.codeInterpreter })}
          >
            <div className="flex items-start gap-3">
              <Checkbox
                checked={data.codeInterpreter}
                onCheckedChange={(checked) => onChange({ codeInterpreter: !!checked })}
                className="mt-1"
              />
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <Code2 className="h-4 w-4 text-primary" />
                  <Label className="font-medium cursor-pointer">Code Interpreter</Label>
                </div>
                <p className="text-sm text-muted-foreground">
                  Execute Python code for data analysis and calculations
                </p>
              </div>
            </div>
          </Card>
        </div>
      </div>

      <div>
        <h3 className="text-lg font-medium mb-1">Enterprise Connectors</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Connect to business systems to access data and take actions (OBO authentication)
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
          {ENTERPRISE_CONNECTORS.map((connector) => {
            const isSelected = data.connectors.includes(connector.id);
            return (
              <Card
                key={connector.id}
                className={cn(
                  'p-3 cursor-pointer transition-all hover:border-primary/50',
                  isSelected && 'border-primary bg-primary/5'
                )}
                onClick={() => toggleConnector(connector.id)}
              >
                <div className="flex items-start gap-2">
                  <div
                    className={cn(
                      'w-5 h-5 rounded border flex items-center justify-center flex-shrink-0 mt-0.5',
                      isSelected
                        ? 'bg-primary border-primary text-primary-foreground'
                        : 'border-input'
                    )}
                  >
                    {isSelected && <Check className="h-3 w-3" />}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <Plug className="h-3.5 w-3.5 text-muted-foreground" />
                      <span className="font-medium text-sm">{connector.name}</span>
                    </div>
                    <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                      {connector.description}
                    </p>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>

        {data.connectors.length > 0 && (
          <div className="mt-4 flex flex-wrap gap-2">
            <span className="text-sm text-muted-foreground">Selected:</span>
            {data.connectors.map((id) => {
              const connector = ENTERPRISE_CONNECTORS.find((c) => c.id === id);
              return (
                <Badge key={id} variant="secondary" className="text-xs">
                  {connector?.name}
                </Badge>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
