import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import SignalLab from './SignalLab';
import BeamLab from './BeamLab';
import PropagationLab from './PropagationLab';
import VesselLab from './VesselLab';
import MotionLab from './MotionLab';
import IntegratedLab from './IntegratedLab';
import './styles.css';
import './signal-lab-polish.css';
import './beam-lab.css';
import './advanced-labs.css';

function resolveView() {
  if (location.hash === '#signal-lab') return 'signal';
  if (location.hash === '#beam-lab') return 'beam';
  if (location.hash === '#propagation-lab') return 'propagation';
  if (location.hash === '#vessel-lab') return 'vessel';
  if (location.hash === '#motion-lab') return 'motion';
  if (location.hash === '#integrated-lab') return 'integrated';
  return 'map';
}

function ConceptRuntime() {
  const [view, setView] = useState(resolveView());
  const back = () => { location.hash = ''; setView('map'); };
  if (view === 'signal') return <SignalLab onBack={back} />;
  if (view === 'beam') return <BeamLab onBack={back} />;
  if (view === 'propagation') return <PropagationLab onBack={back} />;
  if (view === 'vessel') return <VesselLab onBack={back} />;
  if (view === 'motion') return <MotionLab onBack={back} />;
  if (view === 'integrated') return <IntegratedLab onBack={back} />;
  return <App />;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><ConceptRuntime /></React.StrictMode>,
);
