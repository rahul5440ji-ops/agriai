import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import useAppStore from '../store';
import { t } from '../i18n';
import { api } from '../services/api';

const StatCard = ({ label, value, sub }) => (
  <div className="bg-white rounded-xl shadow p-4">
    <p className="text-xs text-gray-500 uppercase tracking-wide">{label}</p>
    <p className="text-xl font-bold text-agri-earth mt-1">{value}</p>
    {sub && <p className="text-xs text-gray-400 mt-1">{sub}</p>}
  </div>
);

export default function Dashboard() {
  const { language } = useAppStore();
  const [farm, setFarm] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchFarm = async () => {
      try {
        setLoading(true);
        let farmId = null;
        const farms = await api.getFarm(1).catch(() => null);
        if (!farms) {
          const newFarm = await api.createFarm({
            state: 'Maharashtra',
            district: 'Pune',
            area_hectare: 1.5,
          });
          farmId = newFarm.id;
        } else {
          farmId = farms.id;
        }

        try {
          const farmData = await api.getFarm(farmId);
          setFarm(farmData);
        } catch {
          setFarm(null);
        }
      } catch (err) {
        setError(err.body?.detail || err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchFarm();
  }, []);

  const cropStatus = loading
    ? t('common.loading', language)
    : !farm
    ? t('nav.myFarm', language) + ' not created'
    : 'Current crop: wheat (Rabi)';

  return (
    <div className="space-y-4">
      <div>
        <h2 className="text-lg font-semibold text-agri-earth">
          {t('dashboard.currentCrop', language)}
        </h2>
        <p className="text-sm text-gray-500">{cropStatus}</p>
      </div>

      {loading && (
        <div className="text-center py-4">
          <div className="inline-block animate-spin rounded-full border-4 border-agri-green border-t-transparent h-8 w-8"></div>
          <p className="text-sm text-gray-500 mt-2">{t('common.loading', language)}</p>
        </div>
      )}

      {error && (
        <div className="bg-red-50 text-red-700 text-sm p-3 rounded-lg">
          {error}
        </div>
      )}

      {!loading && farm && (
        <div className="grid grid-cols-2 gap-3">
          <StatCard
            label={t('dashboard.fieldArea', language)}
            value={`${farm.area_hectare}`}
            sub="hectare"
          />
          <StatCard
            label={t('dashboard.expectedYield', language)}
            value="4.2"
            sub="t/ha"
          />
          <StatCard
            label={t('dashboard.expectedProduction', language)}
            value="6.3"
            sub="tonnes"
          />
          <StatCard
            label={t('dashboard.mspReference', language)}
            value="2150"
            sub="₹/quintal"
          />
        </div>
      )}

      <Link
        to="/farm"
        className="block w-full bg-agri-green text-white font-semibold py-3 rounded-lg text-center"
      >
        {t('nav.myFarm', language)}
      </Link>
    </div>
  );
}