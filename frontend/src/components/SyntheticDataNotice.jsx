import React from 'react';

export default function SyntheticDataNotice({ isHi }) {
  return (
    <aside
      role="note"
      className="rounded-xl border border-amber-300 bg-amber-50 p-3 text-xs text-amber-950"
    >
      <strong className="block">
        {isHi ? 'सिंथेटिक डेमो डेटा — वास्तविक मंडी भाव नहीं' : 'Synthetic demo data — not real mandi prices'}
      </strong>
      <span className="mt-1 block leading-relaxed">
        {isHi
          ? 'ये उदाहरण के लिए बनाए गए मूल्य हैं, वर्तमान मंडी भाव नहीं। बिक्री के फैसले से पहले स्थानीय मंडी से वास्तविक भाव की पुष्टि करें।'
          : 'These generated examples are not current market quotes. Verify actual prices with your local mandi before making selling decisions.'}
      </span>
    </aside>
  );
}
