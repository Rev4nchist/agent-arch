'use client';

import { useEffect, useState, useMemo, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  api,
  MemorySummary,
  MemoryFact,
  MemoryProfile,
  TopicSummary,
  TopicDetail,
} from '@/lib/api';
import {
  Brain,
  Search,
  RefreshCw,
  Check,
  Trash2,
  BookOpen,
  User,
  MessageSquare,
  Clock,
  Filter,
  ChevronRight,
  AlertCircle,
  X,
  CheckCircle2,
  HelpCircle,
  Shield,
  Lightbulb,
  Zap,
  Code,
  Database,
  Layers,
  GitBranch,
} from 'lucide-react';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { useAuth } from '@/components/providers/AuthProvider';
import { responsiveDialogContent } from '@/lib/utils';

const CATEGORY_COLORS: Record<string, string> = {
  Definition: 'bg-blue-100 text-blue-800',
  Acronym: 'bg-purple-100 text-purple-800',
  Entity: 'bg-green-100 text-green-800',
  Secret: 'bg-red-100 text-red-800',
};

export default function MemoriesPage() {
  const { user } = useAuth();
  const userId = useMemo(() => user?.username?.split('@')[0]?.toLowerCase() || '', [user?.username]);

  const [summary, setSummary] = useState<MemorySummary | null>(null);
  const [facts, setFacts] = useState<MemoryFact[]>([]);
  const [profile, setProfile] = useState<MemoryProfile | null>(null);
  const [topics, setTopics] = useState<TopicSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('facts');

  const [factSearch, setFactSearch] = useState('');
  const [factCategory, setFactCategory] = useState<string>('all');
  const [sortVerifiedFirst, setSortVerifiedFirst] = useState(false);

  const [selectedTopic, setSelectedTopic] = useState<TopicDetail | null>(null);
  const [topicDialogOpen, setTopicDialogOpen] = useState(false);
  const [selectedOpenLoopIdx, setSelectedOpenLoopIdx] = useState<number | null>(null);
  const [aboutDialogOpen, setAboutDialogOpen] = useState(false);

  const fetchData = useCallback(async () => {
    if (!userId) return;
    setLoading(true);
    try {
      const [summaryRes, factsRes, profileRes, topicsRes] = await Promise.all([
        api.memories.getSummary(userId),
        api.memories.getFacts(userId, { limit: 100 }),
        api.memories.getProfile(userId),
        api.memories.getTopics(userId, { limit: 50 }),
      ]);
      setSummary(summaryRes);
      setFacts(factsRes.facts);
      setProfile(profileRes);
      setTopics(topicsRes.topics);
    } catch (error) {
      console.error('Failed to fetch memories:', error);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (userId) {
      fetchData();
    }
  }, [userId, fetchData]);

  const handleVerifyFact = async (factId: number) => {
    try {
      await api.memories.verifyFact(factId, userId);
      setFacts(facts.map(f => f.fact_id === factId ? { ...f, verified: true } : f));
      if (summary) {
        setSummary({ ...summary, verified_facts: summary.verified_facts + 1 });
      }
    } catch (error) {
      console.error('Failed to verify fact:', error);
    }
  };

  const handleDeleteFact = async (factId: number) => {
    try {
      await api.memories.deleteFact(factId, userId);
      setFacts(facts.filter(f => f.fact_id !== factId));
      if (summary) {
        const deletedFact = facts.find(f => f.fact_id === factId);
        setSummary({
          ...summary,
          total_facts: summary.total_facts - 1,
          verified_facts: deletedFact?.verified ? summary.verified_facts - 1 : summary.verified_facts,
        });
      }
    } catch (error) {
      console.error('Failed to delete fact:', error);
    }
  };

  const handleDeleteCommonQuery = async (idx: number) => {
    try {
      await api.memories.deleteCommonQuery(userId, idx);
      if (profile) {
        const newQueries = [...profile.common_queries];
        newQueries.splice(idx, 1);
        setProfile({ ...profile, common_queries: newQueries });
      }
    } catch (error) {
      console.error('Failed to delete common query:', error);
    }
  };

  const handleDeleteKnownEntity = async (idx: number) => {
    try {
      await api.memories.deleteKnownEntity(userId, idx);
      if (profile) {
        const newEntities = [...profile.known_entities];
        newEntities.splice(idx, 1);
        setProfile({ ...profile, known_entities: newEntities });
      }
    } catch (error) {
      console.error('Failed to delete entity:', error);
    }
  };

  const handleViewTopic = async (topic: TopicSummary) => {
    try {
      const detail = await api.memories.getTopicDetail(topic.id, topic.session_id);
      setSelectedTopic(detail);
      setTopicDialogOpen(true);
    } catch (error) {
      console.error('Failed to fetch topic detail:', error);
    }
  };

  const handleDeleteOpenLoop = async (topicId: string, sessionId: string, idx: number) => {
    try {
      await api.memories.deleteOpenLoop(topicId, sessionId, idx);
      if (selectedTopic) {
        const newLoops = [...selectedTopic.open_loops];
        newLoops.splice(idx, 1);
        setSelectedTopic({ ...selectedTopic, open_loops: newLoops });
      }
      setTopics(topics.map(t => {
        if (t.id === topicId) {
          const newLoops = [...t.open_loops];
          newLoops.splice(idx, 1);
          return { ...t, open_loops: newLoops };
        }
        return t;
      }));
      if (summary) {
        setSummary({ ...summary, open_loops: summary.open_loops - 1 });
      }
    } catch (error) {
      console.error('Failed to delete open loop:', error);
    }
  };

  const filteredFacts = facts
    .filter(fact => {
      const matchesSearch = !factSearch ||
        fact.key.toLowerCase().includes(factSearch.toLowerCase()) ||
        fact.value.toLowerCase().includes(factSearch.toLowerCase());
      const matchesCategory = factCategory === 'all' || fact.category === factCategory;
      return matchesSearch && matchesCategory;
    })
    .sort((a, b) => {
      if (sortVerifiedFirst) {
        if (a.verified && !b.verified) return -1;
        if (!a.verified && b.verified) return 1;
      }
      return 0;
    });

  if (!userId) {
    return (
      <div className="p-8">
        <Card>
          <CardContent className="p-8 text-center">
            <AlertCircle className="w-12 h-12 mx-auto mb-4 text-yellow-500" />
            <p className="text-gray-600">Please log in to view your memories.</p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="p-6 space-y-6">
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-[#00A693] flex items-center justify-center">
            <Brain className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">User Memories</h1>
            <p className="text-sm text-gray-500">View and manage what the AI has learned about you</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button onClick={() => setAboutDialogOpen(true)} variant="outline" size="sm">
            <HelpCircle className="w-4 h-4 lg:mr-2" />
            <span className="hidden lg:inline">About Memories</span>
          </Button>
          <Button onClick={fetchData} variant="outline" size="sm" disabled={loading}>
            <RefreshCw className={`w-4 h-4 lg:mr-2 ${loading ? 'animate-spin' : ''}`} />
            <span className="hidden lg:inline">Refresh</span>
          </Button>
        </div>
      </div>

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card
          className="cursor-pointer transition-all duration-200 hover:shadow-md hover:border-blue-300 hover:bg-blue-50/50"
          onClick={() => { setSortVerifiedFirst(false); setActiveTab('facts'); }}
        >
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-blue-100 flex items-center justify-center">
                <BookOpen className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{summary?.total_facts ?? '-'}</p>
                <p className="text-sm text-gray-500">Total Facts</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card
          className="cursor-pointer transition-all duration-200 hover:shadow-md hover:border-green-300 hover:bg-green-50/50"
          onClick={() => { setSortVerifiedFirst(true); setActiveTab('facts'); }}
        >
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{summary?.verified_facts ?? '-'}</p>
                <p className="text-sm text-gray-500">Verified</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card
          className="cursor-pointer transition-all duration-200 hover:shadow-md hover:border-purple-300 hover:bg-purple-50/50"
          onClick={() => setActiveTab('topics')}
        >
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-purple-100 flex items-center justify-center">
                <MessageSquare className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{summary?.active_topics ?? '-'}</p>
                <p className="text-sm text-gray-500">Active Topics</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card
          className="cursor-pointer transition-all duration-200 hover:shadow-md hover:border-orange-300 hover:bg-orange-50/50"
          onClick={() => setActiveTab('open-loops')}
        >
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-lg bg-orange-100 flex items-center justify-center">
                <Clock className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <p className="text-2xl font-bold">{summary?.open_loops ?? '-'}</p>
                <p className="text-sm text-gray-500">Open Loops</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="mb-4 w-full overflow-x-auto flex lg:inline-flex">
          <TabsTrigger value="facts" className="flex-shrink-0 flex items-center gap-2">
            <BookOpen className="w-4 h-4" />
            <span className="hidden sm:inline">Facts</span> ({facts.length})
          </TabsTrigger>
          <TabsTrigger value="profile" className="flex-shrink-0 flex items-center gap-2">
            <User className="w-4 h-4" />
            <span className="hidden sm:inline">Profile</span>
          </TabsTrigger>
          <TabsTrigger value="topics" className="flex-shrink-0 flex items-center gap-2">
            <MessageSquare className="w-4 h-4" />
            <span className="hidden sm:inline">Topics</span> ({topics.length})
          </TabsTrigger>
          <TabsTrigger value="open-loops" className="flex-shrink-0 flex items-center gap-2">
            <Clock className="w-4 h-4" />
            <span className="hidden sm:inline">Open Loops</span> ({summary?.open_loops ?? 0})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="facts">
          <Card>
            <CardHeader className="pb-3">
              <div className="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                <CardTitle className="text-lg">Extracted Facts</CardTitle>
                <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2">
                  <div className="relative w-full sm:w-64">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                    <Input
                      placeholder="Search facts..."
                      value={factSearch}
                      onChange={(e) => setFactSearch(e.target.value)}
                      className="pl-9 w-full"
                    />
                  </div>
                  <Select value={factCategory} onValueChange={setFactCategory}>
                    <SelectTrigger className="w-full sm:w-40">
                      <Filter className="w-4 h-4 mr-2" />
                      <SelectValue placeholder="Category" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All Categories</SelectItem>
                      <SelectItem value="Definition">Definition</SelectItem>
                      <SelectItem value="Acronym">Acronym</SelectItem>
                      <SelectItem value="Entity">Entity</SelectItem>
                      <SelectItem value="Secret">Secret</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8 text-gray-500">Loading facts...</div>
              ) : filteredFacts.length === 0 ? (
                <div className="text-center py-8 text-gray-500">No facts found</div>
              ) : (
                <div className="space-y-3">
                  {filteredFacts.map((fact) => (
                    <div
                      key={fact.fact_id}
                      className="p-4 border rounded-lg hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge className={CATEGORY_COLORS[fact.category] || 'bg-gray-100'}>
                              {fact.category}
                            </Badge>
                            {fact.verified && (
                              <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50">
                                <Check className="w-3 h-3 mr-1" />
                                Verified
                              </Badge>
                            )}
                          </div>
                          <p className="font-medium text-gray-900">{fact.key}</p>
                          <p className="text-gray-600 mt-1">{fact.value}</p>
                          {fact.evidence_snippet && (
                            <p className="text-xs text-gray-400 mt-2 italic">
                              Evidence: &ldquo;{fact.evidence_snippet}&rdquo;
                            </p>
                          )}
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-400">
                            <span>Confidence: {Math.round(fact.confidence * 100)}%</span>
                            {fact.created_at && (
                              <span>{new Date(fact.created_at).toLocaleDateString()}</span>
                            )}
                          </div>
                        </div>
                        <div className="flex items-center gap-1">
                          {!fact.verified && (
                            <Button
                              variant="ghost"
                              size="sm"
                              onClick={() => handleVerifyFact(fact.fact_id)}
                              className="text-green-600 hover:text-green-700 hover:bg-green-50"
                            >
                              <Check className="w-4 h-4" />
                            </Button>
                          )}
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDeleteFact(fact.fact_id)}
                            className="text-red-600 hover:text-red-700 hover:bg-red-50"
                          >
                            <Trash2 className="w-4 h-4" />
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="profile">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Common Queries</CardTitle>
              </CardHeader>
              <CardContent>
                {profile?.common_queries.length === 0 ? (
                  <p className="text-gray-500 text-sm">No common queries learned yet</p>
                ) : (
                  <div className="space-y-2">
                    {profile?.common_queries.map((query, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <span className="text-sm">{query}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteCommonQuery(idx)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Known Entities</CardTitle>
              </CardHeader>
              <CardContent>
                {profile?.known_entities.length === 0 ? (
                  <p className="text-gray-500 text-sm">No entities learned yet</p>
                ) : (
                  <div className="space-y-2">
                    {profile?.known_entities.map((entity, idx) => (
                      <div
                        key={idx}
                        className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
                      >
                        <div>
                          <p className="font-medium text-sm">{entity.name}</p>
                          <p className="text-xs text-gray-500">
                            {entity.type}{entity.context && ` - ${entity.context}`}
                          </p>
                        </div>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteKnownEntity(idx)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>

            <Card className="lg:col-span-2">
              <CardHeader>
                <CardTitle className="text-lg">Preferences</CardTitle>
              </CardHeader>
              <CardContent>
                {!profile?.preferences || Object.keys(profile.preferences).length === 0 ? (
                  <p className="text-gray-500 text-sm">No preferences stored</p>
                ) : (
                  <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(profile.preferences).map(([key, value]) => (
                      <div key={key} className="p-3 bg-gray-50 rounded-lg">
                        <p className="text-xs text-gray-500 mb-1">{key}</p>
                        <p className="text-sm font-medium">
                          {Array.isArray(value) ? value.join(', ') : String(value)}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="topics">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Conversation Topics</CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8 text-gray-500">Loading topics...</div>
              ) : topics.length === 0 ? (
                <div className="text-center py-8 text-gray-500">No conversation topics found</div>
              ) : (
                <div className="space-y-3">
                  {topics.map((topic) => (
                    <div
                      key={topic.id}
                      className="p-4 border rounded-lg hover:bg-gray-50 transition-colors cursor-pointer"
                      onClick={() => handleViewTopic(topic)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <Badge variant={topic.status === 'ACTIVE' ? 'default' : 'secondary'}>
                              {topic.status}
                            </Badge>
                            <span className="text-xs text-gray-500">
                              {topic.turn_count} turns
                            </span>
                          </div>
                          <p className="font-medium text-gray-900">{topic.topic_label}</p>
                          {topic.open_loops.length > 0 && (
                            <div className="mt-2 flex flex-wrap gap-1">
                              {topic.open_loops.map((loop, idx) => (
                                <Badge
                                  key={idx}
                                  variant="outline"
                                  className="text-orange-600 border-orange-200 bg-orange-50"
                                >
                                  {loop}
                                </Badge>
                              ))}
                            </div>
                          )}
                          <p className="text-xs text-gray-400 mt-2">
                            Last active: {new Date(topic.last_activity).toLocaleString()}
                          </p>
                        </div>
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="open-loops">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg flex items-center gap-2">
                <Clock className="w-5 h-5 text-orange-600" />
                All Open Loops
              </CardTitle>
            </CardHeader>
            <CardContent>
              {loading ? (
                <div className="text-center py-8 text-gray-500">Loading open loops...</div>
              ) : topics.filter(t => t.open_loops.length > 0).length === 0 ? (
                <div className="text-center py-8 text-gray-500">No open loops found</div>
              ) : (
                <div className="space-y-4">
                  {topics
                    .filter(t => t.open_loops.length > 0)
                    .map((topic) => (
                      <div key={topic.id} className="border rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <p className="font-medium text-gray-900">{topic.topic_label}</p>
                            <p className="text-xs text-gray-400">
                              {new Date(topic.last_activity).toLocaleString()}
                            </p>
                          </div>
                          <Badge variant={topic.status === 'ACTIVE' ? 'default' : 'secondary'}>
                            {topic.status}
                          </Badge>
                        </div>
                        <div className="space-y-2">
                          {topic.open_loops.map((loop, idx) => (
                            <div
                              key={idx}
                              className="flex items-center justify-between p-3 bg-orange-50 rounded-lg cursor-pointer hover:bg-orange-100 hover:shadow-sm transition-all"
                              onClick={() => {
                                setSelectedOpenLoopIdx(idx);
                                handleViewTopic(topic);
                              }}
                            >
                              <div className="flex items-center gap-2">
                                <Clock className="w-4 h-4 text-orange-600" />
                                <span className="text-sm text-orange-800">{loop}</span>
                              </div>
                              <div className="flex items-center gap-1">
                                <ChevronRight className="w-4 h-4 text-gray-400" />
                                <Button
                                  variant="ghost"
                                  size="sm"
                                  onClick={(e) => {
                                    e.stopPropagation();
                                    handleDeleteOpenLoop(topic.id, topic.session_id, idx);
                                  }}
                                  className="text-red-600 hover:text-red-700 hover:bg-red-50"
                                >
                                  <X className="w-4 h-4" />
                                </Button>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      <Dialog open={topicDialogOpen} onOpenChange={(open) => {
        setTopicDialogOpen(open);
        if (!open) setSelectedOpenLoopIdx(null);
      }}>
        <DialogContent className={responsiveDialogContent('lg:max-w-2xl')} onCloseClick={() => {
          setTopicDialogOpen(false);
          setSelectedOpenLoopIdx(null);
        }}>
          <DialogHeader>
            <DialogTitle>{selectedTopic?.topic_label}</DialogTitle>
          </DialogHeader>
          {selectedTopic && (
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <Badge variant={selectedTopic.status === 'ACTIVE' ? 'default' : 'secondary'}>
                  {selectedTopic.status}
                </Badge>
                <span className="text-sm text-gray-500">
                  {selectedTopic.turn_count} turns
                </span>
              </div>

              {selectedTopic.summary && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Summary</p>
                  <p className="text-sm text-gray-600">{selectedTopic.summary}</p>
                </div>
              )}

              {selectedTopic.keywords.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Keywords</p>
                  <div className="flex flex-wrap gap-1">
                    {selectedTopic.keywords.map((kw, idx) => (
                      <Badge key={idx} variant="outline">{kw}</Badge>
                    ))}
                  </div>
                </div>
              )}

              {selectedTopic.open_loops.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Open Loops</p>
                  <div className="space-y-2">
                    {selectedTopic.open_loops.map((loop, idx) => (
                      <div
                        key={idx}
                        className={`flex items-center justify-between p-2 rounded-lg ${
                          idx === selectedOpenLoopIdx
                            ? 'bg-orange-200 border-2 border-orange-400'
                            : 'bg-orange-50'
                        }`}
                      >
                        <span className="text-sm text-orange-800">{loop}</span>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleDeleteOpenLoop(selectedTopic.id, selectedTopic.session_id, idx)}
                          className="text-red-600 hover:text-red-700 hover:bg-red-50"
                        >
                          <X className="w-4 h-4" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {selectedTopic.decisions_made.length > 0 && (
                <div>
                  <p className="text-sm font-medium text-gray-700 mb-1">Decisions Made</p>
                  <div className="space-y-1">
                    {selectedTopic.decisions_made.map((decision, idx) => (
                      <div key={idx} className="flex items-center gap-2 text-sm">
                        <Check className="w-4 h-4 text-green-600" />
                        <span>{decision}</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <p className="text-sm font-medium text-gray-700 mb-2">Conversation History</p>
                <div className="space-y-3 max-h-60 overflow-y-auto">
                  {selectedTopic.turns.map((turn, idx) => (
                    <div key={idx} className="border-l-2 border-gray-200 pl-3">
                      <p className="text-sm font-medium text-blue-600">{turn.query}</p>
                      <p className="text-sm text-gray-600 mt-1">{turn.response_summary}</p>
                      {turn.intent && (
                        <p className="text-xs text-gray-400 mt-1">Intent: {turn.intent}</p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              <div className="text-xs text-gray-400 pt-2 border-t">
                <p>Created: {new Date(selectedTopic.created_at).toLocaleString()}</p>
                <p>Last active: {new Date(selectedTopic.last_activity).toLocaleString()}</p>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      <Dialog open={aboutDialogOpen} onOpenChange={setAboutDialogOpen}>
        <DialogContent className={responsiveDialogContent('lg:max-w-4xl')} onCloseClick={() => setAboutDialogOpen(false)}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-3 text-xl">
              <div className="w-10 h-10 rounded-full bg-[#00A693] flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              About Your AI Memories
            </DialogTitle>
          </DialogHeader>

          <div className="space-y-6 py-4">
            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-2 flex items-center gap-2">
                <Lightbulb className="w-5 h-5 text-yellow-500" />
                What is This?
              </h3>
              <p className="text-gray-600">
                The Fourth AI Agent has a <strong>persistent memory system</strong> that helps it remember important information about you across conversations. Unlike traditional AI assistants that forget everything between sessions, our agent:
              </p>
              <ul className="mt-2 space-y-1 text-gray-600 list-disc list-inside">
                <li>Remembers facts you tell it (names, roles, definitions)</li>
                <li>Learns your preferences over time</li>
                <li>Maintains context during conversations</li>
              </ul>
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <BookOpen className="w-5 h-5 text-blue-500" />
                What Gets Remembered
              </h3>
              <div className="grid grid-cols-3 gap-4">
                <div className="p-4 bg-blue-50 rounded-lg border border-blue-100">
                  <p className="font-medium text-blue-900">Facts</p>
                  <p className="text-sm text-blue-700 mt-1">Information you tell the AI</p>
                  <p className="text-xs text-blue-500 mt-2">Stored permanently</p>
                </div>
                <div className="p-4 bg-purple-50 rounded-lg border border-purple-100">
                  <p className="font-medium text-purple-900">Preferences</p>
                  <p className="text-sm text-purple-700 mt-1">How you like to work</p>
                  <p className="text-xs text-purple-500 mt-2">Stored permanently</p>
                </div>
                <div className="p-4 bg-orange-50 rounded-lg border border-orange-100">
                  <p className="font-medium text-orange-900">Topics</p>
                  <p className="text-sm text-orange-700 mt-1">Current conversation context</p>
                  <p className="text-xs text-orange-500 mt-2">Session-based</p>
                </div>
              </div>
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Zap className="w-5 h-5 text-green-500" />
                How It Works
              </h3>
              <div className="space-y-3">
                <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-medium text-sm">1</div>
                  <div>
                    <p className="font-medium text-gray-900">Continue Same Topic</p>
                    <p className="text-sm text-gray-600">Follow-up questions stay in context</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-medium text-sm">2</div>
                  <div>
                    <p className="font-medium text-gray-900">Return to Previous Topic</p>
                    <p className="text-sm text-gray-600">Pick up where you left off</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-medium text-sm">3</div>
                  <div>
                    <p className="font-medium text-gray-900">Start Fresh Topic</p>
                    <p className="text-sm text-gray-600">New conversation, clean slate</p>
                  </div>
                </div>
                <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
                  <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-700 font-medium text-sm">4</div>
                  <div>
                    <p className="font-medium text-gray-900">Shift to Different Topic</p>
                    <p className="text-sm text-gray-600">Previous topic saved for later</p>
                  </div>
                </div>
              </div>
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Shield className="w-5 h-5 text-red-500" />
                Privacy & Security
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div className="p-3 border rounded-lg">
                  <p className="font-medium text-gray-900">Your Data is Yours</p>
                  <p className="text-sm text-gray-600">All memories are stored per-user. Your information is never shared with others.</p>
                </div>
                <div className="p-3 border rounded-lg">
                  <p className="font-medium text-gray-900">Encrypted & Secure</p>
                  <p className="text-sm text-gray-600">All data is encrypted in transit and at rest, compliant with Fourth policies.</p>
                </div>
              </div>
            </section>

            <section>
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <HelpCircle className="w-5 h-5 text-gray-500" />
                Frequently Asked Questions
              </h3>
              <div className="space-y-3">
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium text-gray-900">Does it remember everything I say?</p>
                  <p className="text-sm text-gray-600">No. It extracts and remembers important facts (definitions, relationships, preferences) - not every word. Casual conversation is not stored permanently.</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium text-gray-900">Can I delete memories?</p>
                  <p className="text-sm text-gray-600">Yes! Use the delete buttons on this page to remove any fact, preference, or open loop you do not want remembered.</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium text-gray-900">What are Open Loops?</p>
                  <p className="text-sm text-gray-600">Open loops are unfinished topics or questions from your conversations that the AI noticed you might want to return to later.</p>
                </div>
                <div className="p-3 bg-gray-50 rounded-lg">
                  <p className="font-medium text-gray-900">Will this slow down responses?</p>
                  <p className="text-sm text-gray-600">Minimal impact. The memory system adds about 100-200ms to each request - barely noticeable.</p>
                </div>
              </div>
            </section>

            <section className="border-t pt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-3 flex items-center gap-2">
                <Code className="w-5 h-5 text-indigo-500" />
                For the Techies
              </h3>
              <p className="text-sm text-gray-500 mb-4">A deeper look at the HMLR (Hierarchical Memory Lookup & Routing) architecture</p>

              <div className="space-y-4">
                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                  <h4 className="font-medium text-slate-900 mb-2 flex items-center gap-2">
                    <Layers className="w-4 h-4 text-indigo-500" />
                    System Components
                  </h4>
                  <div className="grid grid-cols-3 gap-3 text-sm">
                    <div className="p-2 bg-white rounded border">
                      <p className="font-medium text-indigo-700">Governor</p>
                      <p className="text-xs text-gray-600">Routes conversations using 4-scenario pattern. Computes topic similarity and decides whether to continue, resume, shift, or create new topics.</p>
                    </div>
                    <div className="p-2 bg-white rounded border">
                      <p className="font-medium text-green-700">Hydrator</p>
                      <p className="text-xs text-gray-600">Assembles context from multiple sources: block history, relevant facts, user preferences, and open loops into a coherent prompt.</p>
                    </div>
                    <div className="p-2 bg-white rounded border">
                      <p className="font-medium text-purple-700">Scribe</p>
                      <p className="text-xs text-gray-600">Async agent that learns from conversations. Extracts entities, detects query patterns, and updates your profile over time.</p>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                  <h4 className="font-medium text-slate-900 mb-2 flex items-center gap-2">
                    <GitBranch className="w-4 h-4 text-green-500" />
                    Data Flow
                  </h4>
                  <div className="text-sm text-gray-700">
                    <p className="mb-2">Each request triggers <strong>3 parallel tasks</strong> for optimal performance:</p>
                    <ol className="list-decimal list-inside space-y-1 text-xs text-gray-600 ml-2">
                      <li><code className="bg-gray-100 px-1 rounded">BridgeBlockManager</code> - Retrieves session blocks from Cosmos DB</li>
                      <li><code className="bg-gray-100 px-1 rounded">SQLClient</code> - Looks up relevant facts by keywords</li>
                      <li><code className="bg-gray-100 px-1 rounded">MemoryRetrieval</code> - Semantic search for related memories</li>
                    </ol>
                    <p className="mt-2 text-xs">Results converge in the Governor for routing decisions, then flow through the Hydrator before reaching the AI model.</p>
                  </div>
                </div>

                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                  <h4 className="font-medium text-slate-900 mb-2 flex items-center gap-2">
                    <Database className="w-4 h-4 text-blue-500" />
                    Storage Architecture
                  </h4>
                  <div className="grid grid-cols-2 gap-3 text-sm">
                    <div className="p-2 bg-white rounded border">
                      <p className="font-medium text-blue-700">Azure Cosmos DB</p>
                      <p className="text-xs text-gray-600"><strong>Bridge Blocks</strong> - Session-scoped conversation units. Each block tracks topic, turns, keywords, open loops, and decisions. Only one ACTIVE block per session.</p>
                    </div>
                    <div className="p-2 bg-white rounded border">
                      <p className="font-medium text-orange-700">Azure SQL</p>
                      <p className="text-xs text-gray-600"><strong>Facts & Profiles</strong> - Persistent per-user storage. Facts have categories (Definition, Acronym, Entity, Secret) with confidence scores and verification status.</p>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                  <h4 className="font-medium text-slate-900 mb-3">The 4 Routing Scenarios</h4>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div className="p-2 bg-green-50 rounded border border-green-200">
                      <span className="font-medium text-green-800">1. TOPIC_CONTINUATION</span>
                      <p className="text-green-700">Active block exists AND topic similarity &gt; threshold</p>
                    </div>
                    <div className="p-2 bg-blue-50 rounded border border-blue-200">
                      <span className="font-medium text-blue-800">2. TOPIC_RESUMPTION</span>
                      <p className="text-blue-700">Paused block matches better than active block</p>
                    </div>
                    <div className="p-2 bg-purple-50 rounded border border-purple-200">
                      <span className="font-medium text-purple-800">3. NEW_TOPIC_FIRST</span>
                      <p className="text-purple-700">No active block AND no matching paused blocks</p>
                    </div>
                    <div className="p-2 bg-orange-50 rounded border border-orange-200">
                      <span className="font-medium text-orange-800">4. TOPIC_SHIFT</span>
                      <p className="text-orange-700">Active block exists BUT query is new topic</p>
                    </div>
                  </div>
                </div>

                <div className="text-xs text-gray-500 bg-gray-100 p-3 rounded-lg">
                  <p className="font-medium mb-1">Technical References</p>
                  <p>Based on <a href="https://github.com/Sean-V-Dev/HMLR-Agentic-AI-Memory-System" target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:underline">HMLR-Agentic-AI-Memory-System</a> architecture. Fourth implementation uses Azure services (Cosmos DB, SQL, AI Search) with Python/FastAPI backend and Next.js frontend.</p>
                </div>
              </div>
            </section>

            <div className="text-center pt-4 border-t text-sm text-gray-500">
              <p>Questions? Contact the Platform Team</p>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
