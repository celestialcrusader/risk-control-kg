import { useState } from 'react';
import FileUploader from '../components/FileUploader';
import { ArrowRight, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';

export const IngestionPage = () => {
    const [file, setFile] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);

    const handleUpload = async () => {
        if (!file) return;

        setIsLoading(true);
        setError(null);
        setResult(null);

        const formData = new FormData();
        formData.append('file', file);
        formData.append('type', file.type || 'application/octet-stream'); // Fallback

        try {
            const response = await fetch('http://localhost:8000/api/ingest/', {
                method: 'POST',
                body: formData,
            });

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Upload failed');
            }

            const data = await response.json();
            setResult(data);
        } catch (err) {
            setError(err.message);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="page-container">
            <div style={{ maxWidth: '800px', margin: '0 auto' }}>
                <div style={{ marginBottom: '32px' }}>
                    <h1>Data Ingestion</h1>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem', marginTop: '8px' }}>
                        Upload your compliance documents to populate the Knowledge Graph.
                    </p>
                </div>

                <div className="glass-panel" style={{ padding: '32px' }}>
                    <FileUploader
                        selectedFile={file}
                        onFileSelect={setFile}
                        onClear={() => { setFile(null); setResult(null); setError(null); }}
                    />

                    {file && !result && !error && (
                        <div style={{ display: 'flex', justifyContent: 'flex-end', marginTop: '24px' }}>
                            <button className="btn-primary" onClick={handleUpload} disabled={isLoading} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                {isLoading ? (
                                    <>
                                        <Loader2 className="spin" size={20} /> Processing...
                                    </>
                                ) : (
                                    <>
                                        Analyze Document <ArrowRight size={20} />
                                    </>
                                )}
                            </button>
                        </div>
                    )}
                </div>

                {error && (
                    <div className="glass-panel" style={{ marginTop: '24px', padding: '20px', border: '1px solid var(--error)', background: 'rgba(239, 68, 68, 0.1)' }}>
                        <div style={{ display: 'flex', gap: '12px' }}>
                            <AlertCircle color="var(--error)" />
                            <div>
                                <h4 style={{ margin: '0 0 4px 0', color: 'var(--error)' }}>Ingestion Failed</h4>
                                <p style={{ margin: 0, color: 'var(--text-secondary)' }}>{error}</p>
                            </div>
                        </div>
                    </div>
                )}

                {result && (
                    <div className="glass-panel" style={{ marginTop: '24px', padding: '24px', border: '1px solid var(--success)', background: 'rgba(16, 185, 129, 0.05)' }}>
                        <div style={{ display: 'flex', gap: '16px' }}>
                            <CheckCircle color="var(--success)" size={28} style={{ flexShrink: 0 }} />
                            <div style={{ flex: 1 }}>
                                <h3 style={{ margin: '0 0 12px 0', color: 'var(--success)' }}>Ingestion Successful</h3>
                                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '16px' }}>
                                    <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                                        <small style={{ color: 'var(--text-secondary)' }}>Filename</small>
                                        <div style={{ fontWeight: 600 }}>{result.filename}</div>
                                    </div>
                                    <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                                        <small style={{ color: 'var(--text-secondary)' }}>Status</small>
                                        <div style={{ fontWeight: 600 }}>{result.status}</div>
                                    </div>
                                    <div style={{ background: 'var(--bg-card)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                                        <small style={{ color: 'var(--text-secondary)' }}>Controls Processed</small>
                                        <div style={{ fontWeight: 600, fontSize: '1.2rem', color: 'var(--primary)' }}>
                                            {result.controls_processed || 0}
                                        </div>
                                    </div>
                                </div>
                                <p style={{ marginTop: '16px', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                    Your data has been added to the graph. You can now verify it in the Graph Explorer or use the AI Chat.
                                </p>
                            </div>
                        </div>
                    </div>
                )}
            </div>
            <style>{`
                .spin { animation: spin 1s linear infinite; }
                @keyframes spin { 100% { transform: rotate(360deg); } }
            `}</style>
        </div>
    );
};
