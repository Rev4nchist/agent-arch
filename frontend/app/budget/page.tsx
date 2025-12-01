'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
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
} from 'lucide-react';

interface BudgetItem {
  service: string;
  category: string;
  budget: number;
  spent: number;
  icon: string;
}

const mockBudgetData: BudgetItem[] = [
  {
    service: 'Azure OpenAI',
    category: 'AI Services',
    budget: 5000,
    spent: 3200,
    icon: '🤖',
  },
  {
    service: 'Cosmos DB',
    category: 'Database',
    budget: 1500,
    spent: 890,
    icon: '🗄️',
  },
  {
    service: 'Azure AI Search',
    category: 'Search',
    budget: 800,
    spent: 645,
    icon: '🔍',
  },
  {
    service: 'Blob Storage',
    category: 'Storage',
    budget: 300,
    spent: 125,
    icon: '💾',
  },
  {
    service: 'App Service',
    category: 'Compute',
    budget: 600,
    spent: 480,
    icon: '⚙️',
  },
  {
    service: 'AI Foundry',
    category: 'AI Services',
    budget: 2000,
    spent: 1650,
    icon: '🏭',
  },
];

const licenses = [
  {
    name: 'Microsoft 365 Copilot',
    type: 'Subscription',
    seats: 25,
    cost: 7500,
    renewal: '2025-06-15',
    status: 'active',
  },
  {
    name: 'Azure OpenAI Service',
    type: 'Pay-as-you-go',
    seats: null,
    cost: 0,
    renewal: 'N/A',
    status: 'active',
  },
  {
    name: 'GitHub Copilot Business',
    type: 'Subscription',
    seats: 50,
    cost: 950,
    renewal: '2025-04-01',
    status: 'active',
  },
];

export default function BudgetPage() {
  const [timePeriod, setTimePeriod] = useState('month');

  const totalBudget = mockBudgetData.reduce((sum, item) => sum + item.budget, 0);
  const totalSpent = mockBudgetData.reduce((sum, item) => sum + item.spent, 0);
  const percentageUsed = (totalSpent / totalBudget) * 100;
  const remaining = totalBudget - totalSpent;

  const getStatusColor = (spent: number, budget: number) => {
    const percentage = (spent / budget) * 100;
    if (percentage >= 90) return 'text-red-600';
    if (percentage >= 75) return 'text-orange-600';
    return 'text-green-600';
  };

  const getStatusBadge = (spent: number, budget: number) => {
    const percentage = (spent / budget) * 100;
    if (percentage >= 90)
      return { text: 'Critical', color: 'bg-red-100 text-red-800' };
    if (percentage >= 75)
      return { text: 'Warning', color: 'bg-orange-100 text-orange-800' };
    return { text: 'On Track', color: 'bg-green-100 text-green-800' };
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8 flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Budget & Licensing
            </h1>
            <p className="mt-2 text-gray-600">
              Track Azure spending and manage software licenses
            </p>
          </div>
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

        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Total Budget
                  </p>
                  <p className="mt-2 text-2xl font-bold text-gray-900">
                    ${totalBudget.toLocaleString()}
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
                  <p className="text-sm font-medium text-gray-600">Spent</p>
                  <p className="mt-2 text-2xl font-bold text-gray-900">
                    ${totalSpent.toLocaleString()}
                  </p>
                </div>
                <div className="rounded-lg p-3 bg-orange-50">
                  <TrendingUp className="h-6 w-6 text-orange-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">Remaining</p>
                  <p className="mt-2 text-2xl font-bold text-gray-900">
                    ${remaining.toLocaleString()}
                  </p>
                </div>
                <div className="rounded-lg p-3 bg-green-50">
                  <TrendingDown className="h-6 w-6 text-green-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600">
                    Budget Used
                  </p>
                  <p className="mt-2 text-2xl font-bold text-gray-900">
                    {percentageUsed.toFixed(1)}%
                  </p>
                </div>
                <div
                  className={`rounded-lg p-3 ${
                    percentageUsed >= 90
                      ? 'bg-red-50'
                      : percentageUsed >= 75
                        ? 'bg-orange-50'
                        : 'bg-green-50'
                  }`}
                >
                  {percentageUsed >= 90 ? (
                    <AlertTriangle className="h-6 w-6 text-red-600" />
                  ) : (
                    <CheckCircle
                      className={`h-6 w-6 ${
                        percentageUsed >= 75
                          ? 'text-orange-600'
                          : 'text-green-600'
                      }`}
                    />
                  )}
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Service-Level Budget Tracking</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              {mockBudgetData.map((item) => {
                const percentage = (item.spent / item.budget) * 100;
                const status = getStatusBadge(item.spent, item.budget);

                return (
                  <div key={item.service} className="space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <span className="text-2xl">{item.icon}</span>
                        <div>
                          <h4 className="font-semibold text-sm">
                            {item.service}
                          </h4>
                          <p className="text-xs text-gray-600">{item.category}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-4">
                        <Badge className={status.color}>{status.text}</Badge>
                        <div className="text-right">
                          <p
                            className={`text-sm font-semibold ${getStatusColor(
                              item.spent,
                              item.budget
                            )}`}
                          >
                            ${item.spent.toLocaleString()} / $
                            {item.budget.toLocaleString()}
                          </p>
                          <p className="text-xs text-gray-600">
                            {percentage.toFixed(1)}% used
                          </p>
                        </div>
                      </div>
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
            <CardTitle className="flex items-center gap-2">
              <Key className="h-5 w-5" />
              License Management
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {licenses.map((license) => (
                <div
                  key={license.name}
                  className="flex items-start justify-between p-4 border rounded-lg hover:shadow-md transition-shadow"
                >
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-sm">{license.name}</h4>
                      <Badge
                        variant={
                          license.status === 'active' ? 'default' : 'secondary'
                        }
                        className="text-xs"
                      >
                        {license.status}
                      </Badge>
                    </div>
                    <div className="flex items-center gap-4 text-xs text-gray-600">
                      <span>{license.type}</span>
                      {license.seats && <span>{license.seats} seats</span>}
                      <span className="flex items-center gap-1">
                        <Calendar className="h-3 w-3" />
                        Renewal: {license.renewal}
                      </span>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-semibold text-gray-900">
                      {license.cost > 0
                        ? `$${license.cost.toLocaleString()}/mo`
                        : 'Usage-based'}
                    </p>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-6 pt-6 border-t">
              <div className="flex items-center justify-between">
                <p className="text-sm font-semibold text-gray-900">
                  Total License Costs
                </p>
                <p className="text-lg font-bold text-gray-900">
                  $
                  {licenses
                    .reduce((sum, lic) => sum + lic.cost, 0)
                    .toLocaleString()}
                  /month
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
