import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import SignalLab from './SignalLab';
import BeamLab from './BeamLab';
import './styles.css';
import './signal-lab-polish.css';
import './beam-lab.css';

function resolveView() {
  if (location.hash === '#signal-lab') return 'signal';
  if (location.hash === '#beam-lab') return 'beam';
  return 'map';
}

function ConceptRuntime() {
  const [view, setView] = useState(resolveView());
  if (view === 'signal') return <SignalLab onBack={() => { location.hash = ''; setView('map'); }} />;
  if (view === 'beam') return <BeamLab onBack={() => { location.hash = ''; setView('map'); }} />;
  return <div onDoubleClick={() => { location.hash = 'signal-lab'; setView('signal'); }}><App /></div>;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><ConceptRuntime /></React.StrictMode>,
);
