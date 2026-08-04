import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { fetchABCompare } from '../api'

export default function ABPanel() {
  const [modelA, setModelA] = useState(1)
  const [modelB, setModelB] = useState(2)
  const { data } = useQuery({
    queryKey: ['ab', modelA, modelB],
    queryFn: () => fetchABCompare(modelA, modelB),
    enabled: modelA > 0 && modelB > 0,
  })

  return (
    <div style={{ padding: 24 }}>
      <h2>A/B Compare</h2>
      <div style={{ display: 'flex', gap: 16, marginBottom: 16 }}>
        <label>Model A: <input type="number" value={modelA} min={1} onChange={e => setModelA(+e.target.value)} style={{width:60}} /></label>
        <label>Model B: <input type="number" value={modelB} min={1} onChange={e => setModelB(+e.target.value)} style={{width:60}} /></label>
      </div>
      {data && (
        <table style={{ borderCollapse: 'collapse', fontSize: 14 }}>
          <thead>
            <tr>{['Metric','Model A','Model B'].map(h => <th key={h} style={{padding:'8px 16px',borderBottom:'1px solid #ccc'}}>{h}</th>)}</tr>
          </thead>
          <tbody>
            <tr>
              <td style={{padding:'8px 16px'}}>Version</td>
              <td style={{padding:'8px 16px'}}>v{data.model_a.version}</td>
              <td style={{padding:'8px 16px'}}>v{data.model_b.version}</td>
            </tr>
            <tr>
              <td style={{padding:'8px 16px'}}>CTR</td>
              <td style={{padding:'8px 16px'}}>{(data.model_a.ctr*100).toFixed(1)}%</td>
              <td style={{padding:'8px 16px'}}>{(data.model_b.ctr*100).toFixed(1)}%</td>
            </tr>
            <tr>
              <td style={{padding:'8px 16px'}}>Avg Watch</td>
              <td style={{padding:'8px 16px'}}>{(data.model_a.avg_watch_frac*100).toFixed(1)}%</td>
              <td style={{padding:'8px 16px'}}>{(data.model_b.avg_watch_frac*100).toFixed(1)}%</td>
            </tr>
          </tbody>
        </table>
      )}
    </div>
  )
}
