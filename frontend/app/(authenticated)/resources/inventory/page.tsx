'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Input } from '@/components/ui/input';
import {
  Cloud,
  Server,
  Database,
  RefreshCw,
  Filter,
  Search,
  ExternalLink,
  TrendingUp,
  MapPin,
  Tag,
} from 'lucide-react';

interface AzureResource {
  id: string;
  name: string;
  type: string;
  location: string;
  resource_group: string;
  tags: Record<string, string>;
  properties?: Record<string, any>;
  current_month_cost?: number;
  status?: string;
}

interface ResourceSummary {
  total_resources: number;
  running_services: number;
  regions: number;
  resource_groups: number;
  total_cost?: number;
}

export default function AzureInventoryPage() {
  const [resources, setResources] = useState<AzureResource[]>([]);
  const [summary, setSummary] = useState<ResourceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [regionFilter, setRegionFilter] = useState<string>('all');

  useEffect(() => {
    loadResources();
    loadSummary();
  }, []);

  async function loadResources() {
    try {
      setLoading(true);
      const response = await fetch('/api/azure/resources');
      if (response.ok) {
        const data = await response.json();
        setResources(data);
      }
    } catch (error) {
      console.error('Failed to load resources:', error);
    } finally {
      setLoading(false);
    }
  }

  async function loadSummary() {
    try {
      const response = await fetch('/api/azure/resources/summary');
      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (error) {
      console.error('Failed to load summary:', error);
    }
  }

  async function handleRefresh() {
    try {
      setRefreshing(true);
      const response = await fetch('/api/azure/resources/refresh', { method: 'POST' });
      if (response.ok) {
        await loadResources();
        await loadSummary();
      }
    } catch (error) {
      console.error('Failed to refresh:', error);
    } finally {
      setRefreshing(false);
    }
  }

  // Extract unique types and regions for filters
  const uniqueTypes = Array.from(new Set(resources.map((r) => r.type))).sort();
  const uniqueRegions = Array.from(new Set(resources.map((r) => r.location))).sort();

  // Filter resources
  const filteredResources = resources.filter((resource) => {
    const matchesSearch =
      searchTerm === '' ||
      resource.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      resource.type.toLowerCase().includes(searchTerm.toLowerCase());

    const matchesType = typeFilter === 'all' || resource.type === typeFilter;
    const matchesRegion = regionFilter === 'all' || resource.location === regionFilter;

    return matchesSearch && matchesType && matchesRegion;
  });

  // Get resource type icon
  function getResourceIcon(type: string): string {
    if (type.includes('Microsoft.Compute')) return '💻';
    if (type.includes('Microsoft.Storage')) return '💾';
    if (type.includes('Microsoft.Web')) return '🌐';
    if (type.includes('Microsoft.CognitiveServices') || type.includes('Microsoft.AI')) return '🤖';
    if (type.includes('Microsoft.Search')) return '🔍';
    if (type.includes('Microsoft.DocumentDB') || type.includes('Cosmos')) return '🗄️';
    if (type.includes('Microsoft.Network')) return '🔌';
    if (type.includes('Microsoft.KeyVault')) return '🔐';
    return '☁️';
  }

  // Simplify resource type for display
  function simplifyType(type: string): string {
    const parts = type.split('/');
    return parts[parts.length - 1] || type;
  }

  if (loading) {
    return (
      <div className="flex h-screen items-center justify-center">
        <div className="text-center">
          <RefreshCw className="mx-auto h-8 w-8 animate-spin text-blue-600" />
          <p className="mt-2 text-gray-600">Loading Azure resources...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="mx-auto max-w-7xl">
        {/* Header */}
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Azure Cloud Inventory</h1>
            <p className="mt-1 text-gray-600">Real-time infrastructure tracking</p>
          </div>
          <Button
            onClick={handleRefresh}
            disabled={refreshing}
            className="flex items-center gap-2"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Refresh
          </Button>
        </div>

        {/* Summary Cards */}
        {summary && (
          <div className="mb-8 grid grid-cols-1 gap-6 md:grid-cols-4">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Resources</CardTitle>
                <Cloud className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{summary.total_resources}</div>
                <p className="text-xs text-gray-600">Across all resource groups</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Running Services</CardTitle>
                <Server className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{summary.running_services}</div>
                <p className="text-xs text-gray-600">Active compute & apps</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Regions</CardTitle>
                <MapPin className="h-4 w-4 text-purple-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{summary.regions}</div>
                <p className="text-xs text-gray-600">Geographic locations</p>
              </CardContent>
            </Card>

            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Resource Groups</CardTitle>
                <Database className="h-4 w-4 text-orange-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{summary.resource_groups}</div>
                <p className="text-xs text-gray-600">Logical containers</p>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Filters */}
        <Card className="mb-6">
          <CardContent className="pt-6">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-gray-400" />
                <Input
                  placeholder="Search resources..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>

              {/* Type Filter */}
              <Select value={typeFilter} onValueChange={setTypeFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Filter by type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Types</SelectItem>
                  {uniqueTypes.map((type) => (
                    <SelectItem key={type} value={type}>
                      {simplifyType(type)}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>

              {/* Region Filter */}
              <Select value={regionFilter} onValueChange={setRegionFilter}>
                <SelectTrigger>
                  <SelectValue placeholder="Filter by region" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Regions</SelectItem>
                  {uniqueRegions.map((region) => (
                    <SelectItem key={region} value={region}>
                      {region}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </CardContent>
        </Card>

        {/* Resources Grid */}
        {filteredResources.length === 0 ? (
          <Card>
            <CardContent className="py-12 text-center">
              <Cloud className="mx-auto h-12 w-12 text-gray-400" />
              <p className="mt-4 text-gray-600">
                {resources.length === 0
                  ? 'No Azure resources found. Check your subscription configuration.'
                  : 'No resources match your filters.'}
              </p>
            </CardContent>
          </Card>
        ) : (
          <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
            {filteredResources.map((resource) => (
              <Card key={resource.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <div className="flex items-start justify-between">
                    <div className="flex items-center gap-2">
                      <span className="text-2xl">{getResourceIcon(resource.type)}</span>
                      <div>
                        <CardTitle className="text-sm font-semibold">{resource.name}</CardTitle>
                        <p className="text-xs text-gray-500">{simplifyType(resource.type)}</p>
                      </div>
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {/* Location */}
                    <div className="flex items-center justify-between text-sm">
                      <span className="flex items-center gap-1 text-gray-600">
                        <MapPin className="h-3 w-3" />
                        Location
                      </span>
                      <Badge variant="outline">{resource.location}</Badge>
                    </div>

                    {/* Resource Group */}
                    <div className="flex items-center justify-between text-sm">
                      <span className="text-gray-600">Resource Group</span>
                      <span className="text-xs font-mono text-gray-800">
                        {resource.resource_group}
                      </span>
                    </div>

                    {/* Cost */}
                    {resource.current_month_cost !== undefined && (
                      <div className="flex items-center justify-between text-sm">
                        <span className="flex items-center gap-1 text-gray-600">
                          <TrendingUp className="h-3 w-3" />
                          Cost (Month)
                        </span>
                        <span className="font-semibold text-green-600">
                          ${resource.current_month_cost.toFixed(2)}
                        </span>
                      </div>
                    )}

                    {/* Tags */}
                    {Object.keys(resource.tags).length > 0 && (
                      <div className="border-t pt-3">
                        <p className="mb-2 flex items-center gap-1 text-xs text-gray-600">
                          <Tag className="h-3 w-3" />
                          Tags
                        </p>
                        <div className="flex flex-wrap gap-1">
                          {Object.entries(resource.tags)
                            .slice(0, 3)
                            .map(([key, value]) => (
                              <Badge key={key} variant="secondary" className="text-xs">
                                {key}: {value}
                              </Badge>
                            ))}
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <Button
                      variant="outline"
                      size="sm"
                      className="w-full mt-2"
                      onClick={() =>
                        window.open(
                          `https://portal.azure.com/#resource${resource.id}`,
                          '_blank'
                        )
                      }
                    >
                      <ExternalLink className="mr-2 h-3 w-3" />
                      View in Portal
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
