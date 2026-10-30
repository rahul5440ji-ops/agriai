import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../services/api';
import useAppStore from '../store';
import LocationDropdown from '../components/LocationDropdown';
import SyntheticDataNotice from '../components/SyntheticDataNotice';

const CROPS = [
  'wheat', 'rice', 'maize', 'cotton', 'sugarcane',
  'pulses', 'groundnut', 'mustard', 'potato', 'tomato',
  'soybean', 'sunflower', 'jowar', 'bajra'
];

export default function MarketComparison() {
  const { language } = useAppStore();
  const isHi = language === 'hi';

  const [crop, setCrop] = useState('wheat');
  const [state, setState] = useState('Maharashtra');
  const [district, setDistrict] = useState('Pune');
  const [transport, setTransport] = useState('40');
  const [otherCosts, setOtherCosts] = useState('10');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [sortBy, setSortBy] = useState('net');
  const hasSyntheticResults = result?.some((row) => row.is_synthetic);

  const handleCompare = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);
    try {
      const res = await api.compareMarkets({
        crop,
        state,
        district,
        transport_cost: parseFloat(transport) || 0,
        other_costs: parseFloat(otherCosts) || 0,
      });
      setResult(res);
    } catch (err) {
      setError(err.body?.detail || err.message || 'Comparison failed');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleCompare();
  }, [crop, state, district]);

  const sortedResults = result ? [...result].sort((a, b) => {
    if (sortBy === 'net') return (b.estimated_net_price || 0) - (a.estimated_net_price || 0);
    if (sortBy === 'modal') return (b.modal_price_per_quintal || 0) - (a.modal_price_per_quintal || 0);
    if (sortBy === 'freshness') return (a.data_freshness_days || 0) - (b.data_freshness_days || 0);
    return 0;
  }) : [];

  return (
    <div className="space-y-6">
      {/* Title */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>⚖️</span>
            {isHi ? 'मंडी थोक भाव एवं एमएसपी तुलना' : 'Mandi Rates vs MSP Comparison'}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {isHi
              ? 'मंडियों के भाव और सरकारी न्यूनतम समर्थन मूल्य (MSP) संदर्भ की तुलना'
              : 'Detailed side-by-side comparison of local market modal prices and benchmark MSP'}
          </p>
        </div>
        <Link
          to="/market"
          className="text-xs font-bold text-emerald-700 bg-emerald-50 px-3 py-1.5 rounded-xl border border-emerald-200 hover:bg-emerald-100 transition-all"
        >
          {isHi ? '← सलाहकार मोड' : '← Advisor Mode'}
        </Link>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {hasSyntheticResults && <SyntheticDataNotice isHi={isHi} />}

      {/* Filter Card */}
      <form onSubmit={handleCompare} className="bg-white rounded-3xl p-5 border border-slate-200/80 shadow-sm space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wide">
              {isHi ? 'फसल' : 'Commodity'}
            </label>
            <select
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm font-medium text-slate-800 focus:border-emerald-500 outline-none"
            >
              {CROPS.map((c) => (
                <option key={c} value={c}>
                  {c.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          <LocationDropdown
            state={state}
            city={district}
            onStateChange={(s) => { setState(s); setDistrict(''); }}
            onCityChange={setDistrict}
            label={isHi ? 'राज्य एवं जिला' : 'Region & District'}
          />
        </div>

        <div className="grid grid-cols-2 gap-3 pt-1">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Freight Cost (₹/qtl)
            </label>
            <input
              type="number"
              value={transport}
              onChange={(e) => setTransport(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs bg-white focus:border-emerald-500 outline-none"
            />
          </div>
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              Other Charges (₹/qtl)
            </label>
            <input
              type="number"
              value={otherCosts}
              onChange={(e) => setOtherCosts(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs bg-white focus:border-emerald-500 outline-none"
            />
          </div>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs shadow-sm transition-all"
        >
          {loading ? 'Refreshing...' : 'Update Comparison Table'}
        </button>
      </form>

      {/* Comparison Table */}
      {result && result.length > 0 ? (
        <div className="bg-white rounded-3xl border border-slate-200/80 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 flex flex-wrap items-center justify-between gap-3">
            <span className="text-xs font-bold text-slate-700">
              {isHi ? `मंडियां (${result.length} रिकॉर्ड्स)` : `Comparing ${result.length} Markets for ${crop.toUpperCase()}`}
            </span>

            {/* Sort toggles */}
            <div className="flex items-center gap-1 text-xs">
              <span className="text-slate-400 text-[11px] mr-1">Sort:</span>
              <button
                onClick={() => setSortBy('net')}
                className={`px-2.5 py-1 rounded-lg font-semibold text-[11px] transition-all ${
                  sortBy === 'net' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                Net Price
              </button>
              <button
                onClick={() => setSortBy('modal')}
                className={`px-2.5 py-1 rounded-lg font-semibold text-[11px] transition-all ${
                  sortBy === 'modal' ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
                }`}
              >
                Mandi Rate
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-left">
              <thead className="bg-slate-50 text-slate-500 font-bold uppercase text-[10px] tracking-wider border-b border-slate-100">
                <tr>
                  <th className="py-3 px-4">Market / Mandi</th>
                  <th className="py-3 px-4 text-right">Modal Rate</th>
                  <th className="py-3 px-4 text-right">Govt MSP</th>
                  <th className="py-3 px-4 text-right">Freight Adj.</th>
                  <th className="py-3 px-4 text-right font-black text-emerald-800">
                    {hasSyntheticResults ? 'Demo Net Estimate' : 'Est. Net Realization'}
                  </th>
                  <th className="py-3 px-4 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 font-medium">
                {sortedResults.map((row, i) => {
                  const mspDiff = (row.modal_price_per_quintal || 0) - (row.msp_reference_per_quintal || 0);
                  const aboveMsp = mspDiff >= 0;

                  return (
                    <tr key={i} className="hover:bg-slate-50/80 transition-colors">
                      <td className="py-3 px-4 font-bold text-slate-900">
                        <div>{row.market}</div>
                        {row.is_synthetic ? (
                          <span className="text-[10px] text-amber-800 font-bold">
                            {isHi ? 'डेमो डेटा' : 'Synthetic demo data'}
                          </span>
                        ) : row.data_freshness_days > 30 ? (
                          <span className="text-[10px] text-amber-600 font-normal">Stale ({row.data_freshness_days}d ago)</span>
                        ) : (
                          <span className="text-[10px] text-emerald-600 font-normal">Fresh ({row.data_freshness_days}d ago)</span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right font-bold text-slate-800">
                        ₹{row.modal_price_per_quintal}
                      </td>
                      <td className="py-3 px-4 text-right text-slate-600">
                        ₹{row.msp_reference_per_quintal}
                        <span className={`block text-[10px] font-semibold ${aboveMsp ? 'text-emerald-600' : 'text-amber-600'}`}>
                          {aboveMsp ? `+₹${mspDiff.toFixed(0)}` : `-₹${Math.abs(mspDiff).toFixed(0)}`}
                        </span>
                      </td>
                      <td className="py-3 px-4 text-right text-rose-600">
                        -₹{row.estimated_transport_cost?.toFixed(0)}
                      </td>
                      <td className="py-3 px-4 text-right font-black text-emerald-700 text-sm">
                        ₹{row.estimated_net_price?.toFixed(2)}
                      </td>
                      <td className="py-3 px-4 text-center">
                        <Link
                          to={`/forecast?commodity=${crop}&market=${encodeURIComponent(row.market)}`}
                          className="px-2.5 py-1 rounded-lg bg-sky-50 text-sky-800 hover:bg-sky-100 font-bold text-[10px] border border-sky-200 transition-all inline-block"
                        >
                          Forecast 🔮
                        </Link>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        <div className="text-center py-10 bg-white rounded-3xl border border-slate-200/80 p-6 space-y-2">
          <span className="text-3xl">⚖️</span>
          <p className="text-xs text-slate-500">No market comparison records available for this filter.</p>
        </div>
      )}
    </div>
  );
}