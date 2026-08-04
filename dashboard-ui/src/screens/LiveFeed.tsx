import { useEffect, useRef, useState } from 'react'
import type { LiveEvent } from '../api'

export default function LiveFeed() {
  const [events, setEvents] = useState<LiveEvent[]>([])
  const wsRef = useRef<WebSocket | null>(null)

  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.hostname}:8006/ws/live`)
    wsRef.current = ws
    ws.onmessage = (msg) => {
      const batch: LiveEvent[] = JSON.parse(msg.data)
      setEvents(prev => [...batch, ...prev].slice(0, 100))
    }
    return () => ws.close()
  }, [])

  return (
    <div style={{ padding: 24 }}>
      <h2>Live Bot Feed</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr>{['User','Video','Type','Watch%','Time'].map(h => <th key={h} style={{textAlign:'left',borderBottom:'1px solid #ccc',padding:'4px 8px'}}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {events.map((e, i) => (
            <tr key={i} style={{ background: i % 2 ? '#f9f9f9' : 'white' }}>
              <td style={{padding:'4px 8px'}}>{e.user_id}</td>
              <td style={{padding:'4px 8px'}}>{e.video_id}</td>
              <td style={{padding:'4px 8px'}}>{e.event_type}</td>
              <td style={{padding:'4px 8px'}}>{(e.watch_frac * 100).toFixed(0)}%</td>
              <td style={{padding:'4px 8px'}}>{new Date(e.ts_ms).toLocaleTimeString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
