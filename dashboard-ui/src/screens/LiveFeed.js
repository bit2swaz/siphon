import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useEffect, useRef, useState } from 'react';
export default function LiveFeed() {
    const [events, setEvents] = useState([]);
    const wsRef = useRef(null);
    useEffect(() => {
        const ws = new WebSocket(`ws://${window.location.hostname}:8006/ws/live`);
        wsRef.current = ws;
        ws.onmessage = (msg) => {
            const batch = JSON.parse(msg.data);
            setEvents(prev => [...batch, ...prev].slice(0, 100));
        };
        return () => ws.close();
    }, []);
    return (_jsxs("div", { style: { padding: 24 }, children: [_jsx("h2", { children: "Live Bot Feed" }), _jsxs("table", { style: { width: '100%', borderCollapse: 'collapse', fontSize: 13 }, children: [_jsx("thead", { children: _jsx("tr", { children: ['User', 'Video', 'Type', 'Watch%', 'Time'].map(h => _jsx("th", { style: { textAlign: 'left', borderBottom: '1px solid #ccc', padding: '4px 8px' }, children: h }, h)) }) }), _jsx("tbody", { children: events.map((e, i) => (_jsxs("tr", { style: { background: i % 2 ? '#f9f9f9' : 'white' }, children: [_jsx("td", { style: { padding: '4px 8px' }, children: e.user_id }), _jsx("td", { style: { padding: '4px 8px' }, children: e.video_id }), _jsx("td", { style: { padding: '4px 8px' }, children: e.event_type }), _jsxs("td", { style: { padding: '4px 8px' }, children: [(e.watch_frac * 100).toFixed(0), "%"] }), _jsx("td", { style: { padding: '4px 8px' }, children: new Date(e.ts_ms).toLocaleTimeString() })] }, i))) })] })] }));
}
