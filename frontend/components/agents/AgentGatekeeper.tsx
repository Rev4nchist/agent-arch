'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import {
  Brain,
  Database,
  UserCog,
  ArrowRight,
  ArrowLeft,
  CheckCircle,
  Bot,
  Workflow,
} from 'lucide-react';
import { GATEKEEPER_QUESTIONS, type GatekeeperState } from '@/lib/agent-factory-types';

interface AgentGatekeeperProps {
  onComplete: (recommendation: 'copilot' | 'azure') => void;
  onReset?: () => void;
}

const questionIcons = [Brain, Database, UserCog];

export function AgentGatekeeper({ onComplete, onReset }: AgentGatekeeperProps) {
  const [state, setState] = useState<GatekeeperState>({
    currentQuestion: 0,
    answers: [null, null, null],
    recommendation: null,
  });

  const handleAnswer = (answer: boolean) => {
    const newAnswers = [...state.answers] as [boolean | null, boolean | null, boolean | null];
    newAnswers[state.currentQuestion as number] = answer;

    const currentQ = state.currentQuestion as number;
    const isLastQuestion = currentQ === 2;

    if (isLastQuestion) {
      const yesCount = newAnswers.filter((a) => a === true).length;
      const recommendation = yesCount >= 2 ? 'azure' : 'copilot';
      setState({
        currentQuestion: 'complete',
        answers: newAnswers,
        recommendation,
      });
    } else {
      setState({
        ...state,
        currentQuestion: (currentQ + 1) as 0 | 1 | 2,
        answers: newAnswers,
      });
    }
  };

  const handleBack = () => {
    if (state.currentQuestion === 'complete') {
      setState({
        ...state,
        currentQuestion: 2,
        recommendation: null,
      });
    } else if (state.currentQuestion > 0) {
      setState({
        ...state,
        currentQuestion: (state.currentQuestion - 1) as 0 | 1 | 2,
      });
    }
  };

  const handleReset = () => {
    setState({
      currentQuestion: 0,
      answers: [null, null, null],
      recommendation: null,
    });
    onReset?.();
  };

  const handleContinue = () => {
    if (state.recommendation) {
      onComplete(state.recommendation);
    }
  };

  if (state.currentQuestion === 'complete' && state.recommendation) {
    return (
      <RecommendationCard
        recommendation={state.recommendation}
        answers={state.answers}
        onContinue={handleContinue}
        onBack={handleBack}
        onReset={handleReset}
      />
    );
  }

  const currentQ = state.currentQuestion as number;
  const question = GATEKEEPER_QUESTIONS[currentQ];
  const Icon = questionIcons[currentQ];

  return (
    <div className="max-w-2xl mx-auto">
      <div className="mb-8 text-center">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">
          Let&apos;s Find the Right Approach
        </h2>
        <p className="text-gray-600">
          Answer a few questions to determine the best path for your agent
        </p>
      </div>

      <div className="flex justify-center mb-8">
        {GATEKEEPER_QUESTIONS.map((_, idx) => (
          <div key={idx} className="flex items-center">
            <div
              className={cn(
                'w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium transition-all',
                idx < currentQ && 'bg-primary text-primary-foreground',
                idx === currentQ && 'bg-primary text-primary-foreground ring-4 ring-primary/20',
                idx > currentQ && 'bg-muted text-muted-foreground'
              )}
            >
              {idx < currentQ ? <CheckCircle className="h-5 w-5" /> : idx + 1}
            </div>
            {idx < GATEKEEPER_QUESTIONS.length - 1 && (
              <div
                className={cn(
                  'w-16 h-1 mx-2',
                  idx < currentQ ? 'bg-primary' : 'bg-muted'
                )}
              />
            )}
          </div>
        ))}
      </div>

      <Card className="animate-in fade-in-0 slide-in-from-right-4 duration-300">
        <CardHeader className="text-center pb-4">
          <div className="mx-auto mb-4 p-4 rounded-full bg-primary/10">
            <Icon className="h-8 w-8 text-primary" />
          </div>
          <CardTitle className="text-xl">{question.question}</CardTitle>
          <p className="text-sm text-muted-foreground mt-2">
            {question.description}
          </p>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              size="lg"
              variant="outline"
              className="flex-1 sm:max-w-[150px] h-14"
              onClick={() => handleAnswer(false)}
            >
              No
            </Button>
            <Button
              size="lg"
              className="flex-1 sm:max-w-[150px] h-14"
              onClick={() => handleAnswer(true)}
            >
              Yes
            </Button>
          </div>

          {currentQ > 0 && (
            <Button
              variant="ghost"
              className="w-full mt-4"
              onClick={handleBack}
            >
              <ArrowLeft className="h-4 w-4 mr-2" />
              Back to previous question
            </Button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

interface RecommendationCardProps {
  recommendation: 'copilot' | 'azure';
  answers: [boolean | null, boolean | null, boolean | null];
  onContinue: () => void;
  onBack: () => void;
  onReset: () => void;
}

function RecommendationCard({
  recommendation,
  answers,
  onContinue,
  onBack,
  onReset,
}: RecommendationCardProps) {
  const isAzure = recommendation === 'azure';
  const yesCount = answers.filter((a) => a === true).length;

  return (
    <div className="max-w-2xl mx-auto animate-in fade-in-0 slide-in-from-bottom-4 duration-300">
      <Card className={cn(
        'border-2',
        isAzure ? 'border-primary' : 'border-blue-500'
      )}>
        <CardHeader className="text-center pb-4">
          <div className={cn(
            'mx-auto mb-4 p-4 rounded-full',
            isAzure ? 'bg-primary/10' : 'bg-blue-500/10'
          )}>
            {isAzure ? (
              <Bot className="h-10 w-10 text-primary" />
            ) : (
              <Workflow className="h-10 w-10 text-blue-500" />
            )}
          </div>
          <Badge
            variant="secondary"
            className={cn(
              'mb-4 text-sm px-4 py-1',
              isAzure ? 'bg-primary/10 text-primary' : 'bg-blue-500/10 text-blue-600'
            )}
          >
            Recommended Path
          </Badge>
          <CardTitle className="text-2xl">
            {isAzure ? 'Azure AI Agent' : 'Copilot Studio'}
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <p className="text-center text-muted-foreground">
            {isAzure ? (
              <>
                Based on your answers ({yesCount}/3 indicate complex requirements),
                an <strong>Azure AI Agent</strong> is the best fit. This path provides
                advanced reasoning, enterprise integrations, and personalized responses.
              </>
            ) : (
              <>
                Based on your answers ({yesCount}/3 indicate complex requirements),
                <strong> Copilot Studio</strong> is the better fit. This path is ideal
                for structured workflows with predictable patterns.
              </>
            )}
          </p>

          <div className="bg-muted/50 rounded-lg p-4">
            <h4 className="font-medium mb-3 text-sm">Your Answers</h4>
            <ul className="space-y-2 text-sm">
              {GATEKEEPER_QUESTIONS.map((q, idx) => (
                <li key={idx} className="flex items-center gap-2">
                  <span className={cn(
                    'w-5 h-5 rounded-full flex items-center justify-center text-xs font-medium',
                    answers[idx] ? 'bg-green-100 text-green-700' : 'bg-gray-100 text-gray-600'
                  )}>
                    {answers[idx] ? 'Y' : 'N'}
                  </span>
                  <span className="text-muted-foreground">{q.question}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="flex flex-col sm:flex-row gap-3">
            <Button variant="outline" className="flex-1" onClick={onBack}>
              <ArrowLeft className="h-4 w-4 mr-2" />
              Review Answers
            </Button>
            <Button
              className={cn(
                'flex-1',
                !isAzure && 'bg-blue-500 hover:bg-blue-600'
              )}
              onClick={onContinue}
            >
              Continue
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>
          </div>

          <Button
            variant="ghost"
            className="w-full text-muted-foreground"
            onClick={onReset}
          >
            Start Over
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
