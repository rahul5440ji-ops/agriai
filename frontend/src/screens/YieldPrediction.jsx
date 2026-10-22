import React, { useState } from 'react';
import { api } from '../services/api';
import useAppStore from '../store';
import { t } from '../i18n';

export default function YieldPrediction() {
  const { language, farmId } = useAppStore();
  const [crop, setCrop] = useState('wheat');
  const [season, setSeason] = useState('rabi');
  const [area, setArea] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const predict = async (e) => {
    e.preventDefault();
    if (!farmId) return;
    setLoading(true);
    setError(null);
    try {
      const res = await api.predictYield({
        farm_id: farmId,
        crop,
        season,
        area_hectare: parseFloat(area),
        soil: {
          ph: 7.0,
          test_date: new Date().toISOString().slice(0, 10),
        },
        sowing_date: new Date().toISOString().slice(0, 10),
      });
      setResult(res);
    } catch (err) {
      setError(err.body?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  if (result) {
    return (
      <div className="space-y-4">
        <h2 className="text-lg font-semibold text-agri-earth">
          {t('yield.title', language)}
        </h2>

        <div className="bg-gradient-to-br from-agri-green to-agri-leaf text-white rounded-xl shadow p-6">
          <p className="text-xs uppercase tracking-wide opacity-80">
            {t('yield.title', language)}
          </p>
          <p className="text-4xl font-bold mt-2">
            {result.predicted_yield_tph.toFixed(2)}
            <span className="text-base font-normal ml-1">{t('common.perHectare', language)}</span>
          </p>
          <p className="text-sm opacity-80 mt-1">
            {t('yield.range', language)}: {result.lower_bound_tph.toFixed(2)} – {result.upper_bound_tph.toFixed(2)}
          </p>
        </div>

        <div className="bg-white rounded-xl shadow p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">
            {t('yield.production', language)}
          </p>
          <p className="text-2xl font-bold text-agri-earth mt-1">
            {result.total_production_t.toFixed(2)} {t('common.tonnes', language)}
          </p>
        </div>

        {result.top_factors?.length > 0 && (
          <div className="bg-white rounded-xl shadow p-4">
            <p className="font-semibold text-agri-earth mb-2">
              {t('yield.factors', language)}
            </p>
            <div className="space-y-2">
              {result.top_factors.map((f, i) => (
                <div key={i} className="text-sm text-gray-700">
                  {f}
                </div>
              ))}
            </div>
          </div>
        )}

        <p className="text-xs text-gray-400 leading-relaxed">
          {t('yield.disclaimer', language)}
        </p>

        <button
          onClick={() => setResult(null)}
          className="w-full bg-gray-100 text-gray-700 font-semibold py-3 rounded-lg"
        >
          {t('common.back', language)}
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={predict} className="space-y-4">
      <h2 className="text-lg font-semibold text-agri-earth">
        {t('yield.title', language)}
      </h2>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded-lg">{error}</div>
      )}
      {!farmId && (
        <div className="bg-amber-50 text-amber-700 text-sm p-3 rounded-lg">
          Create a farm first from My Farm.
        </div>
      )}

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
          <option value="sugarcane">Sugarcane</option>
          <option value="cotton">Cotton</option>
          <option value="pulses">Pulses</option>
          <option value="groundnut">Groundnut</option>
          <option value="mustard">Mustard</option>
          <option value="potato">Potato</option>
          <option value="tomato">Tomato</option>
        </select>
      </div>

      <div>
        <label className="block text-xs text-gray-500 mb-1">Season</label>
        <select
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
          value={season}
          onChange={(e) => setSeason(e.target.value)}
        >
          <option value="kharif">Kharif</option>
          <option value="rabi">Rabi</option>
          <option value="zaid">Zaid</option>
        </select>
      </div>

      <div>
        <label className="block text-xs text-gray-500 mb-1">Field Area (hectare)</label>
        <input
          type="number"
          step="0.01"
          min="0.01"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          value={area}
          onChange={(e) => setArea(e.target.value)}
          required
        />
      </div>

      <button
        type="submit"
        disabled={loading || !farmId}
        className="w-full bg-agri-green text-white font-semibold py-3 rounded-lg disabled:opacity-50"
      >
        {loading ? t('common.loading', language) : 'Predict Yield'}
      </button>
    </form>
  );
}