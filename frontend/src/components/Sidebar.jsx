import { LayoutDashboard, Network, FileInput, MessageSquareText, Shield, Sparkles } from 'lucide-react';
import { NavLink } from 'react-router-dom';

const Sidebar = () => {
    const navItems = [
        { to: '/', label: 'Ingestion', icon: FileInput },
        { to: '/graph', label: 'Graph Explorer', icon: Network },
        { to: '/linkage', label: 'Linkage Discovery', icon: Sparkles },
        { to: '/chat', label: 'AI Risk Chat', icon: MessageSquareText },
    ];

    return (
        <aside style={{
            width: '260px',
            height: '100vh',
            background: 'var(--bg-panel)',
            borderRight: '1px solid var(--glass-border)',
            display: 'flex',
            flexDirection: 'column',
            padding: '20px'
        }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '40px', paddingLeft: '10px' }}>
                <Shield size={32} color="var(--primary)" />
                <h2 style={{ margin: 0, fontSize: '1.25rem' }}>RCKG <span style={{ color: 'var(--primary)' }}>Audit</span></h2>
            </div>

            <nav style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {navItems.map((item) => (
                    <NavLink
                        key={item.to}
                        to={item.to}
                        style={({ isActive }) => ({
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            padding: '12px 16px',
                            borderRadius: 'var(--radius-sm)',
                            textDecoration: 'none',
                            color: isActive ? 'white' : 'var(--text-secondary)',
                            background: isActive ? 'var(--primary)' : 'transparent',
                            fontWeight: isActive ? 600 : 500,
                            transition: 'all 0.2s ease'
                        })}
                    >
                        <item.icon size={20} />
                        {item.label}
                    </NavLink>
                ))}
            </nav>

            <div style={{ marginTop: 'auto', padding: '16px', background: 'var(--bg-card)', borderRadius: 'var(--radius-sm)' }}>
                <small style={{ color: 'var(--text-secondary)' }}>System Status</small>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginTop: '8px' }}>
                    <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)' }} />
                    <span style={{ fontSize: '0.85rem' }}>Backend Online</span>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
