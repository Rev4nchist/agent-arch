'use client';

import { useReducer, useCallback, useMemo } from 'react';
import type {
  WizardState,
  WizardAction,
  WizardStep,
  WizardData,
  WizardBasicInfo,
  WizardInstructions,
  WizardTools,
  WizardKnowledge,
  WizardGovernance,
} from '@/lib/agent-factory-types';

const initialWizardData: WizardData = {
  basicInfo: {
    name: '',
    description: '',
    department: '',
    owner: '',
  },
  instructions: {
    systemPrompt: '',
    templateId: undefined,
  },
  tools: {
    fileSearch: false,
    codeInterpreter: false,
    connectors: [],
  },
  knowledge: {
    files: [],
    uploadedIds: [],
  },
  governance: {
    classification: 'Internal',
    costCenter: '',
    requiresApproval: false,
  },
};

const initialState: WizardState = {
  currentStep: 1,
  data: initialWizardData,
  validation: {
    1: false,
    2: false,
    3: true,
    4: true,
    5: true,
    6: false,
  },
  isSubmitting: false,
  error: null,
};

function wizardReducer(state: WizardState, action: WizardAction): WizardState {
  switch (action.type) {
    case 'SET_STEP':
      return { ...state, currentStep: action.step };

    case 'NEXT_STEP':
      if (state.currentStep < 6) {
        return { ...state, currentStep: (state.currentStep + 1) as WizardStep };
      }
      return state;

    case 'PREV_STEP':
      if (state.currentStep > 1) {
        return { ...state, currentStep: (state.currentStep - 1) as WizardStep };
      }
      return state;

    case 'UPDATE_BASIC_INFO':
      return {
        ...state,
        data: {
          ...state.data,
          basicInfo: { ...state.data.basicInfo, ...action.data },
        },
      };

    case 'UPDATE_INSTRUCTIONS':
      return {
        ...state,
        data: {
          ...state.data,
          instructions: { ...state.data.instructions, ...action.data },
        },
      };

    case 'UPDATE_TOOLS':
      return {
        ...state,
        data: {
          ...state.data,
          tools: { ...state.data.tools, ...action.data },
        },
      };

    case 'UPDATE_KNOWLEDGE':
      return {
        ...state,
        data: {
          ...state.data,
          knowledge: { ...state.data.knowledge, ...action.data },
        },
      };

    case 'UPDATE_GOVERNANCE':
      return {
        ...state,
        data: {
          ...state.data,
          governance: { ...state.data.governance, ...action.data },
        },
      };

    case 'SET_VALIDATION':
      return {
        ...state,
        validation: { ...state.validation, [action.step]: action.isValid },
      };

    case 'SET_SUBMITTING':
      return { ...state, isSubmitting: action.isSubmitting };

    case 'SET_ERROR':
      return { ...state, error: action.error };

    case 'RESET':
      return initialState;

    default:
      return state;
  }
}

export function useAgentWizard() {
  const [state, dispatch] = useReducer(wizardReducer, initialState);

  const setStep = useCallback((step: WizardStep) => {
    dispatch({ type: 'SET_STEP', step });
  }, []);

  const nextStep = useCallback(() => {
    dispatch({ type: 'NEXT_STEP' });
  }, []);

  const prevStep = useCallback(() => {
    dispatch({ type: 'PREV_STEP' });
  }, []);

  const updateBasicInfo = useCallback((data: Partial<WizardBasicInfo>) => {
    dispatch({ type: 'UPDATE_BASIC_INFO', data });
  }, []);

  const updateInstructions = useCallback((data: Partial<WizardInstructions>) => {
    dispatch({ type: 'UPDATE_INSTRUCTIONS', data });
  }, []);

  const updateTools = useCallback((data: Partial<WizardTools>) => {
    dispatch({ type: 'UPDATE_TOOLS', data });
  }, []);

  const updateKnowledge = useCallback((data: Partial<WizardKnowledge>) => {
    dispatch({ type: 'UPDATE_KNOWLEDGE', data });
  }, []);

  const updateGovernance = useCallback((data: Partial<WizardGovernance>) => {
    dispatch({ type: 'UPDATE_GOVERNANCE', data });
  }, []);

  const setValidation = useCallback((step: WizardStep, isValid: boolean) => {
    dispatch({ type: 'SET_VALIDATION', step, isValid });
  }, []);

  const setSubmitting = useCallback((isSubmitting: boolean) => {
    dispatch({ type: 'SET_SUBMITTING', isSubmitting });
  }, []);

  const setError = useCallback((error: string | null) => {
    dispatch({ type: 'SET_ERROR', error });
  }, []);

  const reset = useCallback(() => {
    dispatch({ type: 'RESET' });
  }, []);

  const validateBasicInfo = useCallback((): boolean => {
    const { name, description, owner } = state.data.basicInfo;
    return name.trim().length > 0 && description.trim().length > 0 && owner.trim().length > 0;
  }, [state.data.basicInfo]);

  const validateInstructions = useCallback((): boolean => {
    const { systemPrompt } = state.data.instructions;
    return systemPrompt.trim().length > 0;
  }, [state.data.instructions]);

  const validateCurrentStep = useCallback((): boolean => {
    switch (state.currentStep) {
      case 1:
        return validateBasicInfo();
      case 2:
        return validateInstructions();
      case 3:
      case 4:
      case 5:
        return true;
      case 6:
        return validateBasicInfo() && validateInstructions();
      default:
        return false;
    }
  }, [state.currentStep, validateBasicInfo, validateInstructions]);

  const canProceed = useMemo(() => {
    return validateCurrentStep();
  }, [validateCurrentStep]);

  const isComplete = useMemo(() => {
    return validateBasicInfo() && validateInstructions();
  }, [validateBasicInfo, validateInstructions]);

  return {
    state,
    setStep,
    nextStep,
    prevStep,
    updateBasicInfo,
    updateInstructions,
    updateTools,
    updateKnowledge,
    updateGovernance,
    setValidation,
    setSubmitting,
    setError,
    reset,
    canProceed,
    isComplete,
    validateCurrentStep,
  };
}
