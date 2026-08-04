import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
// context7: Recharts LineChart, TanStack Query useQuery
import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, Tooltip, CartesianGrid, ResponsiveContainer } from 'recharts';
import { fetchSnapshot } from '../api';
import { useState, useEffect } from 'react';
export default function Metrics() {
    const [history, setHistory] = useState([]);
    const { data } = useQuery({ queryKey: ['snapshot'], queryFn: fetchSnapshot, refetchInterval: 2000 });
    useEffect(() => {
        if (data)
            setHistory(h => [...h.slice(-60), { ...data, t: Date.now() }]);
    }, [data]);
    return (_jsxs("div", { style: { padding: 24 }, children: [_jsx("h2", { children: "Live Metrics" }), data && (_jsxs("p", { children: ["CTR: ", _jsxs("b", { children: [(data.ctr * 100).toFixed(1), "%"] }), " | Avg Watch: ", _jsxs("b", { children: [(data.avg_watch_frac * 100).toFixed(1), "%"] }), " | Events/s: ", _jsx("b", { children: data.events_per_sec.toFixed(1) }), " | Model v", data.model_version] })), _jsx(ResponsiveContainer, { width: "100%", height: 300, children: _jsxs(LineChart, { data: history, children: [_jsx(CartesianGrid, { strokeDasharray: "3 3" }), _jsx(XAxis, { dataKey: "t", tickFormatter: v => new Date(v).toLocaleTimeString() }), _jsx(YAxis, { domain: [0, 1] }), _jsx(Tooltip, {}), _jsx(Line, { type: "monotone", dataKey: "ctr", stroke: "#8884d8", name: "CTR", dot: false }), _jsx(Line, { type: "monotone", dataKey: "avg_watch_frac", stroke: "#82ca9d", name: "Avg Watch", dot: false })] }) })] }));
}
