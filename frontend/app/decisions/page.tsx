'use client';

import { useEffect, useState, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
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
import { api, Decision, Proposal } from '@/lib/api';
import { TeamMemberSelect } from '@/components/ui/team-member-select';
import {
  Lightbulb,
  Search,
  Plus,
  Calendar,
  User,
  Building2,
  Shield,
  Coins,
  FileText,
  CheckCircle,
  ArrowRight,
  Edit3,
  Trash2,
  X,
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

export default function ProposalsDecisionsPage() {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [decisions, setDecisions] = useState<Decision[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [isCreateProposalOpen, setIsCreateProposalOpen] = useState(false);
  const [isCreateDecisionOpen, setIsCreateDecisionOpen] = useState(false);
  const [selectedProposal, setSelectedProposal] = useState<Proposal | null>(null);
  const [selectedDecision, setSelectedDecision] = useState<Decision | null>(null);
  const [isDecisionDetailsOpen, setIsDecisionDetailsOpen] = useState(false);
  const [isEditMode, setIsEditMode] = useState(false);
  const [editedDecision, setEditedDecision] = useState<Partial<Decision>>({});
  const [isDeleting, setIsDeleting] = useState(false);

  const [newProposal, setNewProposal] = useState({
    title: '',
    description: '',
    proposer: '',
    department: '',
    team_member: '',
    category: 'Governance' as 'Agent' | 'Governance' | 'Technical' | 'Licensing' | 'AI Architect',
    rationale: '',
    impact: '',
  });

  const [newDecision, setNewDecision] = useState({
    title: '',
    description: '',
    decision_maker: '',
    decision_date: new Date().toISOString().split('T')[0],
    category: 'Architecture' as 'Governance' | 'Architecture' | 'Licensing' | 'Budget' | 'Security',
    rationale: '',
    impact: '',
  });

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    try {
      const [proposalsData, decisionsData] = await Promise.all([
        api.proposals.list(),
        api.decisions.list(),
      ]);
      setProposals(proposalsData);
      setDecisions(decisionsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  }

  
  function openDecisionDetails(decision: Decision) {
    setSelectedDecision(decision);
    setEditedDecision(decision);
    setIsEditMode(false);
    setIsDecisionDetailsOpen(true);
  }

  async function handleUpdateDecision() {
    if (!selectedDecision) return;
    try {
      await api.decisions.update(selectedDecision.id, editedDecision);
      await loadData();
      setIsEditMode(false);
      setIsDecisionDetailsOpen(false);
    } catch (error) {
      console.error('Failed to update decision:', error);
    }
  }

  async function handleDeleteDecision() {
    if (!selectedDecision) return;
    setIsDeleting(true);
    try {
      await api.decisions.delete(selectedDecision.id);
      await loadData();
      setIsDecisionDetailsOpen(false);
    } catch (error) {
      console.error('Failed to delete decision:', error);
    } finally {
      setIsDeleting(false);
    }
  }

  async function handleCreateProposal() {
    try {
      await api.proposals.create({
        title: newProposal.title,
        description: newProposal.description,
        proposer: newProposal.proposer,
        department: newProposal.department,
        team_member: newProposal.team_member || undefined,
        category: newProposal.category,
        status: 'Proposed',
        rationale: newProposal.rationale || undefined,
        impact: newProposal.impact || undefined,
      });

      setIsCreateProposalOpen(false);
      setNewProposal({
        title: '',
        description: '',
        proposer: '',
        department: '',
        team_member: '',
        category: 'Governance',
        rationale: '',
        impact: '',
      });
      loadData();
    } catch (error) {
      console.error('Failed to create proposal:', error);
      alert('Failed to create proposal. Please try again.');
    }
  }

  async function handleUpdateProposalStatus(proposalId: string, newStatus: 'Proposed' | 'Reviewing' | 'Agreed' | 'Deferred') {
    try {
      await api.proposals.update(proposalId, { status: newStatus });
      loadData();
    } catch (error) {
      console.error('Failed to update proposal status:', error);
      alert('Failed to update status. Please try again.');
    }
  }

  async function handleCreateDecisionFromProposal() {
    if (!selectedProposal) return;

    try {
      await api.decisions.createFromProposal(selectedProposal.id, {
        title: newDecision.title,
        description: newDecision.description,
        decision_maker: newDecision.decision_maker,
        decision_date: new Date(newDecision.decision_date).toISOString(),
        category: newDecision.category,
        rationale: newDecision.rationale || undefined,
        impact: newDecision.impact || undefined,
      });

      setIsCreateDecisionOpen(false);
      setSelectedProposal(null);
      setNewDecision({
        title: '',
        description: '',
        decision_maker: '',
        decision_date: new Date().toISOString().split('T')[0],
        category: 'Architecture',
        rationale: '',
        impact: '',
      });
      loadData();
    } catch (error) {
      console.error('Failed to create decision:', error);
      alert('Failed to create decision. Please try again.');
    }
  }

  function openCreateDecisionDialog(proposal: Proposal) {
    setSelectedProposal(proposal);
    setNewDecision({
      ...newDecision,
      title: proposal.title,
      description: proposal.description,
      rationale: proposal.rationale || '',
      impact: proposal.impact || '',
    });
    setIsCreateDecisionOpen(true);
  }

  const filteredProposals = proposals.filter((proposal) => {
    const matchesSearch =
      proposal.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      proposal.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      proposal.proposer.toLowerCase().includes(searchQuery.toLowerCase()) ||
      proposal.department.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesCategory =
      filterCategory === 'all' || proposal.category === filterCategory;

    return matchesSearch && matchesCategory;
  });

  const filteredDecisions = decisions.filter((decision) => {
    const matchesSearch =
      decision.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      decision.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      decision.decision_maker.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesCategory =
      filterCategory === 'all' || decision.category === filterCategory;

    return matchesSearch && matchesCategory;
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Proposed':
        return 'bg-blue-100 text-blue-800';
      case 'Reviewing':
        return 'bg-yellow-100 text-yellow-800';
      case 'Agreed':
        return 'bg-green-100 text-green-800';
      case 'Deferred':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case 'Governance':
        return <FileText className="h-5 w-5" />;
      case 'Architecture':
        return <Building2 className="h-5 w-5" />;
      case 'Licensing':
        return <Shield className="h-5 w-5" />;
      case 'Budget':
        return <Coins className="h-5 w-5" />;
      case 'Security':
        return <Shield className="h-5 w-5" />;
      case 'Agent':
        return <Lightbulb className="h-5 w-5" />;
      case 'Technical':
        return <Building2 className="h-5 w-5" />;
      case 'AI Architect':
        return <Lightbulb className="h-5 w-5" />;
      default:
        return <Lightbulb className="h-5 w-5" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Governance':
        return 'bg-blue-50 text-blue-600';
      case 'Architecture':
      case 'Technical':
        return 'bg-purple-50 text-purple-600';
      case 'Licensing':
        return 'bg-orange-50 text-orange-600';
      case 'Budget':
        return 'bg-green-50 text-green-600';
      case 'Security':
        return 'bg-red-50 text-red-600';
      case 'Agent':
      case 'AI Architect':
        return 'bg-yellow-50 text-yellow-600';
      default:
        return 'bg-gray-50 text-gray-600';
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Suspense fallback={null}>
        <SearchParamsHandler onCreateOpen={() => setIsCreateProposalOpen(true)} />
      </Suspense>
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Proposals & Decisions</h1>
          <p className="mt-2 text-gray-600">
            Propose ideas, review with the team, and document decisions
          </p>
        </div>

        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search by title, description, proposer, or decision maker..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <Select value={filterCategory} onValueChange={setFilterCategory}>
            <SelectTrigger className="w-full sm:w-[200px]">
              <SelectValue placeholder="Filter by category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              <SelectItem value="Agent">Agent</SelectItem>
              <SelectItem value="Governance">Governance</SelectItem>
              <SelectItem value="Technical">Technical</SelectItem>
              <SelectItem value="Licensing">Licensing</SelectItem>
              <SelectItem value="AI Architect">AI Architect</SelectItem>
              <SelectItem value="Architecture">Architecture</SelectItem>
              <SelectItem value="Budget">Budget</SelectItem>
              <SelectItem value="Security">Security</SelectItem>
            </SelectContent>
          </Select>

          <Button onClick={() => setIsCreateProposalOpen(true)}>
            <Plus className="mr-2 h-4 w-4" />
            New Proposal
          </Button>
        </div>

        <Tabs defaultValue="proposals" className="space-y-6">
          <TabsList>
            <TabsTrigger value="proposals">
              Proposals ({filteredProposals.length})
            </TabsTrigger>
            <TabsTrigger value="decisions">
              Decisions ({filteredDecisions.length})
            </TabsTrigger>
          </TabsList>

          <TabsContent value="proposals" className="space-y-4">
            {filteredProposals.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <Lightbulb className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    No proposals found
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {searchQuery || filterCategory !== 'all'
                      ? 'Try adjusting your search or filters'
                      : 'Get started by creating your first proposal'}
                  </p>
                  <Button onClick={() => setIsCreateProposalOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Your First Proposal
                  </Button>
                </CardContent>
              </Card>
            ) : (
              filteredProposals.map((proposal) => (
                <Card key={proposal.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4 flex-1">
                        <div
                          className={`rounded-lg p-3 ${getCategoryColor(
                            proposal.category
                          )}`}
                        >
                          {getCategoryIcon(proposal.category)}
                        </div>
                        <div className="flex-1">
                          <CardTitle className="text-xl mb-2">
                            {proposal.title}
                          </CardTitle>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <div className="flex items-center gap-1">
                              <User className="h-4 w-4" />
                              {proposal.proposer}
                            </div>
                            <div className="flex items-center gap-1">
                              <Building2 className="h-4 w-4" />
                              {proposal.department}
                            </div>
                            {proposal.team_member && (
                              <Badge variant="outline" className="text-xs">
                                @{proposal.team_member}
                              </Badge>
                            )}
                            <div className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              {formatDate(proposal.created_at)}
                            </div>
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Badge
                          className={`text-xs ${getStatusColor(proposal.status)}`}
                        >
                          {proposal.status}
                        </Badge>
                        <Badge variant="outline" className="text-xs">
                          {proposal.category}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">
                          Proposal
                        </h4>
                        <p className="text-sm text-gray-600">
                          {proposal.description}
                        </p>
                      </div>

                      {proposal.rationale && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-2">
                            Rationale
                          </h4>
                          <p className="text-sm text-gray-600">
                            {proposal.rationale}
                          </p>
                        </div>
                      )}

                      {proposal.impact && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-2">
                            Expected Impact
                          </h4>
                          <p className="text-sm text-gray-600">
                            {proposal.impact}
                          </p>
                        </div>
                      )}

                      <div className="flex gap-2 pt-4 border-t">
                        {proposal.status === 'Proposed' && (
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              handleUpdateProposalStatus(proposal.id, 'Reviewing')
                            }
                          >
                            <ArrowRight className="mr-2 h-4 w-4" />
                            Start Review
                          </Button>
                        )}
                        {proposal.status === 'Reviewing' && (
                          <>
                            <Button
                              variant="default"
                              size="sm"
                              onClick={() =>
                                handleUpdateProposalStatus(proposal.id, 'Agreed')
                              }
                            >
                              <CheckCircle className="mr-2 h-4 w-4" />
                              Agree
                            </Button>
                            <Button
                              variant="outline"
                              size="sm"
                              onClick={() =>
                                handleUpdateProposalStatus(proposal.id, 'Deferred')
                              }
                            >
                              Defer
                            </Button>
                          </>
                        )}
                        {proposal.status === 'Agreed' && (
                          <Button
                            variant="default"
                            size="sm"
                            onClick={() => openCreateDecisionDialog(proposal)}
                          >
                            <FileText className="mr-2 h-4 w-4" />
                            Create Decision
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>

          <TabsContent value="decisions" className="space-y-4">
            {filteredDecisions.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    No decisions found
                  </h3>
                  <p className="text-gray-600">
                    {searchQuery || filterCategory !== 'all'
                      ? 'Try adjusting your search or filters'
                      : 'Decisions will appear here once proposals are agreed upon'}
                  </p>
                </CardContent>
              </Card>
            ) : (
              filteredDecisions.map((decision) => (
                <Card
                  key={decision.id}
                  className="hover:shadow-lg transition-shadow"
                >
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-4 flex-1">
                        <div
                          className={`rounded-lg p-3 ${getCategoryColor(
                            decision.category
                          )}`}
                        >
                          {getCategoryIcon(decision.category)}
                        </div>
                        <div className="flex-1">
                          <CardTitle className="text-xl mb-2">
                            {decision.title}
                          </CardTitle>
                          <div className="flex items-center gap-4 text-sm text-gray-600">
                            <div className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              {formatDate(decision.decision_date)}
                            </div>
                            <div className="flex items-center gap-1">
                              <User className="h-4 w-4" />
                              {decision.decision_maker}
                            </div>
                          </div>
                        </div>
                      </div>
                      <Badge variant="outline" className="text-xs">
                        {decision.category}
                      </Badge>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-4">
                      <div>
                        <h4 className="text-sm font-semibold text-gray-700 mb-2">
                          Decision
                        </h4>
                        <p className="text-sm text-gray-600">
                          {decision.description}
                        </p>
                      </div>

                      {decision.rationale && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-2">
                            Rationale
                          </h4>
                          <p className="text-sm text-gray-600">
                            {decision.rationale}
                          </p>
                        </div>
                      )}

                      {decision.impact && (
                        <div>
                          <h4 className="text-sm font-semibold text-gray-700 mb-2">
                            Impact
                          </h4>
                          <p className="text-sm text-gray-600">
                            {decision.impact}
                          </p>
                        </div>
                      )}

                      <div className="flex gap-2 pt-4 border-t">
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => openDecisionDetails(decision)}
                        >
                          View Details
                        </Button>
                        {decision.proposal_id && (
                          <Button variant="outline" size="sm">
                            View Proposal
                          </Button>
                        )}
                        {decision.meeting && (
                          <Button variant="outline" size="sm">
                            View Meeting
                          </Button>
                        )}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>
        </Tabs>

        <Dialog open={isCreateProposalOpen} onOpenChange={setIsCreateProposalOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create New Proposal</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <label className="text-sm font-medium">Proposal Title</label>
                <Input
                  placeholder="e.g., Implement New Agent for Sales Team"
                  value={newProposal.title}
                  onChange={(e) =>
                    setNewProposal({ ...newProposal, title: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium">Description</label>
                <Textarea
                  placeholder="Describe your proposal"
                  value={newProposal.description}
                  onChange={(e) =>
                    setNewProposal({ ...newProposal, description: e.target.value })
                  }
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Category</label>
                  <Select
                    value={newProposal.category}
                    onValueChange={(value: 'Agent' | 'Governance' | 'Technical' | 'Licensing' | 'AI Architect') =>
                      setNewProposal({ ...newProposal, category: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Agent">Agent</SelectItem>
                      <SelectItem value="Governance">Governance</SelectItem>
                      <SelectItem value="Technical">Technical</SelectItem>
                      <SelectItem value="Licensing">Licensing</SelectItem>
                      <SelectItem value="AI Architect">AI Architect</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Proposer</label>
                  <TeamMemberSelect
                    value={newProposal.proposer}
                    onValueChange={(value) =>
                      setNewProposal({ ...newProposal, proposer: value })
                    }
                    placeholder="Select proposer"
                  />
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Department *</label>
                  <Input
                    placeholder="e.g., Sales"
                    value={newProposal.department}
                    onChange={(e) =>
                      setNewProposal({ ...newProposal, department: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Team Member (optional)</label>
                  <TeamMemberSelect
                    value={newProposal.team_member}
                    onValueChange={(value) =>
                      setNewProposal({ ...newProposal, team_member: value })
                    }
                    placeholder="Select team member"
                    allowEmpty
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">Rationale (optional)</label>
                <Textarea
                  placeholder="Why is this proposal necessary?"
                  value={newProposal.rationale}
                  onChange={(e) =>
                    setNewProposal({ ...newProposal, rationale: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium">Expected Impact (optional)</label>
                <Textarea
                  placeholder="What impact will this have?"
                  value={newProposal.impact}
                  onChange={(e) =>
                    setNewProposal({ ...newProposal, impact: e.target.value })
                  }
                />
              </div>
              <div className="flex gap-3 pt-4">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setIsCreateProposalOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1"
                  onClick={handleCreateProposal}
                  disabled={!newProposal.title || !newProposal.description || !newProposal.proposer || !newProposal.department}
                >
                  Create Proposal
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>

        <Dialog open={isCreateDecisionOpen} onOpenChange={setIsCreateDecisionOpen}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>Create Decision from Proposal</DialogTitle>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div>
                <label className="text-sm font-medium">Decision Title</label>
                <Input
                  placeholder="e.g., Approved: New Sales Agent"
                  value={newDecision.title}
                  onChange={(e) =>
                    setNewDecision({ ...newDecision, title: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium">Description</label>
                <Textarea
                  placeholder="Describe the decision"
                  value={newDecision.description}
                  onChange={(e) =>
                    setNewDecision({ ...newDecision, description: e.target.value })
                  }
                />
              </div>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium">Category</label>
                  <Select
                    value={newDecision.category}
                    onValueChange={(value: 'Governance' | 'Architecture' | 'Licensing' | 'Budget' | 'Security') =>
                      setNewDecision({ ...newDecision, category: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="Governance">Governance</SelectItem>
                      <SelectItem value="Architecture">Architecture</SelectItem>
                      <SelectItem value="Licensing">Licensing</SelectItem>
                      <SelectItem value="Budget">Budget</SelectItem>
                      <SelectItem value="Security">Security</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">Decision Date</label>
                  <Input
                    type="date"
                    value={newDecision.decision_date}
                    onChange={(e) =>
                      setNewDecision({ ...newDecision, decision_date: e.target.value })
                    }
                  />
                </div>
              </div>
              <div>
                <label className="text-sm font-medium">Decision Maker</label>
                <TeamMemberSelect
                  value={newDecision.decision_maker}
                  onValueChange={(value) =>
                    setNewDecision({ ...newDecision, decision_maker: value })
                  }
                  placeholder="Select decision maker"
                />
              </div>
              <div>
                <label className="text-sm font-medium">Rationale (optional)</label>
                <Textarea
                  placeholder="Explain why this decision was made"
                  value={newDecision.rationale}
                  onChange={(e) =>
                    setNewDecision({ ...newDecision, rationale: e.target.value })
                  }
                />
              </div>
              <div>
                <label className="text-sm font-medium">Impact (optional)</label>
                <Textarea
                  placeholder="Describe the expected impact"
                  value={newDecision.impact}
                  onChange={(e) =>
                    setNewDecision({ ...newDecision, impact: e.target.value })
                  }
                />
              </div>
              <div className="flex gap-3 pt-4">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setIsCreateDecisionOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1"
                  onClick={handleCreateDecisionFromProposal}
                  disabled={!newDecision.title || !newDecision.description || !newDecision.decision_maker}
                >
                  Create Decision
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>

        {/* Decision Details Modal */}
        <Dialog open={isDecisionDetailsOpen} onOpenChange={setIsDecisionDetailsOpen}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <div className="flex items-center justify-between">
                <DialogTitle className="text-xl">
                  {isEditMode ? 'Edit Decision' : 'Decision Details'}
                </DialogTitle>
                <div className="flex gap-2">
                  {!isEditMode && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setIsEditMode(true)}
                      >
                        <Edit3 className="h-4 w-4 mr-1" />
                        Edit
                      </Button>
                      <Button
                        variant="destructive"
                        size="sm"
                        onClick={handleDeleteDecision}
                        disabled={isDeleting}
                      >
                        <Trash2 className="h-4 w-4 mr-1" />
                        {isDeleting ? 'Deleting...' : 'Delete'}
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </DialogHeader>
            {selectedDecision && (
              <div className="space-y-6 pt-4">
                {isEditMode ? (
                  /* Edit Mode */
                  <div className="space-y-4">
                    <div>
                      <label className="text-sm font-medium">Title</label>
                      <Input
                        value={editedDecision.title || ''}
                        onChange={(e) => setEditedDecision({ ...editedDecision, title: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Description</label>
                      <Textarea
                        value={editedDecision.description || ''}
                        onChange={(e) => setEditedDecision({ ...editedDecision, description: e.target.value })}
                        rows={4}
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium">Category</label>
                        <Select
                          value={editedDecision.category || 'Architecture'}
                          onValueChange={(value) => setEditedDecision({ ...editedDecision, category: value as Decision['category'] })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Governance">Governance</SelectItem>
                            <SelectItem value="Architecture">Architecture</SelectItem>
                            <SelectItem value="Licensing">Licensing</SelectItem>
                            <SelectItem value="Budget">Budget</SelectItem>
                            <SelectItem value="Security">Security</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <label className="text-sm font-medium">Decision Date</label>
                        <Input
                          type="date"
                          value={editedDecision.decision_date || ''}
                          onChange={(e) => setEditedDecision({ ...editedDecision, decision_date: e.target.value })}
                        />
                      </div>
                    </div>
                    <div>
                      <label className="text-sm font-medium">Decision Maker</label>
                      <TeamMemberSelect
                        value={editedDecision.decision_maker || ''}
                        onValueChange={(value) => setEditedDecision({ ...editedDecision, decision_maker: value })}
                        placeholder="Select decision maker"
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Rationale</label>
                      <Textarea
                        value={editedDecision.rationale || ''}
                        onChange={(e) => setEditedDecision({ ...editedDecision, rationale: e.target.value })}
                        rows={3}
                      />
                    </div>
                    <div>
                      <label className="text-sm font-medium">Impact</label>
                      <Textarea
                        value={editedDecision.impact || ''}
                        onChange={(e) => setEditedDecision({ ...editedDecision, impact: e.target.value })}
                        rows={3}
                      />
                    </div>
                    <div className="flex gap-3 pt-4 border-t">
                      <Button
                        variant="outline"
                        className="flex-1"
                        onClick={() => {
                          setIsEditMode(false);
                          setEditedDecision(selectedDecision);
                        }}
                      >
                        Cancel
                      </Button>
                      <Button
                        className="flex-1"
                        onClick={handleUpdateDecision}
                      >
                        Save Changes
                      </Button>
                    </div>
                  </div>
                ) : (
                  /* View Mode */
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-lg font-semibold">{selectedDecision.title}</h3>
                      <Badge className={getCategoryColor(selectedDecision.category)} variant="secondary">
                        {selectedDecision.category}
                      </Badge>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        <span>Decision Date: {new Date(selectedDecision.decision_date).toLocaleDateString()}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <User className="h-4 w-4" />
                        <span>Decision Maker: {selectedDecision.decision_maker}</span>
                      </div>
                    </div>

                    <div>
                      <h4 className="font-medium mb-2">Description</h4>
                      <p className="text-muted-foreground whitespace-pre-wrap">{selectedDecision.description}</p>
                    </div>

                    {selectedDecision.rationale && (
                      <div>
                        <h4 className="font-medium mb-2">Rationale</h4>
                        <p className="text-muted-foreground whitespace-pre-wrap">{selectedDecision.rationale}</p>
                      </div>
                    )}

                    {selectedDecision.impact && (
                      <div>
                        <h4 className="font-medium mb-2">Impact</h4>
                        <p className="text-muted-foreground whitespace-pre-wrap">{selectedDecision.impact}</p>
                      </div>
                    )}

                    {selectedDecision.meeting && (
                      <div>
                        <h4 className="font-medium mb-2">Related Meeting</h4>
                        <p className="text-muted-foreground">{selectedDecision.meeting}</p>
                      </div>
                    )}

                    <div className="grid grid-cols-2 gap-4 pt-4 border-t text-sm text-muted-foreground">
                      <div>Created: {new Date(selectedDecision.created_at).toLocaleString()}</div>
                      <div>Updated: {new Date(selectedDecision.updated_at).toLocaleString()}</div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </DialogContent>
        </Dialog>
    </div>
  );
}
