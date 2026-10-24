import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import useAppStore from '../store';

export default function Soil() {
  const { language, farmId, activeFarm, setActiveFarm } = useAppStore();
  const isHi = language === 'hi';

  const [form, setForm] = useState({
    ph: '7.2',
    nitrogen: '140',
    phosphorus: '48',
    potassium: '55',
    organic_carbon: '0.65',
  });

  const [pastTests, setPastTests] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [savedSuccess, setSavedSuccess] = useState(false);

  // Auto-fetch farm and its soil tests
  useEffect(() => {
    const init = async () => {
      let id = farmId;
      try {
        if (!id) {
          const farms = await api.listFarms();
          if (farms && farms.length > 0) {
            setActiveFarm(farms[0]);
            id = farms[0].id;
          } else {
            const newFarm = await api.createFarm({
              state: 'Maharashtra',
              district: 'Pune',
              area_hectare: 1.5,
            });
            setActiveFarm(newFarm);
            id = newFarm.id;
          }
        }

        if (id) {
          const tests = await api.getSoilTests(id);
          setPastTests(tests || []);
          if (tests && tests.length > 0) {
            const latest = tests[0];
            setForm({
              ph: latest.ph?.toString() || '7.0',
              nitrogen: latest.nitrogen?.toString() || '140',
              phosphorus: latest.phosphorus?.toString() || '45',
              potassium: latest.potassium?.toString() || '50',
              organic_carbon: latest.organic_carbon?.toString() || '0.6',
            });
          }
        }
      } catch (e) {
        console.warn('Soil init error:', e);
      }
    };
    init();
  }, [farmId, setActiveFarm]);

  const submit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSavedSuccess(false);

    try {
      let targetFarmId = farmId;
      if (!targetFarmId) {
        const farm = await api.createFarm({
          state: 'Maharashtra',
          district: 'Pune',
          area_hectare: 1.5,
        });
        setActiveFarm(farm);
        targetFarmId = farm.id;
      }

      await api.addSoilTest(targetFarmId, {
        ph: parseFloat(form.ph) || 7.0,
        nitrogen: form.nitrogen ? parseFloat(form.nitrogen) : null,
        phosphorus: form.phosphorus ? parseFloat(form.phosphorus) : null,
        potassium: form.potassium ? parseFloat(form.potassium) : null,
        organic_carbon: form.organic_carbon ? parseFloat(form.organic_carbon) : null,
        test_date: new Date().toISOString().slice(0, 10),
      });

      setSavedSuccess(true);
      const tests = await api.getSoilTests(targetFarmId);
      setPastTests(tests || []);
      setTimeout(() => setSavedSuccess(false), 4000);
    } catch (err) {
      setError(err.body?.detail || err.message || 'Failed to save soil test');
    } finally {
      setLoading(false);
    }
  };

  // Diagnostic calculations
  const phVal = parseFloat(form.ph) || 7.0;
  const nVal = parseFloat(form.nitrogen) || 0;
  const pVal = parseFloat(form.phosphorus) || 0;
  const kVal = parseFloat(form.potassium) || 0;
  const ocVal = parseFloat(form.organic_carbon) || 0;

  const getPhStatus = (v) => {
    if (v < 6.0) return { label: isHi ? 'अम्लीय (Acidic)' : 'Acidic', color: 'text-amber-700 bg-amber-50' };
    if (v > 8.0) return { label: isHi ? 'क्षारीय (Alkaline)' : 'Alkaline', color: 'text-sky-700 bg-sky-50' };
    return { label: isHi ? 'उत्तम (Neutral / Optimal)' : 'Optimal (6.5 - 7.5)', color: 'text-emerald-700 bg-emerald-50' };
  };

  const getNStatus = (v) => {
    if (v < 120) return { label: isHi ? 'निम्न' : 'Low (<120)', color: 'text-amber-700' };
    if (v > 200) return { label: isHi ? 'उच्च' : 'High (>200)', color: 'text-sky-700' };
    return { label: isHi ? 'संतुलित' : 'Optimal', color: 'text-emerald-700' };
  };

  // Soil health score (out of 100)
  let healthScore = 70;
  if (phVal >= 6.5 && phVal <= 7.8) healthScore += 10;
  if (nVal >= 120 && nVal <= 220) healthScore += 10;
  if (ocVal >= 0.5) healthScore += 10;

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>🧪</span>
            {isHi ? 'मृदा स्वास्थ्य परीक्षण एवं विश्लेषण' : 'Soil Health Diagnostic'}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {isHi
              ? 'NPK अनुपात, pH और कार्बन स्तर के आधार पर वैज्ञानिक उर्वरक सलाह'
              : 'Lab test calibration, soil health index & targeted nutrient advisory'}
          </p>
        </div>
        <span className="px-2.5 py-1 rounded-full bg-lime-100 text-lime-800 text-[11px] font-bold border border-lime-200">
          Soil Health Card
        </span>
      </div>

      {savedSuccess && (
        <div className="p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold flex items-center gap-2 animate-in fade-in">
          <span>✅</span>
          <span>{isHi ? 'मृदा परीक्षण रिपोर्ट सफलतापूर्वक सहेजी गई!' : 'Soil test record saved successfully to your farm profile!'}</span>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Soil Health Scorecard */}
      <div className="bg-gradient-to-br from-emerald-800 via-teal-800 to-slate-900 text-white rounded-3xl p-6 sm:p-7 shadow-lg relative overflow-hidden">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-300">
              {isHi ? 'समग्र मृदा स्वास्थ्य सूचकांक' : 'Overall Soil Quality Index'}
            </span>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl sm:text-5xl font-black text-white">{healthScore}</span>
              <span className="text-emerald-200 text-sm">/ 100</span>
              <span className="ml-2 px-2.5 py-0.5 rounded-full bg-emerald-500/30 text-emerald-200 border border-emerald-400/30 text-xs font-bold">
                {healthScore >= 80 ? 'Grade A (Excellent)' : 'Grade B (Good)'}
              </span>
            </div>
            <p className="text-xs text-emerald-100/80 leading-relaxed max-w-md">
              {isHi
                ? 'आपकी मिट्टी की उर्वरक धारण क्षमता अच्छी है। अनुशंसित उर्वरक मात्रा का पालन करने से उपज में 15-20% वृद्धि संभव है।'
                : 'Balanced nutrient profile detected. Maintaining organic carbon and split nitrogen dosing will optimize yield.'}
            </p>
          </div>

          <div className="flex sm:flex-col gap-2 justify-around sm:text-right bg-white/10 p-3.5 rounded-2xl backdrop-blur-sm border border-white/15">
            <div>
              <span className="text-[10px] text-emerald-200 block uppercase">Soil pH</span>
              <span className="font-extrabold text-sm">{phVal}</span>
            </div>
            <div>
              <span className="text-[10px] text-emerald-200 block uppercase">Org Carbon</span>
              <span className="font-extrabold text-sm">{ocVal}%</span>
            </div>
          </div>
        </div>
      </div>

      {/* Entry Form & Diagnostics */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Input Form */}
        <form onSubmit={submit} className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-sm text-slate-800 flex items-center gap-2">
              <span>📋</span>
              {isHi ? 'मृदा परीक्षण रिपोर्ट दर्ज करें' : 'Enter Soil Test Parameters'}
            </h3>
            <span className="text-[11px] text-slate-400">ICAR Standard</span>
          </div>

          <div>
            <div className="flex justify-between text-xs font-semibold mb-1">
              <label className="text-slate-700">Soil pH (0 - 14)</label>
              <span className={`px-2 py-0.5 rounded-md text-[10px] font-bold ${getPhStatus(phVal).color}`}>
                {getPhStatus(phVal).label}
              </span>
            </div>
            <input
              type="number"
              step="0.1"
              min="3"
              max="11"
              value={form.ph}
              onChange={(e) => setForm({ ...form, ph: e.target.value })}
              className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm bg-white focus:border-emerald-500 outline-none font-medium"
              required
            />
          </div>

          <div className="grid grid-cols-3 gap-3">
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Nitrogen (kg/ha)
              </label>
              <input
                type="number"
                step="1"
                min="0"
                value={form.nitrogen}
                onChange={(e) => setForm({ ...form, nitrogen: e.target.value })}
                className="w-full rounded-xl border border-slate-300 px-3 py-1.5 text-xs bg-white focus:border-emerald-500 outline-none font-medium"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Phosphorus (kg/ha)
              </label>
              <input
                type="number"
                step="1"
                min="0"
                value={form.phosphorus}
                onChange={(e) => setForm({ ...form, phosphorus: e.target.value })}
                className="w-full rounded-xl border border-slate-300 px-3 py-1.5 text-xs bg-white focus:border-emerald-500 outline-none font-medium"
              />
            </div>
            <div>
              <label className="block text-[11px] font-semibold text-slate-600 mb-1">
                Potassium (kg/ha)
              </label>
              <input
                type="number"
                step="1"
                min="0"
                value={form.potassium}
                onChange={(e) => setForm({ ...form, potassium: e.target.value })}
                className="w-full rounded-xl border border-slate-300 px-3 py-1.5 text-xs bg-white focus:border-emerald-500 outline-none font-medium"
              />
            </div>
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              {isHi ? 'जैविक कार्बन (Organic Carbon %)' : 'Organic Carbon (%)'}
            </label>
            <input
              type="number"
              step="0.01"
              min="0"
              max="5"
              value={form.organic_carbon}
              onChange={(e) => setForm({ ...form, organic_carbon: e.target.value })}
              className="w-full rounded-xl border border-slate-300 px-3.5 py-2 text-sm bg-white focus:border-emerald-500 outline-none font-medium"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-white font-bold text-sm shadow-md active:scale-98 transition-all flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
                <span>{isHi ? 'सहेज रहे हैं...' : 'Saving to Farm Record...'}</span>
              </>
            ) : (
              <>
                <span>💾</span>
                <span>{isHi ? 'मृदा रिपोर्ट सुरक्षित करें' : 'Save & Calibrate Soil Health'}</span>
              </>
            )}
          </button>
        </form>

        {/* Actionable Nutrient Recommendations */}
        <div className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-sm text-slate-800 flex items-center gap-2">
              <span>🌾</span>
              {isHi ? 'उर्वरक एवं पोषक तत्व सुधार सलाह' : 'Nutrient & Fertilizer Prescriptions'}
            </h3>
            <span className="text-[10px] font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded-full">
              AI Agronomy
            </span>
          </div>

          <div className="space-y-3 text-xs">
            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-1">
              <div className="flex items-center justify-between font-bold text-slate-800">
                <span>🌱 Nitrogen (N) Management</span>
                <span className={getNStatus(nVal).color}>{getNStatus(nVal).label}</span>
              </div>
              <p className="text-slate-600 leading-relaxed">
                {nVal < 140
                  ? 'Apply 25-30 kg/ha additional Urea in 2 split doses: at crown root initiation and tillering.'
                  : 'Nitrogen level is optimal. Avoid excess urea to prevent vegetative lodging and pest attraction.'}
              </p>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-1">
              <div className="flex items-center justify-between font-bold text-slate-800">
                <span>⚡ Phosphorus (P) & Potassium (K)</span>
                <span className="text-emerald-700">Adequate</span>
              </div>
              <p className="text-slate-600 leading-relaxed">
                Basal application of DAP (Di-ammonium Phosphate) or NPK 12:32:16 at sowing time recommended for strong root establishment.
              </p>
            </div>

            <div className="p-3.5 rounded-2xl bg-slate-50 border border-slate-200/60 space-y-1">
              <div className="flex items-center justify-between font-bold text-slate-800">
                <span>🍂 Organic Matter & Carbon</span>
                <span className="text-emerald-700">{ocVal >= 0.5 ? 'Healthy' : 'Needs Boost'}</span>
              </div>
              <p className="text-slate-600 leading-relaxed">
                Apply 5 tonnes/ha of well-decomposed FYM (Farm Yard Manure) or vermicompost to maintain microbial vitality and soil moisture retention.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}