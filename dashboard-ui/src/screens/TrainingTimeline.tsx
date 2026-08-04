import { useQuery } from '@tanstack/react-query'
import { fetchTrainingHistory, type TrainingRun } from '../api'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import { useState } from 'react'

export default function TrainingTimeline() {
  const { data = [] } = useQuery({ queryKey: ['training'], queryFn: fetchTrainingHistory, refetchInterval: 10000 })
  const [selected, setSelected] = useState<TrainingRun | null>(null)

  return (
    <div style={{ padding: 24 }}>
      <h2>Training Timeline</h2>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
        <thead>
          <tr>{['Version','AUC','Started','Status'].map(h => <th key={h} style={{textAlign:'left',borderBottom:'1px solid #ccc',padding:'4px 8px'}}>{h}</th>)}</tr>
        </thead>
        <tbody>
          {data.map(run => (
            <tr key={run.version} onClick={() => setSelected(run)} style={{ cursor:'pointer', background: selected?.version === run.version ? '#eef' : 'white' }}>
              <td style={{padding:'4px 8px'}}>v{run.version}</td>
              <td style={{padding:'4px 8px'}}>{run.auc != null ? run.auc.toFixed(3) : '—'}</td>
              <td style={{padding:'4px 8px'}}>{new Date(run.started_at).toLocaleTimeString()}</td>
              <td style={{padding:'4px 8px'}}>{run.finished_at ? '✓' : '⏳'}</td>
            </tr>
          ))}
        </tbody>
      </table>
      {selected?.loss && selected.loss.length > 0 && (
        <>
          <h3>v{selected.version} Loss Curve</h3>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={selected.loss.map((l, i) => ({ epoch: i + 1, loss: l }))}>
              <XAxis dataKey="epoch" />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey="loss" stroke="#ff7300" dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </>
      )}
    </div>
  )
}
