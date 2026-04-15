import { useState, useEffect } from 'react';
import { Sparkles, Check, X, ArrowRight, Loader2 } from 'lucide-react';

export const LinkagePage = () => {
    const [sourceId, setSourceId] = useState('CLOUD-CONTROLS-MATRIX');
    const [targetId, setTargetId] = useState('NIST-SP-800-53-REV-5');
    const [isDiscovering, setIsDiscovering] = useState(false);

    const [drafts, setDrafts] = useState([]);
    const [loadingDrafts, setLoadingDrafts] = useState(true);

    const fetchDrafts = async () => {
        setLoadingDrafts(true);
        try {
            const res = await fetch('http://localhost:8000/api/approvals/');
            const data = await res.json();
            setDrafts(data);
        } catch (e) {
            console.error(e);
        } finally {
            setLoadingDrafts(false);
        }
    };

    useEffect(() => {
        fetchDrafts();
    }, []);

    const handleDiscover = async () => {
        if (!sourceId || !targetId) return;
        setIsDiscovering(true);
        try {
            await fetch('http://localhost:8000/api/discovery/map', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    source_framework_id: sourceId,
                    target_framework_id: targetId
                })
            });
            await fetchDrafts(); // Refresh list
        } catch (e) {
            alert("Discovery failed: " + e.message);
        } finally {
            setIsDiscovering(false);
        }
    };

    const handleAction = async (id, action) => {
        try {
            await fetch(`http://localhost:8000/api/approvals/${id}/${action}`, { method: 'POST' });
            // Optimistic update
            setDrafts(prev => prev.filter(d => d.id !== id));
        } catch (e) {
            alert(`Failed to ${action}: ${e.message}`);
        }
    };

    return (
        <div className="page-container">
            <div style={{ marginBottom: '32px' }}>
                <h1>Linkage Discovery & Approvals</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Map frameworks using AI and review the proposed relationships.</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 2fr', gap: '24px' }}>
                {/* Discovery Panel */}
                <div>
                    <div className="glass-panel" style={{ padding: '24px' }}>
                        <h3 style={{ marginTop: 0, display: 'flex', alignItems: 'center', gap: '8px' }}>
                            <Sparkles size={20} color="var(--primary)" /> AI Mapper
                        </h3>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', marginTop: '16px' }}>
                            <div>
                                <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Source Framework ID</label>
                                <input
                                    type="text"
                                    value={sourceId}
                                    onChange={e => setSourceId(e.target.value)}
                                    style={{ width: '100%', boxSizing: 'border-box' }}
                                />
                            </div>
                            <div>
                                <label style={{ display: 'block', marginBottom: '8px', fontSize: '0.9rem', color: 'var(--text-secondary)' }}>Target Framework ID</label>
                                <input
                                    type="text"
                                    value={targetId}
                                    onChange={e => setTargetId(e.target.value)}
                                    style={{ width: '100%', boxSizing: 'border-box' }}
                                />
                            </div>
                            <button
                                className="btn-primary"
                                onClick={handleDiscover}
                                disabled={isDiscovering}
                                style={{ display: 'flex', justifyContent: 'center', gap: '8px' }}
                            >
                                {isDiscovering ? <Loader2 className="spin" /> : 'Run Discovery'}
                            </button>
                        </div>
                    </div>
                </div>

                {/* Approvals List */}
                <div>
                    <h3 style={{ marginTop: 0 }}>Pending Approvals ({drafts.length})</h3>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginTop: '16px' }}>
                        {loadingDrafts ? (
                            <div style={{ color: 'var(--text-secondary)' }}>Loading...</div>
                        ) : drafts.length === 0 ? (
                            <div className="glass-panel" style={{ padding: '32px', textAlign: 'center', color: 'var(--text-secondary)' }}>
                                All caught up! No pending drafts.
                            </div>
                        ) : (
                            drafts.map(draft => (
                                <div key={draft.id} className="glass-panel" style={{ padding: '16px', display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
                                    <div style={{
                                        padding: '4px 8px', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600,
                                        background: draft.type === 'relationship' ? 'rgba(99, 102, 241, 0.2)' : 'rgba(16, 185, 129, 0.2)',
                                        color: draft.type === 'relationship' ? 'var(--primary)' : 'var(--success)'
                                    }}>
                                        {draft.type === 'relationship' ? 'LINK' : 'NODE'}
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                                            {draft.description || draft.properties?.name || draft.id}
                                        </div>
                                        {draft.properties?.rationale && (
                                            <div style={{ background: 'var(--bg-app)', padding: '8px', borderRadius: '4px', fontSize: '0.9rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                                                "{draft.properties.rationale}"
                                            </div>
                                        )}
                                        {draft.source && (
                                            <small style={{ color: 'var(--text-secondary)' }}>Source: {draft.source}</small>
                                        )}
                                    </div>
                                    <div style={{ display: 'flex', gap: '8px' }}>
                                        <button
                                            onClick={() => handleAction(draft.id, 'approve')}
                                            style={{ background: 'var(--success)', border: 'none', borderRadius: '4px', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'white' }}
                                        >
                                            <Check size={18} />
                                        </button>
                                        <button
                                            onClick={() => handleAction(draft.id, 'reject')}
                                            style={{ background: 'var(--bg-card)', border: '1px solid var(--glass-border)', borderRadius: '4px', width: '32px', height: '32px', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', color: 'var(--text-secondary)' }}
                                        >
                                            <X size={18} />
                                        </button>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
            <style>{`
                .spin { animation: spin 1s linear infinite; }
            `}</style>
        </div>
    );
};
