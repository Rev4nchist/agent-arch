'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Stepper, StepperContent, StepperNavigation } from '@/components/ui/stepper';
import { useAgentWizard } from '@/hooks/useAgentWizard';
import {
  WizardStepBasicInfo,
  WizardStepInstructions,
  WizardStepTools,
  WizardStepKnowledge,
  WizardStepGovernance,
  WizardStepReview,
} from './wizard';
import { WIZARD_STEPS, type WizardStep } from '@/lib/agent-factory-types';
import { api } from '@/lib/api';
import { ArrowLeft, CheckCircle, Bot } from 'lucide-react';

interface AgentBuilderWizardProps {
  onBack: () => void;
  onSuccess?: (agentId: string) => void;
}

export function AgentBuilderWizard({ onBack, onSuccess }: AgentBuilderWizardProps) {
  const {
    state,
    nextStep,
    prevStep,
    setStep,
    updateBasicInfo,
    updateInstructions,
    updateTools,
    updateKnowledge,
    updateGovernance,
    setSubmitting,
    setError,
    canProceed,
    isComplete,
    reset,
  } = useAgentWizard();

  const [isSuccess, setIsSuccess] = useState(false);
  const [createdAgentId, setCreatedAgentId] = useState<string | null>(null);

  const handleSubmit = async () => {
    if (!isComplete) return;

    setSubmitting(true);
    setError(null);

    try {
      const tools: string[] = [];
      if (state.data.tools.fileSearch) tools.push('file_search');
      if (state.data.tools.codeInterpreter) tools.push('code_interpreter');

      const response = await api.agents.create({
        name: state.data.basicInfo.name,
        description: state.data.basicInfo.description,
        owner: state.data.basicInfo.owner,
        department: state.data.basicInfo.department || undefined,
        tier: 'Tier2_Department',
        status: 'Design',
        use_case: state.data.instructions.systemPrompt.slice(0, 200),
        data_sources: state.data.tools.connectors,
        related_tasks: [],
      });

      setCreatedAgentId(response.id || null);
      setIsSuccess(true);
      onSuccess?.(response.id || '');
    } catch (err) {
      console.error('Failed to create agent:', err);
      setError('Failed to create agent. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditStep = (step: number) => {
    setStep(step as WizardStep);
  };

  const handleStartOver = () => {
    reset();
    setIsSuccess(false);
    setCreatedAgentId(null);
  };

  if (isSuccess) {
    return (
      <Card className="max-w-2xl mx-auto">
        <CardContent className="p-12 text-center">
          <div className="mx-auto mb-6 p-4 rounded-full bg-green-100 w-fit">
            <CheckCircle className="h-12 w-12 text-green-600" />
          </div>
          <h3 className="text-2xl font-semibold text-gray-900 mb-2">
            Agent Created Successfully!
          </h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Your agent <strong>{state.data.basicInfo.name}</strong> has been created and
            is now in the Design phase. You can view it in the portfolio and update its
            status as it progresses through development.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button variant="outline" onClick={handleStartOver}>
              Create Another Agent
            </Button>
            <Button onClick={onBack}>
              <Bot className="h-4 w-4 mr-2" />
              View Portfolio
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <Button variant="ghost" onClick={onBack} className="mb-4">
          <ArrowLeft className="h-4 w-4 mr-2" />
          Back to assessment
        </Button>

        <div className="text-center mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">Build Your Azure Agent</h2>
          <p className="text-gray-600">
            Configure your agent step by step. Required fields are marked with *
          </p>
        </div>

        <Stepper
          steps={WIZARD_STEPS.map((s) => ({ id: s.id, title: s.title, description: s.description }))}
          currentStep={state.currentStep}
          onStepClick={handleEditStep}
          allowClickNavigation={true}
          className="mb-8"
        />
      </div>

      <Card>
        <CardHeader>
          <CardTitle>
            {WIZARD_STEPS.find((s) => s.id === state.currentStep)?.title}
          </CardTitle>
        </CardHeader>
        <CardContent>
          <StepperContent step={1} currentStep={state.currentStep}>
            <WizardStepBasicInfo
              data={state.data.basicInfo}
              onChange={updateBasicInfo}
            />
          </StepperContent>

          <StepperContent step={2} currentStep={state.currentStep}>
            <WizardStepInstructions
              data={state.data.instructions}
              onChange={updateInstructions}
            />
          </StepperContent>

          <StepperContent step={3} currentStep={state.currentStep}>
            <WizardStepTools data={state.data.tools} onChange={updateTools} />
          </StepperContent>

          <StepperContent step={4} currentStep={state.currentStep}>
            <WizardStepKnowledge
              data={state.data.knowledge}
              onChange={updateKnowledge}
            />
          </StepperContent>

          <StepperContent step={5} currentStep={state.currentStep}>
            <WizardStepGovernance
              data={state.data.governance}
              onChange={updateGovernance}
            />
          </StepperContent>

          <StepperContent step={6} currentStep={state.currentStep}>
            <WizardStepReview data={state.data} onEditStep={handleEditStep} />
          </StepperContent>

          {state.error && (
            <div className="mt-4 text-sm text-destructive bg-destructive/10 p-3 rounded-md">
              {state.error}
            </div>
          )}

          <StepperNavigation
            currentStep={state.currentStep}
            totalSteps={6}
            onNext={nextStep}
            onPrev={prevStep}
            onSubmit={handleSubmit}
            isNextDisabled={!canProceed}
            isSubmitting={state.isSubmitting}
            submitLabel="Create Agent"
          />
        </CardContent>
      </Card>
    </div>
  );
}
