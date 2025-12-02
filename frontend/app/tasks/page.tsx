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

  const filteredTasks = tasks.filter((task) => {
    const matchesSearch =
      task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.description?.toLowerCase().includes(searchQuery.toLowerCase());

    const matchesPriority =
      filterPriority === 'all' || task.priority === filterPriority;

    const matchesCategory =
      filterCategory === 'all' || task.category === filterCategory;

    const matchesAssignee =
      filterAssignee === 'all' || task.assigned_to === filterAssignee;

    return matchesSearch && matchesPriority && matchesCategory && matchesAssignee;
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
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'move';
  };

  const handleDrop = async (e: React.DragEvent, newStatus: StatusColumn) => {
    e.preventDefault();
    if (!draggedTaskId) return;

    const task = tasks.find((t) => t.id === draggedTaskId);
    if (!task || task.status === newStatus) {
      setDraggedTaskId(null);
      return;
    }

    try {
      const updatedTask = { ...task, status: newStatus };
      await api.tasks.update(task.id, updatedTask);
      setDraggedTaskId(null);
      setTimeout(() => loadTasks(), 100);
    } catch (error) {
      console.error('Failed to update task status:', error);
      setDraggedTaskId(null);
    }
  };

  const handleDragEnd = () => {
    setDraggedTaskId(null);
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
                    No tasks found
                  </h3>
                  <p className="text-gray-600 mb-4">
                    {searchQuery
                      ? 'Try adjusting your search or filter'
                      : 'Get started by creating your first task'}
                  </p>
                  <Button onClick={() => setIsCreateDialogOpen(true)}>
                    <Plus className="mr-2 h-4 w-4" />
                    Create Your First Task
                  </Button>
                </CardContent>
              </Card>
            ) : (
              filteredTasks.map((task) => (
                <Card
                  key={task.id}
                  className="hover:shadow-lg transition-shadow"
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
                            <div className="flex items-center gap-1">
                              <Clock className="h-3 w-3" />
                              {new Date(task.due_date).toLocaleDateString()}
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
              ))
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {(['Pending', 'In-Progress', 'Done', 'Blocked'] as StatusColumn[]).map(
              (status) => (
                <div
                  key={status}
                  className="space-y-4"
                  onDragOver={handleDragOver}
                  onDrop={(e) => handleDrop(e, status)}
                >
                  <Card className="bg-gray-100">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-sm font-semibold uppercase text-gray-600 flex items-center justify-between">
                        <span>{status}</span>
                        <Badge variant="outline" className="ml-2">
                          {groupedTasks[status].length}
                        </Badge>
                      </CardTitle>
                    </CardHeader>
                  </Card>

                  <div className="space-y-3 min-h-[100px]">
                    {groupedTasks[status].length === 0 ? (
                      <Card className="border-dashed border-2 border-gray-300">
                        <CardContent className="p-6 text-center">
                          <p className="text-sm text-gray-500 italic">
                            Drop tasks here
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
                          className={`hover:shadow-lg transition-all cursor-grab active:cursor-grabbing ${
                            draggedTaskId === task.id ? 'opacity-50 scale-95' : ''
                          } ${
                            isOverdue(task)
                              ? 'ring-2 ring-red-400 shadow-[0_0_10px_rgba(239,68,68,0.3)]'
                              : ''
                          }`}
                          onClick={() => setSelectedTask(task)}
                        >
                          <CardContent className="p-4">
                            <div className="flex items-start justify-between mb-2">
                              <h4 className="font-medium text-sm text-gray-900">
                                {task.title}
                              </h4>
                              <Badge
                                className={getPriorityColor(task.priority)}
                                variant="outline"
                              >
                                {(task.priority === 'Critical' || task.priority === 'High') && (
                                  <AlertCircle className="h-3 w-3 mr-1" />
                                )}
                                {task.priority}
                              </Badge>
                            </div>
                            <p className="text-xs text-gray-600 mb-3 line-clamp-2">
                              {task.description}
                            </p>
                            <div className="flex flex-wrap gap-1 mb-2">
                              {task.category && (
                                <Badge variant="outline" className={`text-xs ${getCategoryColor(task.category)}`}>
                                  {task.category}
                                </Badge>
                              )}
                              {task.assigned_to && (
                                <Badge variant="outline" className="text-xs">
                                  {task.assigned_to}
                                </Badge>
                              )}
                            </div>
                            {task.due_date && (
                              <div className={`flex items-center gap-1 mt-2 text-xs ${
                                isOverdue(task) ? 'text-red-600 font-medium' : 'text-gray-500'
                              }`}>
                                <Clock className="h-3 w-3" />
                                {new Date(task.due_date).toLocaleDateString()}
                                {isOverdue(task) && <span className="ml-1">(Overdue)</span>}
                              </div>
                            )}
                          </CardContent>
                        </Card>
                      ))
                    )}
                  </div>
                </div>
              )
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
