import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link2, CornerDownRight, X, Info } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import ConfirmModal from '../components/ConfirmModal';
import api from '../api';

export default function Borrowed() {
  const queryClient = useQueryClient();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [lendError, setLendError] = useState(null);
  const [lendSuccess, setLendSuccess] = useState(null);
  const [confirmConfig, setConfirmConfig] = useState({ isOpen: false, recordId: null });
  const [viewingBook, setViewingBook] = useState(null);

  const { data: borrowedBooks, isLoading: borrowedLoading, isError: isBorrowedError, error: borrowedError } = useQuery({
    queryKey: ['borrowedBooks'],
    queryFn: async () => {
      const { data } = await api.get('/lending/borrowed');
      return data;
    }
  });

  const { data: myBooks, isError: isMyBooksError, error: myBooksError } = useQuery({
    queryKey: ['myBooksForLending'],
    queryFn: async () => {
      const { data } = await api.get('/books/?limit=100');
      return data.items || [];
    }
  });

  const { data: lentBooks, isLoading: lentLoading, isError: isLentError, error: lentError } = useQuery({
    queryKey: ['lentBooks'],
    queryFn: async () => {
      const { data } = await api.get('/lending/lent');
      return data;
    }
  });

  const returnMutation = useMutation({
    mutationFn: (id) => api.post(`/lending/${id}/return`),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lentBooks'] });
      setConfirmConfig({ isOpen: false, recordId: null });
    }
  });

  const lendMutation = useMutation({
    mutationFn: ({ book_id, email }) => api.post(`/lending/${book_id}/lend`, { borrower_email: email }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lentBooks'] });
      setLendSuccess('Book lent successfully!');
      setTimeout(() => {
        setIsModalOpen(false);
        setLendSuccess(null);
      }, 1500);
    },
    onError: (err) => setLendError(err.response?.data?.detail || 'Error lending book')
  });

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '8px' }}>Lending</h1>
          <p style={{ color: 'var(--text-muted)' }}>Keep track of books you've borrowed and lent out.</p>
        </div>
        <button className="btn btn-primary" onClick={() => setIsModalOpen(true)}>
          <Link2 size={18} /> Lend a Book
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px', '@media(max-width: 768px)': { gridTemplateColumns: '1fr' } }}>
        
        {/* Borrowed From Others */}
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <CornerDownRight size={20} color="var(--primary)" /> 
            Borrowed from others
          </h2>
          {isBorrowedError ? (
            <div className="error-text animate-fade-in" style={{ padding: '24px', textAlign: 'center', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>Failed to load borrowed books. {borrowedError?.message || 'Please try again.'}</div>
          ) : borrowedBooks === undefined ? (
            <div style={{ color: 'var(--text-muted)' }}>Loading...</div>
          ) : borrowedBooks?.length === 0 ? (
            <div className="glass-panel" style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
              You are not borrowing any books right now.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {borrowedBooks?.map(record => (
                <div key={record.id} className="glass-panel" style={{ padding: '20px', borderLeft: '4px solid var(--primary)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '4px' }}>{record.book?.title}</h3>
                    <div style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '12px' }}>Owner: {record.lender?.name}</div>
                    <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                      Borrowed {formatDistanceToNow(new Date(record.borrowed_at), { addSuffix: true })}
                    </div>
                  </div>
                  <button onClick={() => setViewingBook(record.book)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }} title="Book Info">
                    <Info size={20} />
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Lent to Others */}
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '16px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Link2 size={20} color="var(--warning)" /> 
            Lent to others
          </h2>
          {isLentError ? (
            <div className="error-text animate-fade-in" style={{ padding: '24px', textAlign: 'center', background: 'rgba(239, 68, 68, 0.1)', borderRadius: '8px' }}>Failed to load lent books. {lentError?.message || 'Please try again.'}</div>
          ) : lentBooks === undefined ? (
            <div style={{ color: 'var(--text-muted)' }}>Loading...</div>
          ) : lentBooks?.length === 0 ? (
            <div className="glass-panel" style={{ padding: '24px', textAlign: 'center', color: 'var(--text-muted)' }}>
              You haven't lent out any books.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {lentBooks?.map(record => (
                <div key={record.id} className="glass-panel" style={{ padding: '20px', borderLeft: '4px solid var(--warning)' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div>
                      <h3 style={{ fontSize: '18px', fontWeight: '600', marginBottom: '4px' }}>{record.book?.title}</h3>
                      <div style={{ fontSize: '14px', color: 'var(--text-muted)', marginBottom: '12px' }}>Borrower: {record.borrower?.name}</div>
                      <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                        Lent {formatDistanceToNow(new Date(record.borrowed_at), { addSuffix: true })}
                      </div>
                    </div>
                    <button 
                      onClick={() => setConfirmConfig({ isOpen: true, recordId: record.id })} 
                      className="btn btn-secondary" 
                      style={{ fontSize: '12px', padding: '6px 12px' }}
                    >
                      Mark Returned
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* Lend Modal */}
      {isModalOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50, backdropFilter: 'blur(4px)' }}>
          <div className="glass-panel animate-fade-in" style={{ padding: '32px', width: '100%', maxWidth: '400px', position: 'relative' }}>
            <button onClick={() => setIsModalOpen(false)} style={{ position: 'absolute', top: '24px', right: '24px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <X size={20} />
            </button>
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>Lend a Book</h2>
            
            {lendError && <div className="error-text" style={{ marginBottom: '16px', background: 'rgba(239, 68, 68, 0.1)', padding: '10px', borderRadius: '8px' }}>{lendError}</div>}
            {lendSuccess && <div style={{ marginBottom: '16px', background: 'rgba(34, 197, 94, 0.1)', color: 'var(--success)', padding: '10px', borderRadius: '8px', fontSize: '13px' }}>{lendSuccess}</div>}
            {isMyBooksError && <div className="error-text" style={{ marginBottom: '16px', background: 'rgba(239, 68, 68, 0.1)', padding: '10px', borderRadius: '8px' }}>Failed to load your books for lending.</div>}
            
            <form onSubmit={(e) => {
              e.preventDefault();
              setLendError(null);
              const fd = new FormData(e.target);
              lendMutation.mutate({ book_id: parseInt(fd.get('book_id'), 10), email: fd.get('email') });
            }}>
              <div className="input-group">
                <label className="input-label">Select Book</label>
                <select name="book_id" required className="input-field" defaultValue="">
                  <option value="" disabled>-- Choose a book --</option>
                  {myBooks?.map(book => (
                    <option key={book.id} value={book.id}>
                      {book.title} (by {book.author})
                    </option>
                  ))}
                </select>
              </div>
              <div className="input-group">
                <label className="input-label">Borrower's Email</label>
                <input name="email" type="email" required className="input-field" placeholder="borrower@example.com" />
              </div>
              <button type="submit" className="btn btn-primary w-full" disabled={lendMutation.isPending}>
                {lendMutation.isPending ? 'Lending...' : 'Lend Book'}
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Book Info Modal */}
      {viewingBook && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 60, backdropFilter: 'blur(4px)' }}>
          <div className="glass-panel animate-fade-in" style={{ padding: '32px', width: '100%', maxWidth: '400px', position: 'relative' }}>
            <button onClick={() => setViewingBook(null)} style={{ position: 'absolute', top: '24px', right: '24px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <X size={20} />
            </button>
            <h2 style={{ fontSize: '24px', fontWeight: '600', marginBottom: '4px' }}>{viewingBook.title}</h2>
            <div style={{ fontSize: '16px', color: 'var(--text-muted)', marginBottom: '24px' }}>by {viewingBook.author || 'Unknown'}</div>
            
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Status</span>
                <span style={{ textTransform: 'capitalize', fontWeight: '500' }}>{viewingBook.status?.replace(/_/g, ' ') || 'Unknown'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', paddingBottom: '8px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
                <span style={{ color: 'var(--text-muted)' }}>Progress</span>
                <span style={{ fontWeight: '500' }}>{viewingBook.current_page || 0} / {viewingBook.total_pages || 0} pages</span>
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

      <ConfirmModal 
        isOpen={confirmConfig.isOpen}
        title="Return Book"
        message="Are you sure you want to mark this book as returned? It will be removed from this list."
        confirmText="Mark Returned"
        isDanger={false}
        isLoading={returnMutation.isPending}
        onConfirm={() => returnMutation.mutate(confirmConfig.recordId)}
        onCancel={() => setConfirmConfig({ isOpen: false, recordId: null })}
      />
    </div>
  );
}
