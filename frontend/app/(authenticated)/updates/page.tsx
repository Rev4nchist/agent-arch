'use client';

import { useState, useEffect } from 'react';
import { api, FeatureUpdate, FeatureUpdateCategory, FeatureUpdateCreate, FeatureUpdateUpdate } from '@/lib/api';
import { useAuth } from '@/components/providers/AuthProvider';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
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
import {
  Newspaper,
  Sparkles,
  TrendingUp,
  Bug,
  Megaphone,
  Plus,
  Pencil,
  Trash2,
  Calendar,
  ExternalLink,
} from 'lucide-react';
import Link from 'next/link';

const categoryConfig: Record<FeatureUpdateCategory, { icon: typeof Sparkles; bg: string; text: string }> = {
  'New Feature': { icon: Sparkles, bg: 'bg-green-100', text: 'text-green-700' },
  'Improvement': { icon: TrendingUp, bg: 'bg-blue-100', text: 'text-blue-700' },
  'Bug Fix': { icon: Bug, bg: 'bg-orange-100', text: 'text-orange-700' },
  'Announcement': { icon: Megaphone, bg: 'bg-purple-100', text: 'text-purple-700' },
};

const pageNames: Record<string, string> = {
  '/': 'Dashboard',
  '/decisions': 'Proposals & Decisions',
  '/meetings': 'Meetings Hub',
  '/tasks': 'Tasks',
  '/agents': 'Agents',
  '/governance': 'Governance',
  '/budget': 'Budget & Licensing',
  '/resources': 'Resources Library',
  '/tech-radar': 'Tech Radar',
  '/architecture': 'Architecture Lab',
  '/feedback': 'Feedback Hub',
  '/audit': 'Audit Trail',
  '/guide': 'Fourth AI Guide',
  '/memories': 'User Memories',
};

const availablePages = Object.entries(pageNames).map(([href, name]) => ({ href, name }));
const categories: FeatureUpdateCategory[] = ['New Feature', 'Improvement', 'Bug Fix', 'Announcement'];

function isNew(publishedAt: string): boolean {
  const publishDate = new Date(publishedAt);
  const sevenDaysAgo = new Date();
  sevenDaysAgo.setDate(sevenDaysAgo.getDate() - 7);
  return publishDate > sevenDaysAgo;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

export default function FeatureUpdatesPage() {
  const { userRole, user } = useAuth();
  const isAdmin = userRole === 'admin';

  const [updates, setUpdates] = useState<FeatureUpdate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<FeatureUpdateCategory | 'all'>('all');

  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingUpdate, setEditingUpdate] = useState<FeatureUpdate | null>(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'New Feature' as FeatureUpdateCategory,
    version: '',
    related_pages: [] as string[],
  });
  const [submitting, setSubmitting] = useState(false);

  const loadUpdates = async () => {
    try {
      setLoading(true);
      const params = selectedCategory !== 'all' ? { category: selectedCategory } : undefined;
      const response = await api.featureUpdates.list(params);
      setUpdates(response.items);
      setError(null);
    } catch (err) {
      setError('Failed to load feature updates');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadUpdates();
  }, [selectedCategory]);

  const openCreateDialog = () => {
    setEditingUpdate(null);
    setFormData({ title: '', description: '', category: 'New Feature', version: '', related_pages: [] });
    setDialogOpen(true);
  };

  const openEditDialog = (update: FeatureUpdate) => {
    setEditingUpdate(update);
    setFormData({
      title: update.title,
      description: update.description,
      category: update.category,
      version: update.version || '',
      related_pages: update.related_pages,
    });
    setDialogOpen(true);
  };

  const handleSubmit = async () => {
    if (!formData.title.trim() || !formData.description.trim()) return;
    setSubmitting(true);
    try {
      if (editingUpdate) {
        const updateData: FeatureUpdateUpdate = {
          title: formData.title,
          description: formData.description,
          category: formData.category,
          version: formData.version || undefined,
          related_pages: formData.related_pages,
        };
        await api.featureUpdates.update(editingUpdate.id, updateData);
      } else {
        const createData: FeatureUpdateCreate = {
          title: formData.title,
          description: formData.description,
          category: formData.category,
          version: formData.version || undefined,
          related_pages: formData.related_pages,
          created_by: user?.name || user?.username || 'Admin',
        };
        await api.featureUpdates.create(createData);
      }
      setDialogOpen(false);
      loadUpdates();
    } catch (err) {
      console.error('Failed to save update:', err);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Are you sure you want to delete this update?')) return;
    try {
      await api.featureUpdates.delete(id);
      loadUpdates();
    } catch (err) {
      console.error('Failed to delete update:', err);
    }
  };

  const toggleRelatedPage = (href: string) => {
    setFormData(prev => ({
      ...prev,
      related_pages: prev.related_pages.includes(href)
        ? prev.related_pages.filter(p => p !== href)
        : [...prev.related_pages, href],
    }));
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <Newspaper className="h-8 w-8 text-blue-600" />
            <div>
              <h1 className="text-2xl font-semibold text-gray-900">What&apos;s New</h1>
              <p className="text-sm text-gray-500">Stay up to date with the latest platform improvements</p>
            </div>
          </div>
          {isAdmin && (
            <Button onClick={openCreateDialog} className="bg-blue-600 hover:bg-blue-700">
              <Plus className="h-4 w-4 mr-2" />
              Add Update
            </Button>
          )}
        </div>

        <div className="flex gap-2 mb-6 flex-wrap">
          <Button
            variant={selectedCategory === 'all' ? 'default' : 'outline'}
            size="sm"
            onClick={() => setSelectedCategory('all')}
          >
            All
          </Button>
          {categories.map(cat => {
            const config = categoryConfig[cat];
            const Icon = config.icon;
            return (
              <Button
                key={cat}
                variant={selectedCategory === cat ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedCategory(cat)}
                className="flex items-center gap-1"
              >
                <Icon className="h-3 w-3" />
                {cat}
              </Button>
            );
          })}
        </div>

        {loading ? (
          <div className="text-center py-12 text-gray-500">Loading updates...</div>
        ) : error ? (
          <div className="text-center py-12 text-red-500">{error}</div>
        ) : updates.length === 0 ? (
          <Card className="text-center py-12">
            <CardContent>
              <Newspaper className="h-12 w-12 text-gray-300 mx-auto mb-4" />
              <p className="text-gray-500">No updates yet</p>
              {isAdmin && (
                <Button variant="link" onClick={openCreateDialog} className="mt-2">
                  Add the first update
                </Button>
              )}
            </CardContent>
          </Card>
        ) : (
          <div className="space-y-4">
            {updates.map(update => {
              const config = categoryConfig[update.category];
              const Icon = config.icon;
              const showNewBadge = isNew(update.published_at);

              return (
                <Card key={update.id} className="bg-white border border-gray-200 hover:shadow-md transition-shadow">
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2 flex-wrap">
                          {showNewBadge && (
                            <Badge className="bg-yellow-100 text-yellow-800 text-xs font-semibold">
                              NEW
                            </Badge>
                          )}
                          <Badge className={config.bg + ' ' + config.text + ' flex items-center gap-1'}>
                            <Icon className="h-3 w-3" />
                            {update.category}
                          </Badge>
                          {update.version && (
                            <Badge variant="outline" className="text-gray-600">
                              {update.version}
                            </Badge>
                          )}
                        </div>

                        <h3 className="text-lg font-semibold text-gray-900 mb-2">{update.title}</h3>
                        <p className="text-gray-600 mb-4 whitespace-pre-wrap">{update.description}</p>

                        {update.related_pages.length > 0 && (
                          <div className="flex items-center gap-2 mb-3 flex-wrap">
                            <span className="text-sm text-gray-500">Related:</span>
                            {update.related_pages.map(page => (
                              <Link
                                key={page}
                                href={page}
                                className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
                              >
                                {pageNames[page] || page}
                                <ExternalLink className="h-3 w-3" />
                              </Link>
                            ))}
                          </div>
                        )}

                        <div className="flex items-center gap-1 text-sm text-gray-400">
                          <Calendar className="h-3 w-3" />
                          {formatDate(update.published_at)}
                        </div>
                      </div>

                      {isAdmin && (
                        <div className="flex gap-1">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => openEditDialog(update)}
                            className="text-gray-500 hover:text-blue-600"
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleDelete(update.id)}
                            className="text-gray-500 hover:text-red-600"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                  </CardContent>
                </Card>
              );
            })}
          </div>
        )}

        <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
          <DialogContent className="max-w-lg">
            <DialogHeader>
              <DialogTitle>{editingUpdate ? 'Edit Update' : 'Add New Update'}</DialogTitle>
            </DialogHeader>

            <div className="space-y-4 mt-4">
              <div>
                <Label htmlFor="title">Title *</Label>
                <Input
                  id="title"
                  value={formData.title}
                  onChange={e => setFormData(prev => ({ ...prev, title: e.target.value }))}
                  placeholder="What's the headline?"
                  maxLength={200}
                />
              </div>

              <div>
                <Label htmlFor="description">Description *</Label>
                <Textarea
                  id="description"
                  value={formData.description}
                  onChange={e => setFormData(prev => ({ ...prev, description: e.target.value }))}
                  placeholder="Describe this update in a user-friendly way..."
                  rows={4}
                  maxLength={2000}
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="category">Category *</Label>
                  <Select
                    value={formData.category}
                    onValueChange={(value: FeatureUpdateCategory) =>
                      setFormData(prev => ({ ...prev, category: value }))
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      {categories.map(cat => (
                        <SelectItem key={cat} value={cat}>{cat}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor="version">Version</Label>
                  <Input
                    id="version"
                    value={formData.version}
                    onChange={e => setFormData(prev => ({ ...prev, version: e.target.value }))}
                    placeholder="e.g., v1.2 or December 2024"
                  />
                </div>
              </div>

              <div>
                <Label>Related Pages</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {availablePages.map(({ href, name }) => (
                    <Badge
                      key={href}
                      variant={formData.related_pages.includes(href) ? 'default' : 'outline'}
                      className="cursor-pointer"
                      onClick={() => toggleRelatedPage(href)}
                    >
                      {name}
                    </Badge>
                  ))}
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline" onClick={() => setDialogOpen(false)}>
                  Cancel
                </Button>
                <Button
                  onClick={handleSubmit}
                  disabled={submitting || !formData.title.trim() || !formData.description.trim()}
                  className="bg-blue-600 hover:bg-blue-700"
                >
                  {submitting ? 'Saving...' : editingUpdate ? 'Save Changes' : 'Create Update'}
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
