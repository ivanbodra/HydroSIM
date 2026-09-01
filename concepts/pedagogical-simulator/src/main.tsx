import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import SignalLab from './SignalLab';
import './styles.css';

function ConceptRuntime() {
  const [view, setView] = useState(location.hash === '#signal-lab' ? 'signal' : 'map');
  if (view === 'signal') return <SignalLab onBack={() => { location.hash = ''; setView('map'); }} />;
  return <div onDoubleClick={() => { location.hash = 'signal-lab'; setView('signal'); }}><App /></div>;
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode><ConceptRuntime /></React.StrictMode>,
);
