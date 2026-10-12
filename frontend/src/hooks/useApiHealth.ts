import { useState, useEffect, useCallback } from 'react';
import { api } from '../services/api';
import type { HealthResponse, ApiStatus } from '../types/api';

export function useApiHealth(pollIntervalMs = 15000) {
  const [status, setStatus] = useState<ApiStatus>('connecting');
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const check = useCallback(async () => {
    try {
      const h = await api.health();
      setHealth(h);
      setStatus('online');
      setError(null);
    } catch (err) {
      setStatus('offline');
      setHealth(null);
      setError(err instanceof Error ? err.message : 'Unknown error');
    }
  }, []);

  useEffect(() => {
    check();
    const id = setInterval(check, pollIntervalMs);
    return () => clearInterval(id);
  }, [check, pollIntervalMs]);

  return { status, health, error, retry: check };
}
