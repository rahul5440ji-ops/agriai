import { create } from 'zustand';
import { loadLanguage } from '../i18n';

const useAppStore = create((set) => ({
  language: loadLanguage(localStorage.getItem('agriai_lang') || 'en'),
  farmId: null,
  setLanguage: (lang) => {
    localStorage.setItem('agriai_lang', lang);
    set({ language: lang });
  },
  setFarmId: (id) => set({ farmId: id }),
}));

export default useAppStore;