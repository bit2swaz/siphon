import { useState } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import LiveFeed from './screens/LiveFeed'
import Metrics from './screens/Metrics'
import TrainingTimeline from './screens/TrainingTimeline'
import ABPanel from './screens/ABPanel'

const qc = new QueryClient()
const SCREENS = ['Live Feed', 'Metrics', 'Training', 'A/B'] as const

export default function App() {
  const [screen, setScreen] = useState<(typeof SCREENS)[number]>('Live Feed')
  return (
    <QueryClientProvider client={qc}>
      <div style={{ fontFamily: 'system-ui', minHeight: '100vh', background: '#fafafa' }}>
        <nav style={{ background: '#1a1a2e', padding: '12px 24px', display: 'flex', gap: 24 }}>
          <span style={{ color: '#fff', fontWeight: 700, marginRight: 24 }}>🎬 Siphon</span>
          {SCREENS.map(s => (
            <button key={s} onClick={() => setScreen(s)}
              style={{ background: 'none', border: 'none', color: screen === s ? '#fff' : '#aaa',
                       cursor: 'pointer', fontWeight: screen === s ? 700 : 400, fontSize: 14 }}>
              {s}
            </button>
          ))}
        </nav>
        {screen === 'Live Feed'  && <LiveFeed />}
        {screen === 'Metrics'    && <Metrics />}
        {screen === 'Training'   && <TrainingTimeline />}
        {screen === 'A/B'        && <ABPanel />}
      </div>
    </QueryClientProvider>
  )
}
