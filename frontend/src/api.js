import axios from 'axios';

export const api = axios.create({ baseURL: '' });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

let refreshing = null;

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config;
    if (error.response?.status === 401 && original && !original._retry && !String(original.url).includes('/oauth2/token')) {
      original._retry = true;
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        localStorage.removeItem('access_token');
        window.dispatchEvent(new Event('auth-lost'));
        return Promise.reject(error);
      }
      try {
        if (!refreshing) {
          const body = new URLSearchParams();
          body.set('grant_type', 'refresh_token');
          body.set('refresh_token', refreshToken);
          body.set('client_id', 'grayboard-web');
          body.set('client_secret', 'grayboard-secret');
          refreshing = axios.post('/oauth2/token', body, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          }).finally(() => { refreshing = null; });
        }
        const res = await refreshing;
        localStorage.setItem('access_token', res.data.access_token);
        if (res.data.refresh_token) localStorage.setItem('refresh_token', res.data.refresh_token);
        original.headers.Authorization = `Bearer ${res.data.access_token}`;
        return api(original);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.dispatchEvent(new Event('auth-lost'));
        return Promise.reject(refreshError);
      }
    }
    return Promise.reject(error);
  }
);

export async function login(username, password) {
  const body = new URLSearchParams();
  body.set('grant_type', 'password');
  body.set('username', username);
  body.set('password', password);
  body.set('client_id', 'grayboard-web');
  body.set('client_secret', 'grayboard-secret');
  body.set('scope', 'erp');
  const res = await axios.post('/oauth2/token', body, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  });
  localStorage.setItem('access_token', res.data.access_token);
  localStorage.setItem('refresh_token', res.data.refresh_token);
  return res.data;
}

export function logout() {
  const token = localStorage.getItem('access_token');
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  if (token) {
    axios.post('/api/auth/logout', null, { headers: { Authorization: `Bearer ${token}` } }).catch(() => {});
  }
}
