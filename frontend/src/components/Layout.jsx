import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import useAppStore from '../store';
import { t } from '../i18n';

const NAV_ITEMS = [
  { to: '/', label: 'Home', hiLabel: 'होम', icon: '🏡' },
  { to: '/farm', label: 'My Farm', hiLabel: 'मेरा खेत', icon: '🌾' },
  { to: '/soil', label: 'Soil Health', hiLabel: 'मृदा स्वास्थ्य', icon: '🧪' },
  { to: '/yield', label: 'Yield AI', hiLabel: 'उपज AI', icon: '📊' },
  { to: '/market', label: 'Markets', hiLabel: 'मंडी भाव', icon: '🛒' },
  { to: '/forecast', label: 'Forecast', hiLabel: 'मूल्य अनुमान', icon: '🔮' },
  { to: '/advisory', label: 'Advisory', hiLabel: 'सलाह', icon: '🌱' },
  { to: '/history', label: 'History', hiLabel: 'इतिहास', icon: '📜' },
  { to: '/settings', label: 'Settings', hiLabel: 'सेटिंग्स', icon: '⚙️' },
];

export default function Layout({ children }) {
  const location = useLocation();
  const { language, setLanguage } = useAppStore();

  const toggleLanguage = () => {
    setLanguage(language === 'hi' ? 'en' : 'hi');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 text-slate-900 selection:bg-emerald-500 selection:text-white">
      {/* Top Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-emerald-800/90 border-b border-emerald-700/50 text-white shadow-lg shadow-emerald-950/10">
        <div className="max-w-4xl mx-auto px-4 py-2.5 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shadow-md shadow-emerald-900/30 ring-2 ring-emerald-300/40 group-hover:scale-105 transition-transform duration-200">
              <span className="text-2xl drop-shadow">🌱</span>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-extrabold text-xl tracking-tight bg-gradient-to-r from-white via-emerald-100 to-emerald-200 bg-clip-text text-transparent">
                  AgriAI
                </span>
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded-full bg-emerald-500/30 text-emerald-200 border border-emerald-400/30 tracking-wider uppercase">
                  v1.0 Pro
                </span>
              </div>
              <p className="text-[11px] text-emerald-200/90 font-medium leading-none mt-0.5">
                {language === 'hi' ? 'स्मार्ट कृषि निर्णय प्रणाली' : 'Smart Farming Decision Engine'}
              </p>
            </div>
          </Link>

          {/* Quick Actions in Header */}
          <div className="flex items-center gap-2">
            <div className="hidden sm:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-emerald-900/50 border border-emerald-700/60 text-emerald-200 text-xs">
              <span className="w-2 h-2 rounded-full bg-amber-300"></span>
              <span className="font-medium text-[11px]">
                {language === 'hi' ? 'डेमो मंडी डेटा' : 'Synthetic Demo Markets'}
              </span>
            </div>

            {/* Language toggle pill */}
            <button
              onClick={toggleLanguage}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-full bg-white/10 hover:bg-white/20 active:scale-95 border border-white/20 text-xs font-semibold text-white transition-all shadow-sm"
              title="Change Language"
            >
              <span>{language === 'hi' ? '🇮🇳 हिंदी' : '🌐 English'}</span>
              <span className="text-[10px] bg-emerald-500/80 px-1 rounded text-white">
                {language === 'hi' ? 'EN' : 'हि'}
              </span>
            </button>
          </div>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="flex-1 max-w-4xl w-full mx-auto px-3 sm:px-6 py-5 pb-24">
        {children}
      </main>

      {/* Floating Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 z-40 bg-white/95 backdrop-blur-lg border-t border-slate-200/80 shadow-[0_-4px_25px_rgba(0,0,0,0.06)] pb-safe">
        <div className="max-w-4xl mx-auto px-2 py-1.5 flex items-center justify-between sm:justify-around overflow-x-auto no-scrollbar">
          {NAV_ITEMS.map((item) => {
            const active = location.pathname === item.to;
            const labelText = language === 'hi' ? item.hiLabel : item.label;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`relative flex flex-col items-center justify-center min-w-[54px] sm:min-w-[70px] py-1 px-1.5 rounded-xl transition-all duration-200 ${
                  active
                    ? 'text-emerald-700 font-bold scale-105'
                    : 'text-slate-500 hover:text-slate-900 hover:bg-slate-100/70 font-medium'
                }`}
              >
                {active && (
                  <span className="absolute -top-1.5 w-6 h-1 rounded-full bg-emerald-600 shadow-sm shadow-emerald-400"></span>
                )}
                <span className={`text-xl transition-transform ${active ? 'scale-110 drop-shadow-sm' : ''}`}>
                  {item.icon}
                </span>
                <span className="text-[10px] sm:text-[11px] leading-tight mt-0.5 whitespace-nowrap text-center">
                  {labelText}
                </span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}