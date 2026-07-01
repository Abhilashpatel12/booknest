import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Search, Info, X, Plus, Minus } from 'lucide-react';
import api from '../api';

export default function ShelfDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const [search, setSearch] = useState('');
  const [actionError, setActionError] = useState(null);
  const [viewingBook, setViewingBook] = useState(null);

  const { data: shelf, isError: isShelfError, error: shelfError } = useQuery({
    queryKey: ['shelf', parseInt(id)],
    queryFn: async () => {
      const { data } = await api.get(`/shelves/${id}`);
      return data;
    }
  });

  const { data: myBooks, isError: isBooksError, error: booksError } = useQuery({
    queryKey: ['myBooksForShelf'],
    queryFn: async () => {
      const { data } = await api.get('/books/?limit=100');
      return data.items || [];
    }
  });

  const addBookMutation = useMutation({
    mutationFn: (bookId) => api.post(`/shelves/${id}/books/${bookId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shelf', parseInt(id)] });
      queryClient.invalidateQueries({ queryKey: ['shelves'] });
      queryClient.invalidateQueries({ queryKey: ['sharedShelves'] });
      setActionError(null);
    },
    onError: (err) => setActionError(err.response?.data?.detail || 'Error adding book. You might not have permission.')
  });

  const removeBookMutation = useMutation({
    mutationFn: (bookId) => api.delete(`/shelves/${id}/books/${bookId}`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['shelf', parseInt(id)] });
      queryClient.invalidateQueries({ queryKey: ['shelves'] });
      queryClient.invalidateQueries({ queryKey: ['sharedShelves'] });
      setActionError(null);
    },
    onError: (err) => setActionError(err.response?.data?.detail || 'Error removing book. You might not have permission.')
  });

  if (isShelfError || isBooksError) {
    return <div className="error-text animate-fade-in" style={{ padding: '24px', textAlign: 'center', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px', marginBottom: '24px' }}>Failed to load shelf details. {shelfError?.message || booksError?.message || 'Please try again.'}</div>;
  }

  if (shelf === undefined || myBooks === undefined) {
    return <div className="animate-fade-in" style={{ color: 'var(--text-muted)' }}>Loading shelf details...</div>;
  }

  const shelfBookIds = new Set(shelf.books?.map(b => b.id) || []);
  const availableToAdd = myBooks.filter(b => !shelfBookIds.has(b.id) && b.title.toLowerCase().includes(search.toLowerCase()));

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '32px' }}>
        <button onClick={() => navigate('/shelves')} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
          <ArrowLeft size={24} />
        </button>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '4px' }}>{shelf.name}</h1>
          <p style={{ color: 'var(--text-muted)' }}>{shelf.books?.length || 0} books in this shelf.</p>
        </div>
      </div>
      
      {actionError && (
        <div className="error-text" style={{ marginBottom: '24px', background: 'rgba(239, 68, 68, 0.1)', padding: '16px', borderRadius: '8px', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>{actionError}</span>
          <button onClick={() => setActionError(null)} style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}>
            <X size={18} />
          </button>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', '@media(max-width: 768px)': { gridTemplateColumns: '1fr' } }}>
        
        {/* Books inside shelf */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '600' }}>In Shelf</h2>
          </div>
          
          {shelf.books?.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)', border: '1px dashed rgba(255,255,255,0.1)', borderRadius: '8px' }}>
              This shelf is empty. Add books from the other panel.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {shelf.books?.map(book => (
                <div key={book.id} style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                  <div style={{ flex: 1, cursor: 'pointer' }} onClick={() => setViewingBook(book)}>
                    <h4 style={{ fontWeight: '500', fontSize: '16px' }}>{book.title}</h4>
                    <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>by {book.author}</div>
                  </div>
                  <button onClick={() => setViewingBook(book)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }} title="Book Info">
                    <Info size={18} />
                  </button>
                  <button 
                    onClick={() => removeBookMutation.mutate(book.id)} 
                    disabled={removeBookMutation.isPending}
                    style={{ background: 'rgba(239, 68, 68, 0.1)', border: 'none', color: 'var(--danger)', cursor: 'pointer', padding: '6px', borderRadius: '4px' }} 
                    title="Remove from shelf"
                  >
                    <Minus size={18} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Add to Shelf */}
        <div className="glass-panel" style={{ padding: '24px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
            <h2 style={{ fontSize: '20px', fontWeight: '600' }}>Add Books</h2>
          </div>

          <div style={{ position: 'relative', marginBottom: '20px' }}>
            <Search size={18} style={{ position: 'absolute', left: '12px', top: '14px', color: 'var(--text-muted)' }} />
            <input 
              type="text" 
              placeholder="Search your library..." 
              className="input-field" 
              style={{ paddingLeft: '40px', width: '100%' }}
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>

          {availableToAdd.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
              {search ? 'No books match your search.' : 'All your books are already in this shelf!'}
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', maxHeight: '500px', overflowY: 'auto', paddingRight: '8px' }}>
              {availableToAdd.map(book => (
                <div key={book.id} style={{ display: 'flex', alignItems: 'center', gap: '16px', padding: '16px', background: 'rgba(255,255,255,0.03)', borderRadius: '8px' }}>
                  <div style={{ flex: 1, cursor: 'pointer' }} onClick={() => setViewingBook(book)}>
                    <h4 style={{ fontWeight: '500', fontSize: '16px' }}>{book.title}</h4>
                    <div style={{ fontSize: '13px', color: 'var(--text-muted)' }}>by {book.author}</div>
                  </div>
                  <button onClick={() => setViewingBook(book)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }} title="Book Info">
                    <Info size={18} />
                  </button>
                  <button 
                    onClick={() => addBookMutation.mutate(book.id)} 
                    disabled={addBookMutation.isPending}
                    style={{ background: 'rgba(59, 130, 246, 0.1)', border: 'none', color: 'var(--primary)', cursor: 'pointer', padding: '6px', borderRadius: '4px' }} 
                    title="Add to shelf"
                  >
                    <Plus size={18} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* Book Info Modal */}
      {viewingBook && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 60, backdropFilter: 'blur(4px)' }}>
          <div className="glass-panel animate-fade-in" style={{ padding: '32px', width: '100%', maxWidth: '400px', position: 'relative' }}>
            <button onClick={() => setViewingBook(null)} style={{ position: 'absolute', top: '24px', right: '24px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <X size={20} />
            </button>
            <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '4px' }}>{viewingBook.title}</h2>
            <div style={{ fontSize: '16px', color: 'var(--text-muted)', marginBottom: '24px' }}>by {viewingBook.author}</div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Status</span>
                <span style={{ textTransform: 'capitalize', fontWeight: '500' }}>{viewingBook.status.replace(/_/g, ' ')}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Progress</span>
                <span style={{ fontWeight: '500' }}>{viewingBook.current_page} / {viewingBook.total_pages} pages</span>
              </div>
              {viewingBook.rating && (
                <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                  <span style={{ color: 'var(--text-muted)' }}>Rating</span>
                  <span style={{ fontWeight: '500' }}>{viewingBook.rating} / 5</span>
                </div>
              )}
            </div>
            
            <button className="btn btn-secondary w-full" style={{ marginTop: '32px' }} onClick={() => setViewingBook(null)}>
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
