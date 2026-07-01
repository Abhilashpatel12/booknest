import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, Plus, Edit2, Trash2, X } from 'lucide-react';
import ConfirmModal from '../components/ConfirmModal';
import api from '../api';

export default function Books() {
  const queryClient = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [sortBy, setSortBy] = useState('date_added');
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingBook, setEditingBook] = useState(null);

  const [confirmConfig, setConfirmConfig] = useState({ isOpen: false, bookId: null });
  
  const { data: books, isLoading } = useQuery({
    queryKey: ['books', { page, search, status, sortBy }],
    queryFn: async () => {
      const params = new URLSearchParams({
        page: page.toString(),
        limit: '20',
        sort_by: sortBy
      });
      if (search) params.append('search', search);
      if (status) params.append('status', status);
      
      const { data } = await api.get(`/books/?${params.toString()}`);
      return data;
    },
    keepPreviousData: true
  });

  const deleteMutation = useMutation({
    mutationFn: (id) => api.delete(`/books/${id}`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['books'] })
  });

  const saveMutation = useMutation({
    mutationFn: (bookData) => {
      if (editingBook) {
        return api.put(`/books/${editingBook.id}`, bookData);
      }
      return api.post('/books/', bookData);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] });
      queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
      closeModal();
    }
  });

  const openModal = (book = null) => {
    setEditingBook(book);
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
    setEditingBook(null);
  };

  return (
    <div className="animate-fade-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '32px' }}>
        <div>
          <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '8px' }}>My Books</h1>
          <p style={{ color: 'var(--text-muted)' }}>Manage your personal library.</p>
        </div>
        <button className="btn btn-primary" onClick={() => openModal()}>
          <Plus size={18} /> Add Book
        </button>
      </div>

      {/* Filters */}
      <div className="glass-panel" style={{ padding: '16px', display: 'flex', gap: '16px', marginBottom: '24px', flexWrap: 'wrap' }}>
        <div style={{ flex: 1, minWidth: '200px', position: 'relative' }}>
          <Search size={18} style={{ position: 'absolute', left: '12px', top: '14px', color: 'var(--text-muted)' }} />
          <input 
            type="text" 
            placeholder="Search title or author..." 
            className="input-field" 
            style={{ paddingLeft: '40px' }}
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          />
        </div>
        <select 
          className="input-field" 
          style={{ width: 'auto', minWidth: '150px' }}
          value={status}
          onChange={(e) => { setStatus(e.target.value); setPage(1); }}
        >
          <option value="">All Statuses</option>
          <option value="want to read">Want to Read</option>
          <option value="reading">Reading</option>
          <option value="finished">Finished</option>
        </select>
        <select 
          className="input-field" 
          style={{ width: 'auto', minWidth: '150px' }}
          value={sortBy}
          onChange={(e) => { setSortBy(e.target.value); setPage(1); }}
        >
          <option value="date_added">Date Added</option>
          <option value="title">Title (A-Z)</option>
          <option value="rating">Highest Rated</option>
        </select>
      </div>

      {/* Book List */}
      {isLoading ? (
        <div style={{ color: 'var(--text-muted)' }}>Loading books...</div>
      ) : books?.length === 0 ? (
        <div className="glass-panel" style={{ padding: '48px', textAlign: 'center', color: 'var(--text-muted)' }}>
          No books found matching your criteria.
        </div>
      ) : (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '20px' }}>
          {books?.map(book => (
            <div key={book.id} className="glass-panel" style={{ padding: '20px', display: 'flex', flexDirection: 'column' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                <h3 style={{ fontSize: '18px', fontWeight: '600', lineHeight: 1.2 }}>{book.title}</h3>
                <div style={{ display: 'flex', gap: '8px' }}>
                  <button onClick={() => openModal(book)} style={{ background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
                    <Edit2 size={16} />
                  </button>
                  <button onClick={() => setConfirmConfig({ isOpen: true, bookId: book.id })} style={{ background: 'none', border: 'none', color: 'var(--danger)', cursor: 'pointer' }}>
                    <Trash2 size={16} />
                  </button>
                </div>
              </div>
              <div style={{ color: 'var(--text-muted)', fontSize: '14px', marginBottom: '16px' }}>
                by {book.author}
              </div>
              <div style={{ marginTop: 'auto', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span className={`badge ${book.status === 'reading' ? 'badge-reading' : book.status === 'finished' ? 'badge-finished' : 'badge-want'}`}>
                  {book.status.replace(/_/g, ' ')}
                </span>
                <span style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                  {book.current_page} / {book.total_pages} p.
                </span>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Pagination */}
      <div style={{ display: 'flex', justifyContent: 'center', gap: '16px', marginTop: '32px' }}>
        <button className="btn btn-secondary" disabled={page === 1} onClick={() => setPage(p => Math.max(1, p - 1))}>Previous</button>
        <span style={{ alignSelf: 'center', fontSize: '14px', color: 'var(--text-muted)' }}>Page {page}</span>
        <button className="btn btn-secondary" disabled={!books || books.length < 20} onClick={() => setPage(p => p + 1)}>Next</button>
      </div>

      {/* Modal for Add/Edit */}
      {isModalOpen && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 50, backdropFilter: 'blur(4px)' }}>
          <div className="glass-panel animate-fade-in" style={{ padding: '32px', width: '100%', maxWidth: '500px', position: 'relative' }}>
            <button onClick={closeModal} style={{ position: 'absolute', top: '24px', right: '24px', background: 'none', border: 'none', color: 'var(--text-muted)', cursor: 'pointer' }}>
              <X size={20} />
            </button>
            <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '24px' }}>
              {editingBook ? 'Edit Book' : 'Add New Book'}
            </h2>
            <form onSubmit={(e) => {
              e.preventDefault();
              const fd = new FormData(e.target);
              const data = Object.fromEntries(fd.entries());
              data.total_pages = parseInt(data.total_pages, 10);
              data.current_page = parseInt(data.current_page || 0, 10);
              if (data.rating) data.rating = parseInt(data.rating, 10);
              else delete data.rating;
              saveMutation.mutate(data);
            }}>
              <div className="input-group">
                <label className="input-label">Title</label>
                <input name="title" required defaultValue={editingBook?.title} className="input-field" />
              </div>
              <div className="input-group">
                <label className="input-label">Author</label>
                <input name="author" required defaultValue={editingBook?.author} className="input-field" />
              </div>
              <div style={{ display: 'flex', gap: '16px' }}>
                <div className="input-group" style={{ flex: 1 }}>
                  <label className="input-label">Total Pages</label>
                  <input name="total_pages" type="number" required min="1" defaultValue={editingBook?.total_pages} className="input-field" />
                </div>
                <div className="input-group" style={{ flex: 1 }}>
                  <label className="input-label">Current Page</label>
                  <input name="current_page" type="number" min="0" defaultValue={editingBook?.current_page || 0} className="input-field" />
                </div>
              </div>
              <div className="input-group">
                <label className="input-label">Status</label>
                <select name="status" className="input-field" defaultValue={editingBook?.status || 'want to read'}>
                  <option value="want to read">Want to Read</option>
                  <option value="reading">Reading</option>
                  <option value="finished">Finished</option>
                </select>
              </div>
              <button type="submit" className="btn btn-primary w-full" style={{ marginTop: '16px' }} disabled={saveMutation.isPending}>
                {saveMutation.isPending ? 'Saving...' : 'Save Book'}
              </button>
            </form>
          </div>
        </div>
      )}

      <ConfirmModal 
        isOpen={confirmConfig.isOpen}
        title="Delete Book"
        message="Are you sure you want to delete this book? This action cannot be undone."
        confirmText="Delete"
        onConfirm={() => deleteMutation.mutate(confirmConfig.bookId)}
        onCancel={() => setConfirmConfig({ isOpen: false, bookId: null })}
      />
    </div>
  );
}
