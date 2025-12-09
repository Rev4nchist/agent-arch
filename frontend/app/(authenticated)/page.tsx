'use client';
import Link from 'next/link';

import { useEffect, useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { api, Meeting, Task } from '@/lib/api';
import {
  Calendar,
  CheckSquare,
  Bot,
  FileText,
  Lightbulb,
  Plus,
  TrendingUp,
  Users,
  Clock,
  AlertCircle,
} from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState({
    meetings: 0,
    tasks: 0,
    agents: 0,
    proposals: 0,
  });
  const [recentMeetings, setRecentMeetings] = useState<Meeting[]>([]);
  const [recentTasks, setRecentTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [activityView, setActivityView] = useState<'recent' | 'upcoming'>('recent');
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [meetingTasks, setMeetingTasks] = useState<Record<string, any[]>>({});

  useEffect(() => {
    async function loadData() {
      try {
        const [meetings, tasks, agents, proposals] = await Promise.all([
          api.meetings.list(),
          api.tasks.list(),
          api.agents.list(),
          api.proposals.list(),
        ]);

        // Filter counts based on status
        const plannedMeetings = meetings.filter(m => m.status === 'Scheduled').length;
        const openTasks = tasks.filter(t => t.status !== 'Done' && t.status !== 'Deferred').length;
        const newAgents = agents.filter(a => a.status === 'Idea' || a.status === 'Design').length;
        const newProposals = proposals.filter(p => p.status === 'Proposed').length;

        setStats({
          meetings: plannedMeetings,
          tasks: openTasks,
          agents: newAgents,
          proposals: newProposals,
        });

        setRecentMeetings(meetings.slice(0, 5));
        setRecentTasks(tasks.slice(0, 5));

        // Load tasks for meetings that have action items
        const tasksMap: Record<string, any[]> = {};
        for (const meeting of meetings.slice(0, 5)) {
          if (meeting.action_items && meeting.action_items.length > 0) {
            try {
              const meetingTaskList = await Promise.all(
                meeting.action_items.map(taskId => api.tasks.get(taskId))
              );
              tasksMap[meeting.id] = meetingTaskList;
            } catch (error) {
              console.error(`Failed to load tasks for meeting ${meeting.id}:`, error);
              tasksMap[meeting.id] = [];
            }
          }
        }
        setMeetingTasks(tasksMap);
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
      } finally {
        setLoading(false);
      }
    }

    loadData();
  }, []);

  const statCards = [
    {
      title: 'Proposals & Decisions',
      subtitle: 'New Proposals',
      value: stats.proposals,
      icon: Lightbulb,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      action: 'New Proposal',
      href: '/decisions',
    },
    {
      title: 'Meetings',
      subtitle: 'Planned',
      value: stats.meetings,
      icon: Calendar,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      action: 'Create Meeting',
      href: '/meetings',
    },
    {
      title: 'Tasks',
      subtitle: 'Open',
      value: stats.tasks,
      icon: CheckSquare,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      action: 'Add Task',
      href: '/tasks',
    },
    {
      title: 'Agents',
      subtitle: 'New',
      value: stats.agents,
      icon: Bot,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      action: 'New Agent',
      href: '/agents',
    },
  ];

  const getTaskStatusColor = (status: string) => {
    switch (status) {
      case 'Done':
        return 'bg-green-100 text-green-800 border-green-300';
      case 'In-Progress':
        return 'bg-blue-100 text-blue-800 border-blue-300';
      case 'Blocked':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'Deferred':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      default:
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Critical':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'High':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Agent':
        return 'bg-purple-50 text-purple-700 border-purple-200';
      case 'Governance':
        return 'bg-blue-50 text-blue-700 border-blue-200';
      case 'Technical':
        return 'bg-green-50 text-green-700 border-green-200';
      case 'Licensing':
        return 'bg-orange-50 text-orange-700 border-orange-200';
      case 'AI Architect':
        return 'bg-indigo-50 text-indigo-700 border-indigo-200';
      default:
        return 'bg-gray-50 text-gray-700 border-gray-200';
    }
  };

  function getDetailSummary(summary: string): string {
    const lines = summary.split('\n').filter(line => line.trim().length > 0);
    const targetLines = Math.min(Math.max(lines.length, 4), 8);
    if (lines.length <= targetLines) {
      return summary;
    }
    return lines.slice(0, targetLines).join('\n') + '\n\n(Full summary available in transcript)';
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="mt-2 text-gray-600">
            Agent Architecture Guide - Overview & Quick Actions
          </p>
        </div>

        <div className="grid grid-cols-2 gap-3 lg:grid-cols-4 lg:gap-6 mb-8">
          {statCards.map((stat) => {
            const Icon = stat.icon;
            return (
              <div key={stat.title} className="flex flex-col gap-3">
                <Link href={stat.href}>
                  <Card className="hover:shadow-lg transition-shadow cursor-pointer h-[200px]" style={{ padding: 0 }}>
                    <CardContent className="h-full" style={{ position: 'relative', padding: 0 }}>
                      <div style={{ paddingLeft: '24px', paddingRight: '24px', paddingTop: '20px' }}>
                        <div className={`rounded-lg p-1.5 ${stat.bgColor} w-fit`}>
                          <Icon className={`h-5 w-5 ${stat.color}`} />
                        </div>
                        <p className="text-sm font-bold text-gray-900 leading-tight mt-1.5">
                          {stat.title}
                        </p>
                      </div>
                      <div style={{ position: 'absolute', bottom: '24px', left: '24px', right: '24px' }}>
                        <p className="text-4xl font-bold text-gray-900 leading-none">
                          {stat.value}
                        </p>
                        <p className="text-xs font-medium text-gray-500 uppercase tracking-wide mt-1">
                          {stat.subtitle}
                        </p>
                      </div>
                    </CardContent>
                  </Card>
                </Link>
                <Link href={`${stat.href}?create=true`} className="w-full">
                  <Button className="w-full" variant="outline">
                    <Plus className="mr-2 h-4 w-4" />
                    {stat.action}
                  </Button>
                </Link>
              </div>
            );
          })}
        </div>

        <Card className="mb-8">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <Clock className="h-5 w-5" />
                  {activityView === 'recent' ? 'Recent Activity' : 'Upcoming Activity'}
                </CardTitle>
                <div className="flex gap-2">
                  <Button
                    variant={activityView === 'recent' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setActivityView('recent')}
                  >
                    Recent
                  </Button>
                  <Button
                    variant={activityView === 'upcoming' ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setActivityView('upcoming')}
                  >
                    Upcoming
                  </Button>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div>
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">
                    {activityView === 'recent' ? 'Recent Meetings' : 'Upcoming Meetings'}
                  </h3>
                  {(() => {
                    const filteredMeetings = activityView === 'recent'
                      ? recentMeetings.filter(m => m.status === 'Completed' || m.status === 'Cancelled')
                      : recentMeetings.filter(m => m.status === 'Scheduled');
                    
                    return filteredMeetings.length === 0 ? (
                      <p className="text-sm text-gray-500 italic">
                        {activityView === 'recent' ? 'No recent meetings' : 'No upcoming meetings'}
                      </p>
                    ) : (
                      <div className="space-y-2">
                        {filteredMeetings.map((meeting) => (
                        <div
                          key={meeting.id}
                          className="flex items-start justify-between p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <p className="font-medium text-sm text-gray-900">
                                {meeting.title}
                              </p>
                              <Badge
                                variant="outline"
                                className={`text-xs ${
                                  meeting.status === 'Completed'
                                    ? 'bg-green-50 text-green-700'
                                    : meeting.status === 'Cancelled'
                                    ? 'bg-red-50 text-red-700'
                                    : 'bg-blue-50 text-blue-700'
                                }`}
                              >
                                {meeting.status}
                              </Badge>
                            </div>
                            <div className="flex flex-wrap items-center gap-2 mt-1">
                              <Badge variant="outline" className="text-xs bg-purple-50 text-purple-700">
                                {meeting.type}
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                {new Date(meeting.date).toLocaleDateString()}
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                <Users className="h-3 w-3 mr-1" />
                                {meeting.facilitator}
                              </Badge>
                              <Badge variant="outline" className="text-xs">
                                {meeting.attendees.length} attendees
                              </Badge>
                            </div>
                            <div className="flex gap-2 pt-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setSelectedMeeting(meeting)}
                              >
                                View Details
                              </Button>
                            </div>
                          </div>
                        </div>
                        ))}
                      </div>
                    );
                  })()}
                </div>

                <div className="pt-4 border-t">
                  <h3 className="text-sm font-semibold text-gray-900 mb-3">
                    {activityView === 'recent' ? 'Recent Tasks' : 'Upcoming Tasks'}
                  </h3>
                  {(() => {
                    const filteredTasks = activityView === 'recent'
                      ? recentTasks.filter(t => t.status === 'Done' || t.status === 'Blocked' || t.status === 'Deferred')
                      : recentTasks.filter(t => t.status === 'Pending' || t.status === 'In-Progress');
                    
                    return filteredTasks.length === 0 ? (
                      <p className="text-sm text-gray-500 italic">
                        {activityView === 'recent' ? 'No recent tasks' : 'No upcoming tasks'}
                      </p>
                    ) : (
                      <div className="space-y-2">
                        {filteredTasks.map((task) => (
                        <div
                          key={task.id}
                          className="flex items-start justify-between p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                        >
                          <div className="flex-1">
                            <p className="font-medium text-sm text-gray-900">
                              {task.title}
                            </p>
                            <div className="flex items-center gap-2 mt-1">
                              <Badge
                                className={`text-xs ${getTaskStatusColor(
                                  task.status
                                )}`}
                              >
                                {task.status}
                              </Badge>
                              <Badge
                                className={`text-xs ${getPriorityColor(
                                  task.priority
                                )}`}
                              >
                                {task.priority}
                              </Badge>
                              {task.category && (
                                <Badge variant="outline" className={`text-xs ${getCategoryColor(task.category)}`}>
                                  {task.category}
                                </Badge>
                              )}
                            </div>
                            <div className="flex gap-2 pt-2">
                              <Button
                                variant="outline"
                                size="sm"
                                onClick={() => setSelectedTask(task)}
                              >
                                View Details
                              </Button>
                            </div>
                          </div>
                        </div>
                        ))}
                      </div>
                    );
                  })()}
                </div>
              </div>
            </CardContent>
        </Card>

        {/* Task Details Modal */}
        {selectedTask && (
          <Dialog
            open={!!selectedTask}
            onOpenChange={() => setSelectedTask(null)}
          >
            <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle className="text-2xl">
                  {selectedTask.title}
                </DialogTitle>
                <DialogDescription>Task Details and Information</DialogDescription>
              </DialogHeader>

              <div className="space-y-6 mt-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge className={getTaskStatusColor(selectedTask.status)}>
                    {selectedTask.status}
                  </Badge>
                  <Badge className={getPriorityColor(selectedTask.priority)}>
                    {selectedTask.priority}
                  </Badge>
                  {selectedTask.category && (
                    <Badge
                      variant="outline"
                      className={getCategoryColor(selectedTask.category)}
                    >
                      {selectedTask.category}
                    </Badge>
                  )}
                </div>

                {selectedTask.description && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">
                      Description
                    </h3>
                    <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                      {selectedTask.description}
                    </p>
                  </div>
                )}

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {selectedTask.assigned_to && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900 mb-2">
                        Assigned To
                      </h3>
                      <p className="text-sm text-gray-700">{selectedTask.assigned_to}</p>
                    </div>
                  )}

                  {selectedTask.due_date && (
                    <div>
                      <h3 className="text-sm font-semibold text-gray-900 mb-2">
                        Due Date
                      </h3>
                      <div className="flex items-center gap-2 text-sm text-gray-700">
                        <Clock className="h-4 w-4" />
                        {new Date(selectedTask.due_date).toLocaleDateString()}
                      </div>
                    </div>
                  )}
                </div>

                {selectedTask.created_at && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">
                      Created On
                    </h3>
                    <p className="text-sm text-gray-700">
                      {new Date(selectedTask.created_at).toLocaleString()}
                    </p>
                  </div>
                )}

                {selectedTask.notes && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">
                      Notes
                    </h3>
                    <p className="text-sm text-gray-700 whitespace-pre-line leading-relaxed">
                      {selectedTask.notes}
                    </p>
                  </div>
                )}

                {selectedTask.dependencies && selectedTask.dependencies.length > 0 && (
                  <div>
                    <h3 className="text-sm font-semibold text-gray-900 mb-2">
                      Dependencies
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedTask.dependencies.map((depId, idx) => (
                        <Badge key={idx} variant="outline" className="text-xs">
                          Task: {depId}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="flex gap-2 mt-6">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setSelectedTask(null)}
                >
                  Close
                </Button>
                <Link href="/tasks" className="flex-1">
                  <Button className="w-full">View in Tasks Page</Button>
                </Link>
              </div>
            </DialogContent>
          </Dialog>
        )}

        {/* Meeting Details Modal */}
        {selectedMeeting && (
          <Dialog open={!!selectedMeeting} onOpenChange={() => setSelectedMeeting(null)}>
            <DialogContent className="sm:max-w-[700px] max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>{selectedMeeting.title}</DialogTitle>
                <DialogDescription>
                  {new Date(selectedMeeting.date).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <h3 className="font-semibold text-sm text-gray-700 mb-2">Details</h3>
                  <div className="space-y-2 text-sm">
                    <div className="flex items-center gap-2">
                      <Badge variant="outline" className="bg-purple-50 text-purple-700">
                        {selectedMeeting.type}
                      </Badge>
                      <Badge
                        variant="outline"
                        className={`${
                          selectedMeeting.status === 'Completed'
                            ? 'bg-green-50 text-green-700'
                            : selectedMeeting.status === 'Cancelled'
                            ? 'bg-red-50 text-red-700'
                            : 'bg-blue-50 text-blue-700'
                        }`}
                      >
                        {selectedMeeting.status}
                      </Badge>
                    </div>
                    <div>
                      <strong>Facilitator:</strong> {selectedMeeting.facilitator}
                    </div>
                    <div>
                      <strong>Attendees:</strong> {selectedMeeting.attendees.join(', ')}
                    </div>
                    {selectedMeeting.agenda && (
                      <div>
                        <strong>Agenda:</strong> {selectedMeeting.agenda}
                      </div>
                    )}
                  </div>
                </div>

                {selectedMeeting.summary && (
                  <div>
                    <h3 className="font-semibold text-sm text-gray-700 mb-2">Agenda Summary</h3>
                    <p className="text-sm text-gray-600 whitespace-pre-line">
                      {getDetailSummary(selectedMeeting.summary)}
                    </p>
                  </div>
                )}

                {selectedMeeting.action_items && selectedMeeting.action_items.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-sm text-gray-700 mb-2">
                      Action Items ({meetingTasks[selectedMeeting.id]?.length || 0})
                    </h3>
                    <div className="space-y-2">
                      {(meetingTasks[selectedMeeting.id] || []).map((task, idx) => (
                        <div
                          key={idx}
                          className="border border-gray-200 rounded-lg p-3 bg-gray-50"
                        >
                          <div className="font-medium text-sm">{task.title}</div>
                          {task.description && (
                            <div className="text-xs text-gray-600 mt-1">
                              {task.description}
                            </div>
                          )}
                          <div className="flex items-center gap-2 mt-2 flex-wrap">
                            {task.assigned_to && (
                              <Badge variant="outline" className="text-xs">
                                {task.assigned_to}
                              </Badge>
                            )}
                            {task.priority && (
                              <Badge
                                variant="outline"
                                className={`text-xs ${
                                  task.priority === 'Critical'
                                    ? 'bg-red-50 text-red-700'
                                    : task.priority === 'High'
                                    ? 'bg-orange-50 text-orange-700'
                                    : task.priority === 'Medium'
                                    ? 'bg-yellow-50 text-yellow-700'
                                    : 'bg-gray-50 text-gray-700'
                                }`}
                              >
                                {task.priority}
                              </Badge>
                            )}
                            {task.status && (
                              <Badge variant="outline" className="text-xs">
                                {task.status}
                              </Badge>
                            )}
                            {task.due_date && (
                              <span className="text-xs text-gray-500">
                                Due: {new Date(task.due_date).toLocaleDateString()}
                              </span>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {selectedMeeting.topics && selectedMeeting.topics.length > 0 && (
                  <div>
                    <h3 className="font-semibold text-sm text-gray-700 mb-2">
                      Topics Discussed
                    </h3>
                    <div className="flex flex-wrap gap-2">
                      {selectedMeeting.topics.map((topic, idx) => (
                        <Badge
                          key={idx}
                          variant="outline"
                          className="bg-blue-50 text-blue-800"
                        >
                          {topic}
                        </Badge>
                      ))}
                    </div>
                  </div>
                )}

                {selectedMeeting.transcript_url && (
                  <div>
                    <h3 className="font-semibold text-sm text-gray-700 mb-2">Transcript</h3>
                    <a
                      href={selectedMeeting.transcript_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-sm text-blue-600 hover:underline"
                    >
                      View full transcript
                    </a>
                  </div>
                )}
              </div>

              <div className="flex gap-2 mt-6">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setSelectedMeeting(null)}
                >
                  Close
                </Button>
                <Link href="/meetings" className="flex-1">
                  <Button className="w-full">View in Meetings Page</Button>
                </Link>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </div>
  );
}
