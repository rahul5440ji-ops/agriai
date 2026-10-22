import React from 'react';
import { t } from '../i18n';
import useAppStore from '../store';

export default function History() {
  const { language } = useAppStore();

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-agri-earth">
        {t('nav.history', language)}
      </h2>
      <div className="bg-white rounded-xl shadow p-6 text-center">
        <div className="text-4xl mb-2">📜</div>
        <p className="text-sm text-gray-500">
          No prediction history yet.
        </p>
        <p className="text-xs text-gray-400 mt-1">
          Your yield predictions and market comparisons will appear here.
        </p>
      </div>
    </div>
  );
}