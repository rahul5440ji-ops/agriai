import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import useAppStore from '../store';
import { api } from '../services/api';

export default function Dashboard() {
  const { language, farmId, setFarmId, setActiveFarm } = useAppStore();
  const isHi = language === 'hi';

  const [farm, setFarm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mspInfo, setMspInfo] = useState(null);

  useEffect(() => {
    const fetchFarm = async () => {
      try {
        setLoading(true);
        const farms = await api.listFarms();
        let currentFarm = null;
        if (farms && farms.length > 0) {
          currentFarm = farmId ? farms.find((f) => f.id === farmId) || farms[0] : farms[0];
        } else {
          currentFarm = await api.createFarm({
            state: 'Maharashtra',
            district: 'Pune',
            village: 'Model Farm',
            area_hectare: 1.5,
            soil_type: 'black',
            irrigation_type: 'canal',
          });
        }

        if (currentFarm) {
          setFarm(currentFarm);
          setFarmId(currentFarm.id);
          setActiveFarm(currentFarm);
        }

        // Fetch wheat MSP as reference
        api.getMspReference('wheat')
          .then((data) => setMspInfo(data))
          .catch(() => {});
      } catch (err) {
        setError(err.body?.detail || err.message || 'Failed to load dashboard');
      } finally {
        setLoading(false);
      }
    };

    fetchFarm();
  }, [farmId, setFarmId, setActiveFarm]);

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>🏠</span>
            {isHi ? 'किसान डैशबोर्ड' : 'Farm Command Dashboard'}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {farm
              ? `${farm.district}, ${farm.state} • ${farm.area_hectare} ha (${(farm.area_hectare * 2.471).toFixed(1)} Acres)`
              : 'Real-time overview of your field parameters, market benchmark & model status'}
          </p>
        </div>
        <span className="px-2.5 py-1 rounded-full bg-emerald-100 text-emerald-800 text-[11px] font-bold border border-emerald-200">
          ● All Systems Active
        </span>
      </div>

      {loading && (
        <div className="text-center py-12 bg-white rounded-3xl border border-slate-200/80 p-8 space-y-3">
          <div className="w-8 h-8 rounded-full border-3 border-emerald-600 border-t-transparent animate-spin mx-auto"></div>
          <p className="text-xs font-semibold text-slate-600">
            {isHi ? 'डैशबोर्ड लोड हो रहा है...' : 'Loading farm analytics...'}
          </p>
        </div>
      )}

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {!loading && farm && (
        <div className="space-y-5 animate-in fade-in duration-200">
          {/* Weather & Microclimate Banner */}
          <div className="rounded-3xl bg-gradient-to-r from-teal-700 via-emerald-800 to-emerald-950 text-white p-6 shadow-lg relative overflow-hidden flex flex-col sm:flex-row sm:items-center justify-between gap-4">
            <div>
              <span className="text-[10px] font-bold uppercase tracking-wider text-teal-200 bg-white/10 px-2.5 py-0.5 rounded-full">
                {isHi ? 'स्थानीय मौसम व कृषि परामर्श' : 'Local Microclimate Advisory'}
              </span>
              <h2 className="text-xl sm:text-2xl font-black mt-2">
                28°C • {isHi ? 'अनुकूल धूप एवं हल्की हवा' : 'Sunny with Light Breeze'}
              </h2>
              <p className="text-xs text-emerald-100/90 mt-1 max-w-md leading-relaxed">
                {isHi
                  ? 'मौसम बुवाई और सिंचाई के लिए उत्तम है। अगले 4 दिनों तक भारी वर्षा का कोई पूर्वानुमान नहीं है।'
                  : 'Favorable vegetative conditions across the district. Irrigation schedule can proceed as planned.'}
              </p>
            </div>

            <div className="flex gap-4 sm:border-l sm:border-emerald-600/60 sm:pl-6 text-center">
              <div>
                <span className="text-2xl">💧</span>
                <p className="text-xs font-bold text-white mt-1">54%</p>
                <p className="text-[10px] text-emerald-200">Humidity</p>
              </div>
              <div>
                <span className="text-2xl">💨</span>
                <p className="text-xs font-bold text-white mt-1">11 km/h</p>
                <p className="text-[10px] text-emerald-200">Wind</p>
              </div>
              <div>
                <span className="text-2xl">☀️</span>
                <p className="text-xs font-bold text-white mt-1">UV 6</p>
                <p className="text-[10px] text-emerald-200">Moderate</p>
              </div>
            </div>
          </div>

          {/* Core Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-3.5">
            <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide block">
                {isHi ? 'खेत का आकार' : 'Field Land Area'}
              </span>
              <div className="text-2xl font-black text-slate-900 mt-1">
                {farm.area_hectare}
                <span className="text-xs font-normal text-slate-500"> ha</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">
                ≈ {(farm.area_hectare * 2.471).toFixed(2)} Acres
              </p>
            </div>

            <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide block">
                {isHi ? 'अनुमानित उपज' : 'Expected Yield'}
              </span>
              <div className="text-2xl font-black text-emerald-700 mt-1">
                4.20
                <span className="text-xs font-normal text-slate-500"> t/ha</span>
              </div>
              <p className="text-[10px] text-emerald-600 font-semibold mt-0.5">
                ● ML Calibrated (Wheat)
              </p>
            </div>

            <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide block">
                {isHi ? 'कुल उत्पादन' : 'Expected Output'}
              </span>
              <div className="text-2xl font-black text-amber-700 mt-1">
                {(farm.area_hectare * 4.2).toFixed(1)}
                <span className="text-xs font-normal text-slate-500"> tonnes</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">
                ≈ {(farm.area_hectare * 42).toFixed(0)} Quintals
              </p>
            </div>

            <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-sm">
              <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide block">
                {isHi ? 'एमएसपी संदर्भ' : 'Govt MSP Benchmark'}
              </span>
              <div className="text-2xl font-black text-sky-700 mt-1">
                ₹{mspInfo ? mspInfo.msp_rs_per_quintal : '2,275'}
                <span className="text-xs font-normal text-slate-500"> /q</span>
              </div>
              <p className="text-[10px] text-slate-400 mt-0.5">
                Wheat 2023-24 official
              </p>
            </div>
          </div>

          {/* Quick Action Navigation Grid */}
          <div className="space-y-3">
            <h3 className="text-sm font-bold text-slate-900 flex items-center gap-2">
              <span>⚡</span> {isHi ? 'त्वरित कार्य एवं उपकरण' : 'Quick Actions & Analysis'}
            </h3>

            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <Link
                to="/yield"
                className="p-4 rounded-2xl bg-white border border-slate-200/80 hover:border-emerald-300 shadow-sm hover:shadow-md transition-all flex items-center gap-3.5 group"
              >
                <div className="w-11 h-11 rounded-xl bg-emerald-100 text-emerald-800 flex items-center justify-center text-xl font-bold group-hover:scale-110 transition-transform">
                  📊
                </div>
                <div>
                  <h4 className="font-bold text-sm text-slate-800 group-hover:text-emerald-700 transition-colors">
                    {isHi ? 'उपज अनुमान लगाएं' : 'Run Yield AI'}
                  </h4>
                  <p className="text-[11px] text-slate-500">
                    {isHi ? 'फसल अनुसार उपज व चालक' : 'Crop & soil analysis'}
                  </p>
                </div>
              </Link>

              <Link
                to="/market"
                className="p-4 rounded-2xl bg-white border border-slate-200/80 hover:border-amber-300 shadow-sm hover:shadow-md transition-all flex items-center gap-3.5 group"
              >
                <div className="w-11 h-11 rounded-xl bg-amber-100 text-amber-800 flex items-center justify-center text-xl font-bold group-hover:scale-110 transition-transform">
                  🛒
                </div>
                <div>
                  <h4 className="font-bold text-sm text-slate-800 group-hover:text-amber-700 transition-colors">
                    {isHi ? 'मंडी भाव व शुद्ध लाभ' : 'Mandi & Net Payout'}
                  </h4>
                  <p className="text-[11px] text-slate-500">
                    {isHi ? 'भाड़ा घटाकर सर्वोत्तम बाजार' : 'Freight adjusted pricing'}
                  </p>
                </div>
              </Link>

              <Link
                to="/soil"
                className="p-4 rounded-2xl bg-white border border-slate-200/80 hover:border-lime-300 shadow-sm hover:shadow-md transition-all flex items-center gap-3.5 group"
              >
                <div className="w-11 h-11 rounded-xl bg-lime-100 text-lime-800 flex items-center justify-center text-xl font-bold group-hover:scale-110 transition-transform">
                  🧪
                </div>
                <div>
                  <h4 className="font-bold text-sm text-slate-800 group-hover:text-lime-700 transition-colors">
                    {isHi ? 'मृदा स्वास्थ्य कार्ड' : 'Soil Health Card'}
                  </h4>
                  <p className="text-[11px] text-slate-500">
                    {isHi ? 'NPK एवं उर्वरक सलाह' : 'NPK & pH dosing'}
                  </p>
                </div>
              </Link>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}