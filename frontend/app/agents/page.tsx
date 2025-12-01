'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { api, Agent } from '@/lib/api';
import { TeamMemberSelect } from '@/components/ui/team-member-select';
import {
  Bot,
  Search,
  Plus,
  Activity,
  Users,
  Building2,
  Database,
} from 'lucide-react';

function SearchParamsHandler({ onCreateOpen }: { onCreateOpen: () => void }) {
  const searchParams = useSearchParams();

  useEffect(() => {
    if (searchParams.get('create') === 'true') {
      onCreateOpen();
    }
  }, [searchParams, onCreateOpen]);

  return null;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTier, setFilterTier] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  const [newAgent, setNewAgent] = useState({
    name: '',
    description: '',
    owner: '',
    department: '',
    tier: 'Tier1_Individual' as 'Tier1_Individual' | 'Tier2_Department' | 'Tier3_Enterprise',
    status: 'Idea' as 'Idea' | 'Design' | 'Development' | 'Testing' | 'Staging' | 'Production' | 'Deprecated',
    use_case: '',
    data_sources: '',
  });

  useEffect(() => {
    loadAgents();
  }, []);

  async function loadAgents() {
    try {
      const data = await api.agents.list();
      setAgents(data);
    } catch (error) {
      console.error('Failed to load agents:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateAgent() {
    try {
      const dataSourcesList = newAgent.data_sources
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      await api.agents.create({
        name: newAgent.name,
        description: newAgent.description,
        owner: newAgent.owner,
        department: newAgent.department || undefined,
        tier: newAgent.tier,
        status: newAgent.status,
        use_case: newAgent.use_case || undefined,
        data_sources: dataSourcesList,
        related_tasks: [],
      });

      setIsCreateDialogOpen(false);
      setNewAgent({
        name: '',
        description: '',
        owner: '',
        department: '',
        tier: 'Tier1_Individual',
        status: 'Idea',
        use_case: '',
        data_sources: '',
      });
      loadAgents();
    } catch (error) {
      console.error('Failed to create agent:', error);
      alert('Failed to create agent. Please try again.');
    }
  }

  const filteredAgents = agents.filter((agent) => {
    const matchesSearch =
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (agent.use_case?.toLowerCase().includes(searchQuery.toLowerCase()) ?? false) ||
      agent.data_sources.some((source) =>
        source.toLowerCase().includes(searchQuery.toLowerCase())
      );

    const matchesTier = filterTier === 'all' || agent.tier === filterTier;
    const matchesStatus =
      filterStatus === 'all' || agent.status === filterStatus;

    return matchesSearch && matchesTier && matchesStatus;
  });

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

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading agents...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Suspense fallback={null}>
        <SearchParamsHandler onCreateOpen={() => setIsCreateDialogOpen(true)} />
      </Suspense>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Agent Portfolio</h1>
          <p className="mt-2 text-gray-600">
            Browse and manage your Microsoft Agent Framework implementations
          </p>
        </div>

        <div className="mb-6 flex flex-col sm:flex-row gap-4">
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

          <Button onClick={() => setIsCreateDialogOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Agent
          </Button>
        </div>

        {filteredAgents.length === 0 ? (
          <Card>
            <CardContent className="p-12 text-center">
              <Bot className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                No agents found
              </h3>
              <p className="text-gray-600 mb-4">
                {searchQuery || filterTier !== 'all' || filterStatus !== 'all'
                  ? 'Try adjusting your search or filters'
                  : 'Get started by creating your first agent'}
              </p>
              <Button onClick={() => setIsCreateDialogOpen(true)}>
                <Plus className="mr-2 h-4 w-4" />
                Create Your First Agent
              </Button>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredAgents.map((agent) => (
              <Card
                key={agent.id}
                className="hover:shadow-lg transition-shadow cursor-pointer"
              >
                <CardHeader className="pb-3">
                  <div className="flex items-start justify-between mb-2">
                    <div
                      className={`rounded-lg p-3 ${getTierColor(agent.tier)}`}
                    >
                      {getTierIcon(agent.tier)}
                    </div>
                    <Badge
                      className={getStatusColor(agent.status)}
                      variant="outline"
                    >
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
                  <p className="text-sm text-gray-600 mb-4">
                    {agent.description}
                  </p>

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
                          <Badge
                            key={idx}
                            variant="secondary"
                            className="text-xs"
                          >
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
                    <Button variant="outline" size="sm" className="flex-1">
                      View Details
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}

        <div className="mt-6 flex items-center justify-between text-sm text-gray-600">
          <div>
            Showing {filteredAgents.length} of {agents.length} agents
          </div>
          {(searchQuery || filterTier !== 'all' || filterStatus !== 'all') && (
            <Button
              variant="ghost"
              size="sm"
              onClick={() => {
                setSearchQuery('');
                setFilterTier('all');
                setFilterStatus('all');
              }}
            >
              Clear filters
            </Button>
          )}
        </div>

        <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Agent</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <label className="text-sm font-medium">Agent Name</label>
                <Input
                  placeholder="e.g., Customer Support Bot"
                  value={newAgent.name}
                  onChange={(e) =>
                    setNewAgent({ ...newAgent, name: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium">Description</label>
                <Textarea
                  placeholder="Brief description of the agent's purpose"
                  value={newAgent.description}
                  onChange={(e) =>
                    setNewAgent({ ...newAgent, description: e.target.value })
                  }
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Tier</label>
                  <Select
                    value={newAgent.tier}
                    onValueChange={(value: 'Tier1_Individual' | 'Tier2_Department' | 'Tier3_Enterprise') =>
                      setNewAgent({ ...newAgent, tier: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Tier1_Individual">Tier 1 - Individual</SelectItem>
                      <SelectItem value="Tier2_Department">Tier 2 - Department</SelectItem>
                      <SelectItem value="Tier3_Enterprise">Tier 3 - Enterprise</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Status</label>
                  <Select
                    value={newAgent.status}
                    onValueChange={(value: 'Idea' | 'Design' | 'Development' | 'Testing' | 'Staging' | 'Production' | 'Deprecated') =>
                      setNewAgent({ ...newAgent, status: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Idea">Idea</SelectItem>
                      <SelectItem value="Design">Design</SelectItem>
                      <SelectItem value="Development">Development</SelectItem>
                      <SelectItem value="Testing">Testing</SelectItem>
                      <SelectItem value="Staging">Staging</SelectItem>
                      <SelectItem value="Production">Production</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">Owner</label>
                <TeamMemberSelect
                  value={newAgent.owner}
                  onValueChange={(value) =>
                    setNewAgent({ ...newAgent, owner: value })
                  }
                  placeholder="Select owner"
                />
              </div>
              <div>
                <label className="text-sm font-medium">Department (optional)</label>
                <Input
                  placeholder="e.g., Customer Success"
                  value={newAgent.department}
                  onChange={(e) =>
                    setNewAgent({ ...newAgent, department: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium">Use Case (optional)</label>
                <Textarea
                  placeholder="Describe the primary use case for this agent"
                  value={newAgent.use_case}
                  onChange={(e) =>
                    setNewAgent({ ...newAgent, use_case: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium">Data Sources (comma-separated)</label>
                <Input
                  placeholder="e.g., Salesforce, SharePoint, Teams"
                  value={newAgent.data_sources}
                  onChange={(e) =>
                    setNewAgent({ ...newAgent, data_sources: e.target.value })
                  }
                />
              </div>
              <div className="flex gap-3 pt-4">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setIsCreateDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1"
                  onClick={handleCreateAgent}
                  disabled={!newAgent.name || !newAgent.description || !newAgent.owner}
                >
                  Create Agent
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
