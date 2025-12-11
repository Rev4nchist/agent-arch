'use client';

import * as React from 'react';
import { cn } from '@/lib/utils';
import { Check } from 'lucide-react';

export interface StepperStep {
  id: number;
  title: string;
  description?: string;
}

interface StepperProps {
  steps: StepperStep[];
  currentStep: number;
  onStepClick?: (step: number) => void;
  className?: string;
  allowClickNavigation?: boolean;
}

export function Stepper({
  steps,
  currentStep,
  onStepClick,
  className,
  allowClickNavigation = false,
}: StepperProps) {
  return (
    <nav aria-label="Progress" className={cn('w-full', className)}>
      <ol className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isCompleted = currentStep > step.id;
          const isCurrent = currentStep === step.id;
          const isClickable = allowClickNavigation && (isCompleted || isCurrent);

          return (
            <li key={step.id} className="relative flex-1">
              <div className="flex flex-col items-center">
                <button
                  type="button"
                  onClick={() => isClickable && onStepClick?.(step.id)}
                  disabled={!isClickable}
                  className={cn(
                    'relative z-10 flex h-10 w-10 items-center justify-center rounded-full border-2 transition-all duration-200',
                    isCompleted && 'border-primary bg-primary text-primary-foreground',
                    isCurrent && 'border-primary bg-background text-primary',
                    !isCompleted && !isCurrent && 'border-muted-foreground/30 bg-background text-muted-foreground',
                    isClickable && 'cursor-pointer hover:border-primary/80',
                    !isClickable && 'cursor-default'
                  )}
                  aria-current={isCurrent ? 'step' : undefined}
                >
                  {isCompleted ? (
                    <Check className="h-5 w-5" />
                  ) : (
                    <span className="text-sm font-medium">{step.id}</span>
                  )}
                </button>
                <div className="mt-2 text-center">
                  <span
                    className={cn(
                      'text-sm font-medium',
                      isCurrent && 'text-primary',
                      !isCurrent && 'text-muted-foreground'
                    )}
                  >
                    {step.title}
                  </span>
                  {step.description && (
                    <span className="block text-xs text-muted-foreground mt-0.5 hidden sm:block">
                      {step.description}
                    </span>
                  )}
                </div>
              </div>
              {index < steps.length - 1 && (
                <div
                  className={cn(
                    'absolute top-5 left-[calc(50%+20px)] w-[calc(100%-40px)] h-0.5 -translate-y-1/2',
                    isCompleted ? 'bg-primary' : 'bg-muted-foreground/30'
                  )}
                  aria-hidden="true"
                />
              )}
            </li>
          );
        })}
      </ol>
    </nav>
  );
}

interface StepperContentProps {
  step: number;
  currentStep: number;
  children: React.ReactNode;
  className?: string;
}

export function StepperContent({
  step,
  currentStep,
  children,
  className,
}: StepperContentProps) {
  if (step !== currentStep) return null;

  return (
    <div
      className={cn('animate-in fade-in-0 slide-in-from-right-4 duration-300', className)}
      role="tabpanel"
      aria-label={`Step ${step}`}
    >
      {children}
    </div>
  );
}

interface StepperNavigationProps {
  currentStep: number;
  totalSteps: number;
  onNext: () => void;
  onPrev: () => void;
  onSubmit?: () => void;
  isNextDisabled?: boolean;
  isSubmitting?: boolean;
  nextLabel?: string;
  prevLabel?: string;
  submitLabel?: string;
  className?: string;
}

export function StepperNavigation({
  currentStep,
  totalSteps,
  onNext,
  onPrev,
  onSubmit,
  isNextDisabled = false,
  isSubmitting = false,
  nextLabel = 'Next',
  prevLabel = 'Back',
  submitLabel = 'Submit',
  className,
}: StepperNavigationProps) {
  const isFirstStep = currentStep === 1;
  const isLastStep = currentStep === totalSteps;

  return (
    <div className={cn('flex justify-between pt-6 border-t', className)}>
      <button
        type="button"
        onClick={onPrev}
        disabled={isFirstStep || isSubmitting}
        className={cn(
          'px-4 py-2 text-sm font-medium rounded-md border transition-colors',
          'hover:bg-accent disabled:opacity-50 disabled:cursor-not-allowed'
        )}
      >
        {prevLabel}
      </button>
      {isLastStep ? (
        <button
          type="button"
          onClick={onSubmit}
          disabled={isNextDisabled || isSubmitting}
          className={cn(
            'px-6 py-2 text-sm font-medium rounded-md transition-colors',
            'bg-primary text-primary-foreground hover:bg-primary/90',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          {isSubmitting ? 'Creating...' : submitLabel}
        </button>
      ) : (
        <button
          type="button"
          onClick={onNext}
          disabled={isNextDisabled || isSubmitting}
          className={cn(
            'px-6 py-2 text-sm font-medium rounded-md transition-colors',
            'bg-primary text-primary-foreground hover:bg-primary/90',
            'disabled:opacity-50 disabled:cursor-not-allowed'
          )}
        >
          {nextLabel}
        </button>
      )}
    </div>
  );
}
