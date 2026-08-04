import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import LiveFeed from './screens/LiveFeed';
import Metrics from './screens/Metrics';
import TrainingTimeline from './screens/TrainingTimeline';
import ABPanel from './screens/ABPanel';
const qc = new QueryClient();
const SCREENS = ['Live Feed', 'Metrics', 'Training', 'A/B'];
export default function App() {
    const [screen, setScreen] = useState('Live Feed');
    return (_jsx(QueryClientProvider, { client: qc, children: _jsxs("div", { style: { fontFamily: 'system-ui', minHeight: '100vh', background: '#fafafa' }, children: [_jsxs("nav", { style: { background: '#1a1a2e', padding: '12px 24px', display: 'flex', gap: 24 }, children: [_jsx("span", { style: { color: '#fff', fontWeight: 700, marginRight: 24 }, children: "\uD83C\uDFAC Siphon" }), SCREENS.map(s => (_jsx("button", { onClick: () => setScreen(s), style: { background: 'none', border: 'none', color: screen === s ? '#fff' : '#aaa',
                                cursor: 'pointer', fontWeight: screen === s ? 700 : 400, fontSize: 14 }, children: s }, s)))] }), screen === 'Live Feed' && _jsx(LiveFeed, {}), screen === 'Metrics' && _jsx(Metrics, {}), screen === 'Training' && _jsx(TrainingTimeline, {}), screen === 'A/B' && _jsx(ABPanel, {})] }) }));
}
