const API_BASE = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}`
  : '/api/v1';

async function request(path, options = {}) {
  const url = path.startsWith('http') ? path : `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
    ...options,
  });
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.detail || `Request failed: ${response.status}`);
    error.status = response.status;
    error.body = data;
    throw error;
  }
  return data;
}

export const api = {
  health: () => request('/health'),
  createFarm: (payload) => request('/farms', { method: 'POST', body: JSON.stringify(payload) }),
  getFarm: (farmId) => request(`/farms/${farmId}`),
  addSoilTest: (farmId, payload) =>
    request(`/farms/${farmId}/soil-test`, { method: 'POST', body: JSON.stringify(payload) }),
  predictYield: (payload) => request('/yield/predict', { method: 'POST', body: JSON.stringify(payload) }),
  compareMarkets: (params) => request('/markets/compare?' + new URLSearchParams(params)),
  recommendMarkets: (payload) =>
    request('/markets/recommend', { method: 'POST', body: JSON.stringify(payload) }),
  priceForecast: (params) => request('/price/forecast?' + new URLSearchParams(params)),
};

export default api;