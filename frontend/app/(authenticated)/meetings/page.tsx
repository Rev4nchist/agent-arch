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
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { api, Meeting } from '@/lib/api';
import { TeamMemberSelect } from '@/components/ui/team-member-select';
import { TeamMemberCheckboxList } from '@/components/ui/team-member-checkbox-list';
import {
  Calendar,
  Upload,
  Plus,
  Users,
  FileText,
  Clock,
  Search,
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

export default function MeetingsHub() {
  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isUploadDialogOpen, setIsUploadDialogOpen] = useState(false);
  const [selectedMeeting, setSelectedMeeting] = useState<Meeting | null>(null);
  const [meetingTasks, setMeetingTasks] = useState<Record<string, any[]>>({});

  // Create meeting form state
  const [newMeeting, setNewMeeting] = useState({
    title: '',
    date: new Date().toISOString().split('T')[0],
    type: 'Technical' as 'Governance' | 'AI Architect' | 'Licensing' | 'Technical' | 'Review',
    facilitator: '',
    participants: [] as string[],
    agenda: '',
    status: 'Scheduled' as 'Scheduled' | 'Completed' | 'Cancelled',
  });

  // Upload transcript state
  const [uploadForm, setUploadForm] = useState({
    meetingId: '',
    transcriptFile: null as File | null,
  });
  const [uploadStatus, setUploadStatus] = useState<'idle' | 'uploading' | 'processing' | 'complete'>('idle');

  useEffect(() => {
    loadMeetings();
  }, []);

  async function loadMeetings() {
    try {
      const data = await api.meetings.list();
      setMeetings(data);

      // Load tasks for meetings that have action items
      const tasksMap: Record<string, any[]> = {};
      for (const meeting of data) {
        if (meeting.action_items && meeting.action_items.length > 0) {
          try {
            const tasks = await Promise.all(
              meeting.action_items.map(taskId => api.tasks.get(taskId))
            );
            tasksMap[meeting.id] = tasks;
          } catch (error) {
            console.error(`Failed to load tasks for meeting ${meeting.id}:`, error);
            tasksMap[meeting.id] = [];
          }
        }
      }
      setMeetingTasks(tasksMap);
    } catch (error) {
      console.error('Failed to load meetings:', error);
    } finally {
      setLoading(false);
    }
  }

  function truncateSummary(summary: string, maxLines: number = 4): string {
    const lines = summary.split('\n').filter(line => line.trim().length > 0);
    if (lines.length <= maxLines) {
      return summary;
    }
    return lines.slice(0, maxLines).join('\n') + '...';
  }

  function getDetailSummary(summary: string): string {
    const lines = summary.split('\n').filter(line => line.trim().length > 0);
    const targetLines = Math.min(Math.max(lines.length, 4), 8);
    if (lines.length <= targetLines) {
      return summary;
    }
    return lines.slice(0, targetLines).join('\n') + '\n\n(Full summary available in transcript)';
  }

  async function handleCreateMeeting() {
    try {
      await api.meetings.create({
        title: newMeeting.title,
        date: new Date(newMeeting.date).toISOString(),
        type: newMeeting.type,
        facilitator: newMeeting.facilitator,
        attendees: newMeeting.participants,
        agenda: newMeeting.agenda || undefined,
        status: newMeeting.status,
      });

      setIsCreateDialogOpen(false);
      setNewMeeting({
        title: '',
        date: new Date().toISOString().split('T')[0],
        type: 'Technical',
        facilitator: '',
        participants: [],
        agenda: '',
        status: 'Scheduled',
      });
      loadMeetings();
    } catch (error) {
      console.error('Failed to create meeting:', error);
      alert('Failed to create meeting. Please try again.');
    }
  }

  async function handleUploadTranscript() {
    if (!uploadForm.meetingId || !uploadForm.transcriptFile) {
      alert('Please select a meeting and choose a file');
      return;
    }

    try {
      setUploadStatus('uploading');

      // Step 1: Upload file to blob storage
      const uploadResult = await api.transcripts.upload(
        uploadForm.transcriptFile,
        uploadForm.meetingId
      );

      setUploadStatus('processing');

      // Step 2: Process transcript with AI
      const processResult = await api.transcripts.process(
        uploadForm.meetingId,
        uploadResult.blob_url
      );

      setUploadStatus('complete');

      // Show success message
      alert(
        `Success! Extracted ${processResult.action_items?.length || 0} action items, ` +
        `${processResult.decisions?.length || 0} decisions, and created ${processResult.tasks_created || 0} tasks.`
      );

      // Reset and refresh
      setIsUploadDialogOpen(false);
      setUploadForm({ meetingId: '', transcriptFile: null });
      setUploadStatus('idle');
      await loadMeetings();

    } catch (error) {
      console.error('Failed to upload transcript:', error);
      alert(`Failed to upload transcript: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setUploadStatus('idle');
    }
  }

  const filteredMeetings = meetings.filter((meeting) => {
    const matchesSearch =
      meeting.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      meeting.attendees.some((p) =>
        p.toLowerCase().includes(searchQuery.toLowerCase())
      );

    const matchesFilter =
      filterStatus === 'all' ||
      (filterStatus === 'with-transcript' && meeting.transcript) ||
      (filterStatus === 'no-transcript' && !meeting.transcript);

    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading meetings...</div>
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
          <h1 className="text-3xl font-bold text-gray-900">Meetings Hub</h1>
          <p className="mt-2 text-gray-600">
            Plan sessions, upload transcripts, and track meeting outcomes
          </p>
        </div>

        <div className="mb-6 flex flex-col lg:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search meetings or participants..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <Select value={filterStatus} onValueChange={setFilterStatus}>
            <SelectTrigger className="w-full sm:w-[200px]">
              <SelectValue placeholder="Filter meetings" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Meetings</SelectItem>
              <SelectItem value="with-transcript">With Transcript</SelectItem>
              <SelectItem value="no-transcript">No Transcript</SelectItem>
            </SelectContent>
          </Select>

          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
            <DialogTrigger asChild>
              <Button className="w-full sm:w-auto">
                <Plus className="mr-2 h-4 w-4" />
                Plan Meeting
              </Button>
            </DialogTrigger>
            <DialogContent className="w-full h-full lg:w-auto lg:h-auto lg:max-w-[500px] max-h-[100vh] lg:max-h-[90vh] overflow-y-auto fixed inset-0 lg:inset-auto lg:top-[50%] lg:left-[50%] lg:translate-x-[-50%] lg:translate-y-[-50%] rounded-none lg:rounded-lg">
              <DialogHeader>
                <DialogTitle>Plan New Meeting</DialogTitle>
                <DialogDescription>
                  Schedule a meeting session with participants and agenda
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <label className="text-sm font-medium">Meeting Title</label>
                  <Input
                    placeholder="e.g., Q4 Planning Session"
                    value={newMeeting.title}
                    onChange={(e) =>
                      setNewMeeting({ ...newMeeting, title: e.target.value })
                    }
                  />
                </div>
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Meeting Type</label>
                    <Select
                      value={newMeeting.type}
                      onValueChange={(value: 'Governance' | 'AI Architect' | 'Licensing' | 'Technical' | 'Review') =>
                        setNewMeeting({ ...newMeeting, type: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Governance">Governance</SelectItem>
                        <SelectItem value="AI Architect">AI Architect</SelectItem>
                        <SelectItem value="Licensing">Licensing</SelectItem>
                        <SelectItem value="Technical">Technical</SelectItem>
                        <SelectItem value="Review">Review</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Status</label>
                    <Select
                      value={newMeeting.status}
                      onValueChange={(value: 'Scheduled' | 'Completed' | 'Cancelled') =>
                        setNewMeeting({ ...newMeeting, status: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Scheduled">Scheduled</SelectItem>
                        <SelectItem value="Cancelled">Cancelled</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-gray-500 mt-1">
                      Status automatically changes to "Completed" when transcript is uploaded
                    </p>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium">Date</label>
                  <Input
                    type="date"
                    value={newMeeting.date}
                    onChange={(e) =>
                      setNewMeeting({ ...newMeeting, date: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Facilitator</label>
                  <TeamMemberSelect
                    value={newMeeting.facilitator}
                    onValueChange={(value) =>
                      setNewMeeting({ ...newMeeting, facilitator: value })
                    }
                    placeholder="Select facilitator"
                  />
                </div>
                <div>
                  <TeamMemberCheckboxList
                    label="Participants"
                    selected={newMeeting.participants}
                    onChange={(selected) =>
                      setNewMeeting({ ...newMeeting, participants: selected })
                    }
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">
                    Agenda (optional)
                  </label>
                  <Textarea
                    placeholder="Meeting topics and goals..."
                    value={newMeeting.agenda}
                    onChange={(e) =>
                      setNewMeeting({ ...newMeeting, agenda: e.target.value })
                    }
                    rows={3}
                  />
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setIsCreateDialogOpen(false)}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1"
                  onClick={handleCreateMeeting}
                  disabled={!newMeeting.title || !newMeeting.date || !newMeeting.facilitator || newMeeting.participants.length === 0}
                >
                  Create Meeting
                </Button>
              </div>
            </DialogContent>
          </Dialog>

          <Dialog open={isUploadDialogOpen} onOpenChange={setIsUploadDialogOpen}>
            <DialogTrigger asChild>
              <Button variant="outline" className="w-full sm:w-auto">
                <Upload className="mr-2 h-4 w-4" />
                Upload Transcript
              </Button>
            </DialogTrigger>
            <DialogContent className="w-full h-full lg:w-auto lg:h-auto lg:max-w-[500px] max-h-[100vh] lg:max-h-[90vh] overflow-y-auto fixed inset-0 lg:inset-auto lg:top-[50%] lg:left-[50%] lg:translate-x-[-50%] lg:translate-y-[-50%] rounded-none lg:rounded-lg">
              <DialogHeader>
                <DialogTitle>Upload Meeting Transcript</DialogTitle>
                <DialogDescription>
                  Select a meeting and upload its transcript file
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <label className="text-sm font-medium">Select Meeting</label>
                  <Select
                    value={uploadForm.meetingId}
                    onValueChange={(value) =>
                      setUploadForm({ ...uploadForm, meetingId: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue placeholder="Choose a meeting" />
                    </SelectTrigger>
                    <SelectContent>
                      {meetings.map((meeting) => (
                        <SelectItem key={meeting.id} value={meeting.id}>
                          {meeting.title} -{' '}
                          {new Date(meeting.date).toLocaleDateString()}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div>
                  <label className="text-sm font-medium">
                    Transcript File (.txt, .md, .docx)
                  </label>
                  <Input
                    type="file"
                    accept=".txt,.md,.docx"
                    onChange={(e) =>
                      setUploadForm({
                        ...uploadForm,
                        transcriptFile: e.target.files?.[0] || null,
                      })
                    }
                    className="cursor-pointer"
                  />
                </div>
                <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
                  <strong>Note:</strong> Uploaded transcripts will be processed
                  by AI to extract action items, decisions, and topics.
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => {
                    setIsUploadDialogOpen(false);
                    setUploadStatus('idle');
                  }}
                  disabled={uploadStatus !== 'idle'}
                >
                  Cancel
                </Button>
                <Button
                  className="flex-1"
                  onClick={handleUploadTranscript}
                  disabled={!uploadForm.meetingId || !uploadForm.transcriptFile || uploadStatus !== 'idle'}
                >
                  {uploadStatus === 'uploading' && 'Uploading...'}
                  {uploadStatus === 'processing' && 'Processing...'}
                  {uploadStatus === 'idle' && 'Upload & Process'}
                  {uploadStatus === 'complete' && 'Complete!'}
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        <div className="grid grid-cols-1 gap-6">
          {filteredMeetings.length === 0 ? (
            <Card>
              <CardContent className="p-12 text-center">
                <Calendar className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No meetings found
                </h3>
                <p className="text-gray-600 mb-4">
                  {searchQuery
                    ? 'Try adjusting your search or filter'
                    : 'Get started by planning your first meeting'}
                </p>
                <Button onClick={() => setIsCreateDialogOpen(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Plan Your First Meeting
                </Button>
              </CardContent>
            </Card>
          ) : (
            filteredMeetings.map((meeting) => (
              <Card key={meeting.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <CardTitle className="text-xl">{meeting.title}</CardTitle>
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
                      <div className="flex flex-wrap items-center gap-2 text-sm text-gray-600">
                        <Badge variant="outline" className="bg-purple-50 text-purple-700">
                          {meeting.type}
                        </Badge>
                        <div className="flex items-center gap-1">
                          <Calendar className="h-4 w-4" />
                          {new Date(meeting.date).toLocaleDateString('en-US', {
                            year: 'numeric',
                            month: 'long',
                            day: 'numeric',
                          })}
                        </div>
                        <div className="flex items-center gap-1">
                          <Users className="h-4 w-4" />
                          {meeting.facilitator}
                        </div>
                        <Badge variant="outline">
                          {meeting.attendees.length} attendees
                        </Badge>
                      </div>
                    </div>
                    {meeting.status !== 'Completed' && (
                      <Badge
                        variant={meeting.transcript ? 'default' : 'outline'}
                        className={
                          meeting.transcript
                            ? 'bg-green-100 text-green-800'
                            : 'bg-gray-100 text-gray-800'
                        }
                      >
                        {meeting.transcript ? (
                          <FileText className="h-3 w-3 mr-1" />
                        ) : (
                          <Clock className="h-3 w-3 mr-1" />
                        )}
                        {meeting.transcript ? 'Transcript' : 'Pending'}
                      </Badge>
                    )}
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div>
                      <div className="text-sm font-semibold text-gray-700 mb-1">
                        Participants:
                      </div>
                      <div className="flex flex-wrap gap-2">
                        {meeting.attendees.map((participant, idx) => (
                          <Badge key={idx} variant="outline">
                            {participant}
                          </Badge>
                        ))}
                      </div>
                    </div>

                    {meeting.summary && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                        <div className="text-sm font-semibold text-blue-900 mb-2">
                          Quick Meeting Summary
                        </div>
                        <p className="text-sm text-blue-800 whitespace-pre-line leading-relaxed">
                          {truncateSummary(meeting.summary)}
                        </p>
                      </div>
                    )}

                    {meeting.action_items && meeting.action_items.length > 0 && (
                      <div>
                        <div className="text-sm font-semibold text-gray-700 mb-1">
                          Action Items:
                        </div>
                        <ul className="list-disc list-inside text-sm text-gray-600 space-y-1">
                          {(meetingTasks[meeting.id] || []).slice(0, 3).map((task, idx) => (
                            <li key={idx}>
                              {task.title}
                              {task.assigned_to && (
                                <span className="text-gray-500"> ({task.assigned_to})</span>
                              )}
                            </li>
                          ))}
                          {(meetingTasks[meeting.id]?.length || 0) > 3 && (
                            <li className="text-gray-500 italic">
                              +{(meetingTasks[meeting.id]?.length || 0) - 3} more...
                            </li>
                          )}
                        </ul>
                      </div>
                    )}

                    {meeting.topics && meeting.topics.length > 0 && (
                      <div>
                        <div className="text-sm font-semibold text-gray-700 mb-1">
                          Topics Discussed:
                        </div>
                        <div className="flex flex-wrap gap-2">
                          {meeting.topics.map((topic, idx) => (
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

                    <div className="flex gap-2 pt-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setSelectedMeeting(meeting)}
                      >
                        View Details
                      </Button>
                      {!meeting.transcript && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => {
                            setUploadForm({ ...uploadForm, meetingId: meeting.id });
                            setIsUploadDialogOpen(true);
                          }}
                        >
                          <Upload className="mr-1 h-3 w-3" />
                          Add Transcript
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))
          )}
        </div>

        {/* Meeting Details Modal */}
        {selectedMeeting && (
          <Dialog open={!!selectedMeeting} onOpenChange={() => setSelectedMeeting(null)}>
            <DialogContent className="w-full h-full lg:w-auto lg:h-auto lg:max-w-[700px] max-h-[100vh] lg:max-h-[80vh] overflow-y-auto fixed inset-0 lg:inset-auto lg:top-[50%] lg:left-[50%] lg:translate-x-[-50%] lg:translate-y-[-50%] rounded-none lg:rounded-lg">
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
            </DialogContent>
          </Dialog>
        )}
      </div>
    </div>
  );
}
