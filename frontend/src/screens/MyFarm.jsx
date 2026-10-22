import React, { useState } from 'react';
import { api } from '../services/api';
import useAppStore from '../store';
import { t } from '../i18n';

export default function MyFarm() {
  const { language, farmId, setFarmId } = useAppStore();
  const [form, setForm] = useState({
    state: 'Maharashtra',
    district: 'Pune',
    village: '',
    area_hectare: '',
    soil_type: '',
    irrigation_type: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.createFarm({
        ...form,
        area_hectare: parseFloat(form.area_hectare),
      });
      setFarmId(res.id);
    } catch (err) {
      setError(err.body?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  if (farmId) {
    return (
      <div className="space-y-4">
        <div className="bg-white rounded-xl shadow p-4">
          <p className="text-xs text-gray-500 uppercase tracking-wide">Farm ID</p>
          <p className="font-bold text-agri-earth">#{farmId}</p>
          <p className="text-sm text-gray-600 mt-2">
            {form.state}, {form.district} · {form.area_hectare} ha
          </p>
        </div>
        <button
          onClick={() => setFarmId(null)}
          className="text-agri-green font-medium text-sm"
        >
          Create another farm
        </button>
      </div>
    );
  }

  return (
    <form onSubmit={submit} className="space-y-3">
      <h2 className="text-lg font-semibold text-agri-earth">
        {t('nav.myFarm', language)}
      </h2>

      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded-lg">
          {error}
        </div>
      )}

      {[
        { label: 'State', key: 'state' },
        { label: 'District', key: 'district' },
        { label: 'Village', key: 'village' },
      ].map(({ label, key }) => (
        <div key={key}>
          <label className="block text-xs text-gray-500 mb-1">{label}</label>
          <input
            className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
            value={form[key]}
            onChange={(e) => setForm({ ...form, [key]: e.target.value })}
            required={key !== 'village'}
          />
        </div>
      ))}

      <div>
        <label className="block text-xs text-gray-500 mb-1">Field Area (hectare)</label>
        <input
          type="number"
          step="0.01"
          min="0.01"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
          value={form.area_hectare}
          onChange={(e) => setForm({ ...form, area_hectare: e.target.value })}
          required
        />
      </div>

      <div>
        <label className="block text-xs text-gray-500 mb-1">Soil Type</label>
        <select
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
          value={form.soil_type}
          onChange={(e) => setForm({ ...form, soil_type: e.target.value })}
        >
          <option value="">Select</option>
          <option value="alluvial">Alluvial</option>
          <option value="black">Black</option>
          <option value="red">Red</option>
          <option value="laterite">Laterite</option>
          <option value="sandy">Sandy</option>
          <option value="clay">Clay</option>
        </select>
      </div>

      <div>
        <label className="block text-xs text-gray-500 mb-1">Irrigation Type</label>
        <select
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white"
          value={form.irrigation_type}
          onChange={(e) => setForm({ ...form, irrigation_type: e.target.value })}
        >
          <option value="">Select</option>
          <option value="canal">Canal</option>
          <option value="tube_well">Tube Well</option>
          <option value="drip">Drip</option>
          <option value="rainfed">Rainfed</option>
        </select>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="w-full bg-agri-green text-white font-semibold py-3 rounded-lg disabled:opacity-50"
      >
        {loading ? t('common.loading', language) : t('common.save', language)}
      </button>
    </form>
  );
}