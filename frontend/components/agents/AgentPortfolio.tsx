'use client';

import { useState, useMemo } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { AgentCard } from './AgentCard';
import { Bot, Search, Plus } from 'lucide-react';
import type { Agent } from '@/lib/api';

interface AgentPortfolioProps {
  agents: Agent[];
  isLoading?: boolean;
  onCreateClick?: () => void;
  onViewDetails?: (agent: Agent) => void;
}

export function AgentPortfolio({
  agents,
  isLoading = false,
  onCreateClick,
  onViewDetails,
}: AgentPortfolioProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTier, setFilterTier] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');

  const filteredAgents = useMemo(() => {
    return agents.filter((agent) => {
      const matchesSearch =
        agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        (agent.use_case?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false) ||
        agent.data_sources.some((source) =>
          source.toLowerCase().includes(searchQuery.toLowerCase())
        );

      const matchesTier = filterTier === 'all' || agent.tier === filterTier;
      const matchesStatus = filterStatus === 'all' || agent.status === filterStatus;

      return matchesSearch && matchesTier && matchesStatus;
    });
  }, [agents, searchQuery, filterTier, filterStatus]);

  const clearFilters = () => {
    setSearchQuery('');
    setFilterTier('all');
    setFilterStatus('all');
  };

  const hasFilters = searchQuery || filterTier !== 'all' || filterStatus !== 'all';

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <div className="text-lg text-gray-600">Loading agents...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col lg:flex-row gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            placeholder="Search agents by name, description, or data sources..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <Select value={filterTier} onValueChange={setFilterTier}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="Filter by tier" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Tiers</SelectItem>
            <SelectItem value="Tier1_Individual">Tier 1 - Individual</SelectItem>
            <SelectItem value="Tier2_Department">Tier 2 - Department</SelectItem>
            <SelectItem value="Tier3_Enterprise">Tier 3 - Enterprise</SelectItem>
          </SelectContent>
        </Select>

        <Select value={filterStatus} onValueChange={setFilterStatus}>
          <SelectTrigger className="w-full sm:w-[180px]">
            <SelectValue placeholder="Filter by status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="Idea">Idea</SelectItem>
            <SelectItem value="Design">Design</SelectItem>
            <SelectItem value="Development">Development</SelectItem>
            <SelectItem value="Testing">Testing</SelectItem>
            <SelectItem value="Staging">Staging</SelectItem>
            <SelectItem value="Production">Production</SelectItem>
            <SelectItem value="Deprecated">Deprecated</SelectItem>
          </SelectContent>
        </Select>

        {onCreateClick && (
          <Button onClick={onCreateClick} className="hidden lg:flex">
            <Plus className="mr-2 h-4 w-4" />
            New Agent
          </Button>
        )}
      </div>

      {filteredAgents.length === 0 ? (
        <Card>
          <CardContent className="p-12 text-center">
            <Bot className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No agents found
            </h3>
            <p className="text-gray-600 mb-4">
              {hasFilters
                ? 'Try adjusting your search or filters'
                : 'Get started by creating your first agent'}
            </p>
            {onCreateClick && (
              <Button onClick={onCreateClick}>
                <Plus className="mr-2 h-4 w-4" />
                Create Your First Agent
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAgents.map((agent) => (
            <AgentCard
              key={agent.id}
              agent={agent}
              onViewDetails={onViewDetails}
            />
          ))}
        </div>
      )}

      <div className="flex items-center justify-between text-sm text-gray-600">
        <div>
          Showing {filteredAgents.length} of {agents.length} agents
        </div>
        {hasFilters && (
          <Button variant="ghost" size="sm" onClick={clearFilters}>
            Clear filters
          </Button>
        )}
      </div>
    </div>
  );
}
