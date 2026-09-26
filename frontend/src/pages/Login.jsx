import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  Sparkles,
  Lock,
  User,
  Mail,
  ShieldCheck,
  AlertCircle,
  CheckCircle2,
  ArrowRight
} from 'lucide-react';

export default function Login() {
  const { user, login, register } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const [authMode, setAuthMode] = useState('login'); // 'login' | 'register'
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);

  const from = location.state?.from?.pathname || '/';

  useEffect(() => {
    if (user) {
      navigate(from, { replace: true });
    }
  }, [user, navigate, from]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage(null);
    setSubmitting(true);

    let res;
    if (authMode === 'register') {
      res = await register(username, email, password);
    } else {
      res = await login(username, password);
    }

    setSubmitting(false);

    if (res.success) {
      navigate(from, { replace: true });
    } else {
      setErrorMessage(res.error || 'Authentication failed.');
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        backgroundColor: 'var(--bg-main, #0b0f19)',
        color: 'var(--text-main, #f8fafc)',
        padding: '1.5rem',
      }}
    >
      <div className="card" style={{ width: '100%', maxWidth: '440px', padding: '2rem' }}>
        {/* Header / Brand Logo */}
        <div style={{ textAlign: 'center', marginBottom: '1.75rem' }}>
          <div
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              width: '48px',
              height: '48px',
              borderRadius: '12px',
              backgroundColor: 'rgba(59, 130, 246, 0.15)',
              color: '#3b82f6',
              marginBottom: '0.75rem',
            }}
          >
            <Sparkles size={26} />
          </div>
          <h2 style={{ fontSize: '1.5rem', fontWeight: 700, margin: '0 0 0.35rem 0', color: '#f8fafc' }}>
            FinSight 2.0
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', margin: 0 }}>
            SmartFinancial Advisor Intelligence Platform
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="tabs" style={{ marginBottom: '1.5rem', display: 'grid', gridTemplateColumns: '1fr 1fr' }}>
          <button
            type="button"
            className={`tab-btn ${authMode === 'login' ? 'active' : ''}`}
            onClick={() => {
              setAuthMode('login');
              setErrorMessage(null);
            }}
            style={{ textAlign: 'center', justifyContent: 'center' }}
          >
            Log In
          </button>
          <button
            type="button"
            className={`tab-btn ${authMode === 'register' ? 'active' : ''}`}
            onClick={() => {
              setAuthMode('register');
              setErrorMessage(null);
            }}
            style={{ textAlign: 'center', justifyContent: 'center' }}
          >
            Register Account
          </button>
        </div>

        {/* Error Alert Box */}
        {errorMessage && (
          <div
            className="info-box"
            style={{
              borderColor: 'rgba(239, 68, 68, 0.4)',
              backgroundColor: 'rgba(239, 68, 68, 0.1)',
              color: '#f87171',
              marginBottom: '1.25rem',
            }}
          >
            <AlertCircle size={16} /> <span>{errorMessage}</span>
          </div>
        )}

        {/* Auth Form */}
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.1rem' }}>
          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <User size={14} color="#94a3b8" /> Username
            </label>
            <input
              type="text"
              className="form-input"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter your username"
              required
              disabled={submitting}
            />
          </div>

          {authMode === 'register' && (
            <div className="form-group">
              <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                <Mail size={14} color="#94a3b8" /> Email Address
              </label>
              <input
                type="email"
                className="form-input"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="analyst@smartfinance.com"
                required
                disabled={submitting}
              />
            </div>
          )}

          <div className="form-group">
            <label className="form-label" style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
              <Lock size={14} color="#94a3b8" /> Password
            </label>
            <input
              type="password"
              className="form-input"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              required
              disabled={submitting}
            />
          </div>

          <button
            type="submit"
            className="btn-primary"
            disabled={submitting}
            style={{
              width: '100%',
              padding: '0.75rem',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: 8,
              fontSize: '0.95rem',
              marginTop: '0.5rem',
            }}
          >
            {submitting ? (
              <>
                <div className="spinner" style={{ width: '16px', height: '16px', borderWidth: '2px' }}></div>
                Authenticating...
              </>
            ) : (
              <>
                <ShieldCheck size={16} />
                {authMode === 'register' ? 'Create Account' : 'Log In'}
                <ArrowRight size={14} />
              </>
            )}
          </button>
        </form>

        {/* Footer Note */}
        <div style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          Protected by FinSight 2.0 PBKDF2 Password Hashing & JWT Security.
        </div>
      </div>
    </div>
  );
}
