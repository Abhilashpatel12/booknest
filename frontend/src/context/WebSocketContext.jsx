import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
import { useAuth } from './AuthContext';
import { useQueryClient } from '@tanstack/react-query';

const WebSocketContext = createContext();

export const useWebSocket = () => useContext(WebSocketContext);

export const WebSocketProvider = ({ children }) => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);

  const connect = () => {
    const token = localStorage.getItem('access_token');
    if (!token) return;

    if (wsRef.current) {
      wsRef.current.close();
    }

    const wsBaseUrl = import.meta.env.VITE_WS_URL;
    const ws = new WebSocket(`${wsBaseUrl}/ws?token=${token}`);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      
      // Only invalidate queries if this is a RE-connection, 
      // to avoid double-fetching data on the initial page load.
      if (reconnectAttemptsRef.current > 0) {
        queryClient.invalidateQueries();
      }
      
      reconnectAttemptsRef.current = 0;
    };

    ws.onmessage = (event) => {
      try {
        const message = JSON.parse(event.data);
        console.log('WS Message:', message);
        
        if (message.type === 'BOOK_LENT_TO_YOU' || message.type === 'BOOK_RETURNED') {
          queryClient.invalidateQueries({ queryKey: ['borrowedBooks'] });
          queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
        } else if (message.type === 'SHELF_UPDATED') {
          queryClient.invalidateQueries({ queryKey: ['shelves'] });
          if (message.shelf_id) {
            queryClient.invalidateQueries({ queryKey: ['shelf', parseInt(message.shelf_id)] });
          }
        } else if (message.action_type) {
          queryClient.invalidateQueries({ queryKey: ['dashboardStats'] });
          queryClient.invalidateQueries({ queryKey: ['dashboardActivity'] });
        }
      } catch (e) {
        console.error('Error parsing WS message', e);
      }
    };

    ws.onclose = (event) => {
      setIsConnected(false);
      console.log('WebSocket disconnected', event.code);
      
      if (event.code !== 1008 && event.code !== 1000) {
        const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 10000);
        reconnectAttemptsRef.current += 1;
        
        reconnectTimeoutRef.current = setTimeout(() => {
          console.log(`Reconnecting... attempt ${reconnectAttemptsRef.current}`);
          connect();
        }, delay);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      ws.close();
    };

    wsRef.current = ws;
  };

  useEffect(() => {
    if (user) {
      connect();
    } else {
      if (wsRef.current) {
        wsRef.current.close(1000, 'User logged out');
        wsRef.current = null;
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close(1000, 'Component unmounting');
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
    };
  }, [user]);

  return (
    <WebSocketContext.Provider value={{ isConnected }}>
      {children}
    </WebSocketContext.Provider>
  );
};
