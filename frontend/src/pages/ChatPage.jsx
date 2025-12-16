import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Send, Bot, User, Loader2 } from 'lucide-react';

export const ChatPage = () => {
    const [messages, setMessages] = useState([
        { role: 'assistant', content: 'Hello! I am your AI Risk Audit assistant. Ask me about your compliance posture, specific controls, or audit steps.' }
    ]);
    const [input, setInput] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const endRef = useRef(null);

    const scrollToBottom = () => {
        endRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    const handleSend = async () => {
        if (!input.trim() || isLoading) return;

        const userMsg = { role: 'user', content: input };
        setMessages(prev => [...prev, userMsg]);
        setInput('');
        setIsLoading(true);

        try {
            const res = await fetch('http://localhost:8000/api/chat/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: userMsg.content })
            });
            const data = await res.json();

            const aiMsg = {
                role: 'assistant',
                content: data.response || "Sorry, I couldn't generate a response.",
                sources: data.sources
            };
            setMessages(prev => [...prev, aiMsg]);
        } catch (e) {
            setMessages(prev => [...prev, { role: 'assistant', content: `Error: ${e.message}` }]);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="page-container" style={{ height: 'calc(100vh - 40px)', display: 'flex', flexDirection: 'column', maxWidth: '1000px', margin: '0 auto' }}>
            <div style={{ marginBottom: '20px' }}>
                <h1>AI Risk Chat</h1>
                <p style={{ color: 'var(--text-secondary)' }}>Context-aware answers from your Knowledge Graph.</p>
            </div>

            {/* Chat Area */}
            <div className="glass-panel" style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
                <div style={{ flex: 1, overflowY: 'auto', padding: '24px', display: 'flex', flexDirection: 'column', gap: '24px' }}>
                    {messages.map((msg, idx) => (
                        <div key={idx} style={{ display: 'flex', gap: '16px', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row' }}>
                            <div style={{
                                width: '36px', height: '36px', borderRadius: '50%',
                                background: msg.role === 'user' ? 'var(--primary)' : 'var(--bg-card)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                border: '1px solid var(--glass-border)'
                            }}>
                                {msg.role === 'user' ? <User size={20} color="white" /> : <Bot size={20} color="var(--primary)" />}
                            </div>

                            <div style={{ maxWidth: '80%', display: 'flex', flexDirection: 'column', alignItems: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
                                <div style={{
                                    background: msg.role === 'user' ? 'rgba(99, 102, 241, 0.2)' : 'var(--bg-card)',
                                    border: `1px solid ${msg.role === 'user' ? 'var(--primary)' : 'var(--glass-border)'}`,
                                    borderRadius: 'var(--radius-md)',
                                    padding: '16px',
                                    color: 'var(--text-primary)',
                                    lineHeight: '1.6'
                                }}>
                                    <ReactMarkdown
                                        components={{
                                            code: ({ node, inline, className, children, ...props }) => (
                                                <code style={{ background: 'rgba(0,0,0,0.3)', padding: '2px 4px', borderRadius: '4px' }} {...props}>{children}</code>
                                            )
                                        }}
                                    >
                                        {msg.content}
                                    </ReactMarkdown>
                                </div>
                                {msg.sources && msg.sources.length > 0 && (
                                    <div style={{ marginTop: '8px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                        Sources: {msg.sources.join(', ')}
                                    </div>
                                )}
                            </div>
                        </div>
                    ))}
                    {isLoading && (
                        <div style={{ display: 'flex', gap: '16px' }}>
                            <div style={{
                                width: '36px', height: '36px', borderRadius: '50%',
                                background: 'var(--bg-card)',
                                display: 'flex', alignItems: 'center', justifyContent: 'center'
                            }}>
                                <Bot size={20} color="var(--primary)" />
                            </div>
                            <div style={{ padding: '16px', color: 'var(--text-secondary)' }}>
                                <Loader2 className="spin" size={20} /> Thinking...
                            </div>
                        </div>
                    )}
                    <div ref={endRef} />
                </div>

                {/* Input Area */}
                <div style={{ padding: '20px', borderTop: '1px solid var(--glass-border)', background: 'var(--bg-panel)' }}>
                    <div style={{ display: 'flex', gap: '12px' }}>
                        <input
                            type="text"
                            value={input}
                            onChange={(e) => setInput(e.target.value)}
                            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                            placeholder="Ask about Generative AI risks..."
                            style={{ flex: 1, padding: '12px 16px', fontSize: '1rem', background: 'var(--bg-app)', border: '1px solid var(--glass-border)' }}
                        />
                        <button className="btn-primary" onClick={handleSend} disabled={isLoading} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '0 24px' }}>
                            <Send size={20} />
                        </button>
                    </div>
                </div>
            </div>
            <style>{`
                .spin { animation: spin 1s linear infinite; }
            `}</style>
        </div>
    );
};
