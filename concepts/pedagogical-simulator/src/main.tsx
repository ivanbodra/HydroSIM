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
type Route={view:View;focus?:string};
function resolveRoute():Route {
  const raw=location.hash.replace(/^#/,'');
  const [lab,focus]=raw.split('/');
  const map:Record<string,View>={'signal-lab':'signal','beam-lab':'beam','propagation-lab':'propagation','vessel-lab':'vessel','motion-lab':'motion','integrated-lab':'integrated'};
  return {view:map[lab]??'map',focus};
}
function ConceptRuntime() {
  const [route,setRoute]=useState<Route>(resolveRoute());
  useEffect(()=>{const sync=()=>setRoute(resolveRoute());window.addEventListener('hashchange',sync);return()=>window.removeEventListener('hashchange',sync)},[]);
  const back=()=>{location.hash='';};
  if(route.view==='signal') return <SignalLab onBack={back} focus={route.focus}/>;
  if(route.view==='beam') return <BeamLab onBack={back} focus={route.focus}/>;
  if(route.view==='propagation') return <PropagationLab onBack={back} focus={route.focus}/>;
  if(route.view==='vessel') return <VesselLab onBack={back} focus={route.focus}/>;
  if(route.view==='motion') return <MotionLab onBack={back} focus={route.focus}/>;
  if(route.view==='integrated') return <IntegratedLab onBack={back} focus={route.focus}/>;
  return <App/>;
}
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><ConceptRuntime/></React.StrictMode>);
