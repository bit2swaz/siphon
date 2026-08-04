const BASE = '/api';
export async function fetchSnapshot() {
    return (await fetch(`${BASE}/metrics/snapshot`)).json();
}
export async function fetchTrainingHistory() {
    return (await fetch(`${BASE}/training/history`)).json();
}
export async function fetchABCompare(a, b) {
    return (await fetch(`${BASE}/ab/compare?model_a=${a}&model_b=${b}`)).json();
}
