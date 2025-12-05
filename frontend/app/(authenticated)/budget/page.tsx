'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  Key,
  Calendar,
  RefreshCw,
  Loader2,
} from 'lucide-react';
import { api, BudgetDashboard, ResourceGroupCost, License } from '@/lib/api';

const SERVICE_ICONS: Record<string, string> = {
  'azure openai': '🤖',
  'openai': '🤖',
  'cosmos db': '🗄️',
  'cosmosdb': '🗄️',
  'azure ai search': '🔍',
  'search': '🔍',
  'blob storage': '💾',
  'storage': '💾',
  'app service': '⚙️',
  'container apps': '📦',
  'ai foundry': '🏭',
  'machine learning': '🧠',
  'cognitive services': '🧠',
  'functions': '⚡',
  'default': '☁️',
};

function getServiceIcon(serviceName: string): string {
  const lower = serviceName.toLowerCase();
  for (const [key, icon] of Object.entries(SERVICE_ICONS)) {
    if (lower.includes(key)) return icon;
  }
  return SERVICE_ICONS.default;
}

function getStatusBadge(spent: number, budget: number) {
  const percentage = budget > 0 ? (spent / budget) * 100 : 0;
  if (percentage >= 90) return { text: 'Critical', color: 'bg-red-100 text-red-800' };
  if (percentage >= 75) return { text: 'Warning', color: 'bg-orange-100 text-orange-800' };
  return { text: 'On Track', color: 'bg-green-100 text-green-800' };
}

function getStatusColor(spent: number, budget: number) {
  const percentage = budget > 0 ? (spent / budget) * 100 : 0;
  if (percentage >= 90) return 'text-red-600';
  if (percentage >= 75) return 'text-orange-600';
  return 'text-green-600';
}

export default function BudgetPage() {
  const [timePeriod, setTimePeriod] = useState('month');
  const [dashboardData, setDashboardData] = useState<BudgetDashboard | null>(null);
  const [resourceGroupCosts, setResourceGroupCosts] = useState<ResourceGroupCost[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchData = async (forceRefresh = false) => {
    try {
      if (forceRefresh) {
        setIsRefreshing(true);
      } else {
        setIsLoading(true);
      }
      setError(null);

      const [dashboard, rgCosts] = await Promise.all([
        api.budget.getDashboard(),
        api.budget.getResourceGroupCosts(forceRefresh),
      ]);

      setDashboardData(dashboard);
      setResourceGroupCosts(rgCosts);
    } catch (err) {
      console.error('Error fetching budget data:', err);
      setError(err instanceof Error ? err.message : 'Failed to load budget data');
    } finally {
      setIsLoading(false);
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <Loader2 className="h-8 w-8 animate-spin text-blue-600 mx-auto mb-4" />
          <p className="text-gray-600">Loading budget data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertTriangle className="h-8 w-8 text-red-600 mx-auto mb-4" />
          <p className="text-red-600 mb-4">{error}</p>
          <Button onClick={() => fetchData()}>Retry</Button>
        </div>
      </div>
    );
  }

  const azureCosts = dashboardData?.azure_costs;
  const licenses = dashboardData?.licenses || [];
  const totals = dashboardData?.totals;

  const totalAzureSpend = azureCosts?.total_cost || 0;
  const totalLicenseSpend = licenses.reduce((sum, lic) => sum + (lic.monthly_cost || 0), 0);
  const totalMonthlySpend = totalAzureSpend + totalLicenseSpend;

  const allServices = resourceGroupCosts.flatMap(rg =>
    rg.services.map(s => ({
      ...s,
      resource_group: rg.resource_group,
    }))
  );

  const serviceAggregates = allServices.reduce((acc, service) => {
    const name = service.name;
    if (!acc[name]) {
      acc[name] = { name, cost: 0, count: 0 };
    }
    acc[name].cost += service.cost;
    acc[name].count += 1;
    return acc;
  }, {} as Record<string, { name: string; cost: number; count: number }>);

  const topServices = Object.values(serviceAggregates)
    .sort((a, b) => b.cost - a.cost)
    .slice(0, 10);

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Budget & Licensing</h1>
            <p className="mt-2 text-gray-600">
              Track Azure spending across {resourceGroupCosts.length} resource groups
            </p>
          </div>
          <div className="flex items-center gap-4">
            <Button
              variant="outline"
              size="sm"
              onClick={() => fetchData(true)}
              disabled={isRefreshing}
            >
              {isRefreshing ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : (
                <RefreshCw className="h-4 w-4 mr-2" />
              )}
              Refresh
            </Button>
            <Select value={timePeriod} onValueChange={setTimePeriod}>
              <SelectTrigger className="w-[180px]">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="week">This Week</SelectItem>
                <SelectItem value="month">This Month</SelectItem>
                <SelectItem value="quarter">This Quarter</SelectItem>
                <SelectItem value="year">This Year</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Azure Spend</p>
                  <p className="mt-2 text-2xl font-bold text-gray-900">
                    ${totalAzureSpend.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </p>
                </div>
                <div className="rounded-lg p-3 bg-blue-50">
                  <DollarSign className="h-6 w-6 text-blue-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">License Costs</p>
                  <p className="mt-2 text-2xl font-bold text-gray-900">
                    ${totalLicenseSpend.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </p>
                </div>
                <div className="rounded-lg p-3 bg-purple-50">
                  <Key className="h-6 w-6 text-purple-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Total Monthly</p>
                  <p className="mt-2 text-2xl font-bold text-gray-900">
                    ${totalMonthlySpend.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </p>
                </div>
                <div className="rounded-lg p-3 bg-green-50">
                  <TrendingUp className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Resource Groups</p>
                  <p className="mt-2 text-2xl font-bold text-gray-900">
                    {resourceGroupCosts.length}
                  </p>
                </div>
                <div className="rounded-lg p-3 bg-orange-50">
                  <CheckCircle className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <Card>
            <CardHeader>
              <CardTitle>Cost by Resource Group</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {resourceGroupCosts
                  .sort((a, b) => b.total_cost - a.total_cost)
                  .map((rg) => {
                    const maxCost = Math.max(...resourceGroupCosts.map(r => r.total_cost), 1);
                    const percentage = (rg.total_cost / maxCost) * 100;

                    return (
                      <div key={rg.resource_group} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium truncate max-w-[200px]">
                            {rg.resource_group}
                          </span>
                          <span className="text-sm font-semibold">
                            ${rg.total_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </span>
                        </div>
                        <Progress value={percentage} className="h-2" />
                      </div>
                    );
                  })}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Top Services by Cost</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topServices.map((service) => {
                  const maxCost = Math.max(...topServices.map(s => s.cost), 1);
                  const percentage = (service.cost / maxCost) * 100;

                  return (
                    <div key={service.name} className="space-y-2">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getServiceIcon(service.name)}</span>
                          <span className="text-sm font-medium truncate max-w-[180px]">
                            {service.name}
                          </span>
                        </div>
                        <span className="text-sm font-semibold">
                          ${service.cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                        </span>
                      </div>
                      <Progress value={percentage} className="h-2" />
                    </div>
                  );
                })}
                {topServices.length === 0 && (
                  <p className="text-gray-500 text-sm text-center py-4">
                    No service cost data available
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-5 w-5" />
              License Management
            </CardTitle>
          </CardHeader>
          <CardContent>
            {licenses.length > 0 ? (
              <div className="space-y-4">
                {licenses.map((license) => (
                  <div
                    key={license.id}
                    className="flex items-start justify-between p-4 border rounded-lg hover:shadow-md transition-shadow"
                  >
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-sm">{license.name}</h4>
                        <Badge
                          variant={license.status === 'Active' ? 'default' : 'secondary'}
                          className="text-xs"
                        >
                          {license.status}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-gray-600">
                        <span>{license.vendor}</span>
                        <span>{license.license_type}</span>
                        {license.seats && <span>{license.seats} seats</span>}
                        {license.renewal_date && (
                          <span className="flex items-center gap-1">
                            <Calendar className="h-3 w-3" />
                            Renewal: {new Date(license.renewal_date).toLocaleDateString()}
                          </span>
                        )}
                      </div>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-semibold text-gray-900">
                        ${license.monthly_cost.toLocaleString()}/mo
                      </p>
                      {license.cost_per_seat && license.seats && (
                        <p className="text-xs text-gray-500">
                          ${license.cost_per_seat}/seat
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Key className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No licenses tracked yet</p>
                <p className="text-sm text-gray-400 mt-1">
                  Add software licenses to track costs
                </p>
              </div>
            )}

            {licenses.length > 0 && (
              <div className="mt-6 pt-6 border-t">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-gray-900">Total License Costs</p>
                  <p className="text-lg font-bold text-gray-900">
                    ${totalLicenseSpend.toLocaleString()}/month
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {azureCosts && (
          <div className="mt-4 text-xs text-gray-500 text-center">
            Data from {azureCosts.period_start?.split('T')[0]} to {azureCosts.period_end?.split('T')[0]}
          </div>
        )}
      </div>
    </div>
  );
}
