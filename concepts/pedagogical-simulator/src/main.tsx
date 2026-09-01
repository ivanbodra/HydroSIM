import React, { useEffect, useState } from 'react';
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
import './map-polish.css';
import './experience-deepening.css';

type View='map'|'signal'|'beam'|'propagation'|'vessel'|'motion'|'integrated';
function resolveView():View {
  const lab=location.hash.replace(/^#/,'').split('/')[0];
  const map:Record<string,View>={'signal-lab':'signal','beam-lab':'beam','propagation-lab':'propagation','vessel-lab':'vessel','motion-lab':'motion','integrated-lab':'integrated'};
  return map[lab]??'map';
}
function ConceptRuntime() {
  const [view,setView]=useState<View>(resolveView());
  useEffect(()=>{const sync=()=>setView(resolveView());window.addEventListener('hashchange',sync);return()=>window.removeEventListener('hashchange',sync)},[]);
  const back=()=>{location.hash='';};
  if(view==='signal') return <SignalLab onBack={back}/>;
  if(view==='beam') return <BeamLab onBack={back}/>;
  if(view==='propagation') return <PropagationLab onBack={back}/>;
  if(view==='vessel') return <VesselLab onBack={back}/>;
  if(view==='motion') return <MotionLab onBack={back}/>;
  if(view==='integrated') return <IntegratedLab onBack={back}/>;
  return <App/>;
}
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><ConceptRuntime/></React.StrictMode>);
