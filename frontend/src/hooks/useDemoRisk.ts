import { useState, useCallback } from 'react';
import { api } from '../services/api';
import type { DemoRiskResponse } from '../types/api';

export function useDemoRisk() {
  const [data, setData] = useState<DemoRiskResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await api.demoRisk();
      setData(resp);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load demo data');
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, load };
}
