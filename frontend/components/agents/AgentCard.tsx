'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Bot, Users, Building2, Activity, Database } from 'lucide-react';
import type { Agent } from '@/lib/api';

interface AgentCardProps {
  agent: Agent;
  onViewDetails?: (agent: Agent) => void;
}

export function AgentCard({ agent, onViewDetails }: AgentCardProps) {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Production':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'Staging':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'Testing':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'Development':
        return 'bg-purple-100 text-purple-800 border-purple-300';
      case 'Design':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'Idea':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      case 'Deprecated':
        return 'bg-red-100 text-red-800 border-red-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getTierIcon = (tier: string) => {
    switch (tier) {
      case 'Tier1_Individual':
        return <Bot className="h-5 w-5" />;
      case 'Tier2_Department':
        return <Users className="h-5 w-5" />;
      case 'Tier3_Enterprise':
        return <Building2 className="h-5 w-5" />;
      default:
        return <Bot className="h-5 w-5" />;
    }
  };

  const getTierColor = (tier: string) => {
    switch (tier) {
      case 'Tier1_Individual':
        return 'bg-blue-50 text-blue-600';
      case 'Tier2_Department':
        return 'bg-purple-50 text-purple-600';
      case 'Tier3_Enterprise':
        return 'bg-orange-50 text-orange-600';
      default:
        return 'bg-gray-50 text-gray-600';
    }
  };

  const getTierLabel = (tier: string) => {
    switch (tier) {
      case 'Tier1_Individual':
        return 'Individual';
      case 'Tier2_Department':
        return 'Department';
      case 'Tier3_Enterprise':
        return 'Enterprise';
      default:
        return tier;
    }
  };

  return (
    <Card className="hover:shadow-lg transition-shadow">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between mb-2">
          <div className={`rounded-lg p-3 ${getTierColor(agent.tier)}`}>
            {getTierIcon(agent.tier)}
          </div>
          <Badge className={getStatusColor(agent.status)} variant="outline">
            <Activity className="h-3 w-3 mr-1" />
            {agent.status}
          </Badge>
        </div>
        <CardTitle className="text-xl">{agent.name}</CardTitle>
        <div className="flex items-center gap-2 mt-1">
          <Badge variant="outline" className="text-xs">
            {getTierLabel(agent.tier)}
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <p className="text-sm text-gray-600 mb-4">{agent.description}</p>

        <div className="space-y-3 mb-4">
          <div className="flex items-start gap-2">
            <Users className="h-4 w-4 text-gray-500 mt-0.5 flex-shrink-0" />
            <div className="text-sm">
              <div className="font-medium text-gray-700">Owner</div>
              <div className="text-gray-600">{agent.owner}</div>
            </div>
          </div>

          {agent.department && (
            <div className="flex items-start gap-2">
              <Building2 className="h-4 w-4 text-gray-500 mt-0.5 flex-shrink-0" />
              <div className="text-sm">
                <div className="font-medium text-gray-700">Department</div>
                <div className="text-gray-600">{agent.department}</div>
              </div>
            </div>
          )}

          {agent.use_case && (
            <div className="text-sm">
              <div className="font-medium text-gray-700 mb-1">Use Case</div>
              <div className="text-gray-600 line-clamp-2">{agent.use_case}</div>
            </div>
          )}
        </div>

        {agent.data_sources.length > 0 && (
          <div className="mb-4">
            <div className="flex items-center gap-2 mb-2">
              <Database className="h-4 w-4 text-gray-500" />
              <h4 className="text-xs font-semibold text-gray-700 uppercase">
                Data Sources
              </h4>
            </div>
            <div className="flex flex-wrap gap-2">
              {agent.data_sources.slice(0, 3).map((source, idx) => (
                <Badge key={idx} variant="secondary" className="text-xs">
                  {source}
                </Badge>
              ))}
              {agent.data_sources.length > 3 && (
                <Badge variant="secondary" className="text-xs">
                  +{agent.data_sources.length - 3} more
                </Badge>
              )}
            </div>
          </div>
        )}

        <div className="flex gap-2 pt-4 border-t">
          <Button
            variant="outline"
            size="sm"
            className="flex-1"
            onClick={() => onViewDetails?.(agent)}
          >
            View Details
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}
