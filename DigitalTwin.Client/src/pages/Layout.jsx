import { useEffect, useState } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import Sidebar from '../components/Sidebar';
import NeuralNetwork from '../components/NeuralNetwork';
import ToastContainer, { showToast } from '../components/Toast';

export default function Layout() {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    // Check if token exists, redirect if not
    const token = localStorage.getItem('dt_token');
    const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

    if (!token && !isAuthPage) {
      navigate('/login');
    } else if (token && isAuthPage) {
      navigate('/');
    }

    // Subscribe to global loading indicator
    const handleLoading = (e) => {
      setLoading(e.detail);
    };

    // Subscribe to auth errors (auto-logout)
    const handleAuthError = () => {
      navigate('/login');
    };

    window.addEventListener('api-loading', handleLoading);
    window.addEventListener('api-auth-error', handleAuthError);

    return () => {
      window.removeEventListener('api-loading', handleLoading);
      window.removeEventListener('api-auth-error', handleAuthError);
    };
  }, [navigate, location.pathname]);

  useEffect(() => {
    // Check for Google OAuth callback parameters
    const searchParams = new URLSearchParams(location.search);
    const googleAuthStatus = searchParams.get('google_auth');
    if (googleAuthStatus) {
      if (googleAuthStatus === 'success') {
        showToast('Google account linked successfully!', 'success');
        window.dispatchEvent(new CustomEvent('google-auth-change'));
      } else if (googleAuthStatus === 'error') {
        const detail = searchParams.get('detail') || 'OAuth flow failed';
        showToast(`Google link failed: ${detail}`, 'error');
      }

      // Clean query parameters from URL
      searchParams.delete('google_auth');
      searchParams.delete('detail');
      const newQuery = searchParams.toString();
      const cleanPath = location.pathname + (newQuery ? `?${newQuery}` : '');
      navigate(cleanPath, { replace: true });
    }
  }, [location, navigate]);

  const token = localStorage.getItem('dt_token');
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register';

  if (!token && !isAuthPage) {
    return null; // Don't flash layout if unauthenticated
  }

  return (
    <>
      {/* Dynamic Background */}
      <NeuralNetwork />

      {/* Global Loading Top Bar */}
      {loading && <div className="global-loading-bar" />}

      {/* Global Toaster Alerts */}
      <ToastContainer />

      {isAuthPage ? (
        <Outlet />
      ) : (
        <div className="app-container">
          <Sidebar />
          <main className="main-content">
            <Outlet />
          </main>
        </div>
      )}
    </>
  );
}
