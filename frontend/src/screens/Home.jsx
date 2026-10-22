import React from 'react';
import { Link } from 'react-router-dom';
import useAppStore from '../store';
import { t } from '../i18n';

export default function Home() {
  const { language } = useAppStore();

  return (
    <div className="space-y-6">
      <section className="text-center py-10">
        <div className="text-5xl mb-4">🌾</div>
        <h1 className="text-3xl font-bold text-agri-earth mb-2">
          {t('welcome.title', language)}
        </h1>
        <p className="text-gray-600 mb-6 max-w-sm mx-auto">
          {t('welcome.subtitle', language)}
        </p>

        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 max-w-md mx-auto">
          <Link
            to="/farm"
            className="bg-agri-green text-white font-semibold py-3 px-6 rounded-lg shadow hover:bg-agri-leaf transition-colors"
          >
            {t('welcome.getStarted', language)}
          </Link>
          <Link
            to="/market"
            className="bg-white border border-agri-green text-agri-green font-semibold py-3 px-6 rounded-lg hover:bg-agri-sky/10 transition-colors"
          >
            {t('welcome.learnMore', language)}
          </Link>
        </div>
      </section>

      <section className="bg-agri-sky/5 rounded-xl p-6 mx-auto max-w-md">
        <h2 className="text-lg font-semibold text-agri-earth mb-3">
          Quick Overview
        </h2>
        <ul className="text-sm text-gray-700 space-y-2">
          <li className="flex items-start">
            <span className="text-agri-green mr-2">✓</span>
            <span>Predict crop yields with ML</span>
          </li>
          <li className="flex items-start">
            <span className="text-agri-green mr-2">✓</span>
            <span>Compare mandi prices with MSP reference</span>
          </li>
          <li className="flex items-start">
            <span className="text-agri-green mr-2">✓</span>
            <span>Forecast market prices (when data available)</span>
          </li>
          <li className="flex items-start">
            <span className="text-agri-green mr-2">✓</span>
            <span>Mobile-first, farmer-friendly UI</span>
          </li>
        </ul>
      </section>

      <div className="text-center text-xs text-gray-400 mt-8">
        <p>{t('yield.disclaimer', language)}</p>
      </div>
    </div>
  );
}