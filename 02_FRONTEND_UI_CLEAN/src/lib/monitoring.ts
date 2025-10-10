import LogRocket from 'logrocket';

let initialized = false;

export function initMonitoring() {
  if (initialized) return;
  const appId = import.meta.env.VITE_LOGROCKET_APP_ID;
  const enabled = import.meta.env.VITE_ENABLE_ERROR_REPORTING === 'true';

  if (appId && enabled) {
    LogRocket.init(appId, {
      release: import.meta.env.VITE_APP_VERSION ?? 'dev',
      network: {
        requestSanitizer: (request) => {
          if (!request.body) return request;
          try {
            const parsed = JSON.parse(request.body);
            if (parsed && parsed.password) {
              parsed.password = '***';
              request.body = JSON.stringify(parsed);
            }
          } catch (error) {
            // ignore non JSON bodies
          }
          return request;
        }
      }
    });
    initialized = true;
  }
}
