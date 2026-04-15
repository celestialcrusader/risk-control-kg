import { UploadCloud, File as FileIcon, X } from 'lucide-react';
import { useState, useRef } from 'react';

const FileUploader = ({ onFileSelect, selectedFile, onClear }) => {
    const [isDragging, setIsDragging] = useState(false);
    const fileInputRef = useRef(null);

    const handleDragOver = (e) => {
        e.preventDefault();
        setIsDragging(true);
    };

    const handleDragLeave = () => {
        setIsDragging(false);
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setIsDragging(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            onFileSelect(e.dataTransfer.files[0]);
        }
    };

    const handleClick = () => {
        fileInputRef.current.click();
    };

    const handleChange = (e) => {
        if (e.target.files && e.target.files[0]) {
            onFileSelect(e.target.files[0]);
        }
    };

    if (selectedFile) {
        return (
            <div className="glass-panel" style={{ padding: '20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: '20px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <div style={{ background: 'var(--bg-card)', padding: '10px', borderRadius: 'var(--radius-sm)' }}>
                        <FileIcon size={24} color="var(--primary)" />
                    </div>
                    <div>
                        <div style={{ fontWeight: 600 }}>{selectedFile.name}</div>
                        <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                            {(selectedFile.size / 1024).toFixed(1)} KB
                        </div>
                    </div>
                </div>
                <button
                    onClick={onClear}
                    style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--text-secondary)' }}
                >
                    <X size={20} />
                </button>
            </div>
        );
    }

    return (
        <div
            onClick={handleClick}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            style={{
                border: `2px dashed ${isDragging ? 'var(--primary)' : 'var(--glass-border)'}`,
                borderRadius: 'var(--radius-md)',
                padding: '40px',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.2s ease',
                background: isDragging ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
                marginTop: '20px'
            }}
        >
            <input
                type="file"
                ref={fileInputRef}
                onChange={handleChange}
                style={{ display: 'none' }}
                accept=".pdf,.json,.csv,.xlsx"
            />
            <div style={{
                background: 'var(--bg-card)',
                width: '60px',
                height: '60px',
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                margin: '0 auto 16px'
            }}>
                <UploadCloud size={32} color={isDragging ? 'var(--primary)' : 'var(--text-secondary)'} />
            </div>
            <h3 style={{ marginBottom: '8px' }}>Click or drag file to this area to upload</h3>
            <p style={{ color: 'var(--text-secondary)', margin: 0 }}>
                Support for PDF, OSCAL JSON, CSV, and Excel
            </p>
        </div>
    );
};

export default FileUploader;
