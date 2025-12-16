import { useState, useEffect } from 'react';
import GraphVisualizer from '../components/GraphVisualizer';
import { RefreshCw, Filter } from 'lucide-react';

export const GraphPage = () => {
    const [graphData, setGraphData] = useState(null);
    const [loading, setLoading] = useState(true);

    const fetchGraph = async () => {
        setLoading(true);
        try {
            const res = await fetch('http://localhost:8000/api/graph/?limit=200'); // Limit for performance
            const data = await res.json();
            // Cytoscape expects flat array of elements or {nodes, edges}
            // API returns { nodes: [...], edges: [...] } which works for cy.json() if formatted right
            // Actually cytoscape constructor takes `elements: { nodes: [], edges: [] }` OR `elements: []`.
            // Our API returns object with nodes/edges keys.
            setGraphData(data);
        } catch (e) {
            console.error("Graph fetch failed", e);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchGraph();
    }, []);

    return (
        <div className="page-container" style={{ height: 'calc(100vh - 40px)', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <div>
                    <h1>Graph Explorer</h1>
                    <p style={{ color: 'var(--text-secondary)' }}>Visualize ecosystem relationships.</p>
                </div>
                <div style={{ display: 'flex', gap: '12px' }}>
                    <button className="glass-panel" style={{ padding: '8px 12px', display: 'flex', gap: '8px', color: 'var(--text-primary)', cursor: 'pointer' }}>
                        <Filter size={18} /> Filter
                    </button>
                    <button className="btn-primary" onClick={fetchGraph} style={{ display: 'flex', gap: '8px', padding: '8px 12px' }}>
                        <RefreshCw size={18} className={loading ? 'spin' : ''} /> Refresh
                    </button>
                </div>
            </div>

            {/* Viz Container */}
            <div style={{ flex: 1, minHeight: 0 }}>
                {graphData ? (
                    <GraphVisualizer elements={graphData} />
                ) : (
                    <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)' }}>
                        {loading ? 'Loading Graph...' : 'No Data'}
                    </div>
                )}
            </div>

            <style>{`
                .spin { animation: spin 1s linear infinite; }
            `}</style>
        </div>
    );
};
