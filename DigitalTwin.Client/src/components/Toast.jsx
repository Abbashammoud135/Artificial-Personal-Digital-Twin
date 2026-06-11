import { useState, useEffect } from 'react';
import { CheckCircle, AlertTriangle, XCircle, Info, X } from 'lucide-react';

export function showToast(message, type = 'info', duration = 3000) {
  window.dispatchEvent(new CustomEvent('show-toast', {
    detail: { id: Math.random().toString(36).substring(2, 9), message, type, duration }
  }));
}

export default function ToastContainer() {
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    const handleToast = (e) => {
      const { id, message, type, duration } = e.detail;
      
      setToasts((prev) => [...prev, { id, message, type }]);

      setTimeout(() => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
      }, duration);
    };

    window.addEventListener('show-toast', handleToast);
    return () => window.removeEventListener('show-toast', handleToast);
  }, []);

  const removeToast = (id) => {
    setToasts((prev) => prev.filter((t) => t.id !== id));
  };

  const getIcon = (type) => {
    switch (type) {
      case 'success': return <CheckCircle size={18} color="var(--success)" />;
      case 'error': return <XCircle size={18} color="var(--danger)" />;
      case 'warning': return <AlertTriangle size={18} color="var(--warning)" />;
      default: return <Info size={18} color="var(--primary)" />;
    }
  };

  return (
    <div className="toast-container">
      {toasts.map((t) => (
        <div key={t.id} className={`toast ${t.type || 'info'}`}>
          {getIcon(t.type)}
          <div style={{ flexGrow: 1, wordBreak: 'break-word' }}>{t.message}</div>
          <button
            onClick={() => removeToast(t.id)}
            style={{
              background: 'transparent',
              border: 'none',
              cursor: 'pointer',
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              padding: '2px',
            }}
          >
            <X size={14} />
          </button>
        </div>
      ))}
    </div>
  );
}
export { ToastContainer };
