import React from 'react';
import { Link } from 'react-router-dom';
import { AlertOctagon, LayoutDashboard } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="page-container" style={{ display: 'flex', justifyContent: 'center', paddingTop: '4rem' }}>
      <div className="card empty-state-card" style={{ maxWidth: 500, width: '100%', textAlign: 'center' }}>
        <AlertOctagon size={56} color="#ef4444" style={{ margin: '0 auto 1rem auto' }} />
        <h2 style={{ fontSize: '1.75rem', fontWeight: 800, marginBottom: '0.5rem' }}>404 - Page Not Found</h2>
        <p style={{ color: 'var(--text-muted)', marginBottom: '1.75rem' }}>
          The requested financial intelligence page route does not exist or has been moved.
        </p>
        <Link to="/" className="btn-primary" style={{ display: 'inline-flex', width: 'auto', textDecoration: 'none' }}>
          <LayoutDashboard size={18} />
          Back to AI Dashboard
        </Link>
      </div>
    </div>
  );
}
