'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import Image from 'next/image';
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
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3 text-xs">
              <p className="text-slate-300 mb-1"><strong>Runtime:</strong> Built on the <strong>Foundry Agent Service</strong></p>
              <p className="text-slate-400 mb-1">A serverless runtime optimized for long-running, stateful agent processes (not just stateless API calls)</p>
              <p className="text-slate-400"><strong>Languages:</strong> .NET (C#) and Python</p>
            </div>
          </>
        ),
      },
      {
        title: 'Key Capabilities',
        content: (
          <>
            <p className="text-slate-300 text-xs font-semibold mb-1">Single Agents</p>
            <ul className="text-slate-400 space-y-0.5 text-xs mb-3">
              <li>• Autonomous decision-making with tool calling</li>
              <li>• Context-aware reasoning with memory systems</li>
              <li>• Built-in support for prompt engineering patterns</li>
            </ul>
            <p className="text-slate-300 text-xs font-semibold mb-1">Multi-Agent Orchestration</p>
            <ul className="text-slate-400 space-y-0.5 text-xs mb-3">
              <li>• <strong>Router Pattern:</strong> Route tasks to specialized agents</li>
              <li>• <strong>Crew Pattern:</strong> Agents collaborate as a team</li>
              <li>• <strong>Manager-Worker Pattern:</strong> Hierarchical agent structures</li>
              <li>• Graph-based workflows with conditional routing</li>
            </ul>
            <p className="text-slate-300 text-xs font-semibold mb-1">Memory & State Management</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>• Short-term memory: Conversation history</li>
              <li>• Long-term memory: Entity extraction and storage</li>
              <li>• Built-in handling without external databases</li>
            </ul>
          </>
        ),
      },
      {
        title: 'MCP Integration 🔗',
        content: (
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
            <p className="text-yellow-300 font-semibold text-xs mb-1">Native Model Context Protocol Support</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>• Dynamic discovery of tools and data sources</li>
              <li>• No custom connectors required for MCP-enabled services</li>
              <li>• Shared ecosystem of capabilities across agents</li>
            </ul>
          </div>
        ),
      },
      {
        title: 'Code-First & Low-Code',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs">
            <li>• <strong>Pure Code:</strong> Full Python/C# control for complex logic</li>
            <li>• <strong>Low-Code:</strong> Visual configuration via Foundry portal</li>
            <li>• <strong>Hybrid:</strong> Combine both approaches in same agent</li>
          </ul>
        ),
      },
      {
        title: 'Quick Start',
        content: (
          <ol className="text-slate-400 space-y-0.5 text-xs">
            <li>1. Install: <code className="bg-slate-800 px-1 rounded text-blue-300">pip install microsoft-agent-framework</code> or NuGet</li>
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
            <p className="text-slate-300 mb-2">
              <strong>Formerly:</strong> Azure AI Foundry / Azure AI Studio<br/>
              <strong>Now:</strong> Microsoft Foundry
            </p>
            <p className="text-slate-400 text-xs">
              Microsoft Foundry is the unified IDE where agents are designed, prototyped, and built. It&apos;s the &quot;Workshop&quot; for AI developers—a single place to access models, design prompts, test agent behavior, and deploy to production.
            </p>
          </>
        ),
      },
      {
        title: 'Unified Model Catalog',
        content: (
          <>
            <p className="text-slate-300 text-xs mb-2"><strong>1,800+ Models Available</strong></p>
            <ul className="text-slate-400 space-y-1 text-xs">
              <li>• <strong>Claude 4.5 Sonnet</strong> 🆕 (NEW at Ignite 2025)</li>
              <li>• GPT-5, o1, o3-mini (OpenAI reasoning models)</li>
              <li>• Gemini 2.0, Llama 3.3, Phi-4</li>
              <li>• Specialized: Vision, embeddings, speech, code</li>
            </ul>
            <p className="text-slate-400 text-xs mt-2">
              <strong>Model Types:</strong> Foundational (base reasoning), Open Source (Llama, Mistral), Reasoning (o1, o3), Multimodal (vision, audio, documents)
            </p>
          </>
        ),
      },
      {
        title: 'Foundry Agent Service (The Runtime)',
        content: (
          <>
            <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-3">
              <p className="text-slate-300 text-xs mb-1">
                <strong>What It Is:</strong> Serverless execution environment for agents
              </p>
              <ul className="text-slate-400 space-y-0.5 text-xs">
                <li>• Agent-native (optimized for stateful, long-running processes)</li>
                <li>• Auto-scaling based on agent load</li>
                <li>• Built-in memory and state management</li>
              </ul>
            </div>
            <p className="text-slate-400 text-xs mt-2">
              <strong>Why It Matters:</strong> Traditional APIs are stateless (request/response). Agents need to &quot;think&quot; across multiple turns. Foundry Agent Service handles this complexity.
            </p>
          </>
        ),
      },
      {
        title: 'Design & Test Tools',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs">
            <li>• <strong>Prompt Flow:</strong> Drag-and-drop agent logic design, visual debugging</li>
            <li>• <strong>Evaluation Studio:</strong> Test against &quot;Golden Datasets&quot;, compare model versions</li>
            <li>• <strong>Agent Loop:</strong> Rapid prototyping in Teams-like environment</li>
          </ul>
        ),
      },
      {
        title: 'MCP Native Support 🔗',
        content: (
          <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-3">
            <p className="text-yellow-300 font-semibold text-xs mb-1">The Universal Connector</p>
            <p className="text-slate-400 text-xs mb-2">
              <strong>Problem Solved:</strong> Previously, connecting to Salesforce, GitHub, SQL required 3 custom connectors.
            </p>
            <p className="text-slate-400 text-xs">
              <strong>MCP Solution:</strong> If a tool/data source exposes an MCP server, agents can discover and use it instantly. No custom connectors required for MCP-enabled services.
            </p>
          </div>
        ),
      },
      {
        title: 'Why Foundry vs Others',
        content: (
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-slate-700">
                  <th className="text-left text-slate-400 pb-2 pr-2">Feature</th>
                  <th className="text-left text-purple-400 pb-2 pr-2">Microsoft Foundry</th>
                  <th className="text-left text-slate-400 pb-2 pr-2">Vertex AI</th>
                  <th className="text-left text-slate-400 pb-2">Bedrock</th>
                </tr>
              </thead>
              <tbody className="text-slate-400">
                <tr className="border-b border-slate-700/50">
                  <td className="py-2 pr-2">Multi-vendor models</td>
                  <td className="py-2 pr-2 text-emerald-400">✅ 1,800+</td>
                  <td className="py-2 pr-2">Limited</td>
                  <td className="py-2">AWS only</td>
                </tr>
                <tr className="border-b border-slate-700/50">
                  <td className="py-2 pr-2">Agent-native runtime</td>
                  <td className="py-2 pr-2 text-emerald-400">✅</td>
                  <td className="py-2 pr-2 text-red-400">❌</td>
                  <td className="py-2 text-red-400">❌</td>
                </tr>
                <tr className="border-b border-slate-700/50">
                  <td className="py-2 pr-2">MCP support</td>
                  <td className="py-2 pr-2 text-emerald-400">✅ Native</td>
                  <td className="py-2 pr-2 text-red-400">❌</td>
                  <td className="py-2 text-red-400">❌</td>
                </tr>
                <tr>
                  <td className="py-2 pr-2">M365 integration</td>
                  <td className="py-2 pr-2 text-emerald-400">✅ Seamless</td>
                  <td className="py-2 pr-2 text-red-400">❌</td>
                  <td className="py-2 text-red-400">❌</td>
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
            <p className="text-slate-300 mb-2">
              The <strong>M365 Agent SDK</strong> is the bridge that turns a raw AI agent into a deployable &quot;app&quot; that can live inside Microsoft Teams, Copilot, or Outlook. It ensures agents are &quot;Agent 365 Compliant.&quot;
            </p>
            <p className="text-slate-400 text-xs">
              <strong>Think of it as:</strong> The packaging that makes your agent fit onto the Microsoft 365 truck and ensures it can be tracked by IT.
            </p>
          </>
        ),
      },
      {
        title: 'Standardized Packaging',
        content: (
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div>
              <p className="text-slate-300 font-semibold mb-1">What Gets Packaged</p>
              <ul className="text-slate-400 space-y-0.5">
                <li>• Agent logic (from Framework/Foundry)</li>
                <li>• Manifest file (capabilities, permissions)</li>
                <li>• Configuration (channel-specific settings)</li>
                <li>• Dependencies and resources</li>
              </ul>
            </div>
            <div>
              <p className="text-slate-300 font-semibold mb-1">Output</p>
              <ul className="text-slate-400 space-y-0.5">
                <li>• .zip file ready for deployment</li>
                <li>• Agent Store submission package</li>
                <li>• Custom app installation bundle</li>
              </ul>
            </div>
          </div>
        ),
      },
      {
        title: 'Telemetry Emission (Agent 365 Requirement)',
        content: (
          <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3">
            <p className="text-emerald-300 font-semibold text-xs mb-1">Automatic Signals</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>• <strong>User ID:</strong> Who used the agent</li>
              <li>• <strong>Token usage:</strong> Cost tracking</li>
              <li>• <strong>Latency:</strong> Performance monitoring</li>
              <li>• <strong>Tool calls:</strong> What the agent accessed</li>
              <li>• <strong>Error rates:</strong> Reliability metrics</li>
            </ul>
            <p className="text-slate-400 text-xs mt-2">
              <strong>Why This Matters:</strong> Agent 365 requires this data for fleet observability. Without SDK telemetry, agents are &quot;invisible&quot; to IT.
            </p>
          </div>
        ),
      },
      {
        title: 'Agent Loop (Rapid Prototyping)',
        content: (
          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
            <p className="text-blue-300 font-semibold text-xs mb-1">Lightweight testing environment</p>
            <p className="text-slate-400 text-xs mb-2">Mimics Teams/Copilot experience. No deployment required.</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>• Test agent responses in real-time</li>
              <li>• Debug tool calls and reasoning</li>
              <li>• Iterate quickly before deployment</li>
            </ul>
          </div>
        ),
      },
      {
        title: 'Channel Customization',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs">
            <li>• <strong>Teams:</strong> Adaptive Cards, tabs, message extensions</li>
            <li>• <strong>Copilot:</strong> Native integration, context awareness</li>
            <li>• <strong>Web:</strong> Embeddable widget, custom styling</li>
            <li>• <strong>Outlook:</strong> Email-triggered actions, calendar integration</li>
          </ul>
        ),
      },
      {
        title: 'Technology Agnostic',
        content: (
          <>
            <p className="text-slate-400 text-xs mb-2">The SDK doesn&apos;t care how you built the agent:</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>• Microsoft Agent Framework (.NET/Python)</li>
              <li>• LangChain/LlamaIndex</li>
              <li>• Custom implementation</li>
              <li>• Any LLM provider (OpenAI, Anthropic, etc.)</li>
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
            <p className="text-slate-300 mb-2">
              <strong>Microsoft Agent 365</strong> is the management and observability plane for AI agents across your organization. Think of it as the &quot;Air Traffic Control&quot; that ensures agents are visible, compliant, and cost-managed.
            </p>
            <div className="bg-orange-500/10 border border-orange-500/20 rounded-lg p-3 text-xs">
              <p className="text-orange-300 font-semibold mb-1">🆕 Announced at Ignite 2025</p>
              <p className="text-slate-400">Expected GA: H1 2025. Currently in private preview with select customers.</p>
            </div>
          </>
        ),
      },
      {
        title: 'Fleet Observability',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs">
            <li>• <strong>Agent Inventory:</strong> See every agent deployed (first-party, third-party, custom)</li>
            <li>• <strong>Usage Metrics:</strong> Who is using which agents, how often</li>
            <li>• <strong>Health Monitoring:</strong> Latency, error rates, availability</li>
            <li>• <strong>Cost Dashboard:</strong> Token usage, model costs per agent</li>
          </ul>
        ),
      },
      {
        title: 'Security & Compliance',
        content: (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
            <p className="text-red-300 font-semibold text-xs mb-1">Enterprise-Grade Controls</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>• <strong>DLP Integration:</strong> Prevent sensitive data leakage</li>
              <li>• <strong>Access Policies:</strong> Who can use which agents</li>
              <li>• <strong>Audit Logs:</strong> Every agent action logged for compliance</li>
              <li>• <strong>Data Residency:</strong> Control where agent data is processed</li>
            </ul>
          </div>
        ),
      },
      {
        title: 'Governance Framework',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs">
            <li>• <strong>Agent Approval Workflow:</strong> IT approves before deployment</li>
            <li>• <strong>Capability Restrictions:</strong> Limit what agents can access</li>
            <li>• <strong>Model Allowlisting:</strong> Only approved models can be used</li>
            <li>• <strong>Usage Quotas:</strong> Prevent runaway costs</li>
          </ul>
        ),
      },
      {
        title: 'Before/After Comparison',
        content: (
          <div className="grid grid-cols-2 gap-3 text-xs">
            <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3">
              <p className="text-red-300 font-semibold mb-1">Before Agent 365</p>
              <ul className="text-slate-400 space-y-0.5">
                <li>• Shadow AI agents everywhere</li>
                <li>• No visibility into costs</li>
                <li>• Security/compliance blind spots</li>
                <li>• Fragmented management</li>
              </ul>
            </div>
            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded-lg p-3">
              <p className="text-emerald-300 font-semibold mb-1">With Agent 365</p>
              <ul className="text-slate-400 space-y-0.5">
                <li>• Complete fleet visibility</li>
                <li>• Cost allocation by team/project</li>
                <li>• Centralized policy enforcement</li>
                <li>• Single pane of glass</li>
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
            <p className="text-slate-300 mb-2">
              <strong>Foundry IQ</strong> is Microsoft&apos;s answer to the RAG (Retrieval-Augmented Generation) challenge. Instead of building custom retrieval pipelines, agents can tap into pre-indexed enterprise knowledge automatically.
            </p>
            <p className="text-slate-400 text-xs">
              <strong>Think of it as:</strong> A librarian that has already organized all your company&apos;s documents and can instantly find relevant context for any agent query.
            </p>
          </>
        ),
      },
      {
        title: 'Why It Matters',
        content: (
          <div className="bg-cyan-500/10 border border-cyan-500/20 rounded-lg p-3">
            <p className="text-cyan-300 font-semibold text-xs mb-1">The RAG Problem</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>• Building retrieval pipelines is 60% of agent dev time</li>
              <li>• Chunking, embedding, indexing, ranking—complex work</li>
              <li>• Every agent reinvents the same wheel</li>
            </ul>
            <p className="text-emerald-300 font-semibold text-xs mt-2 mb-1">Foundry IQ Solution</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>• Pre-built indexing of enterprise content</li>
              <li>• Agents just &quot;ask&quot; for relevant documents</li>
              <li>• No custom retrieval code required</li>
            </ul>
          </div>
        ),
      },
      {
        title: 'Architecture',
        content: (
          <>
            <p className="text-slate-300 text-xs font-semibold mb-1">Work IQ (M365 Content)</p>
            <ul className="text-slate-400 space-y-0.5 text-xs mb-3">
              <li>• SharePoint sites and document libraries</li>
              <li>• OneDrive files and folders</li>
              <li>• Teams messages and meeting transcripts</li>
              <li>• Outlook emails (with permissions)</li>
            </ul>
            <p className="text-slate-300 text-xs font-semibold mb-1">Fabric IQ (Analytics Data)</p>
            <ul className="text-slate-400 space-y-0.5 text-xs">
              <li>• Power BI datasets and reports</li>
              <li>• Fabric lakehouse tables</li>
              <li>• SQL databases via connectors</li>
            </ul>
          </>
        ),
      },
      {
        title: 'Implementation Workflow',
        content: (
          <ol className="text-slate-400 space-y-1 text-xs">
            <li>1. <strong>Connect:</strong> Point IQ at your M365/Fabric sources</li>
            <li>2. <strong>Index:</strong> Automatic chunking and embedding (managed)</li>
            <li>3. <strong>Secure:</strong> Respects existing M365 permissions</li>
            <li>4. <strong>Query:</strong> Agents call IQ via API or MCP</li>
            <li>5. <strong>Ground:</strong> Responses cite sources for transparency</li>
          </ol>
        ),
      },
      {
        title: 'Strategic Value',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs">
            <li>• <strong>Faster Development:</strong> Skip 60% of RAG work</li>
            <li>• <strong>Better Quality:</strong> Microsoft-optimized retrieval</li>
            <li>• <strong>Permission Aware:</strong> Users only see what they&apos;re allowed to</li>
            <li>• <strong>Always Current:</strong> Auto-sync with source changes</li>
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
            <p className="text-slate-300 mb-2">
              <strong>Model Router</strong> sits between your agent and the model catalog. Instead of hardcoding which model to use, you describe your requirements and Router picks the best option dynamically.
            </p>
            <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3 text-xs">
              <p className="text-amber-300 font-semibold mb-1">✅ GA at Ignite 2025</p>
              <p className="text-slate-400">Available now in Microsoft Foundry. No additional cost for routing logic.</p>
            </div>
          </>
        ),
      },
      {
        title: 'Use Case Examples',
        content: (
          <div className="space-y-2 text-xs">
            <div className="bg-slate-800/50 rounded p-2">
              <p className="text-slate-300 font-semibold">Simple Query: &quot;What&apos;s 2+2?&quot;</p>
              <p className="text-slate-400">→ Routes to Phi-4 (cheap, fast)</p>
            </div>
            <div className="bg-slate-800/50 rounded p-2">
              <p className="text-slate-300 font-semibold">Complex Analysis: &quot;Analyze Q3 revenue trends&quot;</p>
              <p className="text-slate-400">→ Routes to GPT-5 or Claude 4.5 Sonnet</p>
            </div>
            <div className="bg-slate-800/50 rounded p-2">
              <p className="text-slate-300 font-semibold">Reasoning Task: &quot;Prove this theorem&quot;</p>
              <p className="text-slate-400">→ Routes to o1 or o3-mini</p>
            </div>
          </div>
        ),
      },
      {
        title: '3 Optimization Modes',
        content: (
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="bg-emerald-500/10 border border-emerald-500/20 rounded p-2 text-center">
              <p className="text-emerald-300 font-semibold">Cost</p>
              <p className="text-slate-400">Cheapest model that can handle the task</p>
            </div>
            <div className="bg-amber-500/10 border border-amber-500/20 rounded p-2 text-center">
              <p className="text-amber-300 font-semibold">Balanced</p>
              <p className="text-slate-400">Best cost/quality tradeoff</p>
            </div>
            <div className="bg-purple-500/10 border border-purple-500/20 rounded p-2 text-center">
              <p className="text-purple-300 font-semibold">Quality</p>
              <p className="text-slate-400">Best model regardless of cost</p>
            </div>
          </div>
        ),
      },
      {
        title: 'Key Features',
        content: (
          <ul className="text-slate-400 space-y-1 text-xs">
            <li>• <strong>Task Classification:</strong> Automatically detects complexity</li>
            <li>• <strong>Fallback Chains:</strong> If Model A fails, try Model B</li>
            <li>• <strong>Latency Constraints:</strong> Route to fastest model under deadline</li>
            <li>• <strong>Cost Budgets:</strong> Stay within per-request spend limits</li>
            <li>• <strong>A/B Testing:</strong> Compare model performance in production</li>
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

const colorClasses: Record<string, { bg: string; text: string; border: string; hoverBorder: string }> = {
  blue: { bg: 'bg-blue-500/20', text: 'text-blue-400', border: 'border-blue-500/50', hoverBorder: 'hover:border-blue-500/50' },
  purple: { bg: 'bg-purple-500/20', text: 'text-purple-400', border: 'border-purple-500/50', hoverBorder: 'hover:border-purple-500/50' },
  emerald: { bg: 'bg-emerald-500/20', text: 'text-emerald-400', border: 'border-emerald-500/50', hoverBorder: 'hover:border-emerald-500/50' },
  orange: { bg: 'bg-orange-500/20', text: 'text-orange-400', border: 'border-orange-500/50', hoverBorder: 'hover:border-orange-500/50' },
  cyan: { bg: 'bg-cyan-500/20', text: 'text-cyan-400', border: 'border-cyan-500/50', hoverBorder: 'hover:border-cyan-500/50' },
  amber: { bg: 'bg-amber-500/20', text: 'text-amber-400', border: 'border-amber-500/50', hoverBorder: 'hover:border-amber-500/50' },
  red: { bg: 'bg-red-500/20', text: 'text-red-400', border: 'border-red-500/50', hoverBorder: 'hover:border-red-500/50' },
  yellow: { bg: 'bg-yellow-500/20', text: 'text-yellow-400', border: 'border-yellow-500/50', hoverBorder: 'hover:border-yellow-500/50' },
  green: { bg: 'bg-green-500/20', text: 'text-green-400', border: 'border-green-500/50', hoverBorder: 'hover:border-green-500/50' },
  indigo: { bg: 'bg-indigo-500/20', text: 'text-indigo-400', border: 'border-indigo-500/50', hoverBorder: 'hover:border-indigo-500/50' },
  sky: { bg: 'bg-sky-500/20', text: 'text-sky-400', border: 'border-sky-500/50', hoverBorder: 'hover:border-sky-500/50' },
  slate: { bg: 'bg-slate-500/20', text: 'text-slate-400', border: 'border-slate-500/50', hoverBorder: 'hover:border-slate-500/50' },
  teal: { bg: 'bg-teal-500/20', text: 'text-teal-400', border: 'border-teal-500/50', hoverBorder: 'hover:border-teal-500/50' },
};

export default function LandingPage() {
  const [floatingNodes, setFloatingNodes] = useState<Array<{ x: number; y: number; delay: number; size: number; driftX: number; driftY: number; duration: number }>>([]);
  const [expandedCard, setExpandedCard] = useState<string | null>(null);

  useEffect(() => {
    const nodes = Array.from({ length: 30 }, () => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 5,
      size: Math.random() * 3 + 1,
      driftX: (Math.random() - 0.5) * 30,
      driftY: (Math.random() - 0.5) * 30,
      duration: 15 + Math.random() * 15,
    }));
    setFloatingNodes(nodes);
  }, []);

  const handleCardClick = (cardId: string) => {
    setExpandedCard(expandedCard === cardId ? null : cardId);
  };

  const closeExpandedCard = (e: React.MouseEvent) => {
    e.stopPropagation();
    setExpandedCard(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-emerald-950 via-slate-900 to-slate-950 relative overflow-hidden">
      {/* Floating circuit nodes with drift animation */}
      {floatingNodes.map((node, i) => (
        <div
          key={i}
          className="absolute bg-emerald-400/30 rounded-full pointer-events-none"
          style={{
            left: `${node.x}%`,
            top: `${node.y}%`,
            width: `${node.size * 4}px`,
            height: `${node.size * 4}px`,
            animation: `float-drift-${i % 4} ${node.duration}s ease-in-out infinite, pulse-glow 3s ease-in-out infinite`,
            animationDelay: `${node.delay}s`,
          }}
        />
      ))}

      {/* Connection lines background with flowing animation */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-15">
        <defs>
          <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10b981" />
            <stop offset="100%" stopColor="#64748b" />
          </linearGradient>
        </defs>
        {floatingNodes.slice(0, 15).map((node, i) => (
          <line
            key={i}
            x1={`${node.x}%`}
            y1={`${node.y}%`}
            x2={`${floatingNodes[(i + 1) % 15].x}%`}
            y2={`${floatingNodes[(i + 1) % 15].y}%`}
            stroke="url(#lineGrad)"
            strokeWidth="1"
            strokeDasharray="8 4"
            style={{
              animation: `line-flow ${8 + i * 0.5}s linear infinite`,
              animationDelay: `${i * 0.3}s`,
            }}
          />
        ))}
      </svg>

      {/* CSS Keyframes for animations */}
      <style jsx>{`
        @keyframes float-drift-0 {
          0%, 100% { transform: translate(0, 0); }
          50% { transform: translate(15px, -20px); }
        }
        @keyframes float-drift-1 {
          0%, 100% { transform: translate(0, 0); }
          50% { transform: translate(-20px, 15px); }
        }
        @keyframes float-drift-2 {
          0%, 100% { transform: translate(0, 0); }
          50% { transform: translate(20px, 10px); }
        }
        @keyframes float-drift-3 {
          0%, 100% { transform: translate(0, 0); }
          50% { transform: translate(-10px, -15px); }
        }
        @keyframes pulse-glow {
          0%, 100% { opacity: 0.3; transform: scale(1); }
          50% { opacity: 0.6; transform: scale(1.1); }
        }
        @keyframes line-flow {
          0% { stroke-dashoffset: 24; }
          100% { stroke-dashoffset: 0; }
        }
      `}</style>

      <div className="relative z-10">
        {/* Navigation */}
        <nav className="fixed top-0 left-0 right-0 z-50 bg-slate-900/80 backdrop-blur-md border-b border-slate-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-between h-16">
              <div className="flex items-center gap-3">
                <Image src="/Fourth_teal_White_icon.png" alt="Fourth" width={32} height={32} className="h-8 w-auto" />
                <span className="text-white font-semibold">Fourth <span className="text-blue-400">Agent Architecture</span></span>
              </div>
              <div className="flex items-center gap-4">
                <Link href="/" className="px-4 py-2 bg-emerald-600 hover:bg-emerald-500 text-white rounded-lg font-medium transition-colors">
                  Launch Platform
                </Link>
                <a href="#orientation" className="text-slate-300 hover:text-white px-3 py-2 text-sm font-medium transition">Features</a>
                <a href="#benefits" className="text-slate-300 hover:text-white px-3 py-2 text-sm font-medium transition">Benefits</a>
              </div>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <div className="pt-32 pb-20 px-4 sm:px-6 lg:px-8">
          <div className="max-w-5xl mx-auto text-center">
            <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight mb-6">
              <span className="text-white">Govern, Scale & Optimize</span>
              <br />
              <span className="bg-gradient-to-r from-blue-400 via-purple-400 to-cyan-400 text-transparent bg-clip-text">
                Enterprise AI Agent Ecosystems
              </span>
            </h1>
            <p className="mt-4 text-xl text-slate-400 max-w-3xl mx-auto mb-4">
              <span className="text-white font-semibold">Microsoft Ignite 2025 rearchitected the agent ecosystem.</span>{' '}
              This is your unified command center for managing adoption and rollout across{' '}
              <span className="text-purple-400 font-semibold">Microsoft Foundry</span>,{' '}
              <span className="text-blue-400 font-semibold">Agent Framework</span>,{' '}
              <span className="text-cyan-400 font-semibold">Foundry IQ</span>,{' '}
              <span className="text-amber-400 font-semibold">Model Router</span>,{' '}
              <span className="text-emerald-400 font-semibold">M365 SDK</span>, and{' '}
              <span className="text-orange-400 font-semibold">Agent 365</span>.
            </p>
            <p className="text-slate-400 mb-10">
              From governance policies to budget tracking, agent portfolio to meeting transcripts.{' '}
              <span className="text-white font-semibold">All in one place.</span>
            </p>
            <div className="flex justify-center gap-4">
              <Link
                href="/"
                className="group px-8 py-3 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold shadow-lg shadow-emerald-500/30 transition transform hover:-translate-y-0.5 flex items-center gap-2"
              >
                Open Platform
                <ArrowRight className="h-5 w-5 group-hover:translate-x-1 transition-transform" />
              </Link>
              <a
                href="#orientation"
                className="px-8 py-3 rounded-lg bg-slate-800/70 backdrop-blur border border-slate-700 hover:bg-slate-800 text-white font-semibold transition transform hover:-translate-y-0.5"
              >
                Explore Capabilities
              </a>
            </div>
          </div>
        </div>

        {/* Get Oriented Section */}
        <div id="orientation" className="bg-slate-900/50 py-20 border-y border-slate-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-white mb-4">Get Oriented</h2>
              <p className="text-slate-400 max-w-2xl mx-auto">
                Understanding the Microsoft agent ecosystem: the tools to build agents and the platform to manage them.
              </p>
            </div>

            {/* Card Grid */}
            {expandedCard ? (
              <div className="flex flex-col md:flex-row gap-6 items-start">
                {/* Expanded Card - Left Column */}
                <div className="w-full md:w-[65%]">
                  {orientationCards.filter(c => c.id === expandedCard).map((card) => {
                    const colors = colorClasses[card.color];
                    return (
                      <div
                        key={card.id}
                        className={`relative bg-slate-800/70 backdrop-blur border ${colors.border} rounded-xl p-6 cursor-pointer transition-all duration-300`}
                        onClick={() => handleCardClick(card.id)}
                      >
                        <button
                          onClick={closeExpandedCard}
                          className="absolute top-4 right-4 w-8 h-8 rounded-full bg-slate-800/80 hover:bg-slate-700 text-slate-400 hover:text-white transition-all flex items-center justify-center z-10"
                        >
                          <X className="w-5 h-5" />
                        </button>
                        <div className="flex items-start justify-between mb-4 pr-12">
                          <h3 className={`text-xl font-bold ${colors.text}`}>{card.title}</h3>
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${colors.bg} ${colors.text}`}>{card.badge}</span>
                        </div>
                        <p className="text-slate-300 text-sm mb-4">{card.summary}</p>
                        <div className="space-y-2 text-sm text-slate-400">
                          {card.bullets.map((bullet, i) => (
                            <div key={i} className="flex items-start">
                              <Check className={`w-4 h-4 ${colors.text} mr-2 mt-0.5 flex-shrink-0`} />
                              <span>{bullet}</span>
                            </div>
                          ))}
                        </div>
                        <div className="mt-6 space-y-6 text-sm">
                          {card.expandedSections.map((section, i) => (
                            <div key={i}>
                              <h4 className={`text-md font-bold ${colors.text} mb-2`}>{section.title}</h4>
                              {section.content}
                            </div>
                          ))}
                          {card.resources && card.resources.length > 0 && (
                            <div className="mt-6 pt-4 border-t border-slate-700">
                              <p className="text-xs font-semibold text-slate-400 mb-2">Technical Resources</p>
                              <div className="flex flex-wrap gap-2">
                                {card.resources.map((resource, i) => (
                                  <a
                                    key={i}
                                    href={resource.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    onClick={(e) => e.stopPropagation()}
                                    className={`inline-flex items-center ${colors.text} hover:underline text-xs`}
                                  >
                                    {resource.label}
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
                {/* Collapsed Cards - Right Column */}
                <div className="w-full md:w-[35%] flex flex-col gap-4">
                  {orientationCards.filter(c => c.id !== expandedCard).map((card) => {
                    const colors = colorClasses[card.color];
                    return (
                      <div
                        key={card.id}
                        className={`bg-slate-800/70 backdrop-blur border border-slate-700/50 ${colors.hoverBorder} rounded-xl p-4 cursor-pointer transition-all duration-300`}
                        onClick={() => handleCardClick(card.id)}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <h3 className="text-lg font-bold text-white">{card.title}</h3>
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${colors.bg} ${colors.text}`}>{card.badge}</span>
                        </div>
                        <div className="space-y-1.5 text-xs text-slate-400">
                          {card.bullets.slice(0, 3).map((bullet, i) => (
                            <div key={i} className="flex items-start">
                              <Check className={`w-3 h-3 ${colors.text} mr-1.5 mt-0.5 flex-shrink-0`} />
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
                      className={`bg-slate-800/70 backdrop-blur border border-slate-700/50 ${colors.hoverBorder} rounded-xl p-6 cursor-pointer transition-all duration-300`}
                      onClick={() => handleCardClick(card.id)}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <h3 className="text-xl font-bold text-white">{card.title}</h3>
                        <span className={`px-2 py-1 rounded text-xs font-semibold ${colors.bg} ${colors.text}`}>{card.badge}</span>
                      </div>
                      <p className="text-slate-300 text-sm mb-4">{card.summary}</p>
                      <div className="space-y-2 text-sm text-slate-400">
                        {card.bullets.map((bullet, i) => (
                          <div key={i} className="flex items-start">
                            <Check className={`w-4 h-4 ${colors.text} mr-2 mt-0.5 flex-shrink-0`} />
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

        {/* Platform Capabilities */}
        <div className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-white mb-4">Platform Capabilities</h2>
              <p className="text-slate-400 max-w-2xl mx-auto">
                Comprehensive tools for managing the complete AI agent lifecycle.
              </p>
            </div>

            <div className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
              {platformCapabilities.map((cap) => {
                const Icon = cap.icon;
                const colors = colorClasses[cap.color];

                return (
                  <div
                    key={cap.name}
                    className={`bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6 ${colors.hoverBorder} transition-all group`}
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className={`w-10 h-10 ${colors.bg} rounded-lg flex items-center justify-center`}>
                        <Icon className={`h-5 w-5 ${colors.text}`} />
                      </div>
                      <span className={`px-2 py-1 rounded text-xs font-semibold ${colors.bg} ${colors.text}`}>{cap.badge}</span>
                    </div>
                    <h3 className="text-lg font-bold text-white mb-2">{cap.name}</h3>
                    <p className="text-slate-400 text-sm">{cap.desc}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Tech Stack */}
        <div className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl font-bold text-white mb-4">Built on Enterprise-Grade Technology</h2>
              <p className="text-slate-400 max-w-2xl mx-auto">
                Modern stack combining Next.js, FastAPI, and Azure services for scalability, performance, and security.
              </p>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {techStack.map((tech) => {
                const colors = colorClasses[tech.color];
                return (
                  <div
                    key={tech.name}
                    className={`bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-lg p-4 flex items-center gap-3 ${colors.hoverBorder} transition-all group`}
                  >
                    <div className={`w-8 h-8 ${colors.bg} rounded flex items-center justify-center font-bold ${colors.text} text-xs group-hover:scale-110 transition-transform`}>
                      {tech.letter}
                    </div>
                    <div>
                      <div className="font-semibold text-white text-sm">{tech.name}</div>
                      <div className="text-xs text-slate-500">{tech.sub}</div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Benefits Section */}
        <div id="benefits" className="py-20 bg-slate-900/50 border-y border-slate-800">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl font-bold text-white mb-12 text-center">
              Why Enterprise Teams Choose Agent Architecture Guide
            </h2>
            <div className="grid md:grid-cols-2 gap-8">
              {benefitCards.map((card) => {
                const colors = colorClasses[card.color];
                return (
                  <div
                    key={card.title}
                    className={`bg-slate-800/50 backdrop-blur border border-slate-700/50 rounded-xl p-6 ${colors.hoverBorder} transition-all group`}
                  >
                    <h4 className="text-lg font-bold text-white mb-3 flex items-center">
                      <Check className={`w-5 h-5 ${colors.text} mr-2`} />
                      {card.title}
                    </h4>
                    <ul className="text-slate-400 text-sm space-y-2">
                      {card.items.map((item, i) => (
                        <li key={i}>• {item}</li>
                      ))}
                    </ul>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* CTA Section */}
        <div className="py-20">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
            <h2 className="text-3xl font-bold text-white mb-6">Ready to Scale Your AI Agent Ecosystem?</h2>
            <p className="text-xl text-slate-400 mb-10">
              Join Fourth&apos;s enterprise teams in building a governed, scalable foundation for Microsoft Agent Framework adoption.
            </p>
            <div className="flex justify-center gap-4">
              <Link
                href="/"
                className="px-10 py-4 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold text-lg shadow-lg shadow-emerald-500/30 transition-all"
              >
                Launch Platform Now
              </Link>
            </div>
            <p className="text-slate-500 text-sm mt-8">
              Agent Architecture Guide • Enterprise AI Governance Platform
            </p>
          </div>
        </div>

        {/* Footer */}
        <footer className="border-t border-slate-800 py-8 bg-slate-900">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center text-slate-500 text-sm">
            <p>Fourth AI Architect Team • Enterprise Agent Architecture Guide</p>
            <p className="mt-2">
              Built with <span className="text-blue-500">Next.js</span>, <span className="text-emerald-500">FastAPI</span>, and <span className="text-purple-500">Azure AI Foundry</span>
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}
