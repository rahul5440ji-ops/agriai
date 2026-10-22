import React from 'react';
import { t } from '../i18n';
import useAppStore from '../store';

const TIPS = [
  {
    en: 'Sow according to the recommended season for your crop and region.',
    hi: 'अपने क्षेत्र और फसल के लिए अनुशंसित सीजन के अनुसार बोवें।',
  },
  {
    en: 'Maintain soil pH between 6.0 and 7.5 for most field crops.',
    hi: 'अधिकांश फसलों के लिए मिट्टी का pH 6.0 से 7.5 के बीच रखें।',
  },
  {
    en: 'Apply balanced N-P-K based on a recent soil test, not guesswork.',
    hi: 'ताजा परीक्षण के आधार पर संतुलित N-P-K डालें, अनुमान नहीं।',
  },
  {
    en: 'Use irrigation efficiently — drip or sprinkler where possible.',
    hi: 'जहां संभव हो ड्रिप या स्प्रिंकलर का उपयोग करके सिंचाई का सदुपयोग करें।',
  },
];

export default function Advisory() {
  const { language } = useAppStore();

  return (
    <div className="space-y-4">
      <h2 className="text-lg font-semibold text-agri-earth">
        {t('nav.advisory', language)}
      </h2>

      <div className="bg-white rounded-xl shadow p-4">
        <p className="text-sm text-gray-600 leading-relaxed">
          {language === 'hi'
            ? 'यह सल्लाह सामान्य कृषि ज्ञान पर आधारित है और आपके खेत की विशेष परिस्थितियों पर लागू नहीं हो सकती।'
            : 'This advice is general agronomy knowledge and may not apply to your specific field conditions.'}
        </p>
      </div>

      <div className="space-y-3">
        {TIPS.map((tip, i) => (
          <div key={i} className="bg-white rounded-xl shadow p-4 flex gap-3">
            <span className="text-agri-green text-lg">✓</span>
            <p className="text-sm text-gray-700">
              {language === 'hi' ? tip.hi : tip.en}
            </p>
          </div>
        ))}
      </div>

      <div className="bg-amber-50 border border-amber-200 rounded-xl p-4">
        <p className="text-xs font-semibold text-amber-800 mb-1">
          {language === 'hi' ? 'सावधानी' : 'Caution'}
        </p>
        <p className="text-xs text-amber-700 leading-relaxed">
          {language === 'hi'
            ? 'कीटनाशक या रसायनों के संबंध में किसी भी खुलरस्त सल्लाह के लिए सत्यापित कृषि स्रोतों और सुरक्षा निर्देशों को देखें।'
            : 'For any pesticide or chemical guidance, consult verified agricultural sources and safety instructions.'}
        </p>
      </div>
    </div>
  );
}