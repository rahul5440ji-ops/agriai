import { create } from 'zustand';
import { loadLanguage } from '../i18n';

const getInitialHistory = () => {
  try {
    const raw = localStorage.getItem('agriai_history');
    return raw ? JSON.parse(raw) : [];
  } catch {
    return [];
  }
};

const useAppStore = create((set, get) => ({
  language: loadLanguage(localStorage.getItem('agriai_lang') || 'en'),
  farmId: localStorage.getItem('agriai_farm_id') ? parseInt(localStorage.getItem('agriai_farm_id'), 10) : null,
  activeFarm: null,
  history: getInitialHistory(),

  setLanguage: (lang) => {
    localStorage.setItem('agriai_lang', lang);
    set({ language: lang });
  },

  setFarmId: (id) => {
    if (id) {
      localStorage.setItem('agriai_farm_id', id.toString());
    } else {
      localStorage.removeItem('agriai_farm_id');
    }
    set({ farmId: id });
  },

  setActiveFarm: (farm) => {
    if (farm?.id) {
      localStorage.setItem('agriai_farm_id', farm.id.toString());
      set({ activeFarm: farm, farmId: farm.id });
    } else {
      set({ activeFarm: farm });
    }
  },

  addHistoryItem: (entry) => {
    const item = {
      id: Date.now().toString(36) + Math.random().toString(36).substr(2, 5),
      timestamp: new Date().toISOString(),
      ...entry,
    };
    const updated = [item, ...get().history.slice(0, 49)];
    try {
      localStorage.setItem('agriai_history', JSON.stringify(updated));
    } catch (e) {
      console.warn('Failed to save history to localStorage', e);
    }
    set({ history: updated });
    return item;
  },

  removeHistoryItem: (id) => {
    const updated = get().history.filter((h) => h.id !== id);
    try {
      localStorage.setItem('agriai_history', JSON.stringify(updated));
    } catch (e) {
      console.warn('Failed to update history', e);
    }
    set({ history: updated });
  },

  clearHistory: () => {
    try {
      localStorage.removeItem('agriai_history');
    } catch {}
    set({ history: [] });
  },
}));

export default useAppStore;