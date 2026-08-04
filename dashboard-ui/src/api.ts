const BASE = '/api'

export interface Snapshot { ctr: number; avg_watch_frac: number; events_per_sec: number; model_version: number }
export interface TrainingRun { version: number; started_at: number; finished_at: number | null; auc: number | null; loss: number[] }
export interface ABStats { version: number; ctr: number; avg_watch_frac: number }
export interface LiveEvent { user_id: string; video_id: string; watch_frac: number; event_type: string; ts_ms: number }

export async function fetchSnapshot(): Promise<Snapshot> {
  return (await fetch(`${BASE}/metrics/snapshot`)).json()
}
export async function fetchTrainingHistory(): Promise<TrainingRun[]> {
  return (await fetch(`${BASE}/training/history`)).json()
}
export async function fetchABCompare(a: number, b: number): Promise<{ model_a: ABStats; model_b: ABStats }> {
  return (await fetch(`${BASE}/ab/compare?model_a=${a}&model_b=${b}`)).json()
}
