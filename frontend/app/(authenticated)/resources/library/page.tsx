'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Label } from '@/components/ui/label';
import {
  BookOpen,
  FileText,
  Link as LinkIcon,
  Search,
  Upload,
  X,
  Eye,
  ExternalLink,
  Download,
  Edit,
  Trash2,
  Loader2
} from 'lucide-react';

// Category descriptions
const CATEGORY_DESCRIPTIONS: Record<string, string> = {
  'Agent': 'AI agent frameworks, SDKs, and implementation patterns for building intelligent agents',
  'Governance': 'AI governance frameworks, compliance guidelines, and organizational policies',
  'Technical': 'Technical documentation, platform guides, and implementation resources',
  'Licensing': 'Licensing information, pricing models, and commercial terms',
  'AI Architect': 'Architecture decision guides, solution design patterns, and best practices',
  'Architecture': 'System architecture patterns, reference architectures, and infrastructure designs',
  'Budget': 'Cost management, budget planning, and financial optimization resources',
  'Security': 'Security frameworks, threat modeling, and AI security best practices'
};

interface Resource {
  id: string;
  type: 'PDF' | 'Document' | 'Link' | 'Video' | 'Image';
  title: string;
  description?: string;
  category: string;
  tags: string[];

  // Document fields
  file_type?: string;
  file_size_bytes?: number;
  blob_url?: string;
  thumbnail_url?: string;
  preview_text?: string;
  page_count?: number;

  // Link fields
  url?: string;
  og_title?: string;
  og_description?: string;
  og_image?: string;

  // Metadata
  uploaded_by: string;
  uploaded_at: string;
  last_accessed?: string;
  view_count: number;
}

interface Category {
  name: string;
  count?: number;
}

interface Tag {
  tag: string;
  count: number;
}

export default function ResourceLibraryPage() {
  const [resources, setResources] = useState<Resource[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter state
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // Modal state
  const [previewOpen, setPreviewOpen] = useState(false);
  const [selectedResource, setSelectedResource] = useState<Resource | null>(null);

  // Upload modal state
  const [uploadOpen, setUploadOpen] = useState(false);

  // Upload form state
  const [uploadType, setUploadType] = useState<'file' | 'url'>('url');
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploadUrl, setUploadUrl] = useState('');
  const [uploadTitle, setUploadTitle] = useState('');
  const [uploadDescription, setUploadDescription] = useState('');
  const [uploadCategory, setUploadCategory] = useState('');
  const [uploadTags, setUploadTags] = useState<string[]>([]);
  const [uploadTagInput, setUploadTagInput] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [uploadedBy, setUploadedBy] = useState('');

  // Edit modal state
  const [editOpen, setEditOpen] = useState(false);
  const [editResource, setEditResource] = useState<Resource | null>(null);
  const [editTitle, setEditTitle] = useState('');
  const [editDescription, setEditDescription] = useState('');
  const [editCategory, setEditCategory] = useState('');
  const [editTags, setEditTags] = useState<string[]>([]);
  const [editTagInput, setEditTagInput] = useState('');
  const [editing, setEditing] = useState(false);
  const [editError, setEditError] = useState('');

  // Delete confirmation state
  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleteResource, setDeleteResource] = useState<Resource | null>(null);
  const [deleting, setDeleting] = useState(false);

  useEffect(() => {
    loadResources();
    loadCategories();
    loadTags();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [searchTerm, selectedCategory, selectedTags]);

  async function loadResources() {
    try {
      const response = await fetch('/api/resources/');
      if (response.ok) {
        const data = await response.json();
        setResources(data);
      }
    } catch (error) {
      console.error('Error loading resources:', error);
    } finally {
      setLoading(false);
    }
  }

  async function loadCategories() {
    try {
      const response = await fetch('/api/resources/categories/list');
      if (response.ok) {
        const data = await response.json();
        setCategories(data.categories || []);
      }
    } catch (error) {
      console.error('Error loading categories:', error);
    }
  }

  async function loadTags() {
    try {
      const response = await fetch('/api/resources/tags/list');
      if (response.ok) {
        const data = await response.json();
        setTags(data.tags || []);
      }
    } catch (error) {
      console.error('Error loading tags:', error);
    }
  }

  async function applyFilters() {
    const params = new URLSearchParams();

    if (searchTerm) params.set('search', searchTerm);
    if (selectedCategory !== 'all') params.set('category', selectedCategory);
    if (selectedTags.length > 0) params.set('tags', selectedTags.join(','));

    try {
      const response = await fetch(`/api/resources/?${params}`);
      if (response.ok) {
        const data = await response.json();
        setResources(data);
      }
    } catch (error) {
      console.error('Error filtering resources:', error);
    }
  }

  async function handlePreview(resource: Resource) {
    setSelectedResource(resource);
    setPreviewOpen(true);

    // Increment view count
    try {
      await fetch(`/api/resources/${resource.id}/view`, { method: 'POST' });
    } catch (error) {
      console.error('Error incrementing view count:', error);
    }
  }

  function toggleTag(tag: string) {
    setSelectedTags(prev =>
      prev.includes(tag) ? prev.filter(t => t !== tag) : [...prev, tag]
    );
  }

  function addUploadTag() {
    if (uploadTagInput.trim() && !uploadTags.includes(uploadTagInput.trim())) {
      setUploadTags([...uploadTags, uploadTagInput.trim()]);
      setUploadTagInput('');
    }
  }

  function removeUploadTag(tag: string) {
    setUploadTags(uploadTags.filter(t => t !== tag));
  }

  function resetUploadForm() {
    setUploadType('url');
    setUploadFile(null);
    setUploadUrl('');
    setUploadTitle('');
    setUploadDescription('');
    setUploadCategory('');
    setUploadTags([]);
    setUploadTagInput('');
    setUploadError('');
    setUploadedBy('');
  }

  async function handleUploadSubmit(e: React.FormEvent) {
    e.preventDefault();
    setUploadError('');

    if (!uploadTitle.trim()) {
      setUploadError('Title is required');
      return;
    }

    if (!uploadCategory) {
      setUploadError('Category is required');
      return;
    }

    if (uploadType === 'file' && !uploadFile) {
      setUploadError('Please select a file to upload');
      return;
    }

    if (uploadType === 'url' && !uploadUrl.trim()) {
      setUploadError('URL is required');
      return;
    }

    setUploading(true);

    try {
      const formData = new FormData();

      if (uploadType === 'file' && uploadFile) {
        formData.append('file', uploadFile);
      } else if (uploadType === 'url') {
        formData.append('url', uploadUrl);
      }

      formData.append('title', uploadTitle);
      if (uploadDescription) formData.append('description', uploadDescription);
      formData.append('category', uploadCategory);
      formData.append('tags', JSON.stringify(uploadTags));
      formData.append('uploaded_by', uploadedBy.trim() || 'Anonymous');

      const response = await fetch('/api/resources/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to upload resource');
      }

      await loadResources();
      setUploadOpen(false);
      resetUploadForm();
    } catch (error) {
      console.error('Error uploading resource:', error);
      setUploadError(error instanceof Error ? error.message : 'Failed to upload resource');
    } finally {
      setUploading(false);
    }
  }

  function openEditModal(resource: Resource) {
    setEditResource(resource);
    setEditTitle(resource.title);
    setEditDescription(resource.description || '');
    setEditCategory(resource.category);
    setEditTags([...resource.tags]);
    setEditTagInput('');
    setEditError('');
    setEditOpen(true);
  }

  function addEditTag() {
    if (editTagInput.trim() && !editTags.includes(editTagInput.trim())) {
      setEditTags([...editTags, editTagInput.trim()]);
      setEditTagInput('');
    }
  }

  function removeEditTag(tag: string) {
    setEditTags(editTags.filter(t => t !== tag));
  }

  async function handleEditSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!editResource) return;
    setEditError('');

    if (!editTitle.trim()) {
      setEditError('Title is required');
      return;
    }

    if (!editCategory) {
      setEditError('Category is required');
      return;
    }

    setEditing(true);

    try {
      const formData = new FormData();
      formData.append('title', editTitle);
      formData.append('description', editDescription);
      formData.append('category', editCategory);
      formData.append('tags', JSON.stringify(editTags));

      const response = await fetch(`/api/resources/${editResource.id}`, {
        method: 'PATCH',
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to update resource');
      }

      await loadResources();
      setEditOpen(false);
      setEditResource(null);
    } catch (error) {
      console.error('Error updating resource:', error);
      setEditError(error instanceof Error ? error.message : 'Failed to update resource');
    } finally {
      setEditing(false);
    }
  }

  function openDeleteConfirm(resource: Resource) {
    setDeleteResource(resource);
    setDeleteOpen(true);
  }

  async function handleDeleteConfirm() {
    if (!deleteResource) return;
    setDeleting(true);

    try {
      const response = await fetch(`/api/resources/${deleteResource.id}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete resource');
      }

      await loadResources();
      setDeleteOpen(false);
      setDeleteResource(null);
    } catch (error) {
      console.error('Error deleting resource:', error);
      alert(error instanceof Error ? error.message : 'Failed to delete resource');
    } finally {
      setDeleting(false);
    }
  }

  function getResourceIcon(type: string) {
    switch (type) {
      case 'PDF':
      case 'Document':
        return <FileText className="h-5 w-5" />;
      case 'Link':
        return <LinkIcon className="h-5 w-5" />;
      default:
        return <BookOpen className="h-5 w-5" />;
    }
  }

  function formatFileSize(bytes?: number): string {
    if (!bytes) return '';
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  }

  return (
    <div className="mx-auto max-w-7xl p-8">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Educational Library</h1>
          <p className="mt-1 text-gray-600">
            Curated knowledge repository for the AI Architect Team
          </p>
        </div>
        <Button onClick={() => setUploadOpen(true)} className="flex items-center gap-2">
          <Upload className="h-4 w-4" />
          Add Resource
        </Button>
      </div>

      {/* Search and Filters */}
      <div className="mb-6 space-y-4">
        {/* Search Bar */}
        <div className="relative">
          <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
          <Input
            type="text"
            placeholder="Search resources..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap gap-4 items-start">
          <div className="flex flex-col gap-2">
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger className="w-[200px]">
                <SelectValue placeholder="All Categories" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Categories</SelectItem>
                {categories.map((category) => (
                  <SelectItem key={category} value={category}>
                    {category}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {selectedCategory !== 'all' && (
              <p className="text-sm text-gray-600 italic max-w-md">
                {CATEGORY_DESCRIPTIONS[selectedCategory]}
              </p>
            )}
          </div>

          {/* Selected Tags */}
          {selectedTags.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {selectedTags.map((tag) => (
                <Badge
                  key={tag}
                  variant="secondary"
                  className="cursor-pointer"
                  onClick={() => toggleTag(tag)}
                >
                  {tag}
                  <X className="ml-1 h-3 w-3" />
                </Badge>
              ))}
            </div>
          )}
        </div>

        {/* Popular Tags */}
        <div className="flex flex-wrap gap-2">
          <span className="text-sm font-medium text-gray-700">Popular tags:</span>
          {tags.slice(0, 10).map((tagObj) => (
            <Badge
              key={tagObj.tag}
              variant="outline"
              className="cursor-pointer hover:bg-gray-100"
              onClick={() => toggleTag(tagObj.tag)}
            >
              {tagObj.tag} ({tagObj.count})
            </Badge>
          ))}
        </div>
      </div>

      {/* Resources Grid */}
      {loading ? (
        <div className="text-center py-12">
          <div className="text-gray-600">Loading resources...</div>
        </div>
      ) : resources.length === 0 ? (
        <div className="text-center py-12">
          <BookOpen className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-4 text-lg font-semibold text-gray-900">No resources found</h3>
          <p className="mt-2 text-gray-600">
            {searchTerm || selectedCategory !== 'all' || selectedTags.length > 0
              ? 'Try adjusting your filters'
              : 'Add your first resource to get started'}
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resources.map((resource) => (
            <Card
              key={resource.id}
              className="cursor-pointer hover:shadow-lg transition-shadow h-full flex flex-col"
              onClick={() => handlePreview(resource)}
            >
              <CardContent className="p-4 flex flex-col h-full">
                {/* Thumbnail or Icon */}
                <div className="mb-3 h-48 flex items-center justify-center bg-gray-100 rounded">
                  {resource.thumbnail_url ? (
                    <img
                      src={resource.thumbnail_url}
                      alt={resource.title}
                      className="h-full w-full object-cover rounded"
                    />
                  ) : resource.og_image ? (
                    <img
                      src={resource.og_image}
                      alt={resource.title}
                      className="h-full w-full object-cover rounded"
                    />
                  ) : (
                    <div className="text-gray-400">
                      {getResourceIcon(resource.type)}
                    </div>
                  )}
                </div>

                {/* Title and Description */}
                <div className="mb-3">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900 line-clamp-2 flex-1">
                      {resource.title}
                    </h3>
                    <Badge variant="secondary" className="ml-2 shrink-0">
                      {resource.type}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {resource.description || resource.og_description || resource.preview_text || 'No description'}
                  </p>
                </div>

                {/* Metadata */}
                <div className="text-xs text-gray-500 mb-3">
                  {resource.page_count && (
                    <span>{resource.page_count} pages | </span>
                  )}
                  {resource.file_size_bytes && (
                    <span>{formatFileSize(resource.file_size_bytes)} | </span>
                  )}
                  <span>{resource.view_count} views</span>
                </div>

                {/* Tags */}
                <div className="flex-1">
                  <div className="flex flex-wrap gap-1">
                    {resource.tags.slice(0, 3).map((tag) => (
                      <Badge key={tag} variant="outline" className="text-xs">
                        {tag}
                      </Badge>
                    ))}
                    {resource.tags.length > 3 && (
                      <Badge variant="outline" className="text-xs">
                        +{resource.tags.length - 3}
                      </Badge>
                    )}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex gap-2 pt-2 mt-3 border-t">
                  <Button
                    variant="ghost"
                    size="sm"
                    className="flex-1"
                    onClick={(e) => {
                      e.stopPropagation();
                      openEditModal(resource);
                    }}
                  >
                    <Edit className="h-4 w-4 mr-1" />
                    Edit
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="flex-1 text-red-600 hover:text-red-700 hover:bg-red-50"
                    onClick={(e) => {
                      e.stopPropagation();
                      openDeleteConfirm(resource);
                    }}
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Preview Modal */}
      <Dialog open={previewOpen} onOpenChange={setPreviewOpen}>
        <DialogContent className="max-w-6xl h-[80vh]">
          {selectedResource && (
            <div className="flex flex-col h-full">
              <DialogHeader>
                <DialogTitle className="flex items-center justify-between">
                  <span>{selectedResource.title}</span>
                  <div className="flex gap-2">
                    {selectedResource.url && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(selectedResource.url, '_blank')}
                      >
                        <ExternalLink className="h-4 w-4 mr-2" />
                        Open
                      </Button>
                    )}
                    {selectedResource.blob_url && (
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => window.open(selectedResource.blob_url, '_blank')}
                      >
                        <Download className="h-4 w-4 mr-2" />
                        Download
                      </Button>
                    )}
                  </div>
                </DialogTitle>
              </DialogHeader>

              <div className="flex-1 grid grid-cols-[3fr_2fr] gap-6 mt-4 overflow-hidden">
                {/* Preview Area */}
                <div className="overflow-auto border rounded p-4">
                  {selectedResource.thumbnail_url && (
                    <img
                      src={selectedResource.thumbnail_url}
                      alt={selectedResource.title}
                      className="w-full mb-4"
                    />
                  )}
                  {selectedResource.og_image && !selectedResource.thumbnail_url && (
                    <img
                      src={selectedResource.og_image}
                      alt={selectedResource.title}
                      className="w-full mb-4"
                    />
                  )}
                  {selectedResource.preview_text && (
                    <div className="prose prose-sm max-w-none">
                      <p>{selectedResource.preview_text}</p>
                    </div>
                  )}
                  {selectedResource.og_description && !selectedResource.preview_text && (
                    <div className="prose prose-sm max-w-none">
                      <p>{selectedResource.og_description}</p>
                    </div>
                  )}
                </div>

                {/* Metadata Panel */}
                <div className="overflow-auto border rounded p-4 space-y-4">
                  <div>
                    <h4 className="font-semibold text-sm mb-2">Details</h4>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="font-medium">Type:</span> {selectedResource.type}
                      </div>
                      <div>
                        <span className="font-medium">Category:</span> {selectedResource.category}
                      </div>
                      {selectedResource.page_count && (
                        <div>
                          <span className="font-medium">Pages:</span> {selectedResource.page_count}
                        </div>
                      )}
                      {selectedResource.file_size_bytes && (
                        <div>
                          <span className="font-medium">Size:</span>{' '}
                          {formatFileSize(selectedResource.file_size_bytes)}
                        </div>
                      )}
                      <div>
                        <span className="font-medium">Views:</span> {selectedResource.view_count}
                      </div>
                      <div>
                        <span className="font-medium">Added by:</span> {selectedResource.uploaded_by}
                      </div>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-semibold text-sm mb-2">Tags</h4>
                    <div className="flex flex-wrap gap-1">
                      {selectedResource.tags.map((tag) => (
                        <Badge key={tag} variant="outline" className="text-xs">
                          {tag}
                        </Badge>
                      ))}
                    </div>
                  </div>

                  {selectedResource.description && (
                    <div>
                      <h4 className="font-semibold text-sm mb-2">Description</h4>
                      <p className="text-sm text-gray-600">{selectedResource.description}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>

      {/* Upload Modal */}
      <Dialog open={uploadOpen} onOpenChange={(open) => {
        setUploadOpen(open);
        if (!open) resetUploadForm();
      }}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Add New Resource</DialogTitle>
          </DialogHeader>

          <form onSubmit={handleUploadSubmit} className="space-y-4">
            {/* Upload Type Tabs */}
            <Tabs value={uploadType} onValueChange={(value) => setUploadType(value as 'file' | 'url')}>
              <TabsList className="grid w-full grid-cols-2">
                <TabsTrigger value="url">Web Link</TabsTrigger>
                <TabsTrigger value="file">File Upload</TabsTrigger>
              </TabsList>

              <TabsContent value="url" className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="upload-url">URL *</Label>
                  <Input
                    id="upload-url"
                    type="url"
                    placeholder="https://example.com/resource"
                    value={uploadUrl}
                    onChange={(e) => setUploadUrl(e.target.value)}
                    disabled={uploading}
                    required
                  />
                  <p className="text-xs text-gray-500">
                    Enter a URL to automatically extract metadata and preview
                  </p>
                </div>
              </TabsContent>

              <TabsContent value="file" className="space-y-4 mt-4">
                <div className="space-y-2">
                  <Label htmlFor="upload-file">File *</Label>
                  <Input
                    id="upload-file"
                    type="file"
                    accept=".pdf,.doc,.docx,.txt,.png,.jpg,.jpeg"
                    onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                    disabled={uploading}
                  />
                  <p className="text-xs text-gray-500">
                    Supported: PDF, Word documents, images (max 50MB)
                  </p>
                </div>
              </TabsContent>
            </Tabs>

            {/* Common Fields */}
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="upload-title">Title *</Label>
                <Input
                  id="upload-title"
                  type="text"
                  placeholder="Resource title"
                  value={uploadTitle}
                  onChange={(e) => setUploadTitle(e.target.value)}
                  disabled={uploading}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="upload-description">Description</Label>
                <Input
                  id="upload-description"
                  type="text"
                  placeholder="Brief description of the resource"
                  value={uploadDescription}
                  onChange={(e) => setUploadDescription(e.target.value)}
                  disabled={uploading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="upload-category">Category *</Label>
                <Select value={uploadCategory} onValueChange={setUploadCategory} disabled={uploading} required>
                  <SelectTrigger id="upload-category">
                    <SelectValue placeholder="Select a category" />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map((category) => (
                      <SelectItem key={category} value={category}>
                        {category}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="upload-addedby">Added by</Label>
                <Input
                  id="upload-addedby"
                  type="text"
                  placeholder="Your name (e.g., John Smith)"
                  value={uploadedBy}
                  onChange={(e) => setUploadedBy(e.target.value)}
                  disabled={uploading}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="upload-tags">Tags</Label>
                <div className="flex gap-2">
                  <Input
                    id="upload-tags"
                    type="text"
                    placeholder="Add a tag and press Enter"
                    value={uploadTagInput}
                    onChange={(e) => setUploadTagInput(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        e.preventDefault();
                        addUploadTag();
                      }
                    }}
                    disabled={uploading}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    onClick={addUploadTag}
                    disabled={uploading || !uploadTagInput.trim()}
                  >
                    Add
                  </Button>
                </div>
                {uploadTags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {uploadTags.map((tag) => (
                      <Badge key={tag} variant="secondary" className="cursor-pointer" onClick={() => removeUploadTag(tag)}>
                        {tag}
                        <X className="ml-1 h-3 w-3" />
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Error Message */}
            {uploadError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-600">
                {uploadError}
              </div>
            )}

            {/* Actions */}
            <div className="flex justify-end gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setUploadOpen(false)}
                disabled={uploading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={uploading}>
                {uploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Uploading...
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" />
                    Add Resource
                  </>
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Edit Modal */}
      <Dialog open={editOpen} onOpenChange={(open) => {
        setEditOpen(open);
        if (!open) setEditResource(null);
      }}>
        <DialogContent className="max-w-lg">
          <DialogHeader>
            <DialogTitle>Edit Resource</DialogTitle>
          </DialogHeader>

          <form onSubmit={handleEditSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="edit-title">Title *</Label>
              <Input
                id="edit-title"
                type="text"
                value={editTitle}
                onChange={(e) => setEditTitle(e.target.value)}
                disabled={editing}
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-description">Description</Label>
              <Input
                id="edit-description"
                type="text"
                value={editDescription}
                onChange={(e) => setEditDescription(e.target.value)}
                disabled={editing}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-category">Category *</Label>
              <Select value={editCategory} onValueChange={setEditCategory} disabled={editing}>
                <SelectTrigger id="edit-category">
                  <SelectValue placeholder="Select a category" />
                </SelectTrigger>
                <SelectContent>
                  {categories.map((category) => (
                    <SelectItem key={category} value={category}>
                      {category}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="edit-tags">Tags</Label>
              <div className="flex gap-2">
                <Input
                  id="edit-tags"
                  type="text"
                  placeholder="Add a tag"
                  value={editTagInput}
                  onChange={(e) => setEditTagInput(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') {
                      e.preventDefault();
                      addEditTag();
                    }
                  }}
                  disabled={editing}
                />
                <Button
                  type="button"
                  variant="outline"
                  onClick={addEditTag}
                  disabled={editing || !editTagInput.trim()}
                >
                  Add
                </Button>
              </div>
              {editTags.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {editTags.map((tag) => (
                    <Badge key={tag} variant="secondary" className="cursor-pointer" onClick={() => removeEditTag(tag)}>
                      {tag}
                      <X className="ml-1 h-3 w-3" />
                    </Badge>
                  ))}
                </div>
              )}
            </div>

            {editError && (
              <div className="p-3 bg-red-50 border border-red-200 rounded text-sm text-red-600">
                {editError}
              </div>
            )}

            <div className="flex justify-end gap-2 pt-4">
              <Button
                type="button"
                variant="outline"
                onClick={() => setEditOpen(false)}
                disabled={editing}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={editing}>
                {editing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  'Save Changes'
                )}
              </Button>
            </div>
          </form>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteOpen} onOpenChange={setDeleteOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>Delete Resource</DialogTitle>
          </DialogHeader>

          <div className="py-4">
            <p className="text-gray-600">
              Are you sure you want to delete <strong>{deleteResource?.title}</strong>?
            </p>
            <p className="text-sm text-gray-500 mt-2">
              This action cannot be undone. The resource and any associated files will be permanently removed.
            </p>
          </div>

          <div className="flex justify-end gap-2">
            <Button
              variant="outline"
              onClick={() => setDeleteOpen(false)}
              disabled={deleting}
            >
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleDeleteConfirm}
              disabled={deleting}
            >
              {deleting ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Deleting...
                </>
              ) : (
                <>
                  <Trash2 className="mr-2 h-4 w-4" />
                  Delete
                </>
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
