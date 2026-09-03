import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom/client';
import { ChevronRight } from 'lucide-react';
import App from './App';
import CurriculumMap from './CurriculumMap';
import WaveLab from './WaveLab';
import SignalLab from './SignalLab';
import BeamLab from './BeamLab';
import PropagationLab from './PropagationLab';
import VesselLab from './VesselLab';
import MotionLab from './MotionLab';
import IntegratedLab from './IntegratedLab';
import './styles.css';
import './wave-lab.css';
import './signal-lab-polish.css';
import './beam-lab.css';
import './advanced-labs.css';
import './map-polish.css';
import './experience-deepening.css';
import './curriculum-map.css';

type View='map'|'legacy'|'wave'|'signal'|'beam'|'propagation'|'vessel'|'motion'|'integrated';type Route={view:View;focus?:string};
const labBase:Record<Exclude<View,'map'|'legacy'|'wave'>,string>={signal:'signal-lab',beam:'beam-lab',propagation:'propagation-lab',vessel:'vessel-lab',motion:'motion-lab',integrated:'integrated-lab'};
const navigation:Record<Exclude<View,'map'|'legacy'|'wave'>,Array<[string,string,string]>>={signal:[['waveform','Waveform','CW, chirp and pulse shapes'],['pulse','Pulse','Duration, timing and repetition'],['spectrum','Spectrum','Bandwidth and frequency content'],['compression','Compression','Matched filtering and resolution']],beam:[['beam-pattern','Beam Pattern','Main lobe and sidelobes'],['steering','Steering','Across-track and along-track'],['beamwidth','Beamwidth','Angular coverage'],['footprint','Footprint','Seafloor projection']],propagation:[['sound-speed','Sound Speed','Profile shapes and assumptions'],['refraction','Refraction','Ray bending through the water'],['attenuation','Attenuation','Loss with range and frequency'],['bottom-interaction','Bottom Interaction','Reflection and scattering']],vessel:[['vessel','Vessel','Platform and body geometry'],['transducer','Transducer','Mounting and orientation'],['gnss','GNSS','Antenna position'],['imu','IMU','Motion sensing'],['lever-arms','Lever Arms','Relative sensor offsets'],['vertical-references','Vertical References','Waterline, datum and levels']],motion:[['heave','Heave','Vertical displacement'],['roll','Roll','Longitudinal-axis rotation'],['pitch','Pitch','Transverse-axis rotation'],['yaw','Yaw','Vertical-axis rotation'],['motion-viewer','Motion Viewer','Linked vessel and beam response'],['sounding-impact','Sounding Impact','Visible geometric consequence']],integrated:[['survey-setup','Survey Setup','Mission and environment'],['realtime-view','Realtime View','Linked 2D and 3D simulation'],['sounding-generation','Sounding Generation','Synthetic observation field'],['uncertainty','Uncertainty','Visual source contributions'],['comparison','Comparison','Baseline versus current'],['experiment-presets','Experiment Presets','Curated learning scenes']]};
function resolveRoute():Route{const[lab,focus]=location.hash.replace(/^#/,'').split('/');const map:Record<string,View>={'legacy':'legacy','wave-lab':'wave','signal-lab':'signal','beam-lab':'beam','propagation-lab':'propagation','vessel-lab':'vessel','motion-lab':'motion','integrated-lab':'integrated'};return{view:map[lab]??'map',focus}}
function LabNavigator({route}:{route:Route}){if(route.view==='map'||route.view==='legacy'||route.view==='wave')return null;const view=route.view as Exclude<View,'map'|'legacy'|'wave'>;const items=navigation[view];const active=route.focus??items[0][0];return <aside className="lab-route-nav"><small>VISUAL LAB VIEWS</small>{items.map(([key,label,desc])=><button key={key} className={active===key?'active':''} onClick={()=>{location.hash=`#${labBase[view]}/${key}`}}><span><strong>{label}</strong><em>{desc}</em></span><ChevronRight size={14}/></button>)}</aside>}
function ConceptRuntime(){const[route,setRoute]=useState<Route>(resolveRoute());useEffect(()=>{const sync=()=>setRoute(resolveRoute());window.addEventListener('hashchange',sync);return()=>window.removeEventListener('hashchange',sync)},[]);const back=()=>{location.hash=''};let lab:React.ReactNode=null;if(route.view==='wave')lab=<WaveLab onBack={back}/>;if(route.view==='signal')lab=<SignalLab onBack={back} focus={route.focus}/>;if(route.view==='beam')lab=<BeamLab onBack={back} focus={route.focus}/>;if(route.view==='propagation')lab=<PropagationLab onBack={back} focus={route.focus}/>;if(route.view==='vessel')lab=<VesselLab onBack={back} focus={route.focus}/>;if(route.view==='motion')lab=<MotionLab onBack={back} focus={route.focus}/>;if(route.view==='integrated')lab=<IntegratedLab onBack={back} focus={route.focus}/>;if(route.view==='map')return <CurriculumMap onOpenLegacy={()=>{location.hash='#legacy'}}/>;if(route.view==='legacy')return <App/>;return <><div className={`routed-lab focus-${route.focus??'overview'}`}>{lab}</div><LabNavigator route={route}/></>}
ReactDOM.createRoot(document.getElementById('root')!).render(<React.StrictMode><ConceptRuntime/></React.StrictMode>);
