import React, { useState } from 'react';
import { api } from '../services/api';
import { t } from '../i18n';
import useAppStore from '../store';

export default function MarketComparison() {
  const { language } = useAppStore();
  const [crop, setCrop] = useState('wheat');
  const [state, setState] = useState('Maharashtra');
  const [district, setDistrict] = useState('Pune');
  const [transport, setTransport] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const compare = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.compareMarkets({
        crop,
        state,
        district,
        transport_cost: parseFloat(transport) || 0,
        other_costs: 0,
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

      <form onSubmit={compare} className="space-y-3 bg-white rounded-xl shadow p-4">
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
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-agri-green text-white font-semibold py-3 rounded-lg disabled:opacity-50"
        >
          {loading ? t('common.loading', language) : t('market.compare', language)}
        </button>
      </form>

      {result && (
        <div className="bg-white rounded-xl shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="bg-gray-50 text-gray-500 text-xs uppercase">
                <tr>
                  <th className="px-3 py-2 text-left">{t('market.market', language)}</th>
                  <th className="px-3 py-2 text-right">{t('market.modalPrice', language)}</th>
                  <th className="px-3 py-2 text-right">{t('market.mspReference', language)}</th>
                  <th className="px-3 py-2 text-right">{t('market.estimatedNet', language)}</th>
                  <th className="px-3 py-2 text-right">{t('market.dataDate', language)}</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {result.map((r, i) => (
                  <tr key={i}>
                    <td className="px-3 py-2 font-medium text-agri-earth">
                      {r.market}
                      {r.data_freshness_days > 30 && (
                        <span className="ml-1 text-xs text-red-500">
                          ({t('market.stale', language)})
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-right">₹{r.modal_price_per_quintal}</td>
                    <td className="px-3 py-2 text-right">₹{r.msp_reference_per_quintal}</td>
                    <td className="px-3 py-2 text-right font-semibold text-agri-green">
                      ₹{r.estimated_net_price}
                    </td>
                    <td className="px-3 py-2 text-right text-gray-500">
                      {r.data_freshness_days} {t('common.days', language)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}