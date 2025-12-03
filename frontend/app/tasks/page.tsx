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
  DialogClose,
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
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { api, Task } from '@/lib/api';
import { TeamMemberSelect } from '@/components/ui/team-member-select';
import { Checkbox } from '@/components/ui/checkbox';
import { TEAM_MEMBERS } from '@/lib/team-members';
import {
  CheckSquare,
  Plus,
  List,
  Columns3,
  Search,
  Clock,
  AlertCircle,
  Trash2,
  Building2,
  MessageCircle,
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

type ViewMode = 'list' | 'kanban';
type StatusColumn = 'Pending' | 'In-Progress' | 'Done' | 'Blocked' | 'Deferred';

const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  'Agent': 'Tasks related to AI agent development, frameworks, and implementation',
  'Governance': 'Tasks for AI governance, compliance, policies, and organizational guidelines',
  'Technical': 'Technical implementation tasks, platform work, and infrastructure',
  'Licensing': 'Tasks related to licensing, pricing, and commercial agreements',
  'AI Architect': 'Architecture design tasks, solution patterns, and technical decisions',
};

export default function TasksPage() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [searchQuery, setSearchQuery] = useState('');
  const [filterPriority, setFilterPriority] = useState<string>('all');
  const [filterCategory, setFilterCategory] = useState<string>('all');
  const [filterAssignee, setFilterAssignee] = useState<string>('all');
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedTask, setEditedTask] = useState<Partial<Task>>({});
  const [taskToDelete, setTaskToDelete] = useState<Task | null>(null);
  const [draggedTaskId, setDraggedTaskId] = useState<string | null>(null);
  const [dragOverColumn, setDragOverColumn] = useState<StatusColumn | null>(null);
  const [taskSource, setTaskSource] = useState<'architecture' | 'feedback'>('architecture');

  const [newTask, setNewTask] = useState({
    title: '',
    description: '',
    priority: 'Medium' as 'Critical' | 'High' | 'Medium' | 'Low',
    category: 'Governance' as 'Agent' | 'Governance' | 'Technical' | 'Licensing' | 'AI Architect',
    status: 'Pending' as StatusColumn,
    assigned_to: '',
    due_date: '',
    complexity: '' as '' | 'beginner' | 'intermediate' | 'advanced',
    learning_friendly: false,
  });

  useEffect(() => {
    // Then reload tasks
      setTimeout(() => loadTasks(), 100);
  }, []);

  async function loadTasks() {
    try {
      const data = await api.tasks.list();
      setTasks(data);
    } catch (error) {
      console.error('Failed to load tasks:', error);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateTask() {
    try {
      await api.tasks.create({
        title: newTask.title,
        description: newTask.description,
        status: newTask.status,
        priority: newTask.priority,
        category: newTask.category,
        assigned_to: newTask.assigned_to.trim() || undefined,
        due_date: newTask.due_date || undefined,
        dependencies: [],
        complexity: newTask.complexity || undefined,
        learning_friendly: newTask.learning_friendly,
      });

      // Close dialog first
      setIsCreateDialogOpen(false);
      setNewTask({
        title: '',
        description: '',
        priority: 'Medium',
        category: 'Governance',
        status: 'Pending',
        assigned_to: '',
        due_date: '',
        complexity: '',
        learning_friendly: false,
      });
      // Then reload tasks
      setTimeout(() => loadTasks(), 100);
    } catch (error) {
      console.error('Failed to create task:', error);
      alert('Failed to create task. Please try again.');
    }
  }

  async function handleUpdateTask() {
    if (!selectedTask || !editedTask) return;

    try {
      // Merge full task with edits - backend expects complete Task object
      const fullTaskUpdate = { ...selectedTask, ...editedTask };
      await api.tasks.update(selectedTask.id, fullTaskUpdate);
      setIsEditing(false);
      setEditedTask({});
      // Then reload tasks
      setTimeout(() => loadTasks(), 100);

      // Update selectedTask with new data
      const updatedTask = { ...selectedTask, ...editedTask };
      setSelectedTask(updatedTask);
    } catch (error) {
      console.error('Failed to update task:', error);
      alert('Failed to update task. Please try again.');
    }
  }

  function handleEditClick() {
    if (selectedTask) {
      setEditedTask({
        title: selectedTask.title,
        description: selectedTask.description,
        status: selectedTask.status,
        priority: selectedTask.priority,
        category: selectedTask.category,
        assigned_to: selectedTask.assigned_to,
        due_date: selectedTask.due_date,
        notes: selectedTask.notes,
      });
      setIsEditing(true);
    }
  }

  function handleCancelEdit() {
    setIsEditing(false);
    setEditedTask({});
  }

  async function handleDeleteTask() {
    if (!taskToDelete) return;

    try {
      await api.tasks.delete(taskToDelete.id);
      setTaskToDelete(null);
      setSelectedTask(null);
      setTimeout(() => loadTasks(), 100);
    } catch (error) {
      console.error('Failed to delete task:', error);
      alert('Failed to delete task. Please try again.');
    }
  }

  const priorityOrder: Record<string, number> = {
    Critical: 0,
    High: 1,
    Medium: 2,
    Low: 3,
  };

  const filteredTasks = tasks
    .filter((task) => {
      const matchesSource = taskSource === 'architecture'
        ? !task.from_submission_id
        : !!task.from_submission_id;

      const matchesSearch =
        task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        task.description?.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesPriority =
        filterPriority === 'all' || task.priority === filterPriority;

      const matchesCategory =
        filterCategory === 'all' || task.category === filterCategory;

      const matchesAssignee =
        filterAssignee === 'all' || task.assigned_to === filterAssignee;

      const hideFromList = viewMode === 'list' && task.status === 'Done';

      return matchesSource && matchesSearch && matchesPriority && matchesCategory && matchesAssignee && !hideFromList;
    })
    .sort((a, b) => {
      const today = new Date();
      today.setHours(0, 0, 0, 0);

      const aDate = a.due_date ? new Date(a.due_date) : null;
      const bDate = b.due_date ? new Date(b.due_date) : null;
      const aOverdue = aDate && aDate < today && a.status !== 'Done';
      const bOverdue = bDate && bDate < today && b.status !== 'Done';

      if (aOverdue && !bOverdue) return -1;
      if (!aOverdue && bOverdue) return 1;

      if (aDate && bDate) {
        const dateCompare = aDate.getTime() - bDate.getTime();
        if (dateCompare !== 0) return dateCompare;
      } else if (aDate && !bDate) {
        return -1;
      } else if (!aDate && bDate) {
        return 1;
      }

      return (priorityOrder[a.priority] ?? 3) - (priorityOrder[b.priority] ?? 3);
    });

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'Critical':
        return 'bg-red-100 text-red-800 border-red-300';
      case 'High':
        return 'bg-orange-100 text-orange-800 border-orange-300';
      case 'Medium':
        return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      case 'Low':
        return 'bg-gray-100 text-gray-800 border-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-300';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Done':
        return 'bg-green-100 text-green-800';
      case 'In-Progress':
        return 'bg-blue-100 text-blue-800';
      case 'Blocked':
        return 'bg-red-100 text-red-800';
      case 'Pending':
        return 'bg-gray-100 text-gray-800';
      case 'Deferred':
        return 'bg-purple-100 text-purple-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'Agent':
        return 'bg-yellow-50 text-yellow-600 border-yellow-300';
      case 'Governance':
        return 'bg-blue-50 text-blue-600 border-blue-300';
      case 'Technical':
        return 'bg-purple-50 text-purple-600 border-purple-300';
      case 'Licensing':
        return 'bg-orange-50 text-orange-600 border-orange-300';
      case 'AI Architect':
        return 'bg-green-50 text-green-600 border-green-300';
      default:
        return 'bg-gray-50 text-gray-600 border-gray-300';
    }
  };

  const isOverdue = (task: Task) => {
    if (!task.due_date || task.status === 'Done') return false;
    const dueDate = new Date(task.due_date);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    return dueDate < today;
  };

  const handleDragStart = (e: React.DragEvent, taskId: string) => {
    setDraggedTaskId(taskId);
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', taskId);
  };

  const handleDragOver = (e: React.DragEvent, column: StatusColumn) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
    if (dragOverColumn !== column) {
      setDragOverColumn(column);
    }
  };

  const handleDragLeave = (e: React.DragEvent) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX;
    const y = e.clientY;
    if (x < rect.left || x > rect.right || y < rect.top || y > rect.bottom) {
      setDragOverColumn(null);
    }
  };

  const handleDrop = async (e: React.DragEvent, newStatus: StatusColumn) => {
    e.preventDefault();
    e.stopPropagation();
    setDragOverColumn(null);

    if (!draggedTaskId) return;

    const task = tasks.find((t) => t.id === draggedTaskId);
    if (!task || task.status === newStatus) {
      setDraggedTaskId(null);
      return;
    }

    const originalStatus = task.status;
    setTasks((prev) =>
      prev.map((t) => (t.id === draggedTaskId ? { ...t, status: newStatus } : t))
    );
    setDraggedTaskId(null);

    try {
      await api.tasks.update(task.id, { ...task, status: newStatus });
    } catch (error) {
      console.error('Failed to update task status:', error);
      setTasks((prev) =>
        prev.map((t) => (t.id === draggedTaskId ? { ...t, status: originalStatus } : t))
      );
    }
  };

  const handleDragEnd = () => {
    setDraggedTaskId(null);
    setDragOverColumn(null);
  };

  const groupedTasks = {
    Pending: filteredTasks.filter((t) => t.status === 'Pending'),
    'In-Progress': filteredTasks.filter((t) => t.status === 'In-Progress'),
    Done: filteredTasks.filter((t) => t.status === 'Done'),
    Blocked: filteredTasks.filter((t) => t.status === 'Blocked'),
    Deferred: filteredTasks.filter((t) => t.status === 'Deferred'),
  };

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-lg text-gray-600">Loading tasks...</div>
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
          <h1 className="text-3xl font-bold text-gray-900">Tasks</h1>
          <p className="mt-2 text-gray-600">
            Track and manage your project tasks
          </p>
        </div>

        <Tabs value={taskSource} onValueChange={(v) => setTaskSource(v as 'architecture' | 'feedback')} className="mb-6">
          <TabsList className="grid w-full max-w-md grid-cols-2">
            <TabsTrigger value="architecture" className="flex items-center gap-2">
              <Building2 className="h-4 w-4" />
              Architecture Tasks
            </TabsTrigger>
            <TabsTrigger value="feedback" className="flex items-center gap-2">
              <MessageCircle className="h-4 w-4" />
              Feedback Tasks
            </TabsTrigger>
          </TabsList>
        </Tabs>

        <div className="mb-6 flex flex-col sm:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
            <Input
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-10"
            />
          </div>

          <Select value={filterPriority} onValueChange={setFilterPriority}>
            <SelectTrigger className="w-full sm:w-[180px]">
              <SelectValue placeholder="Filter priority" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priorities</SelectItem>
              <SelectItem value="Critical">Critical Priority</SelectItem>
              <SelectItem value="High">High Priority</SelectItem>
              <SelectItem value="Medium">Medium Priority</SelectItem>
              <SelectItem value="Low">Low Priority</SelectItem>
            </SelectContent>
          </Select>

          <Select value={filterCategory} onValueChange={setFilterCategory}>
            <SelectTrigger className="w-full sm:w-[180px]">
              <SelectValue placeholder="Filter category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              <SelectItem value="Agent">Agent</SelectItem>
              <SelectItem value="Governance">Governance</SelectItem>
              <SelectItem value="Technical">Technical</SelectItem>
              <SelectItem value="Licensing">Licensing</SelectItem>
              <SelectItem value="AI Architect">AI Architect</SelectItem>
            </SelectContent>
          </Select>

          <Select value={filterAssignee} onValueChange={setFilterAssignee}>
            <SelectTrigger className="w-full sm:w-[180px]">
              <SelectValue placeholder="Filter assignee" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Assignees</SelectItem>
              {TEAM_MEMBERS.map((member) => (
                <SelectItem key={member} value={member}>
                  {member}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          <div className="flex gap-2">
            <Button
              variant={viewMode === 'list' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('list')}
            >
              <List className="h-4 w-4" />
            </Button>
            <Button
              variant={viewMode === 'kanban' ? 'default' : 'outline'}
              size="icon"
              onClick={() => setViewMode('kanban')}
            >
              <Columns3 className="h-4 w-4" />
            </Button>
          </div>

          <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen} modal={true}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                New Task
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[500px]" onCloseClick={() => setIsCreateDialogOpen(false)}>
              <DialogHeader>
                <DialogTitle>Create New Task</DialogTitle>
                <DialogDescription>
                  Add a new task to track work and progress
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 mt-4">
                <div>
                  <label className="text-sm font-medium">Task Title</label>
                  <Input
                    placeholder="e.g., Implement user authentication"
                    value={newTask.title}
                    onChange={(e) =>
                      setNewTask({ ...newTask, title: e.target.value })
                    }
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Description</label>
                  <Textarea
                    placeholder="Task details and requirements..."
                    value={newTask.description}
                    onChange={(e) =>
                      setNewTask({ ...newTask, description: e.target.value })
                    }
                    rows={3}
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Priority</label>
                    <Select
                      value={newTask.priority}
                      onValueChange={(value: 'Critical' | 'High' | 'Medium' | 'Low') =>
                        setNewTask({ ...newTask, priority: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Low">Low</SelectItem>
                        <SelectItem value="Medium">Medium</SelectItem>
                        <SelectItem value="High">High</SelectItem>
                        <SelectItem value="Critical">Critical</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">Category</label>
                    <Select
                      value={newTask.category}
                      onValueChange={(value: 'Agent' | 'Governance' | 'Technical' | 'Licensing' | 'AI Architect') =>
                        setNewTask({ ...newTask, category: value })
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
                </div>
                {newTask.category && (
                  <p className="text-xs text-gray-500 italic bg-gray-50 p-2 rounded">
                    <span className="font-medium">{newTask.category}:</span> {CATEGORY_DESCRIPTIONS[newTask.category]}
                  </p>
                )}
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Status</label>
                    <Select
                      value={newTask.status}
                      onValueChange={(value: StatusColumn) =>
                        setNewTask({ ...newTask, status: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Pending">Pending</SelectItem>
                        <SelectItem value="In-Progress">In Progress</SelectItem>
                        <SelectItem value="Done">Done</SelectItem>
                        <SelectItem value="Blocked">Blocked</SelectItem>
                        <SelectItem value="Deferred">Deferred</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <label className="text-sm font-medium">
                      Assigned To
                    </label>
                    <TeamMemberSelect
                      value={newTask.assigned_to}
                      onValueChange={(value) =>
                        setNewTask({ ...newTask, assigned_to: value })
                      }
                      placeholder="Select assignee"
                      allowEmpty
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium">
                      Due Date (optional)
                    </label>
                    <Input
                      type="date"
                      value={newTask.due_date}
                      onChange={(e) =>
                        setNewTask({ ...newTask, due_date: e.target.value })
                      }
                    />
                  </div>
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="text-sm font-medium">Complexity</label>
                    <Select
                      value={newTask.complexity}
                      onValueChange={(value: '' | 'beginner' | 'intermediate' | 'advanced') =>
                        setNewTask({ ...newTask, complexity: value })
                      }
                    >
                      <SelectTrigger>
                        <SelectValue placeholder="Select complexity" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="beginner">Beginner</SelectItem>
                        <SelectItem value="intermediate">Intermediate</SelectItem>
                        <SelectItem value="advanced">Advanced</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div className="flex items-center space-x-2 pt-6">
                    <Checkbox
                      id="learning_friendly"
                      checked={newTask.learning_friendly}
                      onCheckedChange={(checked) =>
                        setNewTask({ ...newTask, learning_friendly: checked === true })
                      }
                    />
                    <label
                      htmlFor="learning_friendly"
                      className="text-sm font-medium cursor-pointer"
                    >
                      Good for learning/onboarding
                    </label>
                  </div>
                </div>
              </div>
              <div className="flex gap-2 mt-6">
                <DialogClose asChild>
                  <Button
                    type="button"
                    variant="outline"
                    className="flex-1"
                  >
                    Cancel
                  </Button>
                </DialogClose>
                <Button
                  className="flex-1"
                  onClick={handleCreateTask}
                  disabled={!newTask.title}
                >
                  Create Task
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        </div>

        {viewMode === 'list' ? (
          <div className="space-y-4">
            {filteredTasks.length === 0 ? (
              <Card>
                <CardContent className="p-12 text-center">
                  <CheckSquare className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">
                    No {taskSource === 'feedback' ? 'feedback' : 'architecture'} tasks found
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {searchQuery
                      ? 'Try adjusting your search or filter'
                      : taskSource === 'feedback'
                        ? 'Feedback tasks are created when submissions are converted to tasks'
                        : 'Get started by creating your first task'}
                  </p>
                  {taskSource === 'architecture' && (
                    <Button onClick={() => setIsCreateDialogOpen(true)}>
                      <Plus className="mr-2 h-4 w-4" />
                      Create Your First Task
                    </Button>
                  )}
                </CardContent>
              </Card>
            ) : (
              filteredTasks.map((task) => {
                const listGlowStyle = isOverdue(task)
                  ? '0 0 8px rgba(239, 68, 68, 0.25)'
                  : task.priority === 'Critical'
                  ? '0 0 8px rgba(147, 51, 234, 0.25)'
                  : '';
                const listHoverStyle = listGlowStyle
                  ? `${listGlowStyle}, 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1)`
                  : '';

                return (
                <Card
                  key={task.id}
                  className={`transition-all ${
                    isOverdue(task)
                      ? 'ring-1 ring-red-300 hover:ring-red-400'
                      : task.priority === 'Critical'
                      ? 'ring-1 ring-purple-300 hover:ring-purple-400'
                      : 'hover:shadow-lg'
                  }`}
                  style={
                    listGlowStyle
                      ? { boxShadow: listGlowStyle }
                      : undefined
                  }
                  onMouseEnter={(e) => {
                    if (listHoverStyle) {
                      e.currentTarget.style.boxShadow = listHoverStyle;
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (listGlowStyle) {
                      e.currentTarget.style.boxShadow = listGlowStyle;
                    }
                  }}
                >
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {task.title}
                          </h3>
                          <Badge className={getPriorityColor(task.priority)}>
                            {task.priority}
                          </Badge>
                          <Badge className={getStatusColor(task.status)}>
                            {task.status}
                          </Badge>
                          {task.category && (
                            <Badge variant="outline" className={getCategoryColor(task.category)}>
                              {task.category}
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-3">
                          {task.description}
                        </p>
                        <div className="flex items-center gap-4 text-sm text-gray-500">
                          {task.assigned_to && (
                            <div className="flex items-center gap-1">
                              <span className="font-medium">Assigned:</span>
                              {task.assigned_to}
                            </div>
                          )}
                          {task.due_date && (
                            <div className={`flex items-center gap-1 ${
                              isOverdue(task) ? 'text-red-600 font-medium' : ''
                            }`}>
                              <Clock className="h-3 w-3" />
                              {new Date(task.due_date).toLocaleDateString()}
                              {isOverdue(task) && <span className="ml-1">(Overdue)</span>}
                            </div>
                          )}
                        </div>
                        <div className="flex gap-2 pt-3">
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
                  </CardContent>
                </Card>
                );
              })
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {(['Pending', 'In-Progress', 'Done', 'Blocked'] as StatusColumn[]).map(
              (status) => {
                const isDropTarget = dragOverColumn === status && draggedTaskId !== null;
                const draggedTask = draggedTaskId ? tasks.find((t) => t.id === draggedTaskId) : null;
                const canDrop = draggedTask && draggedTask.status !== status;

                return (
                  <div
                    key={status}
                    className="flex flex-col"
                    onDragOver={(e) => handleDragOver(e, status)}
                    onDragLeave={handleDragLeave}
                    onDrop={(e) => handleDrop(e, status)}
                  >
                    <Card
                      className={`bg-gray-100 transition-all duration-200 ${
                        isDropTarget && canDrop ? 'ring-2 ring-blue-400 bg-blue-50' : ''
                      }`}
                    >
                      <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-semibold uppercase text-gray-600 flex items-center justify-between">
                          <span>{status}</span>
                          <Badge variant="outline" className="ml-2">
                            {groupedTasks[status].length}
                          </Badge>
                        </CardTitle>
                      </CardHeader>
                    </Card>

                    <div
                      className={`flex-1 space-y-3 min-h-[200px] mt-4 p-3 rounded-lg transition-all duration-200 ${
                        isDropTarget && canDrop
                          ? 'bg-blue-50/70 border-2 border-dashed border-blue-400'
                          : 'border-2 border-transparent'
                      }`}
                    >
                      {isDropTarget && canDrop && (
                        <div
                          className="h-20 border-2 border-dashed border-blue-400 rounded-lg bg-blue-100/50 flex items-center justify-center animate-pulse"
                          style={{ animation: 'pulse 1.5s ease-in-out infinite' }}
                        >
                          <span className="text-blue-500 text-sm font-medium">
                            Drop to move to {status}
                          </span>
                        </div>
                      )}

                      {groupedTasks[status].length === 0 && !isDropTarget ? (
                        <Card className="border-dashed border-2 border-gray-300 bg-gray-50/50">
                          <CardContent className="p-6 text-center">
                            <p className="text-sm text-gray-400 italic">
                              No tasks
                            </p>
                          </CardContent>
                        </Card>
                      ) : (
                        groupedTasks[status].map((task) => (
                          <Card
                            key={task.id}
                            draggable
                            onDragStart={(e) => handleDragStart(e, task.id)}
                            onDragEnd={handleDragEnd}
                            className={`transition-all duration-200 cursor-grab active:cursor-grabbing ${
                              draggedTaskId === task.id
                                ? 'opacity-40 scale-95 rotate-1 shadow-xl'
                                : 'hover:shadow-lg hover:-translate-y-0.5'
                            } ${
                              isOverdue(task)
                                ? 'ring-2 ring-red-400'
                                : task.priority === 'Critical'
                                ? 'ring-2 ring-purple-400'
                                : ''
                            }`}
                            style={
                              isOverdue(task)
                                ? { boxShadow: '0 0 12px rgba(239, 68, 68, 0.4)' }
                                : task.priority === 'Critical'
                                ? { boxShadow: '0 0 12px rgba(147, 51, 234, 0.4)' }
                                : undefined
                            }
                            onClick={() => !draggedTaskId && setSelectedTask(task)}
                          >
                            <CardContent className="p-3 flex flex-col h-full">
                              <div>
                                <h4 className="font-medium text-sm text-gray-900 mb-1">
                                  {task.title}
                                </h4>
                                <div className="flex flex-wrap gap-1 mb-2">
                                  <Badge
                                    className={getPriorityColor(task.priority)}
                                    variant="outline"
                                  >
                                    {(task.priority === 'Critical' || task.priority === 'High') && (
                                      <AlertCircle className="h-3 w-3 mr-1" />
                                    )}
                                    {task.priority}
                                  </Badge>
                                  {task.category && (
                                    <Badge variant="outline" className={`text-xs ${getCategoryColor(task.category)}`}>
                                      {task.category}
                                    </Badge>
                                  )}
                                </div>
                                {task.description && (
                                  <p className="text-xs text-gray-600 line-clamp-3">
                                    {task.description}
                                  </p>
                                )}
                              </div>
                              <div className="mt-auto pt-3">
                                {task.assigned_to && (
                                  <div className="mb-1.5">
                                    <Badge variant="outline" className="text-xs">
                                      {task.assigned_to}
                                    </Badge>
                                  </div>
                                )}
                                {task.due_date && (
                                  <div className={`flex items-center gap-1 text-xs ${
                                    isOverdue(task) ? 'text-red-600 font-medium' : 'text-gray-500'
                                  }`}>
                                    <Clock className="h-3 w-3" />
                                    {new Date(task.due_date).toLocaleDateString()}
                                    {isOverdue(task) && <span className="ml-1">(Overdue)</span>}
                                  </div>
                                )}
                              </div>
                            </CardContent>
                          </Card>
                        ))
                      )}
                    </div>
                  </div>
                );
              }
            )}
          </div>
        )}

        {selectedTask && (
          <Dialog
            open={!!selectedTask}
            onOpenChange={() => {
              setSelectedTask(null);
              setIsEditing(false);
              setEditedTask({});
            }}
          >
            <DialogContent className="sm:max-w-[700px] max-h-[90vh] overflow-y-auto" onCloseClick={() => { setSelectedTask(null); setIsEditing(false); setEditedTask({}); }}>
              <DialogHeader>
                <DialogTitle className="text-2xl">
                  {isEditing ? 'Edit Task' : selectedTask.title}
                </DialogTitle>
                <DialogDescription>
                  {isEditing ? 'Update task details' : 'Task Details and Information'}
                </DialogDescription>
              </DialogHeader>

              <div className="space-y-6 mt-4">
                {!isEditing ? (
                  <>
                    <div className="flex flex-wrap items-center gap-2">
                      <Badge className={getStatusColor(selectedTask.status)}>
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

                    <div className="grid grid-cols-2 gap-4">
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
                  </>
                ) : (
                  <>
                    <div>
                      <label className="text-sm font-medium">Title</label>
                      <Input
                        value={editedTask.title || ''}
                        onChange={(e) =>
                          setEditedTask({ ...editedTask, title: e.target.value })
                        }
                      />
                    </div>

                    <div>
                      <label className="text-sm font-medium">Description</label>
                      <Textarea
                        value={editedTask.description || ''}
                        onChange={(e) =>
                          setEditedTask({ ...editedTask, description: e.target.value })
                        }
                        rows={4}
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium">Status</label>
                        <Select
                          value={editedTask.status || selectedTask.status}
                          onValueChange={(value: StatusColumn) =>
                            setEditedTask({ ...editedTask, status: value })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Pending">Pending</SelectItem>
                            <SelectItem value="In-Progress">In Progress</SelectItem>
                            <SelectItem value="Done">Done</SelectItem>
                            <SelectItem value="Blocked">Blocked</SelectItem>
                            <SelectItem value="Deferred">Deferred</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div>
                        <label className="text-sm font-medium">Priority</label>
                        <Select
                          value={editedTask.priority || selectedTask.priority}
                          onValueChange={(value: 'Critical' | 'High' | 'Medium' | 'Low') =>
                            setEditedTask({ ...editedTask, priority: value })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="Low">Low</SelectItem>
                            <SelectItem value="Medium">Medium</SelectItem>
                            <SelectItem value="High">High</SelectItem>
                            <SelectItem value="Critical">Critical</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Category</label>
                      <Select
                        value={editedTask.category || selectedTask.category}
                        onValueChange={(
                          value: 'Agent' | 'Governance' | 'Technical' | 'Licensing' | 'AI Architect'
                        ) => setEditedTask({ ...editedTask, category: value })}
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
                      {(editedTask.category || selectedTask.category) && (
                        <p className="text-xs text-gray-500 italic bg-gray-50 p-2 rounded mt-2">
                          <span className="font-medium">{editedTask.category || selectedTask.category}:</span> {CATEGORY_DESCRIPTIONS[(editedTask.category || selectedTask.category) as keyof typeof CATEGORY_DESCRIPTIONS]}
                        </p>
                      )}
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="text-sm font-medium">Assigned To</label>
                        <TeamMemberSelect
                          value={editedTask.assigned_to || ''}
                          onValueChange={(value) =>
                            setEditedTask({ ...editedTask, assigned_to: value })
                          }
                          placeholder="Select assignee"
                          allowEmpty
                        />
                      </div>

                      <div>
                        <label className="text-sm font-medium">Due Date</label>
                        <Input
                          type="date"
                          value={editedTask.due_date || ''}
                          onChange={(e) =>
                            setEditedTask({ ...editedTask, due_date: e.target.value })
                          }
                        />
                      </div>
                    </div>

                    <div>
                      <label className="text-sm font-medium">Notes</label>
                      <Textarea
                        value={editedTask.notes || ''}
                        onChange={(e) =>
                          setEditedTask({ ...editedTask, notes: e.target.value })
                        }
                        rows={3}
                        placeholder="Add notes..."
                      />
                    </div>
                  </>
                )}
              </div>

              <div className="flex gap-2 mt-6">
                {!isEditing ? (
                  <>
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={() => setSelectedTask(null)}
                    >
                      Close
                    </Button>
                    <Button
                      variant="destructive"
                      size="icon"
                      onClick={() => setTaskToDelete(selectedTask)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                    <Button className="flex-1" onClick={handleEditClick}>
                      Edit Task
                    </Button>
                  </>
                ) : (
                  <>
                    <Button
                      variant="outline"
                      className="flex-1"
                      onClick={handleCancelEdit}
                    >
                      Cancel
                    </Button>
                    <Button className="flex-1" onClick={handleUpdateTask}>
                      Save Changes
                    </Button>
                  </>
                )}
              </div>
            </DialogContent>
          </Dialog>
        )}

        {/* Delete Confirmation Dialog */}
        {taskToDelete && (
          <Dialog open={!!taskToDelete} onOpenChange={() => setTaskToDelete(null)}>
            <DialogContent className="sm:max-w-[400px]" onCloseClick={() => setTaskToDelete(null)}>
              <DialogHeader>
                <DialogTitle>Delete Task</DialogTitle>
                <DialogDescription>
                  Are you sure you want to delete &quot;{taskToDelete.title}&quot;? This action cannot be undone.
                </DialogDescription>
              </DialogHeader>
              <div className="flex gap-2 mt-6">
                <Button
                  variant="outline"
                  className="flex-1"
                  onClick={() => setTaskToDelete(null)}
                >
                  Cancel
                </Button>
                <Button
                  variant="destructive"
                  className="flex-1"
                  onClick={handleDeleteTask}
                >
                  Delete Task
                </Button>
              </div>
            </DialogContent>
          </Dialog>
        )}
      </div>
    </div>
  );
}
