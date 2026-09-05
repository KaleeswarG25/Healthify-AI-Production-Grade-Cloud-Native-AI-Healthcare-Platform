import axios from 'axios';


/*
 * All APIs use the same public origin.
 *
 * Production:
 *
 * https://healthify.example.com
 *
 * Gateway routes:
 *
 * /api/auth  -> Auth Service
 * /api       -> Report Service
 * /api/ai    -> AI Service
 *
 * Using relative paths means we do not hardcode
 * localhost or Kubernetes service names into React.
 */

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


/*
 * Attach JWT automatically to protected APIs.
 */
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


export {
  authApi,
  reportApi,
  aiApi,
};