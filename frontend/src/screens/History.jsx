import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import useAppStore from '../store';

export default function History() {
  const { language, history, removeHistoryItem, clearHistory } = useAppStore();
  const [filter, setFilter] = useState('all');
  const isHi = language === 'hi';

  const filteredHistory = history.filter((item) => {
    if (filter === 'all') return true;
    return item.type === filter;
  });

  const formatDate = (isoString) => {
    if (!isoString) return '';
    const date = new Date(isoString);
    return date.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>📜</span>
            {isHi ? 'पूर्वानुमान एवं सलाह इतिहास' : 'Calculation & Advisory History'}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {isHi
              ? 'आपके द्वारा निकाले गए सभी उपज अनुमान व मंडी भाव तुलना'
              : 'Stored logs of your past yield predictions, market assessments, and price forecasts'}
          </p>
        </div>

        {history.length > 0 && (
          <button
            onClick={() => {
              if (window.confirm(isHi ? 'क्या आप पूरा इतिहास मिटाना चाहते हैं?' : 'Clear all history records?')) {
                clearHistory();
              }
            }}
            className="text-xs font-semibold text-rose-600 hover:text-rose-700 bg-rose-50 hover:bg-rose-100 px-3 py-1.5 rounded-xl transition-all"
          >
            {isHi ? '🗑️ पूरा इतिहास साफ़ करें' : '🗑️ Clear All'}
          </button>
        )}
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
        {[
          { id: 'all', label: isHi ? 'सभी रिकॉर्ड्स' : 'All Activities', icon: '📋' },
          { id: 'yield_prediction', label: isHi ? 'उपज अनुमान' : 'Yield Predictions', icon: '📊' },
          { id: 'market_recommendation', label: isHi ? 'मंडी तुलना' : 'Market Checks', icon: '🛒' },
          { id: 'price_forecast', label: isHi ? 'मूल्य रुझान' : 'Price Forecasts', icon: '🔮' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilter(tab.id)}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
              filter === tab.id
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-white border border-slate-200/80 text-slate-600 hover:bg-slate-50'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* History List */}
      {filteredHistory.length > 0 ? (
        <div className="space-y-3">
          {filteredHistory.map((item) => {
            const isYield = item.type === 'yield_prediction';
            const isMarket = item.type === 'market_recommendation';
            const isForecast = item.type === 'price_forecast';

            return (
              <div
                key={item.id}
                className="bg-white rounded-2xl p-4 sm:p-5 border border-slate-200/80 shadow-sm hover:border-slate-300 transition-all flex flex-col sm:flex-row sm:items-center justify-between gap-4"
              >
                <div className="flex items-start gap-3.5">
                  <div
                    className={`w-11 h-11 rounded-xl flex items-center justify-center text-xl flex-shrink-0 ${
                      isYield
                        ? 'bg-emerald-100 text-emerald-800'
                        : isMarket
                        ? 'bg-amber-100 text-amber-800'
                        : 'bg-sky-100 text-sky-800'
                    }`}
                  >
                    {isYield ? '📊' : isMarket ? '🛒' : '🔮'}
                  </div>

                  <div className="space-y-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="font-bold text-sm text-slate-900">
                        {item.title}
                      </h3>
                      <span className="text-[10px] font-semibold text-slate-400 bg-slate-100 px-2 py-0.5 rounded-md">
                        {formatDate(item.timestamp)}
                      </span>
                    </div>

                    {isYield && (
                      <p className="text-xs text-slate-600">
                        Estimated Yield: <strong>{item.predictedYield?.toFixed(2)} t/ha</strong> • Total:{' '}
                        <strong>{item.totalProduction?.toFixed(2)} tonnes</strong> ({item.area} ha)
                      </p>
                    )}

                    {isMarket && (
                      <p className="text-xs text-slate-600">
                        Best Mandi: <strong>{item.bestMarket}</strong> • Net Realization:{' '}
                        <strong className="text-emerald-700">₹{item.netPrice?.toFixed(2)}/qtl</strong>
                      </p>
                    )}

                    {isForecast && (
                      <p className="text-xs text-slate-600">
                        Expected Midpoint: <strong>₹{item.midpoint?.toFixed(0)}/qtl</strong> • Range:{' '}
                        <strong>{item.range}</strong> ({item.horizon})
                      </p>
                    )}
                  </div>
                </div>

                <div className="flex items-center justify-end gap-2 sm:self-center">
                  <Link
                    to={
                      isYield
                        ? '/yield'
                        : isMarket
                        ? `/market?crop=${item.crop}`
                        : `/forecast?commodity=${item.commodity}&market=${encodeURIComponent(item.market)}`
                    }
                    className="px-3 py-1.5 rounded-lg bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-all"
                  >
                    {isHi ? 'फिर से देखें' : 'View Tool'}
                  </Link>

                  <button
                    onClick={() => removeHistoryItem(item.id)}
                    className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-all"
                    title="Remove item"
                  >
                    ✕
                  </button>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        /* Empty State */
        <div className="text-center py-16 bg-white rounded-3xl border border-slate-200/80 p-8 space-y-4">
          <div className="w-16 h-16 rounded-2xl bg-emerald-50 text-emerald-700 flex items-center justify-center text-3xl mx-auto shadow-inner">
            📜
          </div>
          <div>
            <h3 className="text-base font-bold text-slate-900">
              {isHi ? 'कोई सहेजा गया इतिहास नहीं' : 'No History Recorded Yet'}
            </h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto mt-1 leading-relaxed">
              {isHi
                ? 'जब आप उपज अनुमान लगाएंगे या मंडी भाव की तुलना करेंगे, तो आपके परिणाम यहां स्वतः सुरक्षित हो जाएंगे।'
                : 'Whenever you calculate a crop yield or evaluate market prices, your results will be automatically organized here.'}
            </p>
          </div>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <Link
              to="/yield"
              className="px-4 py-2 rounded-xl bg-emerald-600 text-white font-bold text-xs shadow-sm hover:bg-emerald-700 transition-all"
            >
              {isHi ? 'उपज का अनुमान लगाएं' : 'Predict Yield'}
            </Link>
            <Link
              to="/market"
              className="px-4 py-2 rounded-xl bg-slate-100 text-slate-700 font-bold text-xs hover:bg-slate-200 transition-all"
            >
              {isHi ? 'मंडी भाव जांचें' : 'Check Markets'}
            </Link>
          </div>
        </div>
      )}
    </div>
  );
}