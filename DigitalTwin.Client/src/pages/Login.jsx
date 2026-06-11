import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers } from 'lucide-react';
import { api } from '../api';
import { showToast } from '../components/Toast';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      showToast('Please fill in all fields', 'warning');
      return;
    }

    setLoading(true);
    try {
      await api.auth.login(email, password);
      showToast('Welcome back to your Digital Twin!', 'success');
      navigate('/');
    } catch (err) {
      showToast(err.message || 'Login failed. Please check credentials.', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      padding: '24px',
      position: 'relative',
      zIndex: 2,
    }}>
      <div className="glass-card" style={{ width: '100%', maxWidth: '420px', padding: '36px' }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', marginBottom: '32px' }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            width: '60px',
            height: '60px',
            borderRadius: '16px',
            background: 'rgba(0, 212, 255, 0.08)',
            border: '1px solid rgba(0, 212, 255, 0.2)',
            marginBottom: '16px',
            animation: 'float 4s infinite ease-in-out'
          }}>
            <Layers color="var(--primary)" size={32} style={{ filter: 'drop-shadow(0 0 8px var(--primary))' }} />
          </div>
          <h1 style={{ fontSize: '28px', marginBottom: '4px', textAlign: 'center' }}>Welcome Back</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', textAlign: 'center' }}>
            Syncing your Digital Twin interface
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label htmlFor="email">Secure Email</label>
            <input
              id="email"
              type="email"
              placeholder="e.g. user@domain.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div>
            <label htmlFor="password">Access Key</label>
            <input
              id="password"
              type="password"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading}
            style={{ width: '100%', marginTop: '8px' }}
          >
            {loading ? 'Decrypting Access...' : 'Connect to Twin'}
          </button>
        </form>

        <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '13px', color: 'var(--text-muted)' }}>
          Don't have a Digital Twin yet?{' '}
          <Link to="/register" style={{ fontWeight: 600 }}>Create Profile</Link>
        </div>
      </div>
    </div>
  );
}
