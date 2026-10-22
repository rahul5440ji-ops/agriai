import en from './en.json';
import hi from './hi.json';

const translations = { en, hi };
const DEFAULT_LANG = 'en';

export const SUPPORTED_LANGUAGES = ['en', 'hi'];

export function t(key, lang = DEFAULT_LANG) {
  const dict = translations[lang] || translations[DEFAULT_LANG];
  return key.split('.').reduce((acc, part) => {
    if (acc && acc[part] !== undefined) return acc[part];
    return undefined;
  }, dict) ?? key;
}

export function loadLanguage(lang) {
  if (!translations[lang]) return DEFAULT_LANG;
  return lang;
}

export default { t, loadLanguage, SUPPORTED_LANGUAGES };