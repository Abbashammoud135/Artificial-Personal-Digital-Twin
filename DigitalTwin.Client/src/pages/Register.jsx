import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Layers } from 'lucide-react';
import { api } from '../api';
import { showToast } from '../components/Toast';

export default function Register() {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!fullName || !email || !password) {
      showToast('Please fill in all fields', 'warning');
      return;
    }

    setLoading(true);
    try {
      await api.auth.register(fullName, email, password);
      showToast('Registration successful! Please log in.', 'success');
      navigate('/login');
    } catch (err) {
      showToast(err.message || 'Registration failed. Try again.', 'error');
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
            background: 'rgba(123, 97, 255, 0.08)',
            border: '1px solid rgba(123, 97, 255, 0.2)',
            marginBottom: '16px',
            animation: 'float 4s infinite ease-in-out'
          }}>
            <Layers color="var(--secondary)" size={32} style={{ filter: 'drop-shadow(0 0 8px var(--secondary))' }} />
          </div>
          <h1 style={{ fontSize: '28px', marginBottom: '4px', textAlign: 'center' }}>Initialize Twin</h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '14px', textAlign: 'center' }}>
            Set up credentials for your AI double
          </p>
        </div>

        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          <div>
            <label htmlFor="fullname">Full Identity Name</label>
            <input
              id="fullname"
              type="text"
              placeholder="e.g. John Doe"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>

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
            <label htmlFor="password">Secret Passphrase</label>
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
            {loading ? 'Initializing DNA...' : 'Instantiate Twin'}
          </button>
        </form>

        <div style={{ marginTop: '24px', textAlign: 'center', fontSize: '13px', color: 'var(--text-muted)' }}>
          Already registered?{' '}
          <Link to="/login" style={{ fontWeight: 600 }}>Sign In</Link>
        </div>
      </div>
    </div>
  );
}
