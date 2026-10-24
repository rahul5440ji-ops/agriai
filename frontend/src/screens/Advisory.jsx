import React, { useState } from 'react';
import useAppStore from '../store';

const ADVISORIES = [
  {
    category: 'irrigation',
    icon: '💧',
    titleEn: 'Critical Irrigation Windows for Rabi Wheat',
    titleHi: 'रबी गेहूं के लिए संवेदनशील सिंचाई अवस्थाएं',
    descEn: 'Crown root initiation (CRI) at 21-25 days after sowing is the most critical stage. Missing this irrigation can reduce yield by up to 30%. Subsequent stages: Tillering, Jointing, Flowering, and Milking.',
    descHi: 'बुवाई के 21-25 दिन बाद सीआरआई (मुकुट जड़ निकलने की अवस्था) सबसे महत्वपूर्ण है। इस समय सिंचाई न करने से 30% तक उपज घट सकती है। इसके बाद कल्ले निकलते समय और दुग्धावस्था में सिंचाई दें।',
    tagEn: 'High Priority',
    tagHi: 'अति आवश्यक',
    color: 'bg-sky-100 text-sky-800 border-sky-200',
  },
  {
    category: 'pest',
    icon: '🐛',
    titleEn: 'Yellow Rust & Aphid Monitoring in Mustard and Wheat',
    titleHi: 'सरसों व गेहूं में पीला रतुआ और माहू (चेपा) की रोकथाम',
    descEn: 'Inspect leaf undersides in the morning. If yellow powdery pustules appear, spray Propiconazole 25% EC @ 1ml/L. For mustard aphids, spray Dimethoate 30% EC @ 1.5ml/L when 10% plants show infestation.',
    descHi: 'सुबह के समय पत्तियों की निचली सतह देखें। पीला चूर्ण दिखने पर प्रोपीकोनाजोल 25% ईसी 1 मिली/लीटर की दर से छिड़कें। सरसों में माहू दिखने पर डाईमेथोएट 30% ईसी का छिड़काव करें।',
    tagEn: 'Disease Alert',
    tagHi: 'रोग चेतावनी',
    color: 'bg-amber-100 text-amber-800 border-amber-200',
  },
  {
    category: 'nutrient',
    icon: '🌱',
    titleEn: 'Zinc & Micronutrient Deficiency Management',
    titleHi: 'जिंक और सूक्ष्म पोषक तत्वों की कमी का निदान',
    descEn: 'In intensive paddy-wheat rotations, Zinc deficiency causes khaira disease and leaf bronzing. Apply 25 kg/ha Zinc Sulphate (21%) heptahydrate as basal dose or foliar spray 0.5% ZnSO4 with 0.25% lime.',
    descHi: 'धान-गेहूं फसल चक्र में जिंक की कमी से पत्तियां भूरी पड़ने लगती हैं। बुवाई पर 25 किग्रा/हेक्टेयर जिंक सल्फेट डालें अथवा 0.5% जिंक सल्फेट + 0.25% बुझे चूने के घोल का छिड़काव करें।',
    tagEn: 'Nutrition',
    tagHi: 'पोषण सलाह',
    color: 'bg-emerald-100 text-emerald-800 border-emerald-200',
  },
  {
    category: 'harvest',
    icon: '🚜',
    titleEn: 'Safe Storage Moisture & Post-Harvest Realization',
    titleHi: 'भंडारण में सुरक्षित नमी स्तर व फसल रख-रखाव',
    descEn: 'Grain moisture must be below 12% for safe storage to prevent fungus and weevils. Drying grain properly in the sun before taking to mandi prevents moisture deduction by traders.',
    descHi: 'अनाज को सुरक्षित रखने हेतु उसमें नमी 12% से कम होनी चाहिए। मंडी ले जाने से पहले अनाज को अच्छी तरह धूप में सुखाएं ताकि व्यापारी नमी की कटौती न कर सकें।',
    tagEn: 'Post-Harvest',
    tagHi: 'कटाई उपरांत',
    color: 'bg-violet-100 text-violet-800 border-violet-200',
  },
];

export default function Advisory() {
  const { language } = useAppStore();
  const isHi = language === 'hi';
  const [filter, setFilter] = useState('all');

  const filtered = ADVISORIES.filter((a) => filter === 'all' || a.category === filter);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight flex items-center gap-2">
            <span>🌱</span>
            {isHi ? 'कृषि एवं फसल वैज्ञानिक सलाह' : 'Agronomy & Crop Care Advisory'}
          </h1>
          <p className="text-xs text-slate-500 mt-0.5">
            {isHi
              ? 'भारतीय कृषि अनुसंधान परिषद (ICAR) एवं कृषि विश्वविद्यालयों के दिशा-निर्देश'
              : 'Evidence-based agronomic guidelines for irrigation, pest control & crop nutrition'}
          </p>
        </div>
        <span className="px-2.5 py-1 rounded-full bg-violet-100 text-violet-800 text-[11px] font-bold border border-violet-200">
          ICAR Guidelines
        </span>
      </div>

      {/* Filter Tabs */}
      <div className="flex items-center gap-2 overflow-x-auto no-scrollbar pb-1">
        {[
          { id: 'all', label: isHi ? 'सभी सलाहें' : 'All Topics', icon: '📋' },
          { id: 'irrigation', label: isHi ? 'सिंचाई' : 'Irrigation', icon: '💧' },
          { id: 'pest', label: isHi ? 'कीट व रोग' : 'Pests & Diseases', icon: '🐛' },
          { id: 'nutrient', label: isHi ? 'उर्वरक पोषण' : 'Nutrients', icon: '🌱' },
          { id: 'harvest', label: isHi ? 'कटाई व भंडारण' : 'Post-Harvest', icon: '🚜' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setFilter(tab.id)}
            className={`flex items-center gap-1.5 px-3.5 py-1.5 rounded-xl text-xs font-bold whitespace-nowrap transition-all ${
              filter === tab.id
                ? 'bg-emerald-600 text-white shadow-sm'
                : 'bg-white border border-slate-200/80 text-slate-600 hover:bg-slate-50'
            }`}
          >
            <span>{tab.icon}</span>
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      {/* Advisory Cards List */}
      <div className="grid grid-cols-1 gap-4">
        {filtered.map((item, idx) => (
          <div
            key={idx}
            className="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/80 shadow-sm hover:border-slate-300 transition-all space-y-3"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-slate-100 flex items-center justify-center text-xl">
                  {item.icon}
                </div>
                <div>
                  <h3 className="font-bold text-base text-slate-900 leading-snug">
                    {isHi ? item.titleHi : item.titleEn}
                  </h3>
                  <span className="text-[10px] text-slate-400 uppercase font-semibold">
                    {item.category}
                  </span>
                </div>
              </div>
              <span className={`text-[10px] font-bold px-2.5 py-0.5 rounded-full border ${item.color}`}>
                {isHi ? item.tagHi : item.tagEn}
              </span>
            </div>

            <p className="text-xs text-slate-700 leading-relaxed bg-slate-50 p-3.5 rounded-2xl border border-slate-200/60">
              {isHi ? item.descHi : item.descEn}
            </p>
          </div>
        ))}
      </div>

      {/* Caution & Safety Notice */}
      <div className="rounded-2xl bg-amber-50 border border-amber-200 p-4 text-xs text-amber-900 space-y-1">
        <p className="font-bold flex items-center gap-1.5">
          <span>⚠️</span>
          <span>{isHi ? 'सुरक्षा एवं कीटनाशक सावधानी' : 'Agrochemical Safety Notice'}</span>
        </p>
        <p className="text-amber-800 text-[11px] leading-relaxed">
          {isHi
            ? 'किसी भी रासायनिक कीटनाशक का उपयोग करते समय दस्ताने और मास्क अवश्य पहनें। हवा की विपरीत दिशा में कभी छिड़काव न करें। उपयोग के बाद खाली डिब्बे को सुरक्षित नष्ट करें।'
            : 'Always wear protective gear when handling crop protection products. Never spray against prevailing wind. Follow pre-harvest waiting periods (PHI) carefully before taking produce to market.'}
        </p>
      </div>
    </div>
  );
}