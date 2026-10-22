import React, { useState } from 'react';
import { api } from '../services/api';
import { t } from '../i18n';
import useAppStore from '../store';

export default function PriceForecast() {
  const { language } = useAppStore();
  const [crop, setCrop] = useState('wheat');
  const [market, setMarket] = useState('Pune');
  const [horizon, setHorizon] = useState(7);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const forecast = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.priceForecast({
        commodity: crop,
        market,
        horizon_days: horizon,
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
        Price Forecast
      </h2>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded-lg">{error}</div>
      )}

      <form onSubmit={forecast} className="space-y-3 bg-white rounded-xl shadow p-4">
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
          <label className="block text-xs text-gray-500 mb-1">Market</label>
          <input
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            value={market}
            onChange={(e) => setMarket(e.target.value)}
          />
        </div>
        <div>
          <label className="block text-xs text-gray-500 mb-1">Horizon (days)</label>
          <input
            type="number"
            min={1}
            max={30}
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            value={horizon}
            onChange={(e) => setHorizon(parseInt(e.target.value, 10))}
          />
        </div>
        <button
          type="submit"
          disabled={loading}
          className="w-full bg-agri-green text-white font-semibold py-3 rounded-lg disabled:opacity-50"
        >
          {loading ? t('common.loading', language) : 'Forecast Price'}
        </button>
      </form>

      {result && (
        <div className="bg-white rounded-xl shadow p-4">
          {result.available ? (
            <>
              <p className="text-xs text-gray-500 uppercase tracking-wide">
                Forecast Range
              </p>
              <p className="text-2xl font-bold text-agri-earth mt-1">
                ₹{result.forecast_lower} – ₹{result.forecast_upper}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {t('common.rupees', language)} {t('common.perQuintal', language)}
              </p>
              <p className="text-sm text-gray-600 mt-2">
                Expected midpoint: ₹{result.expected_midpoint}
              </p>
              <p className="text-xs text-gray-400 mt-1">
                Horizon: {result.forecast_horizon_days} {t('common.days', language)}
              </p>
              {result.confidence_note && (
                <p className="text-xs text-gray-400 mt-2">
                  {result.confidence_note}
                </p>
              )}
            </>
          ) : (
            <p className="text-sm text-amber-700">
              {t('market.insufficient', language)}
            </p>
          )}
        </div>
      )}
    </div>
  );
}