import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import useAppStore from '../store';
import { api } from '../services/api';

export default function Home() {
  const { language, farmId, setActiveFarm } = useAppStore();
  const [cropsCount, setCropsCount] = useState(14);
  const [recentFarms, setRecentFarms] = useState([]);
  const isHi = language === 'hi';

  useEffect(() => {
    // Attempt to load existing farms to auto-populate farmId if missing
    api.listFarms()
      .then((farms) => {
        if (farms && farms.length > 0) {
          setRecentFarms(farms);
          if (!farmId) {
            setActiveFarm(farms[0]);
          }
        }
      })
      .catch(() => {});
  }, [farmId, setActiveFarm]);

  const quickTools = [
    {
      to: '/yield',
      icon: '📊',
      title: isHi ? 'फसल उपज AI' : 'Crop Yield AI',
      desc: isHi ? 'मिट्टी और मौसम अनुसार सटीक उपज अनुमान' : 'ML-driven yield estimates & driver analysis',
      badge: isHi ? 'R² 0.99 मॉडल' : 'R² 0.99 Model',
      badgeColor: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      gradient: 'from-emerald-500 to-teal-600',
      action: isHi ? 'अनुमान लगाएं' : 'Predict Yield',
    },
    {
      to: '/market',
      icon: '🛒',
      title: isHi ? 'मंडी भाव व MSP' : 'Mandi & MSP Advisor',
      desc: isHi ? 'निकटतम मंडियों की तुलना एवं शुद्ध लाभ गणना' : 'Compare Mandi vs MSP & net realization',
      badge: isHi ? 'डेमो डेटा' : 'Synthetic Demo Data',
      badgeColor: 'bg-amber-100 text-amber-800 border-amber-200',
      gradient: 'from-amber-500 to-orange-600',
      action: isHi ? 'मंडी खोजें' : 'Compare Markets',
    },
    {
      to: '/forecast',
      icon: '🔮',
      title: isHi ? 'मूल्य पूर्वानुमान' : 'Price Trend Forecast',
      desc: isHi ? 'अगले 7 से 30 दिनों का विश्वसनीय मूल्य रुझान' : '7 to 30-day time-series price forecasts',
      badge: isHi ? 'समय श्रृंखला AI' : 'Time-Series ML',
      badgeColor: 'bg-sky-100 text-sky-800 border-sky-200',
      gradient: 'from-sky-500 to-indigo-600',
      action: isHi ? 'रुझान देखें' : 'View Forecast',
    },
    {
      to: '/soil',
      icon: '🧪',
      title: isHi ? 'मृदा स्वास्थ्य जांच' : 'Soil Health Diagnostic',
      desc: isHi ? 'NPK, pH और उर्वरक उपयोग पर वैज्ञानिक सलाह' : 'NPK, pH scoring & tailored fertilizer dosage',
      badge: isHi ? 'मृदा स्कोर' : 'Soil Health Card',
      badgeColor: 'bg-lime-100 text-lime-800 border-lime-200',
      gradient: 'from-lime-500 to-emerald-600',
      action: isHi ? 'जांचें' : 'Check Soil',
    },
    {
      to: '/advisory',
      icon: '🌱',
      title: isHi ? 'कृषि सलाह' : 'Agronomy Advisory',
      desc: isHi ? 'मौसम अलर्ट, रोग रोकथाम और बुवाई कैलेंडर' : 'Pest alerts, weather warnings & crop tips',
      badge: isHi ? 'दैनिक सलाह' : 'Daily Advisory',
      badgeColor: 'bg-violet-100 text-violet-800 border-violet-200',
      gradient: 'from-violet-500 to-purple-600',
      action: isHi ? 'सलाह देखें' : 'View Advice',
    },
    {
      to: '/farm',
      icon: '🌾',
      title: isHi ? 'मेरा खेत प्रोफाइल' : 'My Farm Profile',
      desc: isHi ? 'भूमि क्षेत्र, जिला, सिंचाई और फसल चक्र प्रबंधन' : 'Manage acreage, soil profile & cycles',
      badge: isHi ? 'खेत विवरण' : 'Farm Profile',
      badgeColor: 'bg-rose-100 text-rose-800 border-rose-200',
      gradient: 'from-rose-500 to-pink-600',
      action: isHi ? 'प्रबंधित करें' : 'Manage Farm',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Hero Card */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-emerald-900 via-emerald-800 to-teal-900 text-white p-6 sm:p-8 shadow-xl shadow-emerald-950/20 border border-emerald-700/40">
        {/* Glow circles */}
        <div className="absolute -top-16 -right-16 w-56 h-56 rounded-full bg-emerald-400/20 blur-3xl pointer-events-none"></div>
        <div className="absolute -bottom-16 -left-16 w-56 h-56 rounded-full bg-teal-300/15 blur-3xl pointer-events-none"></div>

        <div className="relative z-10">
          <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-white/10 backdrop-blur-md text-emerald-200 text-xs font-semibold border border-white/15">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
              {isHi ? 'भारतीय किसानों के लिए एआई संबल' : 'AI Decision Support for Indian Farmers'}
            </span>
            <span className="text-xs text-emerald-300/80 font-mono">
              {isHi ? 'एमएसपी संदर्भ 2023-24' : 'MSP Reference 2023-24'}
            </span>
          </div>

          <h1 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white mb-2 leading-tight">
            {isHi ? 'स्मार्ट खेती, बेहतर मुनाफा।' : 'Empowering Farmers with AI-Driven Intelligence.'}
          </h1>
          <p className="text-sm sm:text-base text-emerald-100/90 max-w-xl leading-relaxed mb-6">
            {isHi
              ? 'फसल उपज का अनुमान लगाएं और डेमो मंडी मूल्यों की तुलना 2023-24 MSP संदर्भ से करें। वास्तविक भाव स्थानीय मंडी से सत्यापित करें।'
              : 'Estimate crop yields and compare synthetic demonstration market prices with 2023-24 MSP references. Verify actual prices with your local mandi.'}
          </p>

          <div className="flex flex-wrap items-center gap-3">
            <Link
              to="/yield"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-emerald-400 to-emerald-500 hover:from-emerald-300 hover:to-emerald-400 text-emerald-950 font-bold text-sm shadow-lg shadow-emerald-950/30 hover:scale-[1.02] active:scale-95 transition-all"
            >
              <span>{isHi ? '📊 उपज का अनुमान लगाएं' : '📊 Predict Crop Yield'}</span>
            </Link>
            <Link
              to="/market"
              className="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white font-semibold text-sm border border-white/20 backdrop-blur-sm active:scale-95 transition-all"
            >
              <span>{isHi ? '🛒 मंडी भाव तुलना' : '🛒 Compare Mandis'}</span>
            </Link>
          </div>
        </div>

        {/* Quick Stats Strip */}
        <div className="mt-8 pt-5 border-t border-emerald-700/50 grid grid-cols-2 sm:grid-cols-4 gap-4 text-center sm:text-left">
          <div>
            <div className="text-xl sm:text-2xl font-black text-white">14+</div>
            <div className="text-xs text-emerald-200/80 font-medium">
              {isHi ? 'समर्थित मुख्य फसलें' : 'Supported Crops'}
            </div>
          </div>
          <div>
            <div className="text-xl sm:text-2xl font-black text-emerald-300">26,040</div>
            <div className="text-xs text-emerald-200/80 font-medium">
              {isHi ? 'सिंथेटिक डेमो मूल्य रिकॉर्ड' : 'Synthetic Demo Price Records'}
            </div>
          </div>
          <div>
            <div className="text-xl sm:text-2xl font-black text-amber-300">2 ML Models</div>
            <div className="text-xs text-emerald-200/80 font-medium">
              {isHi ? 'उपज + मूल्य पूर्वानुमान' : 'Yield & Price Forecasters'}
            </div>
          </div>
          <div>
            <div className="text-xl sm:text-2xl font-black text-teal-300">₹ Net</div>
            <div className="text-xs text-emerald-200/80 font-medium">
              {isHi ? 'परिवहन लागत समायोजन' : 'Freight-Adjusted Payout'}
            </div>
          </div>
        </div>
      </section>

      {/* Historical MSP benchmark summary */}
      <section className="bg-white rounded-2xl p-4 shadow-sm border border-slate-200/80 flex flex-wrap items-center justify-between gap-3">
        <div className="flex items-center gap-2.5">
          <span className="w-8 h-8 rounded-lg bg-amber-100 text-amber-800 flex items-center justify-center font-bold text-sm">
            🌾
          </span>
          <div>
            <span className="text-xs font-bold text-slate-800 uppercase tracking-wide">
              {isHi ? '2023-24 एमएसपी संदर्भ दरें' : 'MSP Reference Rates (2023-24)'}
            </span>
            <p className="text-xs text-slate-500">
              {isHi ? 'भारत सरकार द्वारा निर्धारित संदर्भ दरें' : 'Official Ministry of Agriculture Reference Rates'}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span className="px-2.5 py-1 rounded-lg bg-emerald-50 border border-emerald-200 text-xs font-bold text-emerald-800">
            Wheat: ₹2,275/q
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-sky-50 border border-sky-200 text-xs font-bold text-sky-800">
            Rice: ₹2,183/q
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-amber-50 border border-amber-200 text-xs font-bold text-amber-800">
            Cotton: ₹6,620/q
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-violet-50 border border-violet-200 text-xs font-bold text-violet-800">
            Mustard: ₹5,650/q
          </span>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="space-y-3">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <span>🚀</span> {isHi ? 'प्रमुख सेवाएं व उपकरण' : 'Decision Tools & Services'}
          </h2>
          <span className="text-xs text-slate-500 font-medium">
            {isHi ? 'त्वरित चयन करें' : 'Click to launch'}
          </span>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {quickTools.map((tool) => (
            <Link
              key={tool.to}
              to={tool.to}
              className="group relative bg-white hover:bg-slate-50/80 rounded-2xl p-5 border border-slate-200/80 hover:border-emerald-300 shadow-sm hover:shadow-md transition-all duration-200 flex flex-col justify-between"
            >
              <div>
                <div className="flex items-start justify-between gap-2 mb-3">
                  <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${tool.gradient} text-white flex items-center justify-center text-2xl shadow-md group-hover:scale-110 transition-transform`}>
                    {tool.icon}
                  </div>
                  <span className={`text-[11px] font-bold px-2 py-0.5 rounded-full border ${tool.badgeColor}`}>
                    {tool.badge}
                  </span>
                </div>
                <h3 className="text-base font-bold text-slate-900 group-hover:text-emerald-700 transition-colors">
                  {tool.title}
                </h3>
                <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                  {tool.desc}
                </p>
              </div>

              <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-semibold text-emerald-700">
                <span>{tool.action}</span>
                <span className="group-hover:translate-x-1 transition-transform">→</span>
              </div>
            </Link>
          ))}
        </div>
      </section>

      {/* Advisory Notice & Transparency */}
      <footer className="rounded-2xl bg-amber-50/80 border border-amber-200/80 p-4 text-xs text-amber-900/90 flex items-start gap-3">
        <span className="text-lg flex-shrink-0">⚠️</span>
        <div className="space-y-1">
          <p className="font-semibold text-amber-950">
            {isHi ? 'पारदर्शिता एवं कानूनी सूचना (PRD अनुपालन)' : 'Transparency & Predictive Advisory Notice'}
          </p>
          <p className="text-amber-800 leading-relaxed text-[11px]">
            {isHi
              ? 'AgriAI द्वारा दिए गए उपज अनुमान एवं मूल्य पूर्वानुमान सांख्यिकीय और मशीन लर्निंग मॉडल्स पर आधारित हैं। वास्तविक उत्पादन स्थानीय वर्षा, कीट प्रकोप और मंडी की दैनिक आवक पर निर्भर करता है। एमएसपी सरकार द्वारा अधिसूचित संदर्भ मूल्य है।'
              : 'AgriAI estimates and forecasts are generated by statistical and machine learning models. Market price examples are synthetic demonstration data, not current mandi quotes. Verify actual prices locally. MSP figures shown are 2023-24 reference benchmarks, not current rates.'}
          </p>
        </div>
      </footer>
    </div>
  );
}