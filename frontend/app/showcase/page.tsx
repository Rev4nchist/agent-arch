'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { AsciiStarfield } from '@/components/AsciiStarfield';
import {
  AlertCircle,
  ArrowRight,
  Brain,
  ChevronDown,
  ChevronUp,
  Cog,
  Crown,
  Database,
  DollarSign,
  FlaskConical,
  Headphones,
  Layers,
  Megaphone,
  Puzzle,
  Sparkles,
  Terminal,
  TrendingUp,
  X,
  Zap,
} from 'lucide-react';

// TypeScript Interfaces
interface AgentExample {
  title: string;
  scenario: string;
  actions: string[];
  outcome: string;
}

interface DepartmentCard {
  id: string;
  department: string;
  icon: React.ReactNode;
  color: string;
  headline: string;
  summary: string;
  benefits: string[];
  expandableExamples: AgentExample[];
}

interface ProblemStatement {
  icon: React.ReactNode;
  title: string;
  description: string;
  color: string;
}

interface EcosystemStep {
  step: number;
  icon: React.ReactNode;
  label: string;
  description: string;
  color: string;
}

interface JourneyStage {
  stage: string;
  duration: string;
  icon: React.ReactNode;
  color: string;
  activities: string[];
  outcome: string;
}

// Problem Statements Data
const problemStatements: ProblemStatement[] = [
  {
    icon: <AlertCircle className="w-8 h-8" />,
    title: "Generic AI Can't Help",
    description: "A generic Copilot is just the beginning. Off-the-shelf AI can't access your company's specific data reliably or understand Fourth's unique workflows.",
    color: 'red',
  },
  {
    icon: <Database className="w-8 h-8" />,
    title: 'Data Silos Block Intelligence',
    description: "Customer data, financials, and operations exist in separate systems—agents can't connect the dots without unified access.",
    color: 'amber',
  },
  {
    icon: <Puzzle className="w-8 h-8" />,
    title: 'No Custom Tools for Fourth',
    description: "Standard AI can't handle Fourth's specific needs: contract analysis, menu optimization, workforce planning, and more.",
    color: 'purple',
  },
];

// Department Cards Data
const departmentCards: DepartmentCard[] = [
  {
    id: 'customer-support',
    department: 'Customer Support',
    icon: <Headphones className="w-8 h-8" />,
    color: 'blue',
    headline: 'Instant Context, Faster Resolution',
    summary: "AI agents that understand customer history, contract terms, and Fourth services—no more digging through tickets.",
    benefits: [
      'Agent reads past interactions and contract details automatically',
      'Suggests solutions based on similar customer issues',
      "Drafts responses in your team's tone and style",
    ],
    expandableExamples: [
      {
        title: 'Agent: Support Ticket Analyzer',
        scenario: 'Customer reports invoice discrepancy',
        actions: [
          'Retrieves customer contract terms from SharePoint',
          'Pulls invoice history from Finance system',
          'Identifies billing rule mismatch',
          'Drafts explanation email with correction steps',
        ],
        outcome: 'Resolution time reduced from 2 hours to 15 minutes',
      },
    ],
  },
  {
    id: 'marketing',
    department: 'Marketing',
    icon: <Megaphone className="w-8 h-8" />,
    color: 'purple',
    headline: 'Campaigns That Know Your Audience',
    summary: 'Agents analyze customer data to create targeted campaigns, measure impact, and optimize messaging automatically.',
    benefits: [
      'Segment customers based on usage patterns and feedback',
      'Generate campaign copy tailored to each segment',
      'Track campaign performance and suggest optimizations',
    ],
    expandableExamples: [
      {
        title: 'Agent: Campaign Optimizer',
        scenario: 'Launching new product feature to existing customers',
        actions: [
          'Analyzes customer usage data to identify best-fit segments',
          'Generates personalized email variations by segment',
          'Monitors open rates and adjusts messaging in real-time',
          'Reports ROI and suggests next-best actions',
        ],
        outcome: 'Campaign engagement increased 40% vs. generic approach',
      },
    ],
  },
  {
    id: 'sales',
    department: 'Sales',
    icon: <TrendingUp className="w-8 h-8" />,
    color: 'emerald',
    headline: 'Pipeline Intelligence, Deal Acceleration',
    summary: "AI that understands prospect needs, Fourth's offerings, and competitive positioning to help close deals faster.",
    benefits: [
      'Prepares prospect briefings with company research and pain points',
      "Suggests Fourth solutions matching prospect's industry/size",
      'Drafts proposal sections and pricing recommendations',
    ],
    expandableExamples: [
      {
        title: 'Agent: Deal Accelerator',
        scenario: 'Preparing for enterprise prospect meeting',
        actions: [
          'Researches prospect company news and financials',
          'Identifies likely pain points based on industry analysis',
          'Maps Fourth solutions to prospect needs',
          'Generates talking points and proposal outline',
        ],
        outcome: 'Preparation time cut 70%, win rate improved 25%',
      },
    ],
  },
  {
    id: 'finance',
    department: 'Finance',
    icon: <DollarSign className="w-8 h-8" />,
    color: 'green',
    headline: 'Forecast Accuracy, Budget Control',
    summary: 'Agents that analyze spending patterns, predict budget overruns, and recommend cost optimizations.',
    benefits: [
      'Auto-categorizes expenses and flags anomalies',
      'Forecasts quarterly spend based on historical trends',
      'Suggests budget reallocations for better ROI',
    ],
    expandableExamples: [
      {
        title: 'Agent: Budget Guardian',
        scenario: 'Monthly expense review and forecasting',
        actions: [
          'Aggregates expense data across all cost centers',
          'Identifies spending anomalies and trends',
          'Projects end-of-quarter spend with confidence intervals',
          'Recommends reallocation opportunities',
        ],
        outcome: 'Budget variance reduced from 15% to 3%',
      },
    ],
  },
  {
    id: 'bizops',
    department: 'BizOps',
    icon: <Cog className="w-8 h-8" />,
    color: 'orange',
    headline: 'Process Optimization, Data-Driven Decisions',
    summary: 'Identify inefficiencies, automate workflows, and surface insights from operational data.',
    benefits: [
      'Maps current workflows and identifies bottlenecks',
      'Automates repetitive data entry and reporting',
      'Generates operational dashboards with key metrics',
    ],
    expandableExamples: [
      {
        title: 'Agent: Operations Analyst',
        scenario: 'Quarterly operational efficiency review',
        actions: [
          'Collects KPIs from multiple operational systems',
          'Identifies process bottlenecks and waste',
          'Benchmarks against industry standards',
          'Generates improvement recommendations with ROI estimates',
        ],
        outcome: 'Operational efficiency improved 20% in 6 months',
      },
    ],
  },
  {
    id: 'executive',
    department: 'Executive',
    icon: <Crown className="w-8 h-8" />,
    color: 'amber',
    headline: 'Strategic Insights, Risk Visibility',
    summary: 'Board-ready summaries, competitive intelligence, and early warning signals from across the business.',
    benefits: [
      'Synthesizes department reports into executive summaries',
      'Tracks competitor moves and market trends',
      'Flags potential risks based on data anomalies',
    ],
    expandableExamples: [
      {
        title: 'Agent: Executive Briefer',
        scenario: 'Preparing for quarterly board meeting',
        actions: [
          'Aggregates KPIs and highlights from all departments',
          'Identifies key wins, risks, and strategic opportunities',
          'Compiles competitive intelligence summary',
          'Generates board deck with key narratives and visuals',
        ],
        outcome: 'Board prep time reduced 80%, strategic clarity improved',
      },
    ],
  },
];

// Ecosystem Steps Data
const ecosystemSteps: EcosystemStep[] = [
  {
    step: 1,
    icon: <Database className="w-6 h-6" />,
    label: 'Connect Your Data',
    description: "Fourth's data sources (SharePoint, Dynamics, custom databases) linked securely",
    color: 'cyan',
  },
  {
    step: 2,
    icon: <Brain className="w-6 h-6" />,
    label: 'Train Custom Agents',
    description: "AI agents learn Fourth's business rules, terminology, and workflows",
    color: 'purple',
  },
  {
    step: 3,
    icon: <Layers className="w-6 h-6" />,
    label: 'Orchestrate Intelligence',
    description: 'Agents work together: one retrieves data, another analyzes, a third drafts response',
    color: 'emerald',
  },
  {
    step: 4,
    icon: <Sparkles className="w-6 h-6" />,
    label: 'Deliver in Your Tools',
    description: 'Access via Teams/Copilot/Slack/Custom Apps—no new software to learn',
    color: 'amber',
  },
];

// Journey Stages Data
const journeyStages: JourneyStage[] = [
  {
    stage: 'Pilot',
    duration: '1-2 months',
    icon: <FlaskConical className="w-6 h-6" />,
    color: 'blue',
    activities: [
      'Select 1-2 departments for initial agents',
      'Connect relevant data sources',
      'Train agents with department workflows',
      'Gather feedback from 10-20 users',
    ],
    outcome: 'Proof of value with measurable time savings',
  },
  {
    stage: 'Scale',
    duration: '3-6 months',
    icon: <TrendingUp className="w-6 h-6" />,
    color: 'emerald',
    activities: [
      'Expand to additional departments',
      'Build department-specific agent library',
      'Establish governance and security policies',
      'Train champions in each department',
    ],
    outcome: 'Organization-wide adoption with documented ROI',
  },
  {
    stage: 'Optimize',
    duration: 'Ongoing',
    icon: <Zap className="w-6 h-6" />,
    color: 'purple',
    activities: [
      'Refine agents based on usage patterns',
      'Add new data sources as business evolves',
      'Develop advanced orchestration workflows',
      'Monitor costs and optimize efficiency',
    ],
    outcome: 'AI becomes embedded in daily operations',
  },
];

// Color Classes Helper
const colorClasses: Record<string, { bg: string; border: string; text: string; glow: string }> = {
  blue: { bg: 'bg-blue-500/10', border: 'border-blue-500/50', text: 'text-blue-400', glow: 'shadow-blue-500/20' },
  purple: { bg: 'bg-purple-500/10', border: 'border-purple-500/50', text: 'text-purple-400', glow: 'shadow-purple-500/20' },
  emerald: { bg: 'bg-emerald-500/10', border: 'border-emerald-500/50', text: 'text-emerald-400', glow: 'shadow-emerald-500/20' },
  green: { bg: 'bg-green-500/10', border: 'border-green-500/50', text: 'text-green-400', glow: 'shadow-green-500/20' },
  orange: { bg: 'bg-orange-500/10', border: 'border-orange-500/50', text: 'text-orange-400', glow: 'shadow-orange-500/20' },
  amber: { bg: 'bg-amber-500/10', border: 'border-amber-500/50', text: 'text-amber-400', glow: 'shadow-amber-500/20' },
  red: { bg: 'bg-red-500/10', border: 'border-red-500/50', text: 'text-red-400', glow: 'shadow-red-500/20' },
  cyan: { bg: 'bg-cyan-500/10', border: 'border-cyan-500/50', text: 'text-cyan-400', glow: 'shadow-cyan-500/20' },
};

function TypewriterText({ text, delay = 50 }: { text: string; delay?: number }) {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayText((prev) => prev + text[currentIndex]);
        setCurrentIndex((prev) => prev + 1);
      }, delay);
      return () => clearTimeout(timeout);
    }
  }, [currentIndex, text, delay]);

  return (
    <span>
      {displayText}
      <span className="animate-pulse">_</span>
    </span>
  );
}

function GlitchText({ text }: { text: string }) {
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

  return <span>{glitchText}</span>;
}

function DepartmentCardExpanded({ card, onClose }: { card: DepartmentCard; onClose: () => void }) {
  const colors = colorClasses[card.color] || colorClasses.emerald;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
      <div
        className={`relative w-full max-w-3xl max-h-[90vh] overflow-y-auto bg-slate-900 border ${colors.border} rounded-2xl shadow-2xl ${colors.glow}`}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 text-slate-400 hover:text-white transition-colors"
          aria-label="Close"
        >
          <X className="w-6 h-6" />
        </button>

        <div className="p-8">
          <div className="flex items-center gap-4 mb-6">
            <div className={`p-4 ${colors.bg} rounded-xl ${colors.text}`}>
              {card.icon}
            </div>
            <div>
              <span className={`font-mono text-xs ${colors.text} tracking-wider uppercase`}>
                {card.department}
              </span>
              <h3 className="text-2xl font-bold font-mono text-white">
                {card.headline}
              </h3>
            </div>
          </div>

          <p className="text-slate-300 mb-6 leading-relaxed">
            {card.summary}
          </p>

          <div className="mb-8">
            <h4 className="font-mono text-sm text-emerald-400 mb-3 uppercase tracking-wider">
              * Key Benefits
            </h4>
            <ul className="space-y-2">
              {card.benefits.map((benefit, i) => (
                <li key={i} className="flex items-start gap-3 text-slate-300">
                  <span className="text-emerald-400 mt-1">→</span>
                  {benefit}
                </li>
              ))}
            </ul>
          </div>

          {card.expandableExamples.map((example, i) => (
            <div key={i} className="p-6 bg-slate-800/50 border border-slate-700 rounded-xl">
              <h4 className={`font-mono font-bold ${colors.text} mb-2`}>
                {example.title}
              </h4>
              <p className="text-slate-400 text-sm mb-4">
                <span className="text-slate-500">Scenario:</span> {example.scenario}
              </p>

              <div className="mb-4">
                <span className="font-mono text-xs text-slate-500 uppercase tracking-wider">
                  Agent Actions:
                </span>
                <ol className="mt-2 space-y-2">
                  {example.actions.map((action, j) => (
                    <li key={j} className="flex items-start gap-3 text-slate-300 text-sm">
                      <span className={`${colors.text} font-mono text-xs`}>{j + 1}.</span>
                      {action}
                    </li>
                  ))}
                </ol>
              </div>

              <div className={`p-3 ${colors.bg} rounded-lg`}>
                <span className="font-mono text-xs text-slate-500">Outcome: </span>
                <span className={`font-mono text-sm ${colors.text} font-bold`}>
                  {example.outcome}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export default function ShowcasePage() {
  const [mounted, setMounted] = useState(false);
  const [expandedCard, setExpandedCard] = useState<DepartmentCard | null>(null);

  useEffect(() => {
    setMounted(true);
  }, []);

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && expandedCard) {
        setExpandedCard(null);
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [expandedCard]);

  return (
    <div className="relative min-h-screen bg-black text-white overflow-hidden">
      <AsciiStarfield
        starCount={150}
        speed={0.3}
        color="#00ff88"
        glowColor="#00ff8833"
        showTechChars={true}
        opacity={0.4}
      />

      <div className="fixed inset-0 bg-gradient-to-b from-black/80 via-black/60 to-black/90 pointer-events-none z-[1]" />

      <div className="relative z-10">
        {/* Navigation */}
        <nav className="fixed top-0 left-0 right-0 z-50 backdrop-blur-md bg-black/30 border-b border-emerald-500/20">
          <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Terminal className="w-6 h-6 text-emerald-400" />
              <span className="font-mono text-emerald-400 text-lg tracking-wider">
                FOURTH<span className="text-white">.AI</span>
              </span>
            </div>
            <div className="flex items-center gap-6">
              <Link
                href="/landing"
                className="font-mono text-sm text-slate-400 hover:text-emerald-400 transition-colors"
              >
                [DOCS]
              </Link>
              <Link
                href="/"
                className="font-mono text-sm text-slate-400 hover:text-emerald-400 transition-colors"
              >
                [PORTAL]
              </Link>
            </div>
          </div>
        </nav>

        {/* Hero Section */}
        <section className="min-h-screen flex flex-col items-center justify-center px-6 pt-20">
          <div className="text-center max-w-4xl mx-auto">
            <div className="mb-6">
              <span className="font-mono text-xs text-emerald-400/80 tracking-[0.3em] uppercase">
                {'>'} AI THAT UNDERSTANDS FOURTH
              </span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 font-mono">
              {mounted ? (
                <GlitchText text="BEYOND GENERIC" />
              ) : (
                'BEYOND GENERIC'
              )}
              <br />
              <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 via-cyan-400 to-emerald-400">
                COPILOT
              </span>
            </h1>

            <p className="text-lg md:text-xl text-slate-400 mb-8 font-mono leading-relaxed max-w-3xl mx-auto">
              {mounted ? (
                <TypewriterText
                  text="Orchestrator agents that connect your data, understand Fourth's workflows, and deliver results where you work—Teams, Copilot, Slack, or custom apps."
                  delay={25}
                />
              ) : (
                "Orchestrator agents that connect your data, understand Fourth's workflows, and deliver results where you work—Teams, Copilot, Slack, or custom apps."
              )}
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
              <Link
                href="#how-it-works"
                className="group px-8 py-4 bg-emerald-500/20 border border-emerald-500/50 rounded-lg font-mono text-emerald-400 hover:bg-emerald-500/30 hover:border-emerald-400 transition-all flex items-center justify-center gap-2"
              >
                SEE HOW IT WORKS
                <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
              </Link>
              <Link
                href="https://agent-arch.fourth.com/agents/"
                className="px-8 py-4 bg-slate-800/50 border border-slate-700 rounded-lg font-mono text-slate-300 hover:bg-slate-800 hover:border-slate-600 transition-all flex items-center justify-center gap-2"
              >
                <FlaskConical className="w-4 h-4" />
                START A PILOT
              </Link>
            </div>

            <div className="flex flex-wrap justify-center gap-4 text-xs font-mono text-slate-500">
              <span className="px-3 py-1 bg-slate-800/50 rounded-full border border-slate-700">
                <span className="text-emerald-400">✓</span> Your Data Connected
              </span>
              <span className="px-3 py-1 bg-slate-800/50 rounded-full border border-slate-700">
                <span className="text-emerald-400">✓</span> Custom Workflows
              </span>
              <span className="px-3 py-1 bg-slate-800/50 rounded-full border border-slate-700">
                <span className="text-emerald-400">✓</span> Delivered in Teams/Slack
              </span>
            </div>
          </div>

          <div className="absolute bottom-10 left-1/2 -translate-x-1/2 animate-bounce">
            <div className="w-6 h-10 border-2 border-emerald-400/50 rounded-full flex justify-center pt-2">
              <div className="w-1.5 h-3 bg-emerald-400/50 rounded-full animate-scroll" />
            </div>
          </div>
        </section>

        {/* Problem Statement Section */}
        <section className="py-24 px-6">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <span className="font-mono text-xs text-emerald-400/80 tracking-[0.3em] uppercase mb-4 block">
                {'>'} THE_CHALLENGE
              </span>
              <h2 className="text-3xl md:text-5xl font-bold font-mono mb-4">
                WHY <span className="text-red-400">GENERIC AI</span> FALLS SHORT
              </h2>
              <p className="text-slate-400 font-mono max-w-2xl mx-auto">
                Standard AI tools weren&apos;t built for Fourth. Here&apos;s what&apos;s missing.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {problemStatements.map((problem) => {
                const colors = colorClasses[problem.color] || colorClasses.red;
                return (
                  <div
                    key={problem.title}
                    className={`p-6 bg-slate-900/50 border ${colors.border} rounded-xl hover:shadow-lg ${colors.glow} transition-all duration-300`}
                  >
                    <div className={`p-3 ${colors.bg} rounded-lg ${colors.text} w-fit mb-4`}>
                      {problem.icon}
                    </div>
                    <h3 className={`font-mono font-bold text-lg ${colors.text} mb-2`}>
                      {problem.title}
                    </h3>
                    <p className="text-slate-400 text-sm leading-relaxed">
                      {problem.description}
                    </p>
                  </div>
                );
              })}
            </div>
          </div>
        </section>

        {/* Department Value Proposition Cards */}
        <section className="py-24 px-6 border-t border-slate-800/50">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <span className="font-mono text-xs text-emerald-400/80 tracking-[0.3em] uppercase mb-4 block">
                {'>'} SOLUTIONS_BY_DEPARTMENT
              </span>
              <h2 className="text-3xl md:text-5xl font-bold font-mono mb-4">
                AI BUILT FOR <span className="text-emerald-400">YOUR TEAM</span>
              </h2>
              <p className="text-slate-400 font-mono max-w-2xl mx-auto">
                See how intelligent agents transform work across every department.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {departmentCards.map((card) => {
                const colors = colorClasses[card.color] || colorClasses.emerald;
                return (
                  <button
                    key={card.id}
                    onClick={() => setExpandedCard(card)}
                    className={`text-left p-6 bg-slate-900/50 border border-slate-800 rounded-xl hover:border-${card.color}-500/50 hover:shadow-lg ${colors.glow} transition-all duration-300 group`}
                  >
                    <div className="flex items-start gap-4">
                      <div className={`p-3 ${colors.bg} rounded-lg ${colors.text} group-hover:scale-110 transition-transform`}>
                        {card.icon}
                      </div>
                      <div className="flex-1">
                        <span className={`font-mono text-xs ${colors.text} tracking-wider uppercase`}>
                          {card.department}
                        </span>
                        <h3 className="font-mono font-bold text-lg text-white mb-2 group-hover:text-emerald-400 transition-colors">
                          {card.headline}
                        </h3>
                        <p className="text-slate-400 text-sm leading-relaxed line-clamp-2">
                          {card.summary}
                        </p>
                        <div className="mt-4 flex items-center gap-2 text-emerald-400 text-sm font-mono">
                          See Example <ChevronDown className="w-4 h-4" />
                        </div>
                      </div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        </section>

        {/* How It Works Section */}
        <section id="how-it-works" className="py-24 px-6 border-t border-slate-800/50">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <span className="font-mono text-xs text-emerald-400/80 tracking-[0.3em] uppercase mb-4 block">
                {'>'} HOW_IT_WORKS
              </span>
              <h2 className="text-3xl md:text-5xl font-bold font-mono mb-4">
                FROM DATA TO <span className="text-emerald-400">DELIVERY</span>
              </h2>
              <p className="text-slate-400 font-mono max-w-2xl mx-auto">
                Four steps to intelligent automation that fits your workflow.
              </p>
            </div>

            <div className="relative">
              {/* Connection Line - Desktop Only */}
              <div className="hidden lg:block absolute top-1/2 left-0 right-0 h-0.5 bg-gradient-to-r from-cyan-500/30 via-emerald-500/30 to-amber-500/30 -translate-y-1/2" />

              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {ecosystemSteps.map((step) => {
                  const colors = colorClasses[step.color] || colorClasses.emerald;
                  return (
                    <div
                      key={step.step}
                      className="relative p-6 bg-slate-900/70 border border-slate-800 rounded-xl hover:border-emerald-500/30 transition-all text-center group"
                    >
                      <div className={`absolute -top-3 left-1/2 -translate-x-1/2 w-8 h-8 ${colors.bg} ${colors.border} border-2 rounded-full flex items-center justify-center font-mono text-sm ${colors.text} font-bold`}>
                        {step.step}
                      </div>
                      <div className={`w-14 h-14 mx-auto mt-4 mb-4 ${colors.bg} rounded-xl flex items-center justify-center ${colors.text} group-hover:scale-110 transition-transform`}>
                        {step.icon}
                      </div>
                      <h3 className="font-mono font-bold text-white mb-2">{step.label}</h3>
                      <p className="font-mono text-xs text-slate-400 leading-relaxed">{step.description}</p>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        {/* Journey/Roadmap Section */}
        <section id="journey" className="py-24 px-6 border-t border-slate-800/50">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <span className="font-mono text-xs text-emerald-400/80 tracking-[0.3em] uppercase mb-4 block">
                {'>'} YOUR_JOURNEY
              </span>
              <h2 className="text-3xl md:text-5xl font-bold font-mono mb-4">
                START SMALL, <span className="text-emerald-400">SCALE FAST</span>
              </h2>
              <p className="text-slate-400 font-mono max-w-2xl mx-auto">
                A proven path from pilot to production—at your pace.
              </p>
            </div>

            <div className="relative">
              {/* Timeline Line - Desktop Only */}
              <div className="hidden lg:block absolute top-20 left-[16%] right-[16%] h-1 bg-gradient-to-r from-blue-500/50 via-emerald-500/50 to-purple-500/50" />

              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                {journeyStages.map((stage, index) => {
                  const colors = colorClasses[stage.color] || colorClasses.emerald;
                  return (
                    <div key={stage.stage} className="relative">
                      {/* Stage Circle - Desktop */}
                      <div className={`hidden lg:flex absolute -top-3 left-1/2 -translate-x-1/2 w-12 h-12 ${colors.bg} ${colors.border} border-2 rounded-full items-center justify-center ${colors.text}`}>
                        {stage.icon}
                      </div>

                      <div className={`mt-8 lg:mt-16 p-6 bg-slate-900/50 border ${colors.border} rounded-xl hover:shadow-lg ${colors.glow} transition-all`}>
                        <div className="flex items-center gap-3 mb-4 lg:hidden">
                          <div className={`p-2 ${colors.bg} rounded-lg ${colors.text}`}>
                            {stage.icon}
                          </div>
                          <div>
                            <h3 className={`font-mono font-bold text-xl ${colors.text}`}>{stage.stage}</h3>
                            <span className="font-mono text-xs text-slate-500">{stage.duration}</span>
                          </div>
                        </div>

                        <div className="hidden lg:block text-center mb-4">
                          <h3 className={`font-mono font-bold text-xl ${colors.text}`}>{stage.stage}</h3>
                          <span className="font-mono text-xs text-slate-500">{stage.duration}</span>
                        </div>

                        <ul className="space-y-2 mb-4">
                          {stage.activities.map((activity, i) => (
                            <li key={i} className="flex items-start gap-2 text-slate-300 text-sm">
                              <span className={`${colors.text} mt-1`}>→</span>
                              {activity}
                            </li>
                          ))}
                        </ul>

                        <div className={`p-3 ${colors.bg} rounded-lg`}>
                          <span className="font-mono text-xs text-slate-500">Outcome: </span>
                          <span className={`font-mono text-sm ${colors.text}`}>{stage.outcome}</span>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-24 px-6 border-t border-slate-800/50">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-emerald-500/10 border border-emerald-500/30 rounded-full font-mono text-xs text-emerald-400 mb-8">
              <Zap className="w-4 h-4" />
              READY TO TRANSFORM YOUR BUSINESS
            </div>

            <h2 className="text-3xl md:text-5xl font-bold font-mono mb-6">
              LET&apos;S BUILD YOUR <span className="text-emerald-400">AI FUTURE</span>
            </h2>

            <p className="text-slate-400 font-mono mb-8 max-w-2xl mx-auto">
              Start with a pilot in your department. See measurable results within weeks, not months.
            </p>

            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/landing"
                className="inline-flex items-center gap-2 px-8 py-4 bg-emerald-500 text-black font-mono font-bold rounded-lg hover:bg-emerald-400 transition-colors"
              >
                <ArrowRight className="w-5 h-5" />
                EXPLORE ARCHITECTURE DOCS
              </Link>
              <Link
                href="/"
                className="inline-flex items-center gap-2 px-8 py-4 bg-slate-800/50 border border-slate-700 text-white font-mono rounded-lg hover:bg-slate-800 hover:border-slate-600 transition-colors"
              >
                <Terminal className="w-5 h-5" />
                ACCESS PORTAL
              </Link>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="py-8 px-6 border-t border-slate-800/50">
          <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
            <div className="font-mono text-xs text-slate-500">
              © 2025 Fourth Ltd. All rights reserved.
            </div>
            <div className="font-mono text-xs text-slate-600">
              Powered by Microsoft AI Ecosystem
            </div>
          </div>
        </footer>
      </div>

      {/* Expanded Card Modal */}
      {expandedCard && (
        <DepartmentCardExpanded card={expandedCard} onClose={() => setExpandedCard(null)} />
      )}

      <style jsx>{`
        @keyframes scroll {
          0% { transform: translateY(0); opacity: 1; }
          100% { transform: translateY(8px); opacity: 0; }
        }
        .animate-scroll {
          animation: scroll 1.5s ease-in-out infinite;
        }
      `}</style>
    </div>
  );
}
