import React, { useState, useEffect } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api } from '../services/api';
import useAppStore from '../store';
import LocationDropdown from '../components/LocationDropdown';
import SyntheticDataNotice from '../components/SyntheticDataNotice';

const CROPS = [
  'wheat', 'rice', 'maize', 'cotton', 'sugarcane',
  'pulses', 'groundnut', 'mustard', 'potato', 'tomato',
  'soybean', 'sunflower', 'jowar', 'bajra'
];

export default function MarketAdvisor() {
  const { language, addHistoryItem } = useAppStore();
  const [searchParams] = useSearchParams();
  const isHi = language === 'hi';

  const [crop, setCrop] = useState(searchParams.get('crop') || 'wheat');
  const [state, setState] = useState('Maharashtra');
  const [district, setDistrict] = useState('Pune');
  const [transportCost, setTransportCost] = useState('45');
  const [otherCosts, setOtherCosts] = useState('15');
  const [maxDistance, setMaxDistance] = useState('300');

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [recommendations, setRecommendations] = useState(null);
  const [mspData, setMspData] = useState(null);
  const hasSyntheticRecommendations = recommendations?.some((item) => item.is_synthetic);

  // Fetch MSP reference when crop changes
  useEffect(() => {
    api.getMspReference(crop)
      .then((data) => setMspData(data))
      .catch(() => setMspData(null));
  }, [crop]);

  const handleRecommend = async (e) => {
    if (e) e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        crop,
        state,
        district,
        transport_cost_per_quintal: parseFloat(transportCost) || 0,
        other_costs: parseFloat(otherCosts) || 0,
        max_distance_km: parseFloat(maxDistance) || 300,
      };

      const res = await api.recommendMarkets(payload);
      setRecommendations(res);

      if (res && res.length > 0) {
        addHistoryItem({
          type: 'market_recommendation',
          title: `Market Advice: ${crop.toUpperCase()}`,
          crop,
          bestMarket: res[0].market,
          netPrice: res[0].estimated_net_price,
          modalPrice: res[0].modal_price_per_quintal,
          msp: res[0].msp_reference_per_quintal,
        });
      }
    } catch (err) {
      setError(err.body?.detail || err.message || 'Failed to fetch recommendations');
    } finally {
      setLoading(false);
    }
  };

  // Run on mount or if query param crop is passed
  useEffect(() => {
    handleRecommend();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>🛒</span>
            {isHi ? 'मंडी सलाहकार एवं शुद्ध मूल्य' : 'Mandi Advisor & Net Realization'}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {isHi
              ? 'परिवहन और स्थानीय शुल्क घटाकर सर्वोत्तम बिक्री मूल्य प्राप्त करें'
              : 'Ranked selling markets after freight and handling cost deduction'}
          </p>
        </div>
        <Link
          to={`/forecast?commodity=${crop}&market=${district || 'Pune'} Mandi`}
          className="hidden sm:inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-sky-50 text-sky-800 text-xs font-bold border border-sky-200 hover:bg-sky-100 transition-all"
        >
          <span>🔮 मूल्य पूर्वानुमान</span>
        </Link>
      </div>

      {error && (
        <div className="p-4 rounded-xl bg-rose-50 border border-rose-200 text-rose-800 text-xs flex items-center gap-2">
          <span>⚠️</span>
          <span>{error}</span>
        </div>
      )}

      {hasSyntheticRecommendations && <SyntheticDataNotice isHi={isHi} />}

      {/* Control Panel / Filter Card */}
      <form onSubmit={handleRecommend} className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/80 shadow-sm space-y-4">
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {/* Crop Selector */}
          <div>
            <label className="block text-xs font-bold text-slate-700 mb-1.5 uppercase tracking-wide">
              {isHi ? 'फसल चुनें' : 'Commodity / Crop'}
            </label>
            <select
              value={crop}
              onChange={(e) => setCrop(e.target.value)}
              className="w-full rounded-xl border border-slate-300 bg-white px-3.5 py-2 text-sm font-medium text-slate-800 focus:border-emerald-500 focus:ring-2 focus:ring-emerald-200 outline-none"
            >
              {CROPS.map((c) => (
                <option key={c} value={c}>
                  {c.toUpperCase()}
                </option>
              ))}
            </select>
          </div>

          {/* Location */}
          <LocationDropdown
            state={state}
            city={district}
            onStateChange={(s) => { setState(s); setDistrict(''); }}
            onCityChange={setDistrict}
            label={isHi ? 'राज्य एवं जिला' : 'Farmer Location (State & District)'}
          />
        </div>

        {/* Cost adjustments strip */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 pt-2">
          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              {isHi ? 'परिवहन व्यय (₹/क्विंटल)' : 'Freight / Transport (₹/qtl)'}
            </label>
            <input
              type="number"
              step="1"
              min="0"
              value={transportCost}
              onChange={(e) => setTransportCost(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs bg-white focus:border-emerald-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              {isHi ? 'पल्लेदारी/अन्य खर्च (₹/क्विंटल)' : 'Labor & Market Cess (₹/qtl)'}
            </label>
            <input
              type="number"
              step="1"
              min="0"
              value={otherCosts}
              onChange={(e) => setOtherCosts(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs bg-white focus:border-emerald-500 outline-none"
            />
          </div>

          <div>
            <label className="block text-[11px] font-semibold text-slate-600 mb-1">
              {isHi ? 'अधिकतम दूरी (किमी)' : 'Search Radius (km)'}
            </label>
            <input
              type="number"
              step="10"
              min="10"
              value={maxDistance}
              onChange={(e) => setMaxDistance(e.target.value)}
              className="w-full rounded-lg border border-slate-300 px-3 py-1.5 text-xs bg-white focus:border-emerald-500 outline-none"
            />
          </div>
        </div>

        {/* Submit */}
        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 px-5 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-700 hover:from-emerald-500 hover:to-teal-600 text-white font-bold text-sm shadow-md active:scale-98 transition-all flex items-center justify-center gap-2"
        >
          {loading ? (
            <>
              <span className="w-4 h-4 rounded-full border-2 border-white border-t-transparent animate-spin"></span>
              <span>{isHi ? 'मंडियों का विश्लेषण जारी...' : 'Analyzing Mandi Rates & Freight...'}</span>
            </>
          ) : (
            <>
              <span>🔍</span>
              <span>{isHi ? 'सर्वोत्तम मंडियां खोजें' : 'Calculate & Recommend Best Mandis'}</span>
            </>
          )}
        </button>
      </form>

      {/* MSP Reference Banner */}
      {mspData && (
        <div className="rounded-2xl bg-amber-50 border border-amber-200/80 p-4 flex flex-wrap items-center justify-between gap-3 text-xs">
          <div className="flex items-center gap-2.5">
            <span className="w-8 h-8 rounded-lg bg-amber-200/70 text-amber-900 flex items-center justify-center font-bold text-base">
              🏛️
            </span>
            <div>
              <span className="font-bold text-amber-950 uppercase tracking-wide">
                Govt MSP Reference ({mspData.year || '2023-24'})
              </span>
              <p className="text-amber-800 text-[11px]">
                {crop.toUpperCase()} official benchmark rate
              </p>
            </div>
          </div>
          <div className="text-right">
            <span className="text-xl font-black text-amber-950">
              ₹{mspData.msp_rs_per_quintal}
            </span>
            <span className="text-slate-500 text-[11px] block">/ quintal</span>
          </div>
        </div>
      )}

      {/* Recommendations List */}
      {recommendations && recommendations.length > 0 ? (
        <div className="space-y-3">
          <div className="flex items-center justify-between text-xs font-bold text-slate-700 px-1">
            <span>
              {isHi ? `शीर्ष अनुशंसित मंडियां (${recommendations.length})` : `Top Ranked Selling Mandis (${recommendations.length})`}
            </span>
            <span className="text-slate-500 font-normal">
              {isHi ? 'शुद्ध लाभ अनुसार क्रमबद्ध' : 'Sorted by Net Payout'}
            </span>
          </div>

          <div className="space-y-3">
            {recommendations.map((rec) => {
              const isTop = rec.rank === 1;
              const mspDiff = rec.modal_price_per_quintal - rec.msp_reference_per_quintal;
              const aboveMsp = mspDiff >= 0;

              return (
                <div
                  key={rec.rank}
                  className={`relative rounded-3xl p-5 border transition-all duration-200 ${
                    isTop
                      ? 'bg-gradient-to-br from-emerald-50/90 via-white to-teal-50/50 border-emerald-400 shadow-lg shadow-emerald-950/5 ring-1 ring-emerald-300'
                      : 'bg-white border-slate-200/80 shadow-sm hover:border-slate-300'
                  }`}
                >
                  {isTop && (
                    <span className="absolute -top-3 left-6 px-3 py-0.5 rounded-full bg-emerald-600 text-white text-[10px] font-extrabold uppercase tracking-wider shadow-sm flex items-center gap-1">
                      <span>⭐</span> {isHi
                        ? (rec.is_synthetic ? 'सर्वोत्तम डेमो अनुमान' : 'सर्वोत्तम विकल्प')
                        : (rec.is_synthetic ? 'Best Demo Estimate' : 'Best Net Realization')}
                    </span>
                  )}

                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
                    <div>
                      <div className="flex items-center gap-2">
                        <span className={`w-7 h-7 rounded-lg flex items-center justify-center font-bold text-xs ${
                          isTop ? 'bg-emerald-600 text-white' : 'bg-slate-100 text-slate-700'
                        }`}>
                          #{rec.rank}
                        </span>
                        <h3 className="font-extrabold text-base text-slate-900 tracking-tight">
                          {rec.market}
                        </h3>
                        {rec.is_synthetic && (
                          <span className="rounded-full bg-amber-100 px-2 py-0.5 text-[10px] font-bold text-amber-900">
                            {isHi ? 'डेमो डेटा' : 'DEMO DATA'}
                          </span>
                        )}
                        {rec.distance_km && (
                          <span className="text-[11px] font-medium text-slate-500 bg-slate-100 px-2 py-0.5 rounded-full">
                            📍 {rec.distance_km} km
                          </span>
                        )}
                      </div>

                      <div className="flex flex-wrap items-center gap-2 mt-2">
                        <span className="text-xs text-slate-600">
                          {isHi ? 'मंडी थोक भाव:' : 'Mandi Rate:'} <strong>₹{rec.modal_price_per_quintal}</strong>/qtl
                        </span>
                        <span className={`text-[11px] font-bold px-2 py-0.5 rounded-md ${
                          aboveMsp
                            ? 'bg-emerald-100 text-emerald-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}>
                          {aboveMsp ? `+₹${mspDiff.toFixed(0)} above MSP` : `-₹${Math.abs(mspDiff).toFixed(0)} below MSP`}
                        </span>
                      </div>
                    </div>

                    {/* Net Realization Box */}
                    <div className="sm:text-right bg-emerald-50/60 sm:bg-transparent p-3 sm:p-0 rounded-2xl border border-emerald-100 sm:border-0">
                      <span className="text-[11px] font-bold text-slate-500 uppercase tracking-wide block">
                        {isHi
                          ? (rec.is_synthetic ? 'डेमो शुद्ध अनुमान' : 'अपेक्षित शुद्ध आय')
                          : (rec.is_synthetic ? 'Demo Net Estimate' : 'Est. Net Realization')}
                      </span>
                      <div className="text-2xl font-black text-emerald-700">
                        ₹{rec.estimated_net_price?.toFixed(2)}
                        <span className="text-xs font-normal text-slate-500"> /qtl</span>
                      </div>
                      <span className="text-[10px] text-slate-400 block">
                        ({isHi ? 'भाड़ा व पल्लेदारी काटकर' : 'after freight & fees'})
                      </span>
                    </div>
                  </div>

                  {/* Cost breakdown pill */}
                  <div className="mt-4 pt-3 border-t border-slate-100 grid grid-cols-3 gap-2 text-center text-xs">
                    <div className="bg-slate-50 p-2 rounded-xl">
                      <span className="text-[10px] text-slate-400 block">{isHi ? 'एमएसपी संदर्भ' : 'Govt MSP'}</span>
                      <span className="font-bold text-slate-700">₹{rec.msp_reference_per_quintal?.toFixed(0)}</span>
                    </div>
                    <div className="bg-slate-50 p-2 rounded-xl">
                      <span className="text-[10px] text-slate-400 block">{isHi ? 'परिवहन व्यय' : 'Freight'}</span>
                      <span className="font-bold text-rose-600">-₹{rec.estimated_transport_cost?.toFixed(0)}</span>
                    </div>
                    <div className="bg-slate-50 p-2 rounded-xl">
                      <span className="text-[10px] text-slate-400 block">{isHi ? 'डेटा ताजगी' : 'Freshness'}</span>
                      <span className={`font-bold ${rec.is_synthetic ? 'text-amber-800' : 'text-emerald-700'}`}>
                        {rec.is_synthetic
                          ? (isHi ? 'डेमो रिकॉर्ड' : 'Demo record')
                          : (rec.data_freshness_days === 0 ? 'Today' : `${rec.data_freshness_days}d ago`)}
                      </span>
                    </div>
                  </div>

                  {/* Recommendation Reason */}
                  {rec.explanation && (
                    <div className="mt-3 flex items-start gap-1.5 text-xs text-slate-600 bg-slate-50/80 p-2.5 rounded-xl">
                      <span className="text-emerald-600 font-bold">💡</span>
                      <span className="leading-relaxed">{rec.explanation}</span>
                    </div>
                  )}

                  {/* Quick Forecast Link */}
                  <div className="mt-3 flex justify-end">
                    <Link
                      to={`/forecast?commodity=${crop}&market=${rec.market}`}
                      className="text-xs font-bold text-sky-700 hover:text-sky-800 hover:underline inline-flex items-center gap-1"
                    >
                      <span>🔮 {isHi ? 'इस मंडी का भविष्य मूल्य देखें' : 'View Price Forecast for this Mandi'}</span>
                      <span>→</span>
                    </Link>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ) : recommendations && (
        <div className="text-center py-10 bg-white rounded-3xl border border-slate-200/80 p-6 space-y-2">
          <span className="text-4xl">🌾</span>
          <h3 className="font-bold text-slate-800">
            {isHi ? 'कोई मंडी उपलब्ध नहीं मिली' : 'No Nearby Mandis Found'}
          </h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            {isHi ? 'कृपया दूरी या राज्य बदल कर पुनः प्रयास करें।' : 'Try expanding your search radius or changing the location.'}
          </p>
        </div>
      )}
    </div>
  );
}