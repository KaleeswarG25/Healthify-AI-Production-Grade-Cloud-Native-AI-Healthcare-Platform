import axios from 'axios';

const API_ORIGIN = process.env.REACT_APP_API_URL || '';

const authApi = axios.create({
  baseURL: `${API_ORIGIN}/api/auth`,
  headers: {
    'Content-Type': 'application/json',
  },
});

const reportApi = axios.create({
  baseURL: `${API_ORIGIN}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
});

const aiApi = axios.create({
  baseURL: `${API_ORIGIN}/api/ai`,
  headers: {
    'Content-Type': 'application/json',
  },
});

const tokenInterceptor = (config) => {
  const token = localStorage.getItem('token');

  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  return config;
};

reportApi.interceptors.request.use(tokenInterceptor);
aiApi.interceptors.request.use(tokenInterceptor);

export { authApi, reportApi, aiApi };