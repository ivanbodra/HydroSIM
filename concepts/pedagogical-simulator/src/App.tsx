import { AnimatePresence, motion } from 'motion/react';
import {
  Activity,
  Anchor,
  Box,
  ChevronDown,
  CircleDot,
  Compass,
  Cpu,
  Gauge,
  GitCompare,
  Layers3,
  Menu,
  Navigation,
  Orbit,
  PanelLeftClose,
  PanelLeftOpen,
  Play,
  Radio,
  Rotate3D,
  Satellite,
  Settings2,
  Ship,
  SlidersHorizontal,
  Sparkles,
  Target,
  Waves,
  Zap,
} from 'lucide-react';
import { useMemo, useState } from 'react';

type ModuleKey = 'signal' | 'beam' | 'propagation' | 'vessel' | 'motion' | 'integrated';

type Submodule = {
  title: string;
  subtitle: string;
  icon: React.ComponentType<{ size?: number; strokeWidth?: number }>;
};

type Module = {
  key: ModuleKey;
  index: string;
  title: string;
  description: string;
  icon: React.ComponentType<{ size?: number; strokeWidth?: number }>;
  accent: string;
  accentRgb: string;
  submodules: Submodule[];
};

const modules: Module[] = [
  {
    key: 'signal', index: '01', title: 'Signal', description: 'Waveform, pulse structure and compression', icon: Activity, accent: '#34d9ef', accentRgb: '52,217,239',
    submodules: [
      { title: 'Waveform', subtitle: 'CW, chirp and pulse shapes', icon: Activity },
      { title: 'Pulse', subtitle: 'Duration, timing and repetition', icon: Radio },
      { title: 'Spectrum', subtitle: 'Bandwidth and frequency content', icon: Gauge },
      { title: 'Compression', subtitle: 'Matched filtering and resolution', icon: Zap },
    ],
  },
  {
    key: 'beam', index: '02', title: 'Beam', description: 'Directivity, steering and footprint', icon: Target, accent: '#58c7ff', accentRgb: '88,199,255',
    submodules: [
      { title: 'Beam Pattern', subtitle: 'Main lobe and sidelobes', icon: Target },
      { title: 'Steering', subtitle: 'Across-track and along-track', icon: Navigation },
      { title: 'Beamwidth', subtitle: 'Angular coverage', icon: Compass },
      { title: 'Footprint', subtitle: 'Seafloor projection', icon: CircleDot },
    ],
  },
  {
    key: 'propagation', index: '03', title: 'Propagation', description: 'Water-column path and acoustic loss', icon: Layers3, accent: '#50dfce', accentRgb: '80,223,206',
    submodules: [
      { title: 'Sound Speed', subtitle: 'Profile shapes and assumptions', icon: SlidersHorizontal },
      { title: 'Refraction', subtitle: 'Ray bending through the water', icon: Orbit },
      { title: 'Attenuation', subtitle: 'Loss with range and frequency', icon: Waves },
      { title: 'Bottom Interaction', subtitle: 'Reflection and scattering', icon: Layers3 },
    ],
  },
  {
    key: 'vessel', index: '04', title: 'Vessel & Sensors', description: 'Geometry, sensors and reference levels', icon: Ship, accent: '#ffbd4f', accentRgb: '255,189,79',
    submodules: [
      { title: 'Vessel', subtitle: 'Platform and body geometry', icon: Ship },
      { title: 'Transducer', subtitle: 'Mounting and orientation', icon: Radio },
      { title: 'GNSS', subtitle: 'Antenna position', icon: Satellite },
      { title: 'IMU', subtitle: 'Motion sensing', icon: Cpu },
      { title: 'Lever Arms', subtitle: 'Relative sensor offsets', icon: Anchor },
      { title: 'Vertical References', subtitle: 'Waterline, datum and levels', icon: Box },
    ],
  },
  {
    key: 'motion', index: '05', title: 'Motion', description: 'Platform motion and sounding consequences', icon: Rotate3D, accent: '#af7cff', accentRgb: '175,124,255',
    submodules: [
      { title: 'Heave', subtitle: 'Vertical displacement', icon: Waves },
      { title: 'Roll', subtitle: 'Rotation around longitudinal axis', icon: Rotate3D },
      { title: 'Pitch', subtitle: 'Rotation around transverse axis', icon: Rotate3D },
      { title: 'Yaw', subtitle: 'Rotation around vertical axis', icon: Compass },
      { title: 'Motion Viewer', subtitle: 'Linked vessel and beam response', icon: Orbit },
      { title: 'Sounding Impact', subtitle: 'Visible geometric consequence', icon: Target },
    ],
  },
  {
    key: 'integrated', index: '06', title: 'Integrated Lab', description: 'Complete pedagogical survey experience', icon: Sparkles, accent: '#8ce35f', accentRgb: '140,227,95',
    submodules: [
      { title: 'Survey Setup', subtitle: 'Mission and environment', icon: Navigation },
      { title: 'Realtime View', subtitle: 'Linked 2D and 3D simulation', icon: Play },
      { title: 'Sounding Generation', subtitle: 'Synthetic observation field', icon: CircleDot },
      { title: 'Uncertainty', subtitle: 'Visual source contributions', icon: Gauge },
      { title: 'Comparison', subtitle: 'Baseline versus current', icon: GitCompare },
      { title: 'Experiment Presets', subtitle: 'Curated learning scenes', icon: Sparkles },
    ],
  },
];

const navItems = ['Explore', 'Scenarios', 'Lab', 'Compare'];

export default function App() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [expanded, setExpanded] = useState<ModuleKey>('signal');
  const [selected, setSelected] = useState<{ module: Module; submodule?: Submodule } | null>(null);
  const [activeNav, setActiveNav] = useState('Explore');

  const selectedAccent = selected?.module.accent ?? '#34d9ef';
  const selectedRgb = selected?.module.accentRgb ?? '52,217,239';

  const heroTitle = useMemo(() => {
    if (!selected) return 'Hydrographic concepts, made tangible.';
    return selected.submodule ? selected.submodule.title : selected.module.title;
  }, [selected]);

  return (
    <div className="app-shell" style={{ '--selected': selectedAccent, '--selected-rgb': selectedRgb } as React.CSSProperties}>
      <header className="topbar">
        <div className="brand-row">
          <button className="icon-button" aria-label="Toggle sidebar" onClick={() => setSidebarOpen(v => !v)}>
            {sidebarOpen ? <PanelLeftClose size={19} /> : <PanelLeftOpen size={19} />}
          </button>
          <div className="brand"><strong>Hydro<span>SIM</span></strong><small>Concept Lab</small></div>
        </div>
        <nav className="topnav">
          {navItems.map(item => (
            <button key={item} className={activeNav === item ? 'active' : ''} onClick={() => setActiveNav(item)}>{item}</button>
          ))}
        </nav>
        <div className="status-group">
          <span className="status-dot" />
          <span>Concept runtime</span>
          <button className="icon-button"><Settings2 size={18} /></button>
        </div>
      </header>

      <div className="workspace">
        <AnimatePresence initial={false}>
          {sidebarOpen && (
            <motion.aside className="sidebar" initial={{ x: -34, opacity: 0 }} animate={{ x: 0, opacity: 1 }} exit={{ x: -34, opacity: 0 }} transition={{ duration: .22 }}>
              <div className="sidebar-heading"><span>Modules</span><Menu size={16} /></div>
              <div className="module-menu">
                {modules.map(module => {
                  const Icon = module.icon;
                  const isExpanded = expanded === module.key;
                  return (
                    <div className="menu-section" key={module.key} style={{ '--accent': module.accent, '--accent-rgb': module.accentRgb } as React.CSSProperties}>
                      <button className={`menu-module ${isExpanded ? 'expanded' : ''}`} onClick={() => setExpanded(isExpanded ? module.key : module.key)}>
                        <span className="module-icon"><Icon size={20} strokeWidth={1.8} /></span>
                        <span className="menu-copy"><strong>{module.index} {module.title}</strong><small>{module.description}</small></span>
                        <motion.span animate={{ rotate: isExpanded ? 180 : 0 }}><ChevronDown size={16} /></motion.span>
                      </button>
                      <AnimatePresence initial={false}>
                        {isExpanded && (
                          <motion.div className="submenu" initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }} exit={{ height: 0, opacity: 0 }}>
                            {module.submodules.map(sub => (
                              <button key={sub.title} onClick={() => setSelected({ module, submodule: sub })}>{sub.title}</button>
                            ))}
                          </motion.div>
                        )}
                      </AnimatePresence>
                    </div>
                  );
                })}
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        <main className="main-stage">
          <section className="hero">
            <div className="hero-copy">
              <motion.div key={heroTitle} initial={{ y: 10, opacity: 0 }} animate={{ y: 0, opacity: 1 }} transition={{ duration: .25 }}>
                <span className="eyebrow">PEDAGOGICAL SIMULATOR · DESIGN SANDBOX</span>
                <h1>{heroTitle}</h1>
                <p>{selected?.submodule?.subtitle ?? 'Choose a phenomenon, manipulate it directly and read the physical consequence through synchronized visualizations.'}</p>
              </motion.div>
              <div className="hero-actions">
                <button className="primary-action"><Play size={17} fill="currentColor" /> Open experiment</button>
                <button className="secondary-action"><GitCompare size={17} /> Baseline × Current</button>
              </div>
            </div>
            <div className="hero-visual" aria-hidden="true">
              <div className="ocean-line" />
              <motion.div className="vessel-mark" animate={{ y: [0, -5, 0], rotate: [0, .5, 0] }} transition={{ duration: 5, repeat: Infinity, ease: 'easeInOut' }}><Ship size={72} strokeWidth={1.2} /></motion.div>
              <motion.div className="beam-cone" animate={{ opacity: [.5, .9, .5], scaleX: [.94, 1.02, .94] }} transition={{ duration: 3.2, repeat: Infinity, ease: 'easeInOut' }} />
              <div className="seafloor"><span /><span /><span /><span /><span /></div>
            </div>
          </section>

          <section className="content-head">
            <div><span className="eyebrow">SYSTEM MAP</span><h2>Explore by phenomenon</h2></div>
            <span className="mock-badge">Illustrative concept · mock values allowed</span>
          </section>

          <motion.section className="module-grid" layout>
            {modules.map(module => {
              const Icon = module.icon;
              return (
                <motion.article
                  layout
                  key={module.key}
                  className="module-card"
                  style={{ '--accent': module.accent, '--accent-rgb': module.accentRgb } as React.CSSProperties}
                  whileHover={{ y: -4 }}
                  transition={{ type: 'spring', stiffness: 350, damping: 28 }}
                >
                  <button className="card-title" onClick={() => { setExpanded(module.key); setSelected({ module }); }}>
                    <span className="module-icon large"><Icon size={25} strokeWidth={1.7} /></span>
                    <span><small>{module.index}</small><strong>{module.title}</strong></span>
                    <ChevronDown size={18} />
                  </button>
                  <div className="submodule-grid">
                    {module.submodules.map(sub => {
                      const SubIcon = sub.icon;
                      return (
                        <motion.button key={sub.title} className="submodule-card" whileTap={{ scale: .985 }} onClick={() => setSelected({ module, submodule: sub })}>
                          <SubIcon size={22} strokeWidth={1.65} />
                          <strong>{sub.title}</strong>
                          <small>{sub.subtitle}</small>
                        </motion.button>
                      );
                    })}
                  </div>
                </motion.article>
              );
            })}
          </motion.section>
        </main>
      </div>

      <AnimatePresence>
        {selected?.submodule && (
          <motion.div className="floating-inspector" initial={{ y: 18, opacity: 0, scale: .98 }} animate={{ y: 0, opacity: 1, scale: 1 }} exit={{ y: 12, opacity: 0, scale: .98 }}>
            <div className="inspector-icon">{(() => { const I = selected.submodule!.icon; return <I size={21} />; })()}</div>
            <div><small>{selected.module.title}</small><strong>{selected.submodule.title}</strong></div>
            <div className="inspector-spacer" />
            <button onClick={() => setSelected(null)}>Close</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
