'use client';

import { useEffect, useState, Suspense, useCallback } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  AgentPortfolio,
  AgentGatekeeper,
  CopilotRequestForm,
  AgentBuilderWizard,
  AgentViewerPlaceholder,
} from '@/components/agents';
import { api, Agent } from '@/lib/api';
import { Briefcase, PlusCircle, MessageSquare } from 'lucide-react';

type CreateFlowState = 'gatekeeper' | 'copilot' | 'wizard';

function SearchParamsHandler({
  onCreateOpen,
}: {
  onCreateOpen: () => void;
}) {
  const searchParams = useSearchParams();

  useEffect(() => {
    if (searchParams.get('create') === 'true') {
      onCreateOpen();
    }
  }, [searchParams, onCreateOpen]);

  return null;
}

export default function AgentsPage() {
  const router = useRouter();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('portfolio');
  const [createFlowState, setCreateFlowState] = useState<CreateFlowState>('gatekeeper');

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

  const handleCreateClick = useCallback(() => {
    setActiveTab('create');
    setCreateFlowState('gatekeeper');
  }, []);

  const handleGatekeeperComplete = (recommendation: 'copilot' | 'azure') => {
    if (recommendation === 'copilot') {
      setCreateFlowState('copilot');
    } else {
      setCreateFlowState('wizard');
    }
  };

  const handleBackToGatekeeper = () => {
    setCreateFlowState('gatekeeper');
  };

  const handleBackToPortfolio = () => {
    setActiveTab('portfolio');
    setCreateFlowState('gatekeeper');
  };

  const handleAgentCreated = () => {
    loadAgents();
    setActiveTab('portfolio');
    setCreateFlowState('gatekeeper');
  };

  const handleViewDetails = (agent: Agent) => {
    console.log('View details for agent:', agent.id);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Suspense fallback={null}>
        <SearchParamsHandler onCreateOpen={handleCreateClick} />
      </Suspense>

      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Agent Factory</h1>
          <p className="mt-2 text-gray-600">
            Build, manage, and interact with your AI agents
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-3">
            <TabsTrigger value="portfolio" className="gap-2">
              <Briefcase className="h-4 w-4" />
              <span className="hidden sm:inline">Portfolio</span>
            </TabsTrigger>
            <TabsTrigger value="create" className="gap-2">
              <PlusCircle className="h-4 w-4" />
              <span className="hidden sm:inline">Create New</span>
            </TabsTrigger>
            <TabsTrigger value="viewer" className="gap-2">
              <MessageSquare className="h-4 w-4" />
              <span className="hidden sm:inline">Agent Viewer</span>
            </TabsTrigger>
          </TabsList>

          <TabsContent value="portfolio" className="mt-6">
            <AgentPortfolio
              agents={agents}
              isLoading={loading}
              onCreateClick={handleCreateClick}
              onViewDetails={handleViewDetails}
            />
          </TabsContent>

          <TabsContent value="create" className="mt-6">
            {createFlowState === 'gatekeeper' && (
              <AgentGatekeeper
                onComplete={handleGatekeeperComplete}
                onReset={handleBackToPortfolio}
              />
            )}
            {createFlowState === 'copilot' && (
              <CopilotRequestForm
                onBack={handleBackToGatekeeper}
                onSuccess={handleBackToPortfolio}
              />
            )}
            {createFlowState === 'wizard' && (
              <AgentBuilderWizard
                onBack={handleBackToGatekeeper}
                onSuccess={handleAgentCreated}
              />
            )}
          </TabsContent>

          <TabsContent value="viewer" className="mt-6">
            <AgentViewerPlaceholder />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
