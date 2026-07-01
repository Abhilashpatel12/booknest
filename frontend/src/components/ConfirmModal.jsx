import React from 'react';
import { X, AlertTriangle, Info } from 'lucide-react';

export default function ConfirmModal({ 
  isOpen, 
  title, 
  message, 
  onConfirm, 
  onCancel, 
  confirmText = 'Confirm', 
  isDanger = true 
}) {
  if (!isOpen) return null;

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100, backdropFilter: 'blur(4px)' }}>
      <div className="glass-panel animate-fade-in" style={{ padding: '32px', width: '100%', maxWidth: '400px', position: 'relative' }}>
        <button onClick={onCancel} style={{ position: 'absolute', top: '24px', right: '24px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
          <X size={20} />
        </button>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '16px' }}>
          {isDanger ? <AlertTriangle size={24} color="var(--danger)" /> : <Info size={24} color="var(--primary)" />}
          <h2 style={{ fontSize: '20px', fontWeight: '600' }}>{title}</h2>
        </div>
        
        <p style={{ color: 'var(--text-muted)', marginBottom: '32px', lineHeight: 1.5 }}>
          {message}
        </p>

        <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button className="btn btn-secondary" onClick={onCancel}>
            Cancel
          </button>
          <button 
            className={`btn ${isDanger ? 'btn-danger' : 'btn-primary'}`} 
            onClick={() => { onConfirm(); onCancel(); }}
          >
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
}
