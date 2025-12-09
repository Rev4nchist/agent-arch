'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { AsciiStarfield } from '@/components/AsciiStarfield';
import {
  X,
  Check,
  ArrowRight,
  ExternalLink,
  Calendar,
  ClipboardList,
  Bot,
  Shield,
  FileText,
  DollarSign,
  Code,
  Users,
  Terminal,
} from 'lucide-react';

interface OrientationCard {
  id: string;
  title: string;
  color: string;
  badge: string;
  summary: string;
  bullets: string[];
  expandedSections: {
    title: string;
    content: React.ReactNode;
  }[];
  resources?: { label: string; url: string }[];
}

const orientationCards: OrientationCard[] = [
  {
    id: 'framework',
    title: 'Microsoft Agent Framework',
    color: 'blue',
    badge: 'BUILD',
    summary: 'Open-source framework (.NET/Python) for building AI agents with autonomous decision-making. Built on Foundry Agent Service runtime with native MCP support. Successor to Semantic Kernel and AutoGen—created by the same Microsoft teams.',
    bullets: [
      'Single & multi-agent workflows with graph-based routing',
      'Native MCP support for tool/data connections',
      'Agent-native execution on Foundry Agent Service',
    ],
    expandedSections: [
      {
        title: 'What It Is - "The Engine Room"',
        content: (
          <>
            <p className="text-slate-300 mb-2">
              The <strong>Microsoft Agent Framework</strong> is the open-source code-first framework that defines how agents think and act. It&apos;s the successor to Semantic Kernel and AutoGen, created by the same Microsoft teams.
            </p>
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3 text-xs font-mono">
              <p className="text-slate-300 mb-1"><strong className="text-emerald-400">Runtime:</strong> Built on the <strong>Foundry Agent Service</strong></p>
              <p className="text-slate-400 mb-1">A serverless runtime optimized for long-running, stateful agent processes (not just stateless API calls)</p>
              <p className="text-slate-400"><strong className="text-emerald-400">Languages:</strong> .NET (C#) and Python</p>
            </div>
          </>
        ),
      },
      {
        title: 'Key Capabilities',
        content: (
          <>
            <p className="text-emerald-400 text-xs font-mono font-semibold mb-1">// Single Agents</p>
            <ul className="text-slate-400 space-y-0.5 text-xs mb-3 font-mono">
              <li>* Autonomous decision-making with tool calling</li>
              <li>* Context-aware reasoning with memory systems</li>
              <li>* Built-in support for prompt engineering patterns</li>
            </ul>
            <p className="text-emerald-400 text-xs font-mono font-semibold mb-1">// Multi-Agent Orchestration</p>
            <ul className="text-slate-400 space-y-0.5 text-xs mb-3 font-mono">
              <li>* <strong className="text-cyan-400">Router Pattern:</strong> Route tasks to specialized agents</li>
              <li>* <strong className="text-cyan-400">Crew Pattern:</strong> Agents collaborate as a team</li>
              <li>* <strong className="text-cyan-400">Manager-Worker Pattern:</strong> Hierarchical agent structures</li>
              <li>* Graph-based workflows with conditional routing</li>
            </ul>
            <p className="text-emerald-400 text-xs font-mono font-semibold mb-1">// Memory & State Management</p>
            <ul className="text-slate-400 space-y-0.5 text-xs font-mono">
              <li>* Short-term memory: Conversation history</li>
              <li>* Long-term memory: Entity extraction and storage</li>
              <li>* Built-in handling without external databases</li>
            </ul>
          </>
        ),
      },
      {
        title: 'MCP Integration',
        content: (
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 font-mono">
            <p className="text-amber-400 font-semibold text-xs mb-1">[MCP] Native Model Context Protocol Support</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>* Dynamic discovery of tools and data sources</li>
              <li>* No custom connectors required for MCP-enabled services</li>
              <li>* Shared ecosystem of capabilities across agents</li>
            </ul>
          </div>
        ),
      },
      {
        title: 'Code-First & Low-Code',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs font-mono">
            <li>* <strong className="text-emerald-400">Pure Code:</strong> Full Python/C# control for complex logic</li>
            <li>* <strong className="text-emerald-400">Low-Code:</strong> Visual configuration via Foundry portal</li>
            <li>* <strong className="text-emerald-400">Hybrid:</strong> Combine both approaches in same agent</li>
          </ul>
        ),
      },
      {
        title: 'Quick Start',
        content: (
          <ol className="text-slate-400 space-y-0.5 text-xs font-mono">
            <li>1. Install: <code className="bg-slate-900 px-1 rounded text-emerald-400">pip install microsoft-agent-framework</code> or NuGet</li>
            <li>2. Prototype with Agent Loop in Foundry</li>
            <li>3. Deploy to Foundry Agent Service</li>
            <li>4. Monitor via Agent 365 control plane</li>
          </ol>
        ),
      },
    ],
    resources: [
      { label: 'Framework Overview', url: 'https://learn.microsoft.com/en-us/agent-framework/overview/agent-framework-overview' },
      { label: 'Agent Service', url: 'https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/foundry-agent-service-at-ignite-2025' },
      { label: 'GitHub', url: 'https://github.com/microsoft/agent-framework' },
    ],
  },
  {
    id: 'foundry',
    title: 'Microsoft Foundry',
    color: 'purple',
    badge: 'BUILD STUDIO',
    summary: 'The unified IDE for building AI agents. Access 1,800+ models including Claude 4.5 Sonnet, GPT-5, and o1. Design with Prompt Flow, test with Evaluation Studio, deploy to Foundry Agent Service. Native MCP support for instant data connectivity.',
    bullets: [
      '1,800+ models: Claude 4.5 Sonnet, GPT-5, o1, Gemini 2.0',
      'Native MCP protocol for zero-code tool integration',
      'Foundry Agent Service runtime for production deployment',
    ],
    expandedSections: [
      {
        title: 'The Rebrand - "The Workshop"',
        content: (
          <>
            <p className="text-slate-300 mb-2 font-mono text-xs">
              <strong className="text-purple-400">Formerly:</strong> Azure AI Foundry / Azure AI Studio<br/>
              <strong className="text-purple-400">Now:</strong> Microsoft Foundry
            </p>
            <p className="text-slate-400 text-xs font-mono">
              Microsoft Foundry is the unified IDE where agents are designed, prototyped, and built. It&apos;s the &quot;Workshop&quot; for AI developers—a single place to access models, design prompts, test agent behavior, and deploy to production.
            </p>
          </>
        ),
      },
      {
        title: 'Unified Model Catalog',
        content: (
          <>
            <p className="text-emerald-400 text-xs mb-2 font-mono font-semibold">// 1,800+ Models Available</p>
            <ul className="text-slate-400 space-y-1 text-xs font-mono">
              <li>* <strong className="text-cyan-400">Claude 4.5 Sonnet</strong> [NEW] (Ignite 2025)</li>
              <li>* GPT-5, o1, o3-mini (OpenAI reasoning models)</li>
              <li>* Gemini 2.0, Llama 3.3, Phi-4</li>
              <li>* Specialized: Vision, embeddings, speech, code</li>
            </ul>
            <p className="text-slate-400 text-xs mt-2 font-mono">
              <strong className="text-emerald-400">Model Types:</strong> Foundational (base reasoning), Open Source (Llama, Mistral), Reasoning (o1, o3), Multimodal (vision, audio, documents)
            </p>
          </>
        ),
      },
      {
        title: 'Foundry Agent Service (The Runtime)',
        content: (
          <>
            <div className="bg-purple-500/10 border border-purple-500/30 rounded-lg p-3 font-mono">
              <p className="text-slate-300 text-xs mb-1">
                <strong className="text-purple-400">What It Is:</strong> Serverless execution environment for agents
              </p>
              <ul className="text-slate-400 space-y-0.5 text-xs">
                <li>* Agent-native (optimized for stateful, long-running processes)</li>
                <li>* Auto-scaling based on agent load</li>
                <li>* Built-in memory and state management</li>
              </ul>
            </div>
            <p className="text-slate-400 text-xs mt-2 font-mono">
              <strong className="text-purple-400">Why It Matters:</strong> Traditional APIs are stateless (request/response). Agents need to &quot;think&quot; across multiple turns. Foundry Agent Service handles this complexity.
            </p>
          </>
        ),
      },
      {
        title: 'Design & Test Tools',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs font-mono">
            <li>* <strong className="text-purple-400">Prompt Flow:</strong> Drag-and-drop agent logic design, visual debugging</li>
            <li>* <strong className="text-purple-400">Evaluation Studio:</strong> Test against &quot;Golden Datasets&quot;, compare model versions</li>
            <li>* <strong className="text-purple-400">Agent Loop:</strong> Rapid prototyping in Teams-like environment</li>
          </ul>
        ),
      },
      {
        title: 'MCP Native Support',
        content: (
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 font-mono">
            <p className="text-amber-400 font-semibold text-xs mb-1">[MCP] The Universal Connector</p>
            <p className="text-slate-400 text-xs mb-2">
              <strong className="text-slate-300">Problem Solved:</strong> Previously, connecting to Salesforce, GitHub, SQL required 3 custom connectors.
            </p>
            <p className="text-slate-400 text-xs">
              <strong className="text-emerald-400">MCP Solution:</strong> If a tool/data source exposes an MCP server, agents can discover and use it instantly. No custom connectors required for MCP-enabled services.
            </p>
          </div>
        ),
      },
      {
        title: 'Why Foundry vs Others',
        content: (
          <div className="overflow-x-auto font-mono">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-emerald-500/30">
                  <th className="text-left text-slate-400 pb-2 pr-2">Feature</th>
                  <th className="text-left text-purple-400 pb-2 pr-2">MS Foundry</th>
                  <th className="text-left text-slate-400 pb-2 pr-2">Vertex</th>
                  <th className="text-left text-slate-400 pb-2">Bedrock</th>
                </tr>
              </thead>
              <tbody className="text-slate-400">
                <tr className="border-b border-slate-700/50">
                  <td className="py-2 pr-2">Multi-vendor</td>
                  <td className="py-2 pr-2 text-emerald-400">[x] 1,800+</td>
                  <td className="py-2 pr-2">Limited</td>
                  <td className="py-2">AWS only</td>
                </tr>
                <tr className="border-b border-slate-700/50">
                  <td className="py-2 pr-2">Agent runtime</td>
                  <td className="py-2 pr-2 text-emerald-400">[x]</td>
                  <td className="py-2 pr-2 text-red-400">[ ]</td>
                  <td className="py-2 text-red-400">[ ]</td>
                </tr>
                <tr className="border-b border-slate-700/50">
                  <td className="py-2 pr-2">MCP support</td>
                  <td className="py-2 pr-2 text-emerald-400">[x] Native</td>
                  <td className="py-2 pr-2 text-red-400">[ ]</td>
                  <td className="py-2 text-red-400">[ ]</td>
                </tr>
                <tr>
                  <td className="py-2 pr-2">M365</td>
                  <td className="py-2 pr-2 text-emerald-400">[x] Seamless</td>
                  <td className="py-2 pr-2 text-red-400">[ ]</td>
                  <td className="py-2 text-red-400">[ ]</td>
                </tr>
              </tbody>
            </table>
          </div>
        ),
      },
    ],
    resources: [
      { label: 'Foundry Overview', url: 'https://azure.microsoft.com/en-us/blog/microsoft-foundry-scale-innovation' },
      { label: 'Agent Service', url: 'https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/foundry-agent-service-at-ignite-2025' },
      { label: 'MCP Guide', url: 'https://techcommunity.microsoft.com/foundry-tools-mcp' },
    ],
  },
  {
    id: 'm365sdk',
    title: 'M365 Agent SDK',
    color: 'emerald',
    badge: 'PACKAGING',
    summary: 'The "Shipping Container". Wraps agents built with Framework/Foundry into deployable packages for M365 Copilot, Teams, and Web. Required for Agent Store publishing. Emits telemetry for Agent 365 observability. Includes Agent Loop for rapid prototyping.',
    bullets: [
      'Agent Store requirement + Agent 365 telemetry emission',
      'Agent Loop: Test in Teams-like environment instantly',
      'Deploy to M365 Copilot, Teams, Web (C#/JS/Python)',
    ],
    expandedSections: [
      {
        title: 'What It Is - "The Shipping Container"',
        content: (
          <>
            <p className="text-slate-300 mb-2 font-mono text-xs">
              The <strong className="text-emerald-400">M365 Agent SDK</strong> is the bridge that turns a raw AI agent into a deployable &quot;app&quot; that can live inside Microsoft Teams, Copilot, or Outlook. It ensures agents are &quot;Agent 365 Compliant.&quot;
            </p>
            <p className="text-slate-400 text-xs font-mono">
              <strong className="text-slate-300">Think of it as:</strong> The packaging that makes your agent fit onto the Microsoft 365 truck and ensures it can be tracked by IT.
            </p>
          </>
        ),
      },
      {
        title: 'Standardized Packaging',
        content: (
          <div className="grid grid-cols-2 gap-3 text-xs font-mono">
            <div>
              <p className="text-emerald-400 font-semibold mb-1">// What Gets Packaged</p>
              <ul className="text-slate-400 space-y-0.5">
                <li>* Agent logic (from Framework/Foundry)</li>
                <li>* Manifest file (capabilities, permissions)</li>
                <li>* Configuration (channel-specific settings)</li>
                <li>* Dependencies and resources</li>
              </ul>
            </div>
            <div>
              <p className="text-emerald-400 font-semibold mb-1">// Output</p>
              <ul className="text-slate-400 space-y-0.5">
                <li>* .zip file ready for deployment</li>
                <li>* Agent Store submission package</li>
                <li>* Custom app installation bundle</li>
              </ul>
            </div>
          </div>
        ),
      },
      {
        title: 'Telemetry Emission (Agent 365 Requirement)',
        content: (
          <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3 font-mono">
            <p className="text-emerald-400 font-semibold text-xs mb-1">[TELEMETRY] Automatic Signals</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>* <strong className="text-cyan-400">User ID:</strong> Who used the agent</li>
              <li>* <strong className="text-cyan-400">Token usage:</strong> Cost tracking</li>
              <li>* <strong className="text-cyan-400">Latency:</strong> Performance monitoring</li>
              <li>* <strong className="text-cyan-400">Tool calls:</strong> What the agent accessed</li>
              <li>* <strong className="text-cyan-400">Error rates:</strong> Reliability metrics</li>
            </ul>
            <p className="text-slate-400 text-xs mt-2">
              <strong className="text-amber-400">Why This Matters:</strong> Agent 365 requires this data for fleet observability. Without SDK telemetry, agents are &quot;invisible&quot; to IT.
            </p>
          </div>
        ),
      },
      {
        title: 'Agent Loop (Rapid Prototyping)',
        content: (
          <div className="bg-blue-500/10 border border-blue-500/30 rounded-lg p-3 font-mono">
            <p className="text-blue-400 font-semibold text-xs mb-1">[LOOP] Lightweight testing environment</p>
            <p className="text-slate-400 text-xs mb-2">Mimics Teams/Copilot experience. No deployment required.</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>* Test agent responses in real-time</li>
              <li>* Debug tool calls and reasoning</li>
              <li>* Iterate quickly before deployment</li>
            </ul>
          </div>
        ),
      },
      {
        title: 'Channel Customization',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs font-mono">
            <li>* <strong className="text-emerald-400">Teams:</strong> Adaptive Cards, tabs, message extensions</li>
            <li>* <strong className="text-emerald-400">Copilot:</strong> Native integration, context awareness</li>
            <li>* <strong className="text-emerald-400">Web:</strong> Embeddable widget, custom styling</li>
            <li>* <strong className="text-emerald-400">Outlook:</strong> Email-triggered actions, calendar integration</li>
          </ul>
        ),
      },
      {
        title: 'Technology Agnostic',
        content: (
          <>
            <p className="text-slate-400 text-xs mb-2 font-mono">The SDK doesn&apos;t care how you built the agent:</p>
            <ul className="text-slate-400 space-y-0.5 text-xs font-mono">
              <li>* Microsoft Agent Framework (.NET/Python)</li>
              <li>* LangChain/LlamaIndex</li>
              <li>* Custom implementation</li>
              <li>* Any LLM provider (OpenAI, Anthropic, etc.)</li>
            </ul>
          </>
        ),
      },
    ],
    resources: [
      { label: 'SDK Documentation', url: 'https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agents-sdk-overview' },
      { label: 'Agent Loop Guide', url: 'https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agents-sdk-agent-loop' },
      { label: 'Quickstart', url: 'https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agents-sdk-quickstart' },
    ],
  },
  {
    id: 'agent365',
    title: 'Microsoft Agent 365',
    color: 'orange',
    badge: 'CONTROL PLANE',
    summary: 'The "Air Traffic Control" for your agent fleet. IT admins see every agent deployed across the organization. Usage dashboards, cost allocation, policy enforcement, and security controls. Announced at Ignite 2025 - GA expected H1 2025.',
    bullets: [
      'Fleet observability: See all agents across the organization',
      'Security & compliance: Policy enforcement, DLP, access controls',
      'Cost management: Per-agent spend tracking and allocation',
    ],
    expandedSections: [
      {
        title: 'What Is Agent 365',
        content: (
          <>
            <p className="text-slate-300 mb-2 font-mono text-xs">
              <strong className="text-orange-400">Microsoft Agent 365</strong> is the management and observability plane for AI agents across your organization. Think of it as the &quot;Air Traffic Control&quot; that ensures agents are visible, compliant, and cost-managed.
            </p>
            <div className="bg-orange-500/10 border border-orange-500/30 rounded-lg p-3 text-xs font-mono">
              <p className="text-orange-400 font-semibold mb-1">[NEW] Announced at Ignite 2025</p>
              <p className="text-slate-400">Expected GA: H1 2025. Currently in private preview with select customers.</p>
            </div>
          </>
        ),
      },
      {
        title: 'Fleet Observability',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs font-mono">
            <li>* <strong className="text-orange-400">Agent Inventory:</strong> See every agent deployed (first-party, third-party, custom)</li>
            <li>* <strong className="text-orange-400">Usage Metrics:</strong> Who is using which agents, how often</li>
            <li>* <strong className="text-orange-400">Health Monitoring:</strong> Latency, error rates, availability</li>
            <li>* <strong className="text-orange-400">Cost Dashboard:</strong> Token usage, model costs per agent</li>
          </ul>
        ),
      },
      {
        title: 'Security & Compliance',
        content: (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 font-mono">
            <p className="text-red-400 font-semibold text-xs mb-1">[SECURITY] Enterprise-Grade Controls</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>* <strong className="text-cyan-400">DLP Integration:</strong> Prevent sensitive data leakage</li>
              <li>* <strong className="text-cyan-400">Access Policies:</strong> Who can use which agents</li>
              <li>* <strong className="text-cyan-400">Audit Logs:</strong> Every agent action logged for compliance</li>
              <li>* <strong className="text-cyan-400">Data Residency:</strong> Control where agent data is processed</li>
            </ul>
          </div>
        ),
      },
      {
        title: 'Governance Framework',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs font-mono">
            <li>* <strong className="text-orange-400">Agent Approval Workflow:</strong> IT approves before deployment</li>
            <li>* <strong className="text-orange-400">Capability Restrictions:</strong> Limit what agents can access</li>
            <li>* <strong className="text-orange-400">Model Allowlisting:</strong> Only approved models can be used</li>
            <li>* <strong className="text-orange-400">Usage Quotas:</strong> Prevent runaway costs</li>
          </ul>
        ),
      },
      {
        title: 'Before/After Comparison',
        content: (
          <div className="grid grid-cols-2 gap-3 text-xs font-mono">
            <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
              <p className="text-red-400 font-semibold mb-1">// Before Agent 365</p>
              <ul className="text-slate-400 space-y-0.5">
                <li>* Shadow AI agents everywhere</li>
                <li>* No visibility into costs</li>
                <li>* Security/compliance blind spots</li>
                <li>* Fragmented management</li>
              </ul>
            </div>
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3">
              <p className="text-emerald-400 font-semibold mb-1">// With Agent 365</p>
              <ul className="text-slate-400 space-y-0.5">
                <li>* Complete fleet visibility</li>
                <li>* Cost allocation by team/project</li>
                <li>* Centralized policy enforcement</li>
                <li>* Single pane of glass</li>
              </ul>
            </div>
          </div>
        ),
      },
    ],
    resources: [
      { label: 'Agent 365 Overview', url: 'https://techcommunity.microsoft.com/blog/microsoftcopilotstudioblog/ignite-2025-announcing-microsoft-agents-365' },
      { label: 'Governance Guide', url: 'https://learn.microsoft.com/en-us/microsoft-365-copilot/extensibility/agent-governance' },
    ],
  },
  {
    id: 'foundryiq',
    title: 'Foundry IQ',
    color: 'cyan',
    badge: 'KNOWLEDGE',
    summary: 'The "Agentic RAG Engine". Automatically indexes your enterprise data (SharePoint, Teams, Fabric) and makes it available to agents. Work IQ for M365 content, Fabric IQ for analytics data. Agents get instant, grounded answers without custom retrieval code.',
    bullets: [
      'Auto-indexes M365 content (SharePoint, OneDrive, Teams)',
      'Fabric IQ for structured analytics data',
      'Agentic retrieval: Agents query data without custom code',
    ],
    expandedSections: [
      {
        title: 'What It Is - "Agentic RAG Engine"',
        content: (
          <>
            <p className="text-slate-300 mb-2 font-mono text-xs">
              <strong className="text-cyan-400">Foundry IQ</strong> is Microsoft&apos;s answer to the RAG (Retrieval-Augmented Generation) challenge. Instead of building custom retrieval pipelines, agents can tap into pre-indexed enterprise knowledge automatically.
            </p>
            <p className="text-slate-400 text-xs font-mono">
              <strong className="text-slate-300">Think of it as:</strong> A librarian that has already organized all your company&apos;s documents and can instantly find relevant context for any agent query.
            </p>
          </>
        ),
      },
      {
        title: 'Why It Matters',
        content: (
          <div className="bg-cyan-500/10 border border-cyan-500/30 rounded-lg p-3 font-mono">
            <p className="text-cyan-400 font-semibold text-xs mb-1">[PROBLEM] The RAG Challenge</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>* Building retrieval pipelines is 60% of agent dev time</li>
              <li>* Chunking, embedding, indexing, ranking—complex work</li>
              <li>* Every agent reinvents the same wheel</li>
            </ul>
            <p className="text-emerald-400 font-semibold text-xs mt-2 mb-1">[SOLUTION] Foundry IQ</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>* Pre-built indexing of enterprise content</li>
              <li>* Agents just &quot;ask&quot; for relevant documents</li>
              <li>* No custom retrieval code required</li>
            </ul>
          </div>
        ),
      },
      {
        title: 'Architecture',
        content: (
          <>
            <p className="text-cyan-400 text-xs font-mono font-semibold mb-1">// Work IQ (M365 Content)</p>
            <ul className="text-slate-400 space-y-0.5 text-xs mb-3 font-mono">
              <li>* SharePoint sites and document libraries</li>
              <li>* OneDrive files and folders</li>
              <li>* Teams messages and meeting transcripts</li>
              <li>* Outlook emails (with permissions)</li>
            </ul>
            <p className="text-cyan-400 text-xs font-mono font-semibold mb-1">// Fabric IQ (Analytics Data)</p>
            <ul className="text-slate-400 space-y-0.5 text-xs font-mono">
              <li>* Power BI datasets and reports</li>
              <li>* Fabric lakehouse tables</li>
              <li>* SQL databases via connectors</li>
            </ul>
          </>
        ),
      },
      {
        title: 'Implementation Workflow',
        content: (
          <ol className="text-slate-400 space-y-1 text-xs font-mono">
            <li>1. <strong className="text-cyan-400">Connect:</strong> Point IQ at your M365/Fabric sources</li>
            <li>2. <strong className="text-cyan-400">Index:</strong> Automatic chunking and embedding (managed)</li>
            <li>3. <strong className="text-cyan-400">Secure:</strong> Respects existing M365 permissions</li>
            <li>4. <strong className="text-cyan-400">Query:</strong> Agents call IQ via API or MCP</li>
            <li>5. <strong className="text-cyan-400">Ground:</strong> Responses cite sources for transparency</li>
          </ol>
        ),
      },
      {
        title: 'Strategic Value',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs font-mono">
            <li>* <strong className="text-cyan-400">Faster Development:</strong> Skip 60% of RAG work</li>
            <li>* <strong className="text-cyan-400">Better Quality:</strong> Microsoft-optimized retrieval</li>
            <li>* <strong className="text-cyan-400">Permission Aware:</strong> Users only see what they&apos;re allowed to</li>
            <li>* <strong className="text-cyan-400">Always Current:</strong> Auto-sync with source changes</li>
          </ul>
        ),
      },
    ],
    resources: [
      { label: 'Foundry IQ Preview', url: 'https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/foundry-iq-preview' },
      { label: 'Work IQ Docs', url: 'https://learn.microsoft.com/en-us/microsoft-365-copilot/work-iq' },
    ],
  },
  {
    id: 'modelrouter',
    title: 'Model Router',
    color: 'amber',
    badge: 'ROUTING',
    summary: 'The "Smart Traffic Controller" for AI models. Automatically routes requests to the best model based on task complexity, cost targets, and latency requirements. Three modes: Cost-optimized, Quality-optimized, or Balanced. GA as of Ignite 2025.',
    bullets: [
      'Automatic model selection based on task complexity',
      'Cost optimization: Route simple tasks to cheaper models',
      'Fallback handling: Auto-retry with different models on failure',
    ],
    expandedSections: [
      {
        title: 'What It Is - "Smart Traffic Controller"',
        content: (
          <>
            <p className="text-slate-300 mb-2 font-mono text-xs">
              <strong className="text-amber-400">Model Router</strong> sits between your agent and the model catalog. Instead of hardcoding which model to use, you describe your requirements and Router picks the best option dynamically.
            </p>
            <div className="bg-amber-500/10 border border-amber-500/30 rounded-lg p-3 text-xs font-mono">
              <p className="text-amber-400 font-semibold mb-1">[GA] Available at Ignite 2025</p>
              <p className="text-slate-400">Available now in Microsoft Foundry. No additional cost for routing logic.</p>
            </div>
          </>
        ),
      },
      {
        title: 'Use Case Examples',
        content: (
          <div className="space-y-2 text-xs font-mono">
            <div className="bg-slate-900/80 rounded p-2 border border-slate-700/50">
              <p className="text-slate-300 font-semibold">query: &quot;What&apos;s 2+2?&quot;</p>
              <p className="text-emerald-400">-&gt; Routes to Phi-4 (cheap, fast)</p>
            </div>
            <div className="bg-slate-900/80 rounded p-2 border border-slate-700/50">
              <p className="text-slate-300 font-semibold">query: &quot;Analyze Q3 revenue trends&quot;</p>
              <p className="text-purple-400">-&gt; Routes to GPT-5 or Claude 4.5 Sonnet</p>
            </div>
            <div className="bg-slate-900/80 rounded p-2 border border-slate-700/50">
              <p className="text-slate-300 font-semibold">query: &quot;Prove this theorem&quot;</p>
              <p className="text-cyan-400">-&gt; Routes to o1 or o3-mini</p>
            </div>
          </div>
        ),
      },
      {
        title: '3 Optimization Modes',
        content: (
          <div className="grid grid-cols-3 gap-2 text-xs font-mono">
            <div className="bg-emerald-500/10 border border-emerald-500/30 rounded p-2 text-center">
              <p className="text-emerald-400 font-semibold">$COST</p>
              <p className="text-slate-400">Cheapest model that can handle the task</p>
            </div>
            <div className="bg-amber-500/10 border border-amber-500/30 rounded p-2 text-center">
              <p className="text-amber-400 font-semibold">~BALANCED</p>
              <p className="text-slate-400">Best cost/quality tradeoff</p>
            </div>
            <div className="bg-purple-500/10 border border-purple-500/30 rounded p-2 text-center">
              <p className="text-purple-400 font-semibold">*QUALITY</p>
              <p className="text-slate-400">Best model regardless of cost</p>
            </div>
          </div>
        ),
      },
      {
        title: 'Key Features',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs font-mono">
            <li>* <strong className="text-amber-400">Task Classification:</strong> Automatically detects complexity</li>
            <li>* <strong className="text-amber-400">Fallback Chains:</strong> If Model A fails, try Model B</li>
            <li>* <strong className="text-amber-400">Latency Constraints:</strong> Route to fastest model under deadline</li>
            <li>* <strong className="text-amber-400">Cost Budgets:</strong> Stay within per-request spend limits</li>
            <li>* <strong className="text-amber-400">A/B Testing:</strong> Compare model performance in production</li>
          </ul>
        ),
      },
    ],
    resources: [
      { label: 'Model Router Docs', url: 'https://learn.microsoft.com/en-us/azure/ai-foundry/model-router' },
      { label: 'Ignite Announcement', url: 'https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/model-router-ga' },
    ],
  },
];

const platformCapabilities = [
  { name: 'Meetings Hub', icon: Users, desc: 'Schedule sessions, upload transcripts, extract action items', badge: 'CORE', color: 'purple' },
  { name: 'Task Management', icon: ClipboardList, desc: 'Kanban board with priority, dependencies, and tracking', badge: 'CORE', color: 'emerald' },
  { name: 'Agent Portfolio', icon: Bot, desc: 'Track agents by tier from Idea to Production', badge: 'CORE', color: 'orange' },
  { name: 'Governance', icon: Shield, desc: '6-week framework with policy repository and compliance', badge: 'CRITICAL', color: 'red' },
  { name: 'Decisions', icon: FileText, desc: 'Decision log with rationale and audit trail', badge: 'AUDIT', color: 'yellow' },
  { name: 'Budget', icon: DollarSign, desc: 'License inventory and spend tracking with forecasting', badge: 'FINANCE', color: 'green' },
  { name: 'Architecture Lab', icon: Code, desc: 'Technology radar and code pattern repository', badge: 'DEV', color: 'indigo' },
];

const techStack = [
  { name: 'Next.js 16', sub: 'React 19 + TS', color: 'blue', letter: 'N' },
  { name: 'FastAPI', sub: 'Python 3.11', color: 'emerald', letter: 'F' },
  { name: 'Cosmos DB', sub: 'NoSQL Storage', color: 'sky', letter: 'Az' },
  { name: 'Azure AI', sub: 'Model Router', color: 'purple', letter: 'AI' },
  { name: 'Blob Storage', sub: 'Large Files', color: 'orange', letter: 'B' },
  { name: 'AI Search', sub: 'Transcripts', color: 'indigo', letter: 'S' },
  { name: 'Docker', sub: 'Compose Stack', color: 'slate', letter: 'D' },
  { name: 'Shadcn UI', sub: 'Components', color: 'teal', letter: 'UI' },
];

const benefitCards = [
  {
    title: 'For Leadership',
    color: 'blue',
    items: [
      'Single dashboard for all agent initiatives',
      'Real-time budget tracking with optimization',
      'Complete audit trails for compliance',
      'Risk management through framework adherence',
    ],
  },
  {
    title: 'For Architects',
    color: 'purple',
    items: [
      'Technology radar for approved tools',
      'Proven Single & Multi-Agent architectures',
      'Shared governance decisions and rationale',
      'Dependency management across portfolio',
    ],
  },
  {
    title: 'For Development Teams',
    color: 'emerald',
    items: [
      'Clear requirements from meetings automatically',
      'Integrated task tracking with Kanban',
      'Knowledge base with patterns and practices',
      'Fourth AI Guide for instant context',
    ],
  },
  {
    title: 'For Operations',
    color: 'orange',
    items: [
      'Step-by-step deployment guides',
      'Agent status tracking Idea to Production',
      'Change management documentation',
      'Observability requirements in governance',
    ],
  },
];

const colorClasses: Record<string, { bg: string; text: string; border: string; hoverBorder: string; glow: string }> = {
  blue: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/50', hoverBorder: 'hover:border-blue-400', glow: 'shadow-blue-500/20' },
  purple: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/50', hoverBorder: 'hover:border-purple-400', glow: 'shadow-purple-500/20' },
  emerald: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500/50', hoverBorder: 'hover:border-emerald-400', glow: 'shadow-emerald-500/20' },
  orange: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/50', hoverBorder: 'hover:border-orange-400', glow: 'shadow-orange-500/20' },
  cyan: { bg: 'bg-cyan-500/20', text: 'text-cyan-400', border: 'border-cyan-500/50', hoverBorder: 'hover:border-cyan-400', glow: 'shadow-cyan-500/20' },
  amber: { bg: 'bg-amber-500/20', text: 'text-amber-400', border: 'border-amber-500/50', hoverBorder: 'hover:border-amber-400', glow: 'shadow-amber-500/20' },
  red: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/50', hoverBorder: 'hover:border-red-400', glow: 'shadow-red-500/20' },
  yellow: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/50', hoverBorder: 'hover:border-yellow-400', glow: 'shadow-yellow-500/20' },
  green: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/50', hoverBorder: 'hover:border-green-400', glow: 'shadow-green-500/20' },
  indigo: { bg: 'bg-indigo-500/20', text: 'text-indigo-400', border: 'border-indigo-500/50', hoverBorder: 'hover:border-indigo-400', glow: 'shadow-indigo-500/20' },
  sky: { bg: 'bg-sky-500/20', text: 'text-sky-400', border: 'border-sky-500/50', hoverBorder: 'hover:border-sky-400', glow: 'shadow-sky-500/20' },
  slate: { bg: 'bg-slate-500/20', text: 'text-slate-400', border: 'border-slate-500/50', hoverBorder: 'hover:border-slate-400', glow: 'shadow-slate-500/20' },
  teal: { bg: 'bg-teal-500/20', text: 'text-teal-400', border: 'border-teal-500/50', hoverBorder: 'hover:border-teal-400', glow: 'shadow-teal-500/20' },
};

function GlitchText({ text, className = '' }: { text: string; className?: string }) {
  const [glitchText, setGlitchText] = useState(text);

  useEffect(() => {
    const glitchChars = '!<>-_\\/[]{}—=+*^?#________';
    let iteration = 0;

    const interval = setInterval(() => {
      setGlitchText(
        text
          .split('')
          .map((char, index) => {
            if (index < iteration) {
              return text[index];
            }
            return glitchChars[Math.floor(Math.random() * glitchChars.length)];
          })
          .join('')
      );

      if (iteration >= text.length) {
        clearInterval(interval);
      }

      iteration += 1 / 3;
    }, 30);

    return () => clearInterval(interval);
  }, [text]);

  return <span className={className}>{glitchText}</span>;
}

export default function LandingPageV2() {
  const [mounted, setMounted] = useState(false);
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  const handleCardClick = (cardId: string) => {
    setExpandedCard(expandedCard === cardId ? null : cardId);
  };

  const closeExpandedCard = (e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedCard(null);
  };

  return (
    <div className="min-h-screen bg-black text-white relative overflow-hidden">
      <AsciiStarfield
        starCount={180}
        speed={0.25}
        color="#00ff88"
        glowColor="#00ff8822"
        showTechChars={true}
        opacity={0.35}
      />

      <div className="fixed inset-0 bg-gradient-to-b from-black/70 via-black/50 to-black/80 pointer-events-none z-[1]" />

      <div className="relative z-10">
        <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-black/40 border-b border-emerald-500/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-3">
                <Terminal className="w-5 h-5 text-emerald-400" />
                <Image src="/Fourth_teal_White_icon.png" alt="Fourth" width={28} height={28} className="h-7 w-auto" />
                <span className="font-mono text-emerald-400 tracking-wider">
                  FOURTH<span className="text-white">_</span><span className="text-blue-400">AGENT_ARCH</span>
                </span>
              </div>
              <div className="flex items-center gap-4">
                <Link href="/" className="px-4 py-2 bg-emerald-500/20 border border-emerald-500/50 hover:bg-emerald-500/30 text-emerald-400 rounded font-mono text-sm transition-colors">
                  [LAUNCH]
                </Link>
                <a href="#orientation" className="font-mono text-slate-400 hover:text-emerald-400 px-3 py-2 text-sm transition">[FEATURES]</a>
                <a href="#benefits" className="font-mono text-slate-400 hover:text-emerald-400 px-3 py-2 text-sm transition">[BENEFITS]</a>
              </div>
            </div>
          </div>
        </nav>

        <div className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-5xl mx-auto text-center">
            <div className="mb-6">
              <span className="font-mono text-xs text-emerald-400/80 tracking-[0.3em] uppercase">
                {'>'} SYSTEM_INITIALIZED // FOURTH_AI_PLATFORM
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl font-bold tracking-tight mb-6 font-mono">
              {mounted ? (
                <GlitchText text="GOVERN, SCALE & OPTIMIZE" className="text-white" />
              ) : (
                <span className="text-white">GOVERN, SCALE & OPTIMIZE</span>
              )}
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-cyan-400 to-blue-400">
                ENTERPRISE AI AGENTS
              </span>
            </h1>

            <p className="mt-4 text-lg text-slate-400 max-w-3xl mx-auto mb-4 font-mono leading-relaxed">
              <span className="text-white">Microsoft Ignite 2025 rearchitected the agent ecosystem.</span>{' '}
              Your unified command center for{' '}
              <span className="text-purple-400">Foundry</span>,{' '}
              <span className="text-blue-400">Agent Framework</span>,{' '}
              <span className="text-cyan-400">Foundry IQ</span>,{' '}
              <span className="text-amber-400">Model Router</span>,{' '}
              <span className="text-emerald-400">M365 SDK</span>, and{' '}
              <span className="text-orange-400">Agent 365</span>.
            </p>

            <p className="text-slate-500 mb-10 font-mono text-sm">
              // governance | budgets | portfolio | transcripts | all_in_one
            </p>

            <div className="flex justify-center gap-4">
              <Link
                href="/"
                className="group px-8 py-3 rounded bg-emerald-500/20 border border-emerald-500/50 hover:bg-emerald-500/30 hover:border-emerald-400 text-emerald-400 font-mono font-semibold transition-all flex items-center gap-2"
              >
                OPEN_PLATFORM
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <a
                href="#orientation"
                className="px-8 py-3 rounded bg-slate-900/70 border border-slate-700 hover:border-slate-600 text-slate-300 font-mono font-semibold transition-all"
              >
                EXPLORE_FEATURES
              </a>
            </div>
          </div>
        </div>

        <div id="orientation" className="bg-black/50 py-20 border-y border-emerald-500/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <span className="font-mono text-xs text-emerald-400/80 tracking-[0.3em] uppercase mb-4 block">
                {'>'} LOADING_DOCUMENTATION
              </span>
              <h2 className="text-3xl font-bold text-white mb-4 font-mono">GET <span className="text-emerald-400">ORIENTED</span></h2>
              <p className="text-slate-400 max-w-2xl mx-auto font-mono text-sm">
                // Understanding the Microsoft agent ecosystem: tools to build + platform to manage
              </p>
            </div>

            {expandedCard ? (
              <div className="flex flex-col md:flex-row gap-6 items-start">
                <div className="w-full md:w-[65%]">
                  {orientationCards.filter(c => c.id === expandedCard).map((card) => {
                    const colors = colorClasses[card.color];
                    return (
                      <div
                        key={card.id}
                        className={`relative bg-slate-900/80 backdrop-blur border ${colors.border} rounded-xl p-6 cursor-pointer transition-all duration-300 shadow-lg ${colors.glow}`}
                        onClick={() => handleCardClick(card.id)}
                      >
                        <button
                          onClick={closeExpandedCard}
                          className="absolute top-4 right-4 w-8 h-8 rounded bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-emerald-400 transition-all flex items-center justify-center z-10 font-mono"
                        >
                          <X className="w-5 h-5" />
                        </button>
                        <div className="flex items-start justify-between mb-4 pr-12">
                          <h3 className={`text-xl font-bold ${colors.text} font-mono`}>{card.title}</h3>
                          <span className={`px-2 py-1 rounded text-xs font-mono font-semibold ${colors.bg} ${colors.text} border ${colors.border}`}>[{card.badge}]</span>
                        </div>
                        <p className="text-slate-300 text-sm mb-4 font-mono">{card.summary}</p>
                        <div className="space-y-2 text-sm text-slate-400 font-mono">
                          {card.bullets.map((bullet, i) => (
                            <div key={i} className="flex items-start">
                              <span className={`${colors.text} mr-2 mt-0.5`}>*</span>
                              <span>{bullet}</span>
                            </div>
                          ))}
                        </div>
                        <div className="mt-6 space-y-6 text-sm">
                          {card.expandedSections.map((section, i) => (
                            <div key={i}>
                              <h4 className={`text-md font-bold ${colors.text} mb-2 font-mono`}>// {section.title}</h4>
                              {section.content}
                            </div>
                          ))}
                          {card.resources && card.resources.length > 0 && (
                            <div className="mt-6 pt-4 border-t border-emerald-500/20">
                              <p className="text-xs font-mono font-semibold text-slate-500 mb-2">// RESOURCES</p>
                              <div className="flex flex-wrap gap-2">
                                {card.resources.map((resource, i) => (
                                  <a
                                    key={i}
                                    href={resource.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    onClick={(e) => e.stopPropagation()}
                                    className={`inline-flex items-center ${colors.text} hover:underline text-xs font-mono`}
                                  >
                                    [{resource.label}]
                                    <ExternalLink className="w-3 h-3 ml-1" />
                                  </a>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
                <div className="w-full md:w-[35%] flex flex-col gap-4">
                  {orientationCards.filter(c => c.id !== expandedCard).map((card) => {
                    const colors = colorClasses[card.color];
                    return (
                      <div
                        key={card.id}
                        className={`bg-slate-900/60 backdrop-blur border border-slate-700/50 ${colors.hoverBorder} rounded-xl p-4 cursor-pointer transition-all duration-300 hover:shadow-lg ${colors.glow}`}
                        onClick={() => handleCardClick(card.id)}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="text-lg font-bold text-white font-mono">{card.title}</h3>
                          <span className={`px-2 py-1 rounded text-xs font-mono font-semibold ${colors.bg} ${colors.text}`}>[{card.badge}]</span>
                        </div>
                        <div className="space-y-1.5 text-xs text-slate-400 font-mono">
                          {card.bullets.slice(0, 2).map((bullet, i) => (
                            <div key={i} className="flex items-start">
                              <span className={`${colors.text} mr-1.5`}>*</span>
                              <span className="line-clamp-1">{bullet}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {orientationCards.map((card) => {
                  const colors = colorClasses[card.color];
                  return (
                    <div
                      key={card.id}
                      className={`bg-slate-900/60 backdrop-blur border border-slate-700/50 ${colors.hoverBorder} rounded-xl p-6 cursor-pointer transition-all duration-300 hover:shadow-lg ${colors.glow}`}
                      onClick={() => handleCardClick(card.id)}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <h3 className="text-xl font-bold text-white font-mono">{card.title}</h3>
                        <span className={`px-2 py-1 rounded text-xs font-mono font-semibold ${colors.bg} ${colors.text} border ${colors.border}`}>[{card.badge}]</span>
                      </div>
                      <p className="text-slate-300 text-sm mb-4 font-mono">{card.summary}</p>
                      <div className="space-y-2 text-sm text-slate-400 font-mono">
                        {card.bullets.map((bullet, i) => (
                          <div key={i} className="flex items-start">
                            <span className={`${colors.text} mr-2 mt-0.5`}>*</span>
                            <span>{bullet}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>

        <div className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <span className="font-mono text-xs text-emerald-400/80 tracking-[0.3em] uppercase mb-4 block">
                {'>'} CAPABILITIES_LOADED
              </span>
              <h2 className="text-3xl font-bold text-white mb-4 font-mono">PLATFORM <span className="text-emerald-400">CAPABILITIES</span></h2>
              <p className="text-slate-400 max-w-2xl mx-auto font-mono text-sm">
                // Comprehensive tools for managing the complete AI agent lifecycle
              </p>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {platformCapabilities.map((cap) => {
                const Icon = cap.icon;
                const colors = colorClasses[cap.color];

                return (
                  <div
                    key={cap.name}
                    className={`bg-slate-900/50 backdrop-blur border border-slate-700/50 rounded-xl p-6 ${colors.hoverBorder} transition-all group hover:shadow-lg ${colors.glow}`}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className={`w-10 h-10 ${colors.bg} rounded-lg flex items-center justify-center border ${colors.border}`}>
                        <Icon className={`h-5 w-5 ${colors.text}`} />
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-mono font-semibold ${colors.bg} ${colors.text}`}>[{cap.badge}]</span>
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2 font-mono">{cap.name}</h3>
                    <p className="text-slate-400 text-sm font-mono">{cap.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="py-16 border-t border-emerald-500/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <span className="font-mono text-xs text-emerald-400/80 tracking-[0.3em] uppercase mb-4 block">
                {'>'} TECH_STACK_INFO
              </span>
              <h2 className="text-3xl font-bold text-white mb-4 font-mono">ENTERPRISE-GRADE <span className="text-emerald-400">TECHNOLOGY</span></h2>
              <p className="text-slate-400 max-w-2xl mx-auto font-mono text-sm">
                // Modern stack: Next.js + FastAPI + Azure // scalability + performance + security
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {techStack.map((tech) => {
                const colors = colorClasses[tech.color];
                return (
                  <div
                    key={tech.name}
                    className={`bg-slate-900/50 backdrop-blur border border-slate-700/50 rounded-lg p-4 flex items-center gap-3 ${colors.hoverBorder} transition-all group hover:shadow-lg ${colors.glow}`}
                  >
                    <div className={`w-10 h-10 ${colors.bg} rounded flex items-center justify-center font-mono font-bold ${colors.text} text-xs group-hover:scale-110 transition-transform border ${colors.border}`}>
                      {tech.letter}
                    </div>
                    <div>
                      <div className="font-mono font-semibold text-white text-sm">{tech.name}</div>
                      <div className="font-mono text-xs text-slate-500">{tech.sub}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div id="benefits" className="py-20 bg-black/50 border-y border-emerald-500/20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <span className="font-mono text-xs text-emerald-400/80 tracking-[0.3em] uppercase mb-4 block">
                {'>'} VALUE_PROPOSITION
              </span>
              <h2 className="text-3xl font-bold text-white font-mono">
                WHY TEAMS CHOOSE <span className="text-emerald-400">AGENT ARCH</span>
              </h2>
            </div>
            <div className="grid md:grid-cols-2 gap-8">
              {benefitCards.map((card) => {
                const colors = colorClasses[card.color];
                return (
                  <div
                    key={card.title}
                    className={`bg-slate-900/50 backdrop-blur border border-slate-700/50 rounded-xl p-6 ${colors.hoverBorder} transition-all group hover:shadow-lg ${colors.glow}`}
                  >
                    <h4 className="text-lg font-bold text-white mb-3 flex items-center font-mono">
                      <span className={`${colors.text} mr-2`}>[*]</span>
                      {card.title}
                    </h4>
                    <ul className="text-slate-400 text-sm space-y-2 font-mono">
                      {card.items.map((item, i) => (
                        <li key={i} className="flex items-start">
                          <span className={`${colors.text} mr-2`}>-</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        <div className="py-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full font-mono text-xs text-emerald-400 mb-8">
              <Terminal className="w-4 h-4" />
              SYSTEM_READY
            </div>

            <h2 className="text-3xl font-bold text-white mb-6 font-mono">
              READY TO <span className="text-emerald-400">SCALE</span> YOUR AI ECOSYSTEM?
            </h2>

            <p className="text-lg text-slate-400 mb-10 font-mono">
              // Join Fourth&apos;s enterprise teams in building a governed, scalable foundation for Microsoft Agent Framework adoption
            </p>

            <Link
              href="/"
              className="inline-flex items-center gap-2 px-10 py-4 bg-emerald-500 text-black font-mono font-bold rounded hover:bg-emerald-400 transition-colors"
            >
              <Terminal className="w-5 h-5" />
              LAUNCH_PLATFORM_NOW
            </Link>

            <p className="text-slate-600 text-sm mt-8 font-mono">
              // agent_architecture_guide // enterprise_ai_governance
            </p>
          </div>
        </div>

        <footer className="border-t border-emerald-500/20 py-8 bg-black/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center font-mono">
            <p className="text-slate-500 text-sm">
              Fourth AI Architect Team // Enterprise Agent Architecture Guide
            </p>
            <p className="mt-2 text-slate-600 text-xs">
              Built with <span className="text-blue-400">Next.js</span> + <span className="text-emerald-400">FastAPI</span> + <span className="text-purple-400">Azure AI Foundry</span>
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
