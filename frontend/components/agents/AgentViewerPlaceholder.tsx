'use client';

import { Card, CardContent } from '@/components/ui/card';
import { MessageSquare, Construction } from 'lucide-react';

export function AgentViewerPlaceholder() {
  return (
    <Card className="max-w-2xl mx-auto">
      <CardContent className="p-12 text-center">
        <div className="relative inline-block mb-6">
          <MessageSquare className="h-16 w-16 text-muted-foreground/50" />
          <Construction className="h-8 w-8 text-yellow-500 absolute -bottom-1 -right-1" />
        </div>
        <h3 className="text-xl font-semibold text-gray-900 mb-2">
          Agent Viewer Coming Soon
        </h3>
        <p className="text-gray-600 mb-4 max-w-md mx-auto">
          The Agent Viewer will allow you to interact with your provisioned agents
          through a chat interface, manage conversation threads, and monitor tool
          executions in real-time.
        </p>
        <div className="text-sm text-muted-foreground">
          <p className="font-medium mb-2">Planned features:</p>
          <ul className="space-y-1">
            <li>Chat with any agent by selecting from the dropdown</li>
            <li>Create and manage conversation threads</li>
            <li>View tool call execution and results</li>
            <li>On-Behalf-Of (OBO) token status indicator</li>
          </ul>
        </div>
      </CardContent>
    </Card>
  );
}
