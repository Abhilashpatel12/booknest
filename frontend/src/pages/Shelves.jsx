import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Trash2, Users, Folder, X, Eye } from 'lucide-react';
import ConfirmModal from '../components/ConfirmModal';
import api from '../api';

export default function Shelves() {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
  const [activeShelf, setActiveShelf] = useState(null);
  const [shareError, setShareError] = useState(null);
  const [shareSuccess, setShareSuccess] = useState(null);
  const [confirmConfig, setConfirmConfig] = useState({ isOpen: false, shelfId: null });

  const { data: shelves, isLoading } = useQuery({
    queryKey: ['shelves'],
    queryFn: async () => {
      const { data } = await api.get('/shelves/');
      return data;
    }
  });

  const { data: sharedShelves } = useQuery({
    queryKey: ['sharedShelves'],
    queryFn: async () => {
      const { data } = await api.get('/sharing/shared-with-me');
      return data;
    }
  });

  const [globalError, setGlobalError] = useState(null);

  const createMutation = useMutation({
    mutationFn: (name) => api.post('/shelves/', { name }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shelves'] });
      setIsModalOpen(false);
      setGlobalError(null);
    },
    onError: (err) => setGlobalError(err.response?.data?.detail || 'Error creating shelf.')
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/shelves/${id}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shelves'] });
      setGlobalError(null);
    },
    onError: (err) => setGlobalError(err.response?.data?.detail || 'Error deleting shelf. You may not have permission.')
  });

  const updateRoleMutation = useMutation({
    mutationFn: ({ shareId, role }) => api.put(`/sharing/${shareId}`, { role }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shelves'] });
      setGlobalError(null);
    },
    onError: (err) => setGlobalError(err.response?.data?.detail || 'Error updating role. You may not have permission.')
  });

  const removeShareMutation = useMutation({
    mutationFn: (shareId) => api.delete(`/sharing/${shareId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shelves'] });
      setGlobalError(null);
    },
    onError: (err) => setGlobalError(err.response?.data?.detail || 'Error removing user. You may not have permission.')
  });

  const shareMutation = useMutation({
    mutationFn: ({ id, email, role }) => api.post(`/sharing/shelves/${id}`, { email, role }),
    onSuccess: () => {
      setShareSuccess('Shelf shared successfully!');
      setTimeout(() => {
        setIsShareModalOpen(false);
        setShareSuccess(null);
      }, 1500);
    },
    onError: (err) => setShareError(err.response?.data?.detail || 'Error sharing shelf')
  });

  if (shelves === undefined) return <div className="animate-fade-in" style={{ color: 'var(--text-muted)' }}>Loading shelves...</div>;

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '8px' }}>Shelves</h1>
          <p style={{ color: 'var(--text-muted)' }}>Organize your books into custom collections.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Plus size={18} /> New Shelf
        </button>
      </div>

      {globalError && (
        <div className="error-text" style={{ marginBottom: '24px', background: 'rgba(239, 68, 68, 0.1)', padding: '16px', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{globalError}</span>
          <button onClick={() => setGlobalError(null)} style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px', marginBottom: '40px' }}>
        {shelves?.map(shelf => (
          <div key={shelf.id} className="glass-panel" style={{ padding: '24px', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <Folder size={20} color="var(--primary)" />
                <h3 style={{ fontSize: '18px', fontWeight: '600' }}>{shelf.name}</h3>
              </div>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button onClick={() => navigate(`/shelves/${shelf.id}`)} style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer' }} title="View Books">
                  <Eye size={16} />
                </button>
                <button onClick={() => { setActiveShelf(shelf); setIsShareModalOpen(true); setShareError(null); setShareSuccess(null); }} style={{ background: 'none', border: 'none', color: 'var(--secondary)', cursor: 'pointer' }} title="Share Shelf">
                  <Users size={16} />
                </button>
                <button onClick={() => setConfirmConfig({ isOpen: true, shelfId: shelf.id })} style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}>
                  <Trash2 size={16} />
                </button>
              </div>
            </div>
            <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
              {shelf.books?.length || 0} books inside
            </div>
          </div>
        ))}
      </div>

      <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px' }}>Shared with me</h2>
      {sharedShelves?.length === 0 ? (
        <div className="glass-panel" style={{ padding: '24px', color: 'var(--text-muted)', textAlign: 'center' }}>
          No shelves shared with you yet.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
          {sharedShelves?.map(shelf => (
            <div key={shelf.id} className="glass-panel" style={{ padding: '24px', borderLeft: '4px solid var(--secondary)' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                <Folder size={20} color="var(--secondary)" />
                <h3 style={{ fontSize: '18px', fontWeight: '600' }}>{shelf.name}</h3>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div style={{ color: 'var(--text-muted)', fontSize: '14px' }}>
                  {shelf.books?.length || 0} books inside
                </div>
                <button onClick={() => navigate(`/shelves/${shelf.id}`)} style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer' }} title="View Books">
                  <Eye size={16} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modals */}
      {isModalOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50, backdropFilter: 'blur(4px)' }}>
          <div className="glass-panel animate-fade-in" style={{ padding: '32px', width: '100%', maxWidth: '400px', position: 'relative' }}>
            <button onClick={() => setIsModalOpen(false)} style={{ position: 'absolute', top: '24px', right: '24px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <X size={20} />
            </button>
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>Create Shelf</h2>
            <form onSubmit={(e) => {
              e.preventDefault();
              createMutation.mutate(new FormData(e.target).get('name'));
            }}>
              <div className="input-group">
                <label className="input-label">Shelf Name</label>
                <input name="name" required className="input-field" placeholder="e.g. Sci-Fi Favorites" />
              </div>
              <button type="submit" className="btn btn-primary w-full" disabled={createMutation.isPending}>
                Create
              </button>
            </form>
          </div>
        </div>
      )}

      {isShareModalOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50, backdropFilter: 'blur(4px)' }}>
          <div className="glass-panel animate-fade-in" style={{ padding: '32px', width: '100%', maxWidth: '400px', position: 'relative' }}>
            <button onClick={() => setIsShareModalOpen(false)} style={{ position: 'absolute', top: '24px', right: '24px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <X size={20} />
            </button>
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>Share '{activeShelf?.name}'</h2>
            
            {shareError && <div className="error-text" style={{ marginBottom: '16px', background: 'rgba(239, 68, 68, 0.1)', padding: '10px', borderRadius: '8px' }}>{shareError}</div>}
            {shareSuccess && <div style={{ marginBottom: '16px', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--success)', padding: '10px', borderRadius: '8px', fontSize: '13px' }}>{shareSuccess}</div>}
            
            {activeShelf?.shares?.length > 0 && (
              <div style={{ marginBottom: '24px' }}>
                <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-muted)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Current Collaborators</h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                  {activeShelf.shares.map(share => (
                    <div key={share.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '12px', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                      <div style={{ flex: 1, minWidth: 0, paddingRight: '12px' }}>
                        <div style={{ fontWeight: '500', fontSize: '14px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{share.user.name}</div>
                        <div style={{ fontSize: '12px', color: 'var(--text-muted)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{share.user.email}</div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <select 
                          className="input-field" 
                          style={{ width: '100px', padding: '6px 28px 6px 10px', fontSize: '13px' }}
                          value={share.role}
                          onChange={(e) => updateRoleMutation.mutate({ shareId: share.id, role: e.target.value })}
                          disabled={updateRoleMutation.isPending}
                        >
                          <option value="viewer">Viewer</option>
                          <option value="editor">Editor</option>
                        </select>
                        <button 
                          onClick={() => removeShareMutation.mutate(share.id)} 
                          disabled={removeShareMutation.isPending}
                          style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer', padding: '4px' }}
                          title="Remove user"
                        >
                          <X size={16} />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            <h3 style={{ fontSize: '14px', fontWeight: '600', color: 'var(--text-muted)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Add Collaborator</h3>
            <form onSubmit={(e) => {
              e.preventDefault();
              setShareError(null);
              const fd = new FormData(e.target);
              shareMutation.mutate({ id: activeShelf.id, email: fd.get('email'), role: fd.get('role') });
            }}>
              <div className="input-group">
                <label className="input-label">User Email</label>
                <input name="email" type="email" required className="input-field" />
              </div>
              <div className="input-group">
                <label className="input-label">Role</label>
                <select name="role" className="input-field">
                  <option value="viewer">Viewer</option>
                  <option value="editor">Editor</option>
                </select>
              </div>
              <button type="submit" className="btn btn-primary w-full" disabled={shareMutation.isPending}>
                {shareMutation.isPending ? 'Sharing...' : 'Share Shelf'}
              </button>
            </form>
          </div>
        </div>
      )}

      <ConfirmModal 
        isOpen={confirmConfig.isOpen}
        title="Delete Shelf"
        message="Are you sure you want to delete this shelf? The books will remain in your library."
        confirmText="Delete"
        onConfirm={() => deleteMutation.mutate(confirmConfig.shelfId)}
        onCancel={() => setConfirmConfig({ isOpen: false, shelfId: null })}
      />
    </div>
  );
}
