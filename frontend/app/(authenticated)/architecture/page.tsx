'use client';

import { useState, useEffect } from 'react';
import { BookOpen, Code2, Rocket, FileCode2, Terminal, Cpu, Layers, GitBranch, Sparkles } from 'lucide-react';

const features = [
  { name: 'Code Patterns', icon: Code2, desc: 'Code-First, Low-Code & Hybrid patterns' },
  { name: 'Deployment Guides', icon: Rocket, desc: 'Step-by-step platform deployment' },
  { name: 'Syntax Highlighting', icon: FileCode2, desc: 'Beautiful code presentation' },
  { name: 'Prerequisites', icon: Layers, desc: 'Dependency checklists' },
];

const codeSnippet = `// Agent Architecture Pattern
class IntelligentAgent {
  private orchestrator: Orchestrator;
  private memory: VectorStore;

  async process(input: UserQuery) {
    const context = await this.memory.search(input);
    const plan = await this.orchestrator.plan(input, context);

    for (const step of plan.steps) {
      await this.execute(step);
    }

    return this.synthesize(plan.results);
  }
}`;

export default function ArchitecturePage() {
  const [typedCode, setTypedCode] = useState('');
  const [cursorVisible, setCursorVisible] = useState(true);
  const [floatingNodes, setFloatingNodes] = useState<Array<{ x: number; y: number; delay: number }>>([]);

  useEffect(() => {
    // Generate floating nodes
    const nodes = Array.from({ length: 20 }, () => ({
      x: Math.random() * 100,
      y: Math.random() * 100,
      delay: Math.random() * 5,
    }));
    setFloatingNodes(nodes);

    // Typing effect
    let index = 0;
    const typeInterval = setInterval(() => {
      if (index < codeSnippet.length) {
        setTypedCode(codeSnippet.slice(0, index + 1));
        index++;
      } else {
        clearInterval(typeInterval);
      }
    }, 30);

    // Cursor blink
    const cursorInterval = setInterval(() => {
      setCursorVisible(prev => !prev);
    }, 530);

    return () => {
      clearInterval(typeInterval);
      clearInterval(cursorInterval);
    };
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-950 to-slate-900 relative overflow-hidden">
      {/* Floating circuit nodes */}
      {floatingNodes.map((node, i) => (
        <div
          key={i}
          className="absolute w-2 h-2 bg-purple-400/30 rounded-full animate-pulse"
          style={{
            left: `${node.x}%`,
            top: `${node.y}%`,
            animationDelay: `${node.delay}s`,
            animationDuration: '3s',
          }}
        />
      ))}

      {/* Connection lines background */}
      <svg className="absolute inset-0 w-full h-full pointer-events-none opacity-10">
        <defs>
          <linearGradient id="lineGrad" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#a855f7" />
            <stop offset="100%" stopColor="#3b82f6" />
          </linearGradient>
        </defs>
        {floatingNodes.slice(0, 10).map((node, i) => (
          <line
            key={i}
            x1={`${node.x}%`}
            y1={`${node.y}%`}
            x2={`${floatingNodes[(i + 1) % 10].x}%`}
            y2={`${floatingNodes[(i + 1) % 10].y}%`}
            stroke="url(#lineGrad)"
            strokeWidth="1"
          />
        ))}
      </svg>

      <div className="relative z-20 p-8 max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-16 pt-8">
          <div className="inline-flex items-center gap-4 mb-6">
            <div className="relative">
              <div className="absolute inset-0 bg-purple-500/50 blur-xl rounded-full animate-pulse" />
              <div className="relative p-4 bg-gradient-to-br from-purple-500 to-blue-600 rounded-2xl shadow-lg shadow-purple-500/25">
                <BookOpen className="h-12 w-12 text-white" />
              </div>
            </div>
          </div>

          <h1 className="text-6xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 mb-4">
            ARCHITECTURE LAB
          </h1>

          <div className="flex items-center justify-center gap-3 mb-8">
            <div className="h-px w-16 bg-gradient-to-r from-transparent to-purple-400" />
            <span className="text-purple-400 font-mono text-sm tracking-widest uppercase flex items-center gap-2">
              <Sparkles className="h-4 w-4" />
              Coming Soon
              <Sparkles className="h-4 w-4" />
            </span>
            <div className="h-px w-16 bg-gradient-to-l from-transparent to-purple-400" />
          </div>

          <p className="text-slate-400 text-lg max-w-2xl mx-auto font-light">
            A comprehensive knowledge base featuring code patterns, deployment guides,
            and best practices for building AI agent architectures.
          </p>
        </div>

        {/* Two-column layout */}
        <div className="grid md:grid-cols-2 gap-8 mb-16">
          {/* Code preview panel */}
          <div className="bg-slate-950/80 backdrop-blur rounded-2xl border border-purple-500/20 overflow-hidden shadow-2xl shadow-purple-500/10">
            <div className="flex items-center gap-2 px-4 py-3 bg-slate-900/80 border-b border-purple-500/20">
              <Terminal className="h-4 w-4 text-purple-400" />
              <span className="text-purple-300 font-mono text-sm">agent-pattern.ts</span>
              <div className="ml-auto flex gap-1.5">
                <div className="w-3 h-3 rounded-full bg-red-500/80" />
                <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                <div className="w-3 h-3 rounded-full bg-green-500/80" />
              </div>
            </div>
            <pre className="p-6 text-sm font-mono overflow-hidden">
              <code className="text-slate-300">
                {typedCode.split('\n').map((line, i) => (
                  <div key={i} className="leading-relaxed">
                    <span className="text-slate-600 select-none mr-4">{String(i + 1).padStart(2, '0')}</span>
                    {line.includes('//') && <span className="text-slate-500">{line}</span>}
                    {line.includes('class') && (
                      <>
                        <span className="text-purple-400">class </span>
                        <span className="text-blue-400">{line.replace('class ', '').replace(' {', '')}</span>
                        <span className="text-slate-300"> {'{'}</span>
                      </>
                    )}
                    {line.includes('private') && (
                      <>
                        <span className="text-purple-400">  private </span>
                        <span className="text-slate-300">{line.replace('  private ', '')}</span>
                      </>
                    )}
                    {line.includes('async') && (
                      <>
                        <span className="text-purple-400">  async </span>
                        <span className="text-yellow-400">{line.replace('  async ', '').split('(')[0]}</span>
                        <span className="text-slate-300">({line.split('(')[1]}</span>
                      </>
                    )}
                    {line.includes('const') && (
                      <>
                        <span className="text-purple-400">    const </span>
                        <span className="text-slate-300">{line.replace('    const ', '')}</span>
                      </>
                    )}
                    {line.includes('for') && <span className="text-purple-400">{line}</span>}
                    {line.includes('await') && !line.includes('const') && (
                      <>
                        <span className="text-purple-400">      await </span>
                        <span className="text-slate-300">{line.replace('      await ', '')}</span>
                      </>
                    )}
                    {line.includes('return') && (
                      <>
                        <span className="text-purple-400">    return </span>
                        <span className="text-slate-300">{line.replace('    return ', '')}</span>
                      </>
                    )}
                    {(line === '  }' || line === '}') && <span className="text-slate-300">{line}</span>}
                    {line === '' && <br />}
                  </div>
                ))}
                <span className={`inline-block w-2 h-4 bg-purple-400 ${cursorVisible ? 'opacity-100' : 'opacity-0'}`} />
              </code>
            </pre>
          </div>

          {/* Features grid */}
          <div className="space-y-4">
            {features.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <div
                  key={feature.name}
                  className="group flex items-center gap-4 p-5 bg-slate-800/30 backdrop-blur border border-slate-700/50 rounded-xl hover:border-purple-500/50 transition-all duration-300"
                >
                  <div className="p-3 bg-gradient-to-br from-purple-500/20 to-blue-500/20 rounded-lg group-hover:from-purple-500/30 group-hover:to-blue-500/30 transition-all">
                    <Icon className="h-6 w-6 text-purple-400" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-white mb-1">{feature.name}</h3>
                    <p className="text-slate-500 text-sm">{feature.desc}</p>
                  </div>
                  <GitBranch className="h-5 w-5 text-slate-600 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom stats bar */}
        <div className="bg-slate-800/30 backdrop-blur border border-slate-700/50 rounded-xl p-6">
          <div className="grid grid-cols-3 gap-8 text-center">
            <div>
              <div className="flex items-center justify-center gap-2 mb-2">
                <Cpu className="h-5 w-5 text-purple-400" />
                <span className="text-2xl font-bold text-white">3</span>
              </div>
              <p className="text-slate-500 text-sm">Pattern Types</p>
              <p className="text-purple-400 text-xs font-mono mt-1">Code-First • Low-Code • Hybrid</p>
            </div>
            <div>
              <div className="flex items-center justify-center gap-2 mb-2">
                <Rocket className="h-5 w-5 text-blue-400" />
                <span className="text-2xl font-bold text-white">∞</span>
              </div>
              <p className="text-slate-500 text-sm">Deployment Guides</p>
              <p className="text-blue-400 text-xs font-mono mt-1">Azure • AWS • Local</p>
            </div>
            <div>
              <div className="flex items-center justify-center gap-2 mb-2">
                <Code2 className="h-5 w-5 text-pink-400" />
                <span className="text-2xl font-bold text-white">MD</span>
              </div>
              <p className="text-slate-500 text-sm">Rich Documentation</p>
              <p className="text-pink-400 text-xs font-mono mt-1">Markdown • Code Blocks</p>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center">
          <div className="inline-flex items-center gap-2 text-slate-600 font-mono text-xs">
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" />
            KNOWLEDGE BASE: INITIALIZING
          </div>
        </div>
      </div>
    </div>
  );
}
