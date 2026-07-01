import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Book, CheckCircle, Clock, Link2, Activity as ActivityIcon } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import api from '../api';

export default function Dashboard() {
  const { data: dashboardData } = useQuery({
    queryKey: ['dashboardStats'],
    queryFn: async () => {
      const { data } = await api.get('/dashboard/stats');
      return data;
    }
  });

  if (dashboardData === undefined) {
    return <div className="animate-fade-in" style={{ color: 'var(--text-muted)' }}>Loading dashboard...</div>;
  }

  const activities = dashboardData.recent_activity;

  const statCards = [
    { title: 'Total Books', value: dashboardData.total_books || 0, icon: Book, color: 'var(--primary)' },
    { title: 'Finished', value: dashboardData.finished || 0, icon: CheckCircle, color: 'var(--success)' },
    { title: 'Currently Reading', value: dashboardData.reading || 0, icon: Clock, color: 'var(--warning)' },
    { title: 'Books Lent', value: dashboardData.books_currently_lent || 0, icon: Link2, color: 'var(--secondary)' },
  ];

  return (
    <div className="animate-fade-in">
      <div style={{ marginBottom: '32px' }}>
        <h1 style={{ fontSize: '28px', fontWeight: '700', marginBottom: '8px' }}>Dashboard</h1>
        <p style={{ color: 'var(--text-muted)' }}>Welcome back! Here's what's happening with your books.</p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: '24px', marginBottom: '40px' }}>
        {statCards.map((stat, i) => {
          const Icon = stat.icon;
          return (
            <div key={i} className="glass-panel" style={{ padding: '24px', display: 'flex', alignItems: 'center', gap: '20px' }}>
              <div style={{ 
                width: '48px', height: '48px', borderRadius: '12px', 
                background: `color-mix(in srgb, ${stat.color} 15%, transparent)`,
                color: stat.color,
                display: 'flex', alignItems: 'center', justifyContent: 'center'
              }}>
                <Icon size={24} />
              </div>
              <div>
                <div style={{ color: 'var(--text-muted)', fontSize: '14px', fontWeight: '500', marginBottom: '4px' }}>
                  {stat.title}
                </div>
                <div style={{ fontSize: '24px', fontWeight: '700' }}>
                  {stat.value}
                </div>
              </div>
            </div>
          );
        })}
      </div>

      <div className="glass-panel" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '24px' }}>
          <ActivityIcon size={20} color="var(--primary)" />
          <h2 style={{ fontSize: '20px', fontWeight: '600' }}>Recent Activity</h2>
        </div>
        
        {activities?.length === 0 ? (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
            No activity yet. Start adding books or shelves!
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {activities?.map((activity, index) => (
              <div key={index} style={{ 
                display: 'flex', gap: '16px', padding: '16px', 
                background: 'rgba(255,255,255,0.02)', borderRadius: 'var(--radius-md)' 
              }}>
                <div style={{ 
                  width: '8px', height: '8px', borderRadius: '50%', 
                  background: 'var(--primary)', marginTop: '6px' 
                }} />
                <div>
                  <div style={{ fontSize: '14px', color: 'var(--text-main)', marginBottom: '4px' }}>
                    {activity.description}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--text-muted)' }}>
                    {formatDistanceToNow(new Date(activity.timestamp), { addSuffix: true })}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
