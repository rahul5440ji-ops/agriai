import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import useAppStore from '../store';
import { t } from '../i18n';

const NAV_ITEMS = [
  { to: '/', key: 'dashboard', icon: '🏠' },
  { to: '/farm', key: 'myFarm', icon: '🌾' },
  { to: '/soil', key: 'soil', icon: '🧪' },
  { to: '/yield', key: 'yield', icon: '📊' },
  { to: '/market', key: 'market', icon: '🛒' },
  { to: '/forecast', key: 'forecast', icon: '🔮' },
  { to: '/history', key: 'history', icon: '📜' },
  { to: '/settings', key: 'settings', icon: '⚙️' },
];

export default function Layout({ children }) {
  const location = useLocation();
  const { language } = useAppStore();
  const isDashboard = location.pathname === '/';

  return (
    <div className="min-h-screen bg-agri-sky/5 flex flex-col">
      <header className="bg-agri-green text-white shadow-md">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span className="text-2xl">🌾</span>
            <div>
              <h1 className="font-bold text-lg leading-tight">{t('app.name', language)}</h1>
              <p className="text-xs text-green-100 leading-tight">{t('app.tagline', language)}</p>
            </div>
          </div>
        </div>
      </header>

      <main className="flex-1 max-w-3xl w-full mx-auto px-4 py-4 pb-safe">
        {children}
      </main>

      <nav className="bg-white border-t border-gray-200 sticky bottom-0">
        <div className="max-w-3xl mx-auto flex justify-around">
          {NAV_ITEMS.map((item) => {
            const active = location.pathname === item.to;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`flex flex-col items-center py-2 px-3 text-xs ${
                  active ? 'text-agri-green font-semibold' : 'text-gray-500'
                }`}
              >
                <span className="text-lg">{item.icon}</span>
                <span>{t(`nav.${item.key}`, language)}</span>
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}