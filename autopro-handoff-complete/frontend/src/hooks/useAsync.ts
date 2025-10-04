import { useState, useEffect, useCallback } from 'react';

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export interface UseAsyncOptions<T> {
  immediate?: boolean;
  onSuccess?: (data: T) => void;
  onError?: (error: Error) => void;
}

/**
 * Hook for handling async operations with loading, error, and data states
 * 
 * @example
 * const { data, loading, error, execute } = useAsync(
 *   () => LeadService.getLeads(),
 *   { immediate: true }
 * );
 */
export function useAsync<T>(
  asyncFunction: () => Promise<T>,
  options: UseAsyncOptions<T> = {}
) {
  const { immediate = false, onSuccess, onError } = options;

  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  const execute = useCallback(async () => {
    setState({ data: null, loading: true, error: null });

    try {
      const data = await asyncFunction();
      setState({ data, loading: false, error: null });
      
      if (onSuccess) {
        onSuccess(data);
      }
      
      return data;
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error));
      setState({ data: null, loading: false, error: err });
      
      if (onError) {
        onError(err);
      }
      
      throw err;
    }
  }, [asyncFunction, onSuccess, onError]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [immediate, execute]);

  return {
    ...state,
    execute,
  };
}

/**
 * Hook for handling mutations (POST, PUT, DELETE) with loading and error states
 * 
 * @example
 * const { mutate, loading, error } = useMutation(
 *   (data) => LeadService.createLead(data),
 *   {
 *     onSuccess: () => {
 *       toast({ title: 'Lead created!' });
 *       refetch();
 *     }
 *   }
 * );
 */
export function useMutation<T, P = void>(
  mutationFunction: (params: P) => Promise<T>,
  options: UseAsyncOptions<T> = {}
) {
  const { onSuccess, onError } = options;

  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: false,
    error: null,
  });

  const mutate = useCallback(
    async (params: P) => {
      setState({ data: null, loading: true, error: null });

      try {
        const data = await mutationFunction(params);
        setState({ data, loading: false, error: null });
        
        if (onSuccess) {
          onSuccess(data);
        }
        
        return data;
      } catch (error) {
        const err = error instanceof Error ? error : new Error(String(error));
        setState({ data: null, loading: false, error: err });
        
        if (onError) {
          onError(err);
        }
        
        throw err;
      }
    },
    [mutationFunction, onSuccess, onError]
  );

  const reset = useCallback(() => {
    setState({ data: null, loading: false, error: null });
  }, []);

  return {
    ...state,
    mutate,
    reset,
  };
}
