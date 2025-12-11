'use client';

import { FileUpload } from '@/components/ui/file-upload';
import { Card } from '@/components/ui/card';
import type { WizardKnowledge } from '@/lib/agent-factory-types';
import { BookOpen, Info } from 'lucide-react';

interface WizardStepKnowledgeProps {
  data: WizardKnowledge;
  onChange: (data: Partial<WizardKnowledge>) => void;
}

export function WizardStepKnowledge({ data, onChange }: WizardStepKnowledgeProps) {
  return (
    <div className="space-y-6">
      <Card className="p-4 bg-amber-50/50 border-amber-200">
        <div className="flex gap-3">
          <Info className="h-5 w-5 text-amber-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-medium text-amber-900 mb-1">Knowledge Base (Optional)</p>
            <p className="text-amber-700">
              Upload documents to create a searchable knowledge base for your agent.
              The agent will use these documents to answer questions and provide accurate
              information. Files are processed into a vector store for semantic search.
            </p>
          </div>
        </div>
      </Card>

      <div>
        <div className="flex items-center gap-2 mb-4">
          <BookOpen className="h-5 w-5 text-primary" />
          <h3 className="text-lg font-medium">Upload Documents</h3>
        </div>

        <FileUpload
          files={data.files}
          onFilesChange={(files) => onChange({ files })}
          maxFiles={10}
          maxSizeMB={50}
          acceptedTypes={['.pdf', '.doc', '.docx', '.txt', '.md', '.json', '.csv', '.xlsx']}
        />
      </div>

      <div className="text-sm text-muted-foreground space-y-2">
        <p className="font-medium">Supported file types:</p>
        <ul className="list-disc list-inside space-y-1 ml-2">
          <li>Documents: PDF, DOC, DOCX, TXT, MD</li>
          <li>Data: JSON, CSV, XLSX</li>
        </ul>
        <p className="mt-4">
          Files will be processed and indexed when the agent is provisioned. This may
          take a few minutes depending on the file size and quantity.
        </p>
      </div>
    </div>
  );
}
