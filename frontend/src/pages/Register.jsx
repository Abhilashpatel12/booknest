import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, Link } from 'react-router-dom';

export default function Register() {
  const { signup } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors(null);
    setIsLoading(true);
    try {
      await signup(name, email, password);
      navigate('/');
    } catch (err) {
      if (err.response?.data?.detail) {
        // Handle Pydantic validation errors
        if (Array.isArray(err.response.data.detail)) {
          const formattedErrors = err.response.data.detail.map(d => d.msg).join('. ');
          setErrors(formattedErrors);
        } else {
          setErrors(err.response.data.detail);
        }
      } else if (err.response?.data?.message) {
        setErrors(err.response.data.message);
      } else {
        setErrors('Signup failed. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
      <div className="glass-panel" style={{ width: '100%', maxWidth: '400px', padding: '32px' }}>
        <h2 style={{ marginBottom: '24px', textAlign: 'center', fontSize: '24px', fontWeight: '600' }}>Create an Account</h2>
        {errors && <div className="error-text" style={{ marginBottom: '16px', textAlign: 'center', background: 'rgba(239, 68, 68, 0.1)', padding: '10px', borderRadius: '8px' }}>{errors}</div>}
        <form onSubmit={handleSubmit}>
          <div className="input-group">
            <label className="input-label">Name</label>
            <input 
              type="text" 
              className="input-field" 
              placeholder="Jane Doe" 
              value={name}
              onChange={(e) => setName(e.target.value)}
              required 
            />
          </div>
          <div className="input-group">
            <label className="input-label">Email</label>
            <input 
              type="email" 
              className="input-field" 
              placeholder="you@example.com" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          <div className="input-group" style={{ marginBottom: '24px' }}>
            <label className="input-label">Password</label>
            <input 
              type="password" 
              className="input-field" 
              placeholder="••••••••" 
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginTop: '6px' }}>
              Must be at least 8 characters, include a number and uppercase letter.
            </p>
          </div>
          <button type="submit" className="btn btn-primary w-full" disabled={isLoading}>
            {isLoading ? 'Creating account...' : 'Register'}
          </button>
        </form>
        <p style={{ marginTop: '24px', textAlign: 'center', fontSize: '14px', color: 'var(--text-muted)' }}>
          Already have an account? <Link to="/login" style={{ color: 'var(--primary)', textDecoration: 'none' }}>Sign in</Link>
        </p>
      </div>
    </div>
  );
}
