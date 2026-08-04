// context7: Recharts LineChart, TanStack Query useQuery
import { useQuery } from '@tanstack/react-query'
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts'
import { fetchSnapshot, type Snapshot } from '../api'
import { useState, useEffect } from 'react'

export default function Metrics() {
  const [history, setHistory] = useState<Array<Snapshot & { t: number }>>([])
  const { data } = useQuery({ queryKey: ['snapshot'], queryFn: fetchSnapshot, refetchInterval: 2000 })

  useEffect(() => {
    if (data) setHistory(h => [...h.slice(-60), { ...data, t: Date.now() }])
  }, [data])

  return (
    <div style={{ padding: 24 }}>
      <h2>Live Metrics</h2>
      {data && (
        <p>CTR: <b>{(data.ctr * 100).toFixed(1)}%</b> | Avg Watch: <b>{(data.avg_watch_frac * 100).toFixed(1)}%</b> | Events/s: <b>{data.events_per_sec.toFixed(1)}</b> | Model v{data.model_version}</p>
      )}
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={history}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="t" tickFormatter={v => new Date(v).toLocaleTimeString()} />
          <YAxis domain={[0, 1]} />
          <Tooltip />
          <Line type="monotone" dataKey="ctr"            stroke="#8884d8" name="CTR" dot={false} />
          <Line type="monotone" dataKey="avg_watch_frac" stroke="#82ca9d" name="Avg Watch" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
