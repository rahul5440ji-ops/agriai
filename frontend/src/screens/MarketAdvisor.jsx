import React, { useState } from 'react';
import { api } from '../services/api';
import useAppStore from '../store';
import { t } from '../i18n';

export default function MarketAdvisor() {
  const { language, farmId } = useAppStore();
  const [crop, setCrop] = useState('wheat');
  const [state, setState] = useState('Maharashtra');
  const [district, setDistrict] = useState('Pune');
  const [transport, setTransport] = useState('');
  const [other, setOther] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const recommend = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.recommendMarkets({
        crop,
        state,
        district,
        transport_cost_per_quintal: parseFloat(transport) || 0,
        other_costs: parseFloat(other) || 0,
      });
      setResult(res);
    } catch (err) {
      setError(err.body?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-agri-earth">
        {t('market.title', language)}
      </h2>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded-lg">{error}</div>
      )}

      <form onSubmit={recommend} className="space-y-3 bg-white rounded-xl shadow p-4">
        <div>
          <label className="block text-xs text-gray-500 mb-1">Crop</label>
          <select
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
            value={crop}
            onChange={(e) => setCrop(e.target.value)}
          >
            <option value="wheat">Wheat</option>
            <option value="rice">Rice</option>
            <option value="maize">Maize</option>
            <option value="cotton">Cotton</option>
            <option value="groundnut">Groundnut</option>
          </select>
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">State</label>
          <input
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            value={state}
            onChange={(e) => setState(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">District</label>
          <input
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            value={district}
            onChange={(e) => setDistrict(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">
            {t('market.transportCost', language)} (₹/quintal)
          </label>
          <input
            type="number"
            step="0.1"
            min="0"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            value={transport}
            onChange={(e) => setTransport(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">
            Other costs (₹/quintal)
          </label>
          <input
            type="number"
            step="0.1"
            min="0"
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            value={other}
            onChange={(e) => setOther(e.target.value)}
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-agri-green text-white font-semibold py-3 rounded-lg disabled:opacity-50"
        >
          {loading ? t('common.loading', language) : t('market.recommend', language)}
        </button>
      </form>

      {result && (
        <div className="space-y-3">
          <p className="text-sm font-semibold text-agri-earth">
            {t('market.recommend', language)}
          </p>
          {result.map((r) => (
            <div key={r.rank} className="bg-white rounded-xl shadow p-4">
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-bold text-agri-earth">
                    #{r.rank} {r.market}
                  </p>
                  <p className="text-xs text-gray-500">
                    {t('market.modalPrice', language)}: {r.modal_price_per_quintal}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-lg font-bold text-agri-green">
                    ₹{r.estimated_net_price.toFixed(2)}
                  </p>
                  <p className="text-xs text-gray-500">{t('market.estimatedNet', language)}</p>
                </div>
              </div>
              <div className="grid grid-cols-3 gap-2 mt-3 text-center">
                <div>
                  <p className="text-xs text-gray-400">{t('market.mspReference', language)}</p>
                  <p className="text-sm font-semibold">₹{r.msp_reference_per_quintal.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">{t('market.transportCost', language)}</p>
                  <p className="text-sm font-semibold">₹{r.estimated_transport_cost.toFixed(2)}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-400">{t('market.distance', language)}</p>
                  <p className="text-sm font-semibold">{r.distance_km ?? '—'}</p>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">{r.explanation}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}