"use client";
import { useEffect } from 'react';
import { syncOfflineQueue } from '@/lib/offlineQueue';

export default function OfflineSync() {
  useEffect(() => {
    const handleOnline = () => {
      syncOfflineQueue();
    };
    
    window.addEventListener('online', handleOnline);
    
    // Also try syncing on mount if online
    if (typeof navigator !== 'undefined' && navigator.onLine) {
        syncOfflineQueue();
    }
    
    return () => window.removeEventListener('online', handleOnline);
  }, []);
  
  return null;
}
