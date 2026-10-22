import React, { useState } from 'react';
import { api } from '../services/api';
import useAppStore from '../store';
import { t } from '../i18n';

export default function Soil() {
  const { language, farmId } = useAppStore();
  const [form, setForm] = useState({
    ph: '', nitrogen: '', phosphorus: '', potassium: '', organic_carbon: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [saved, setSaved] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    if (!farmId) return;
    setLoading(true);
    setError(null);
    try {
      await api.addSoilTest(farmId, {
        ...form,
        ph: parseFloat(form.ph),
        nitrogen: form.nitrogen ? parseFloat(form.nitrogen) : null,
        phosphorus: form.phosphorus ? parseFloat(form.phosphorus) : null,
        potassium: form.potassium ? parseFloat(form.potassium) : null,
        organic_carbon: form.organic_carbon ? parseFloat(form.organic_carbon) : null,
        test_date: new Date().toISOString().slice(0, 10),
      });
      setSaved(true);
    } catch (err) {
      setError(err.body?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const Field = ({ label, key, hint, min, max }) => (
    <div>
      <label className="block text-xs text-gray-500 mb-1">
        {label} {hint && <span className="text-gray-400">({hint})</span>}
      </label>
      <input
        type="number"
        step="0.1"
        min={min}
        max={max}
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
        value={form[key]}
        onChange={(e) => setForm({ ...form, [key]: e.target.value })}
      />
    </div>
  );

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-agri-earth">
        {t('nav.myFarm', language)} — Soil Information
      </h2>

      {saved && (
        <div className="bg-green-50 text-agri-green text-sm p-3 rounded-lg">
          Soil test saved.
        </div>
      )}
      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded-lg">{error}</div>
      )}

      <form onSubmit={submit} className="space-y-3">
        <Field label="Soil pH" key="ph" hint="0–14" min={0} max={14} />
        <Field label="Nitrogen (kg/ha)" key="nitrogen" min={0} />
        <Field label="Phosphorus (kg/ha)" key="phosphorus" min={0} />
        <Field label="Potassium (kg/ha)" key="potassium" min={0} />
        <Field label="Organic Carbon (%)" key="organic_carbon" hint="≥0" min={0} />

        <button
          type="submit"
          disabled={loading || !farmId}
          className="w-full bg-agri-green text-white font-semibold py-3 rounded-lg disabled:opacity-50"
        >
          {loading ? t('common.loading', language) : t('common.save', language)}
        </button>
      </form>
    </div>
  );
}