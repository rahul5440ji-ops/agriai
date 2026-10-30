import React, { useState, useEffect } from 'react';
import useAppStore from '../store';
import { api } from '../services/api';

export default function Settings() {
  const { language, setLanguage, clearHistory, setFarmId } = useAppStore();
  const isHi = language === 'hi';
  const [healthStatus, setHealthStatus] = useState('checking');

  useEffect(() => {
    api.health()
      .then((res) => setHealthStatus(res.status === 'ok' ? 'Online (v0.1.0)' : 'Connected'))
      .catch(() => setHealthStatus('Local Ready'));
  }, []);

  return (
    <div className="space-y-6">
      {/* Title */}
      <div>
        <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
          <span>⚙️</span>
          {isHi ? 'एप्लिकेशन सेटिंग्स' : 'App Settings & Preferences'}
        </h1>
        <p className="text-xs text-slate-500 mt-0.5">
          {isHi
            ? 'भाषा, इकाई प्राथमिकताएं और सिस्टम स्थिति'
            : 'Language selection, system health & local data control'}
        </p>
      </div>

      {/* Language Section */}
      <div className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/80 shadow-sm space-y-4">
        <h3 className="font-bold text-sm text-slate-800 flex items-center gap-2">
          <span>🌐</span>
          {isHi ? 'भाषा चयन (Select Language)' : 'Preferred Language'}
        </h3>

        <div className="grid grid-cols-2 gap-3">
          <button
            onClick={() => setLanguage('en')}
            className={`p-4 rounded-2xl border text-left transition-all ${
              language === 'en'
                ? 'border-emerald-500 bg-emerald-50/70 shadow-sm ring-2 ring-emerald-200'
                : 'border-slate-200 hover:border-slate-300 bg-white'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-lg">🌐</span>
              {language === 'en' && <span className="text-emerald-700 font-bold text-xs">✓ Active</span>}
            </div>
            <p className="font-bold text-sm text-slate-900">English</p>
            <p className="text-[11px] text-slate-500">Standard Agricultural Terminology</p>
          </button>

          <button
            onClick={() => setLanguage('hi')}
            className={`p-4 rounded-2xl border text-left transition-all ${
              language === 'hi'
                ? 'border-emerald-500 bg-emerald-50/70 shadow-sm ring-2 ring-emerald-200'
                : 'border-slate-200 hover:border-slate-300 bg-white'
            }`}
          >
            <div className="flex items-center justify-between mb-1">
              <span className="text-lg">🇮🇳</span>
              {language === 'hi' && <span className="text-emerald-700 font-bold text-xs">✓ सक्रिय</span>}
            </div>
            <p className="font-bold text-sm text-slate-900">हिन्दी</p>
            <p className="text-[11px] text-slate-500">किसान अनुकूल सरल शब्दावली</p>
          </button>
        </div>
      </div>

      {/* System Status & ML Registry Card */}
      <div className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/80 shadow-sm space-y-3">
        <h3 className="font-bold text-sm text-slate-800 flex items-center gap-2">
          <span>🖥️</span>
          {isHi ? 'सिस्टम व मॉडल स्थिति' : 'System Engine & ML Registry'}
        </h3>

        <div className="grid grid-cols-2 gap-3 text-xs">
          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200/60">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block">API Status</span>
            <span className="font-bold text-emerald-700 flex items-center gap-1.5 mt-0.5">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              {healthStatus}
            </span>
          </div>

          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200/60">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block">Crop Yield ML</span>
            <span className="font-bold text-slate-800 block mt-0.5">yield-v1 (R² 0.99)</span>
          </div>

          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200/60">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block">Price Forecast ML</span>
            <span className="font-bold text-slate-800 block mt-0.5">price-v1 (434 series)</span>
          </div>

          <div className="p-3 rounded-2xl bg-slate-50 border border-slate-200/60">
            <span className="text-[10px] text-slate-400 uppercase font-semibold block">Database</span>
            <span className="font-bold text-slate-800 block mt-0.5">Synthetic Demo Market Prices</span>
          </div>
        </div>
      </div>

      {/* Data Management */}
      <div className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/80 shadow-sm space-y-3">
        <h3 className="font-bold text-sm text-slate-800 flex items-center gap-2">
          <span>🧹</span>
          {isHi ? 'डेटा नियंत्रण एवं रीसेट' : 'Data Management & Privacy'}
        </h3>
        <p className="text-xs text-slate-600 leading-relaxed">
          {isHi
            ? 'आपके द्वारा निकाले गए सभी अनुमान आपके डिवाइस के लोकल स्टोरेज में सुरक्षित रहते हैं।'
            : 'All calculation history is kept client-side in your browser storage.'}
        </p>

        <div className="flex flex-wrap gap-3 pt-1">
          <button
            onClick={() => {
              if (window.confirm(isHi ? 'सभी इतिहास रिकॉर्ड मिटाएं?' : 'Clear all history records?')) {
                clearHistory();
                alert(isHi ? 'इतिहास साफ़ कर दिया गया है।' : 'History cleared.');
              }
            }}
            className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-all"
          >
            {isHi ? '🗑️ इतिहास मिटाएं' : 'Clear History Cache'}
          </button>

          <button
            onClick={() => {
              if (window.confirm(isHi ? 'सक्रिय खेत रीसेट करें?' : 'Reset active farm selector?')) {
                setFarmId(null);
                alert(isHi ? 'खेत चयन रीसेट किया गया।' : 'Farm profile reset.');
              }
            }}
            className="px-4 py-2 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold transition-all"
          >
            {isHi ? '🔄 खेत चयन रीसेट करें' : 'Reset Active Farm'}
          </button>
        </div>
      </div>
    </div>
  );
}