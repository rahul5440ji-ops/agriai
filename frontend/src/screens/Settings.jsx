import React from 'react';
import { t } from '../i18n';
import useAppStore from '../store';
import { SUPPORTED_LANGUAGES } from '../i18n';

const LANG_LABELS = {
  en: 'English',
  hi: 'हिन्दी',
};

export default function Settings() {
  const { language, setLanguage } = useAppStore();

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-agri-earth">
        {t('nav.settings', language)}
      </h2>

      <div className="bg-white rounded-xl shadow p-4">
        <p className="text-xs text-gray-500 uppercase tracking-wide mb-3">
          {t('common.language', language)}
        </p>
        <div className="space-y-2">
          {SUPPORTED_LANGUAGES.map((lang) => (
            <button
              key={lang}
              onClick={() => setLanguage(lang)}
              className={`w-full text-left px-3 py-2 rounded-lg text-sm ${
                language === lang
                  ? 'bg-agri-green/10 text-agri-green font-semibold'
                  : 'hover:bg-gray-50 text-gray-700'
              }`}
            >
              {LANG_LABELS[lang]}
            </button>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-xl shadow p-4">
        <p className="text-xs text-gray-500 uppercase tracking-wide">AgriAI</p>
        <p className="text-sm text-gray-600 mt-1">Version 0.1.0 (Stage 2 — Foundation)</p>
        <p className="text-xs text-gray-400 mt-2">
          {t('yield.disclaimer', language)}
        </p>
      </div>
    </div>
  );
}