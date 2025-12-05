'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog';
import {
  DollarSign,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  Key,
  Calendar,
  RefreshCw,
  Loader2,
  Plus,
  Pencil,
  Trash2,
  X,
} from 'lucide-react';
import { api, BudgetDashboard, ResourceGroupCost, License, LicenseCreate } from '@/lib/api';

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

const LICENSE_PRESETS = [
  { name: 'GitHub Copilot Business', vendor: 'GitHub', type: 'Subscription', costPerSeat: 19 },
  { name: 'GitHub Copilot Enterprise', vendor: 'GitHub', type: 'Subscription', costPerSeat: 39 },
  { name: 'ChatGPT Plus', vendor: 'OpenAI', type: 'Subscription', costPerSeat: 20 },
  { name: 'ChatGPT Team', vendor: 'OpenAI', type: 'Subscription', costPerSeat: 25 },
  { name: 'ChatGPT Enterprise', vendor: 'OpenAI', type: 'Enterprise', costPerSeat: 0 },
  { name: 'Claude Pro', vendor: 'Anthropic', type: 'Subscription', costPerSeat: 20 },
  { name: 'Claude Team', vendor: 'Anthropic', type: 'Subscription', costPerSeat: 25 },
  { name: 'Claude Enterprise', vendor: 'Anthropic', type: 'Enterprise', costPerSeat: 0 },
  { name: 'M365 Copilot', vendor: 'Microsoft', type: 'Subscription', costPerSeat: 30 },
  { name: 'Custom License', vendor: '', type: 'Subscription', costPerSeat: 0 },
];

function getServiceIcon(serviceName: string): string {
  const lower = serviceName.toLowerCase();
  for (const [key, icon] of Object.entries(SERVICE_ICONS)) {
    if (lower.includes(key)) return icon;
  }
  return SERVICE_ICONS.default;
}

function getLicenseIcon(vendor: string): string {
  const v = vendor.toLowerCase();
  if (v.includes('github')) return '🐙';
  if (v.includes('openai')) return '🤖';
  if (v.includes('anthropic')) return '🧠';
  if (v.includes('microsoft')) return '🪟';
  return '📄';
}

export default function BudgetPage() {
  const [timePeriod, setTimePeriod] = useState('month');
  const [dashboardData, setDashboardData] = useState<BudgetDashboard | null>(null);
  const [resourceGroupCosts, setResourceGroupCosts] = useState<ResourceGroupCost[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedRG, setSelectedRG] = useState<string | null>(null);

  const [isLicenseDialogOpen, setIsLicenseDialogOpen] = useState(false);
  const [editingLicense, setEditingLicense] = useState<License | null>(null);
  const [licenseForm, setLicenseForm] = useState<LicenseCreate>({
    name: '',
    vendor: '',
    license_type: 'Subscription',
    seats: 1,
    cost_per_seat: 0,
    monthly_cost: 0,
  });
  const [isSavingLicense, setIsSavingLicense] = useState(false);

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

  const handleRGClick = (rgName: string) => {
    setSelectedRG(selectedRG === rgName ? null : rgName);
  };

  const openAddLicenseDialog = () => {
    setEditingLicense(null);
    setLicenseForm({
      name: '',
      vendor: '',
      license_type: 'Subscription',
      seats: 1,
      cost_per_seat: 0,
      monthly_cost: 0,
    });
    setIsLicenseDialogOpen(true);
  };

  const openEditLicenseDialog = (license: License) => {
    setEditingLicense(license);
    setLicenseForm({
      name: license.name,
      vendor: license.vendor,
      license_type: license.license_type,
      seats: license.seats || 1,
      cost_per_seat: license.cost_per_seat || 0,
      monthly_cost: license.monthly_cost,
    });
    setIsLicenseDialogOpen(true);
  };

  const handlePresetSelect = (presetName: string) => {
    const preset = LICENSE_PRESETS.find(p => p.name === presetName);
    if (preset) {
      const seats = licenseForm.seats || 1;
      setLicenseForm({
        ...licenseForm,
        name: preset.name === 'Custom License' ? '' : preset.name,
        vendor: preset.vendor,
        license_type: preset.type as 'Subscription' | 'Pay-as-you-go' | 'Perpetual' | 'Enterprise',
        cost_per_seat: preset.costPerSeat,
        monthly_cost: preset.costPerSeat * seats,
      });
    }
  };

  const handleSeatsChange = (seats: number) => {
    const costPerSeat = licenseForm.cost_per_seat || 0;
    setLicenseForm({
      ...licenseForm,
      seats,
      monthly_cost: costPerSeat * seats,
    });
  };

  const handleCostPerSeatChange = (costPerSeat: number) => {
    const seats = licenseForm.seats || 1;
    setLicenseForm({
      ...licenseForm,
      cost_per_seat: costPerSeat,
      monthly_cost: costPerSeat * seats,
    });
  };

  const saveLicense = async () => {
    if (!licenseForm.name || !licenseForm.vendor) return;

    setIsSavingLicense(true);
    try {
      if (editingLicense) {
        await api.budget.updateLicense(editingLicense.id, licenseForm);
      } else {
        await api.budget.createLicense(licenseForm);
      }
      setIsLicenseDialogOpen(false);
      fetchData();
    } catch (err) {
      console.error('Error saving license:', err);
    } finally {
      setIsSavingLicense(false);
    }
  };

  const deleteLicense = async (id: string) => {
    if (!confirm('Are you sure you want to delete this license?')) return;
    try {
      await api.budget.deleteLicense(id);
      fetchData();
    } catch (err) {
      console.error('Error deleting license:', err);
    }
  };

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

  const totalAzureSpend = azureCosts?.total_cost || 0;
  const totalLicenseSpend = licenses.reduce((sum, lic) => sum + (lic.monthly_cost || 0), 0);
  const totalMonthlySpend = totalAzureSpend + totalLicenseSpend;

  const selectedRGData = selectedRG
    ? resourceGroupCosts.find(rg => rg.resource_group === selectedRG)
    : null;

  const servicesToShow = selectedRGData
    ? selectedRGData.services
    : resourceGroupCosts.flatMap(rg => rg.services);

  const serviceAggregates = servicesToShow.reduce((acc, service) => {
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
              <CardTitle className="flex items-center justify-between">
                <span>Cost by Resource Group</span>
                {selectedRG && (
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setSelectedRG(null)}
                    className="text-xs"
                  >
                    <X className="h-3 w-3 mr-1" />
                    Clear selection
                  </Button>
                )}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {resourceGroupCosts
                  .sort((a, b) => b.total_cost - a.total_cost)
                  .map((rg) => {
                    const maxCost = Math.max(...resourceGroupCosts.map(r => r.total_cost), 1);
                    const percentage = (rg.total_cost / maxCost) * 100;
                    const isSelected = selectedRG === rg.resource_group;

                    return (
                      <div
                        key={rg.resource_group}
                        onClick={() => handleRGClick(rg.resource_group)}
                        className={`p-3 rounded-lg cursor-pointer transition-all ${
                          isSelected
                            ? 'bg-blue-50 border-2 border-blue-500 shadow-sm'
                            : 'hover:bg-gray-50 border-2 border-transparent'
                        }`}
                      >
                        <div className="flex items-center justify-between mb-2">
                          <span className={`text-sm font-medium truncate max-w-[200px] ${
                            isSelected ? 'text-blue-700' : ''
                          }`}>
                            {rg.resource_group}
                          </span>
                          <span className={`text-sm font-semibold ${
                            isSelected ? 'text-blue-700' : ''
                          }`}>
                            ${rg.total_cost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                          </span>
                        </div>
                        <Progress
                          value={percentage}
                          className={`h-2 ${isSelected ? '[&>div]:bg-blue-500' : ''}`}
                        />
                        {isSelected && rg.services.length > 0 && (
                          <p className="text-xs text-blue-600 mt-2">
                            {rg.services.length} services → see breakdown
                          </p>
                        )}
                      </div>
                    );
                  })}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>
                {selectedRG ? (
                  <span className="flex items-center gap-2">
                    <span className="text-blue-600">{selectedRG}</span>
                    <span className="text-gray-400 font-normal">Services</span>
                  </span>
                ) : (
                  'Top Services by Cost'
                )}
              </CardTitle>
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
                    {selectedRG ? 'No service data for this resource group' : 'No service cost data available'}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Key className="h-5 w-5" />
                License Management
              </div>
              <Button size="sm" onClick={openAddLicenseDialog}>
                <Plus className="h-4 w-4 mr-2" />
                Add License
              </Button>
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
                        <span className="text-xl">{getLicenseIcon(license.vendor)}</span>
                        <h4 className="font-semibold text-sm">{license.name}</h4>
                        <Badge
                          variant={license.status === 'Active' ? 'default' : 'secondary'}
                          className="text-xs"
                        >
                          {license.status}
                        </Badge>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-gray-600 ml-7">
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
                    <div className="flex items-center gap-4">
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
                      <div className="flex gap-1">
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => openEditLicenseDialog(license)}
                        >
                          <Pencil className="h-4 w-4" />
                        </Button>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => deleteLicense(license.id)}
                          className="text-red-600 hover:text-red-700"
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Key className="h-12 w-12 text-gray-300 mx-auto mb-4" />
                <p className="text-gray-500">No licenses tracked yet</p>
                <p className="text-sm text-gray-400 mt-1 mb-4">
                  Track your AI tool subscriptions
                </p>
                <Button onClick={openAddLicenseDialog}>
                  <Plus className="h-4 w-4 mr-2" />
                  Add Your First License
                </Button>
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

      <Dialog open={isLicenseDialogOpen} onOpenChange={setIsLicenseDialogOpen}>
        <DialogContent className="max-w-md">
          <DialogHeader>
            <DialogTitle>
              {editingLicense ? 'Edit License' : 'Add License'}
            </DialogTitle>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <div>
              <Label>Quick Select</Label>
              <Select onValueChange={handlePresetSelect}>
                <SelectTrigger>
                  <SelectValue placeholder="Choose a preset..." />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="GitHub Copilot Business">🐙 GitHub Copilot Business ($19/seat)</SelectItem>
                  <SelectItem value="GitHub Copilot Enterprise">🐙 GitHub Copilot Enterprise ($39/seat)</SelectItem>
                  <SelectItem value="ChatGPT Plus">🤖 ChatGPT Plus ($20/seat)</SelectItem>
                  <SelectItem value="ChatGPT Team">🤖 ChatGPT Team ($25/seat)</SelectItem>
                  <SelectItem value="ChatGPT Enterprise">🤖 ChatGPT Enterprise (Custom)</SelectItem>
                  <SelectItem value="Claude Pro">🧠 Claude Pro ($20/seat)</SelectItem>
                  <SelectItem value="Claude Team">🧠 Claude Team ($25/seat)</SelectItem>
                  <SelectItem value="Claude Enterprise">🧠 Claude Enterprise (Custom)</SelectItem>
                  <SelectItem value="M365 Copilot">🪟 M365 Copilot ($30/seat)</SelectItem>
                  <SelectItem value="Custom License">📄 Custom License</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="name">License Name</Label>
                <Input
                  id="name"
                  value={licenseForm.name}
                  onChange={(e) => setLicenseForm({ ...licenseForm, name: e.target.value })}
                  placeholder="e.g., GitHub Copilot"
                />
              </div>
              <div>
                <Label htmlFor="vendor">Vendor</Label>
                <Input
                  id="vendor"
                  value={licenseForm.vendor}
                  onChange={(e) => setLicenseForm({ ...licenseForm, vendor: e.target.value })}
                  placeholder="e.g., GitHub"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="seats">Number of Seats</Label>
                <Input
                  id="seats"
                  type="number"
                  min="1"
                  value={licenseForm.seats || ''}
                  onChange={(e) => handleSeatsChange(parseInt(e.target.value) || 1)}
                />
              </div>
              <div>
                <Label htmlFor="costPerSeat">Cost per Seat ($)</Label>
                <Input
                  id="costPerSeat"
                  type="number"
                  min="0"
                  step="0.01"
                  value={licenseForm.cost_per_seat || ''}
                  onChange={(e) => handleCostPerSeatChange(parseFloat(e.target.value) || 0)}
                />
              </div>
            </div>

            <div>
              <Label htmlFor="monthlyTotal">Monthly Total</Label>
              <Input
                id="monthlyTotal"
                type="number"
                min="0"
                step="0.01"
                value={licenseForm.monthly_cost || ''}
                onChange={(e) => setLicenseForm({ ...licenseForm, monthly_cost: parseFloat(e.target.value) || 0 })}
              />
              <p className="text-xs text-gray-500 mt-1">
                Auto-calculated from seats × cost per seat, or enter custom amount
              </p>
            </div>

            <div>
              <Label htmlFor="type">License Type</Label>
              <Select
                value={licenseForm.license_type}
                onValueChange={(v) => setLicenseForm({ ...licenseForm, license_type: v as 'Subscription' | 'Pay-as-you-go' | 'Perpetual' | 'Enterprise' })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Subscription">Subscription</SelectItem>
                  <SelectItem value="Pay-as-you-go">Pay-as-you-go</SelectItem>
                  <SelectItem value="Enterprise">Enterprise</SelectItem>
                  <SelectItem value="Perpetual">Perpetual</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsLicenseDialogOpen(false)}>
              Cancel
            </Button>
            <Button onClick={saveLicense} disabled={isSavingLicense || !licenseForm.name || !licenseForm.vendor}>
              {isSavingLicense ? (
                <Loader2 className="h-4 w-4 animate-spin mr-2" />
              ) : null}
              {editingLicense ? 'Update' : 'Add'} License
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
