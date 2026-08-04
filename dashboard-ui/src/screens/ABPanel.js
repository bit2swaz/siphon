import { jsx as _jsx, jsxs as _jsxs } from "react/jsx-runtime";
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { fetchABCompare } from '../api';
export default function ABPanel() {
    const [modelA, setModelA] = useState(1);
    const [modelB, setModelB] = useState(2);
    const { data } = useQuery({
        queryKey: ['ab', modelA, modelB],
        queryFn: () => fetchABCompare(modelA, modelB),
        enabled: modelA > 0 && modelB > 0,
    });
    return (_jsxs("div", { style: { padding: 24 }, children: [_jsx("h2", { children: "A/B Compare" }), _jsxs("div", { style: { display: 'flex', gap: 16, marginBottom: 16 }, children: [_jsxs("label", { children: ["Model A: ", _jsx("input", { type: "number", value: modelA, min: 1, onChange: e => setModelA(+e.target.value), style: { width: 60 } })] }), _jsxs("label", { children: ["Model B: ", _jsx("input", { type: "number", value: modelB, min: 1, onChange: e => setModelB(+e.target.value), style: { width: 60 } })] })] }), data && (_jsxs("table", { style: { borderCollapse: 'collapse', fontSize: 14 }, children: [_jsx("thead", { children: _jsx("tr", { children: ['Metric', 'Model A', 'Model B'].map(h => _jsx("th", { style: { padding: '8px 16px', borderBottom: '1px solid #ccc' }, children: h }, h)) }) }), _jsxs("tbody", { children: [_jsxs("tr", { children: [_jsx("td", { style: { padding: '8px 16px' }, children: "Version" }), _jsxs("td", { style: { padding: '8px 16px' }, children: ["v", data.model_a.version] }), _jsxs("td", { style: { padding: '8px 16px' }, children: ["v", data.model_b.version] })] }), _jsxs("tr", { children: [_jsx("td", { style: { padding: '8px 16px' }, children: "CTR" }), _jsxs("td", { style: { padding: '8px 16px' }, children: [(data.model_a.ctr * 100).toFixed(1), "%"] }), _jsxs("td", { style: { padding: '8px 16px' }, children: [(data.model_b.ctr * 100).toFixed(1), "%"] })] }), _jsxs("tr", { children: [_jsx("td", { style: { padding: '8px 16px' }, children: "Avg Watch" }), _jsxs("td", { style: { padding: '8px 16px' }, children: [(data.model_a.avg_watch_frac * 100).toFixed(1), "%"] }), _jsxs("td", { style: { padding: '8px 16px' }, children: [(data.model_b.avg_watch_frac * 100).toFixed(1), "%"] })] })] })] }))] }));
}
