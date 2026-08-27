/**
 * @file AUTO-GENERATED
 */
import React from 'react';
import { IdentityStep } from './steps/IdentityStep.js';
import { ModelStep } from './steps/ModelStep.js';
import { ToolsStep } from './steps/ToolsStep.js';
import { ContextStep } from './steps/ContextStep.js';
import { MemoryStep } from './steps/MemoryStep.js';
import { EvaluatorStep } from './steps/EvaluatorStep.js';
import { ProfileStep } from './steps/ProfileStep.js';
import { TopologyStep } from './steps/TopologyStep.js';
import { TestStep } from './steps/TestStep.js';
import { ReviewStep } from './steps/ReviewStep.js';

export function AgentBuilderWizard() {
  const [step, setStep] = React.useState(0);
  const steps = [
    <IdentityStep key="identity" />,
    <ModelStep key="model" />,
    <ToolsStep key="tools" />,
    <ContextStep key="context" />,
    <MemoryStep key="memory" />,
    <EvaluatorStep key="evaluator" />,
    <ProfileStep key="profile" />,
    <TopologyStep key="topology" />,
    <TestStep key="test" />,
    <ReviewStep key="review" />
  ];

  return (
    <div className="agent-builder-wizard">
      <h2>Agent Builder (10-Step Wizard)</h2>
      <div className="wizard-step-content">
        {steps[step]}
      </div>
      <div className="wizard-controls">
        <button disabled={step === 0} onClick={() => setStep(step - 1)}>Back</button>
        <button disabled={step === steps.length - 1} onClick={() => setStep(step + 1)}>Next</button>
      </div>
    </div>
  );
}
