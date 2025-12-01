'use client';

import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  FileText,
  Shield,
  BookOpen,
  CheckCircle,
  ExternalLink,
  AlertTriangle,
  Info,
  Layers,
} from 'lucide-react';

const frameworkPrinciples = [
  {
    title: 'Semantic Kernel Integration',
    description:
      'Build agents using Microsoft Semantic Kernel for function calling, prompt management, and LLM orchestration',
    icon: Layers,
    status: 'required',
  },
  {
    title: 'Security by Design',
    description:
      'Implement robust authentication, authorization, and data protection measures from the start',
    icon: Shield,
    status: 'required',
  },
  {
    title: 'Responsible AI',
    description:
      'Follow Responsible AI principles including transparency, fairness, and accountability',
    icon: CheckCircle,
    status: 'required',
  },
  {
    title: 'Observability',
    description:
      'Implement comprehensive logging, monitoring, and tracing for all agent interactions',
    icon: Info,
    status: 'recommended',
  },
];

const policies = [
  {
    category: 'Security & Compliance',
    items: [
      { name: 'Authentication & Authorization Policy', link: '#' },
      { name: 'Data Privacy & Protection Guidelines', link: '#' },
      { name: 'API Security Standards', link: '#' },
      { name: 'Audit Logging Requirements', link: '#' },
    ],
  },
  {
    category: 'Development Standards',
    items: [
      { name: 'Agent Development Best Practices', link: '#' },
      { name: 'Code Review Checklist', link: '#' },
      { name: 'Testing Requirements', link: '#' },
      { name: 'Documentation Standards', link: '#' },
    ],
  },
  {
    category: 'Operational Guidelines',
    items: [
      { name: 'Deployment Procedures', link: '#' },
      { name: 'Incident Response Plan', link: '#' },
      { name: 'Change Management Process', link: '#' },
      { name: 'Performance Monitoring', link: '#' },
    ],
  },
];

const architecturePatterns = [
  {
    name: 'Single Agent Pattern',
    description: 'Simple assistant for focused tasks with defined scope',
    use: 'FAQ bots, simple automations',
  },
  {
    name: 'Orchestrator Pattern',
    description: 'Coordinator agent that delegates to specialized sub-agents',
    use: 'Complex workflows, multi-step processes',
  },
  {
    name: 'Multi-Agent System',
    description: 'Collaborative agents working together on complex problems',
    use: 'Enterprise applications, sophisticated decision-making',
  },
];

export default function GovernancePage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">
            Agent Framework Governance
          </h1>
          <p className="mt-2 text-gray-600">
            Policies, standards, and best practices for Microsoft Agent
            Framework development
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BookOpen className="h-5 w-5" />
                Framework Overview
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <p className="text-sm text-gray-600">
                  The Microsoft Agent Framework provides a comprehensive
                  platform for building, deploying, and managing AI agents using
                  Semantic Kernel, Azure AI services, and industry best
                  practices.
                </p>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
                  {frameworkPrinciples.map((principle) => {
                    const Icon = principle.icon;
                    return (
                      <div
                        key={principle.title}
                        className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start gap-3">
                          <div className="rounded-lg p-2 bg-blue-50 text-blue-600">
                            <Icon className="h-5 w-5" />
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center justify-between mb-1">
                              <h4 className="font-semibold text-sm">
                                {principle.title}
                              </h4>
                              <Badge
                                variant={
                                  principle.status === 'required'
                                    ? 'default'
                                    : 'secondary'
                                }
                                className="text-xs"
                              >
                                {principle.status}
                              </Badge>
                            </div>
                            <p className="text-xs text-gray-600">
                              {principle.description}
                            </p>
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <AlertTriangle className="h-5 w-5 text-orange-600" />
                Quick Links
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" className="w-full justify-start" asChild>
                <a href="#" className="flex items-center gap-2">
                  <ExternalLink className="h-4 w-4" />
                  Microsoft Agent Framework Docs
                </a>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <a href="#" className="flex items-center gap-2">
                  <ExternalLink className="h-4 w-4" />
                  Semantic Kernel Documentation
                </a>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <a href="#" className="flex items-center gap-2">
                  <ExternalLink className="h-4 w-4" />
                  Azure AI Services
                </a>
              </Button>
              <Button variant="outline" className="w-full justify-start" asChild>
                <a href="#" className="flex items-center gap-2">
                  <ExternalLink className="h-4 w-4" />
                  Responsible AI Guidelines
                </a>
              </Button>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Policies & Standards
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {policies.map((section) => (
                  <div key={section.category}>
                    <h3 className="font-semibold text-sm text-gray-900 mb-3">
                      {section.category}
                    </h3>
                    <div className="space-y-2">
                      {section.items.map((item) => (
                        <a
                          key={item.name}
                          href={item.link}
                          className="flex items-center justify-between p-2 rounded hover:bg-gray-50 transition-colors group"
                        >
                          <span className="text-sm text-gray-700 group-hover:text-gray-900">
                            {item.name}
                          </span>
                          <ExternalLink className="h-4 w-4 text-gray-400 group-hover:text-gray-600" />
                        </a>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Layers className="h-5 w-5" />
                Architecture Patterns
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {architecturePatterns.map((pattern) => (
                  <div
                    key={pattern.name}
                    className="border rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <h4 className="font-semibold text-sm mb-2">
                      {pattern.name}
                    </h4>
                    <p className="text-xs text-gray-600 mb-2">
                      {pattern.description}
                    </p>
                    <div className="flex items-center gap-2 text-xs">
                      <Badge variant="outline" className="text-xs">
                        Use: {pattern.use}
                      </Badge>
                    </div>
                  </div>
                ))}

                <Button variant="outline" className="w-full mt-4">
                  View Full Architecture Guide
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Shield className="h-5 w-5" />
              Compliance Checklist
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {[
                'Authentication implemented',
                'Authorization configured',
                'Data encryption enabled',
                'Audit logging active',
                'Error handling robust',
                'Input validation present',
                'Rate limiting configured',
                'Monitoring dashboards set up',
                'Documentation complete',
                'Security review passed',
                'Performance tested',
                'Disaster recovery plan',
              ].map((item) => (
                <div
                  key={item}
                  className="flex items-center gap-2 p-2 rounded hover:bg-gray-50"
                >
                  <CheckCircle className="h-4 w-4 text-green-600 flex-shrink-0" />
                  <span className="text-sm text-gray-700">{item}</span>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
