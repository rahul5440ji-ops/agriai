import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import useAppStore from '../store';
import AreaInput from '../components/AreaInput';
import LocationDropdown from '../components/LocationDropdown';

export default function MyFarm() {
  const { language, farmId, setFarmId, setActiveFarm } = useAppStore();
  const isHi = language === 'hi';

  const [farms, setFarms] = useState([]);
  const [activeFarmData, setActiveFarmData] = useState(null);
  const [isCreatingNew, setIsCreatingNew] = useState(false);

  const [form, setForm] = useState({
    state: 'Maharashtra',
    district: 'Pune',
    village: '',
    pincode: '',
    area_hectare: '1.5',
    soil_type: 'black',
    irrigation_type: 'canal',
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Load all farms
  const loadFarms = async () => {
    try {
      const data = await api.listFarms();
      setFarms(data || []);
      if (data && data.length > 0) {
        const current = farmId ? data.find((f) => f.id === farmId) || data[0] : data[0];
        setActiveFarmData(current);
        setFarmId(current.id);
        setActiveFarm(current);
      } else {
        setIsCreatingNew(true);
      }
    } catch (e) {
      console.warn('Failed to load farms', e);
    }
  };

  useEffect(() => {
    loadFarms();
  }, [farmId]);

  const submit = async (e) => {
    e.preventDefault();
    if (form.pincode && !/^\d{6}$/.test(form.pincode)) {
      setError(isHi ? 'पिनकोड 6 अंकों का होना चाहिए।' : 'Pincode must be a 6-digit number.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const res = await api.createFarm({
        state: form.state,
        district: form.district,
        village: form.village,
        area_hectare: parseFloat(form.area_hectare) || 1.0,
        soil_type: form.soil_type || 'black',
        irrigation_type: form.irrigation_type || 'canal',
      });

      setFarmId(res.id);
      setActiveFarm(res);
      setActiveFarmData(res);
      setIsCreatingNew(false);
      await loadFarms();
    } catch (err) {
      setError(err.body?.detail || err.message || 'Failed to create farm');
    } finally {
      setLoading(false);
    }
  };

  const getIrrigationIcon = (type) => {
    switch (type) {
      case 'drip': return '💧 Drip Irrigation';
      case 'canal': return '🌊 Canal Water';
      case 'tube_well': return '⚡ Tube Well';
      case 'rainfed': return '🌧️ Rainfed';
      default: return '💦 Standard Irrigation';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>🌾</span>
            {isHi ? 'मेरा खेत प्रोफाइल' : 'My Farm Profile'}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {isHi
              ? 'खेत का क्षेत्रफल, मृदा प्रकार, सिंचाई साधन और क्षेत्रीय विवरण'
              : 'Plot area, geographic location, soil classification, and irrigation source'}
          </p>
        </div>

        {farms.length > 0 && !isCreatingNew && (
          <button
            onClick={() => setIsCreatingNew(true)}
            className="px-3.5 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition-all flex items-center gap-1.5"
          >
            <span>+</span>
            <span>{isHi ? 'नया खेत जोड़ें' : 'Add New Farm'}</span>
          </button>
        )}
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {/* Active Farm Display Card */}
      {!isCreatingNew && activeFarmData ? (
        <div className="space-y-5 animate-in fade-in duration-200">
          <div className="rounded-3xl bg-gradient-to-br from-emerald-800 via-emerald-900 to-teal-950 text-white p-6 sm:p-7 shadow-xl relative overflow-hidden">
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div>
                <div className="flex items-center gap-2 mb-2">
                  <span className="px-2.5 py-0.5 rounded-full bg-emerald-500/30 text-emerald-200 border border-emerald-400/30 text-xs font-mono font-bold">
                    Farm ID #{activeFarmData.id}
                  </span>
                  <span className="text-xs text-emerald-200">Active Profile</span>
                </div>
                <h2 className="text-2xl font-black text-white tracking-tight">
                  {activeFarmData.district}, {activeFarmData.state}
                </h2>
                {activeFarmData.village && (
                  <p className="text-xs text-emerald-100/90 mt-0.5">
                    📍 Village: {activeFarmData.village}
                  </p>
                )}
              </div>

              <div className="bg-white/10 backdrop-blur-md p-4 rounded-2xl border border-white/15 text-left sm:text-right">
                <span className="text-[11px] font-bold uppercase tracking-wider text-emerald-200 block">
                  {isHi ? 'कुल भूमि क्षेत्र' : 'Total Field Area'}
                </span>
                <span className="text-3xl font-black text-white">
                  {activeFarmData.area_hectare}
                </span>
                <span className="text-xs text-emerald-100 font-medium"> ha</span>
                <p className="text-[11px] text-emerald-200/80 mt-0.5">
                  ≈ {(activeFarmData.area_hectare * 2.471).toFixed(2)} Acres
                </p>
              </div>
            </div>

            {/* Farm attributes */}
            <div className="mt-6 pt-4 border-t border-emerald-700/60 grid grid-cols-2 sm:grid-cols-3 gap-3 text-xs">
              <div className="bg-emerald-950/40 p-2.5 rounded-xl border border-emerald-700/30">
                <span className="text-emerald-300/80 text-[10px] uppercase block">
                  {isHi ? 'मृदा प्रकार' : 'Soil Classification'}
                </span>
                <span className="font-bold text-white capitalize">
                  {activeFarmData.soil_type || 'Black Soil (काली मिट्टी)'}
                </span>
              </div>

              <div className="bg-emerald-950/40 p-2.5 rounded-xl border border-emerald-700/30">
                <span className="text-emerald-300/80 text-[10px] uppercase block">
                  {isHi ? 'सिंचाई स्रोत' : 'Irrigation Method'}
                </span>
                <span className="font-bold text-white">
                  {getIrrigationIcon(activeFarmData.irrigation_type)}
                </span>
              </div>

              <div className="bg-emerald-950/40 p-2.5 rounded-xl border border-emerald-700/30 col-span-2 sm:col-span-1">
                <span className="text-emerald-300/80 text-[10px] uppercase block">
                  {isHi ? 'पंजीकरण दिनांक' : 'Registered On'}
                </span>
                <span className="font-bold text-white">
                  {activeFarmData.created_at ? new Date(activeFarmData.created_at).toLocaleDateString() : 'Recent'}
                </span>
              </div>
            </div>
          </div>

          {/* Quick Shortcuts */}
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <Link
              to="/yield"
              className="p-4 rounded-2xl bg-white border border-slate-200/80 hover:border-emerald-400 shadow-sm hover:shadow-md transition-all flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center text-xl font-bold">
                  📊
                </div>
                <div>
                  <h4 className="font-bold text-sm text-slate-800">
                    {isHi ? 'उपज का अनुमान लगाएं' : 'Predict Yield for this Farm'}
                  </h4>
                  <p className="text-[11px] text-slate-500">
                    {isHi ? 'फसल चयन कर उपज देखें' : 'Run ML model for your crop & soil'}
                  </p>
                </div>
              </div>
              <span className="text-emerald-700 font-bold">→</span>
            </Link>

            <Link
              to="/soil"
              className="p-4 rounded-2xl bg-white border border-slate-200/80 hover:border-lime-400 shadow-sm hover:shadow-md transition-all flex items-center justify-between"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-lime-100 text-lime-800 flex items-center justify-center text-xl font-bold">
                  🧪
                </div>
                <div>
                  <h4 className="font-bold text-sm text-slate-800">
                    {isHi ? 'मृदा स्वास्थ्य जांचें' : 'Check Soil Health Card'}
                  </h4>
                  <p className="text-[11px] text-slate-500">
                    {isHi ? 'NPK एवं pH मान अद्यतित करें' : 'Record NPK & get fertilizer dosage'}
                  </p>
                </div>
              </div>
              <span className="text-lime-700 font-bold">→</span>
            </Link>
          </div>

          {/* Farm Switcher if multiple */}
          {farms.length > 1 && (
            <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-wide mb-2.5">
                {isHi ? 'आपके अन्य पंजीकृत खेत' : 'Switch Farm Profile'}
              </h4>
              <div className="flex flex-wrap gap-2">
                {farms.map((f) => (
                  <button
                    key={f.id}
                    onClick={() => {
                      setFarmId(f.id);
                      setActiveFarm(f);
                      setActiveFarmData(f);
                    }}
                    className={`px-3 py-1.5 rounded-xl text-xs font-semibold transition-all ${
                      f.id === activeFarmData.id
                        ? 'bg-emerald-600 text-white shadow-sm'
                        : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
                    }`}
                  >
                    #{f.id} {f.district} ({f.area_hectare} ha)
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Create New Farm Form */
        <form onSubmit={submit} className="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-sm space-y-4">
          <div className="flex items-center justify-between border-b border-slate-100 pb-3">
            <h3 className="font-bold text-sm text-slate-800 flex items-center gap-2">
              <span>🌾</span>
              {isHi ? 'नए खेत का विवरण दर्ज करें' : 'Register Farm Profile'}
            </h3>
            {farms.length > 0 && (
              <button
                type="button"
                onClick={() => setIsCreatingNew(false)}
                className="text-xs text-slate-500 hover:text-slate-700 underline"
              >
                {isHi ? 'रद्द करें' : 'Cancel'}
              </button>
            )}
          </div>

          <LocationDropdown
            state={form.state}
            city={form.district}
            onStateChange={(s) => setForm((prev) => ({ ...prev, state: s, district: '' }))}
            onCityChange={(c) => setForm((prev) => ({ ...prev, district: c }))}
            label={isHi ? 'राज्य एवं जिला' : 'State & District'}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                {isHi ? 'गांव का नाम (वैकल्पिक)' : 'Village Name (Optional)'}
              </label>
              <input
                className="w-full border border-slate-300 rounded-xl px-3.5 py-2 text-sm bg-white focus:border-emerald-500 outline-none"
                value={form.village}
                onChange={(e) => setForm({ ...form, village: e.target.value })}
                placeholder="e.g. Haveli, Baramati"
              />
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                {isHi ? 'पिनकोड' : 'Pincode'}
              </label>
              <input
                type="text"
                inputMode="numeric"
                maxLength={6}
                className="w-full border border-slate-300 rounded-xl px-3.5 py-2 text-sm bg-white focus:border-emerald-500 outline-none"
                value={form.pincode}
                onChange={(e) => setForm({ ...form, pincode: e.target.value.replace(/\D/g, '') })}
                placeholder="6-digit pincode"
              />
            </div>
          </div>

          <AreaInput
            onChange={(val) => setForm((prev) => ({ ...prev, area_hectare: val }))}
            required
            label={isHi ? 'खेत का क्षेत्रफल' : 'Field Land Area'}
          />

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                {isHi ? 'मिट्टी का प्रकार' : 'Soil Classification'}
              </label>
              <select
                className="w-full border border-slate-300 rounded-xl px-3.5 py-2 text-sm bg-white focus:border-emerald-500 outline-none"
                value={form.soil_type}
                onChange={(e) => setForm({ ...form, soil_type: e.target.value })}
              >
                <option value="black">Black Soil (काली मिट्टी)</option>
                <option value="alluvial">Alluvial (जलोढ़ मिट्टी)</option>
                <option value="red">Red Soil (लाल मिट्टी)</option>
                <option value="laterite">Laterite (लैटेराइट)</option>
                <option value="sandy">Sandy Loam (बलुई दोमट)</option>
                <option value="clay">Clay Loam (मटियार दोमट)</option>
              </select>
            </div>

            <div>
              <label className="block text-xs font-bold text-slate-700 mb-1">
                {isHi ? 'सिंचाई व्यवस्था' : 'Irrigation Facility'}
              </label>
              <select
                className="w-full border border-slate-300 rounded-xl px-3.5 py-2 text-sm bg-white focus:border-emerald-500 outline-none"
                value={form.irrigation_type}
                onChange={(e) => setForm({ ...form, irrigation_type: e.target.value })}
              >
                <option value="canal">Canal (नहर जल)</option>
                <option value="tube_well">Tube Well / Borewell (नलकूप)</option>
                <option value="drip">Drip / Micro-irrigation (टपक सिंचाई)</option>
                <option value="rainfed">Rainfed (वर्षा आधारित)</option>
              </select>
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-white font-bold text-sm shadow-md active:scale-98 transition-all flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <span className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
                <span>{isHi ? 'सहेज रहे हैं...' : 'Saving Farm Profile...'}</span>
              </>
            ) : (
              <>
                <span>🌾</span>
                <span>{isHi ? 'खेत का प्रोफाइल सहेजें' : 'Save Farm Profile'}</span>
              </>
            )}
          </button>
        </form>
      )}
    </div>
  );
}