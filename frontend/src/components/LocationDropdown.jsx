import React, { useState, useRef, useEffect } from 'react';
import { INDIA_LOCATIONS, STATES } from '../data/indiaLocations';

/**
 * LocationDropdown
 * Hover over the field → panel slides open with:
 *   - List of Indian states (left column)
 *   - When a state is hovered → cities appear on right
 * Click a city to select it (fills both state & city/district).
 */
export default function LocationDropdown({ state, city, onStateChange, onCityChange, label = 'Location' }) {
  const [open, setOpen] = useState(false);
  const [hoveredState, setHoveredState] = useState(state || STATES[0]);
  const ref = useRef(null);

  // Close when clicking outside
  useEffect(() => {
    const handler = (e) => {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('mousedown', handler);
    return () => document.removeEventListener('mousedown', handler);
  }, []);

  const handleSelectCity = (selectedState, selectedCity) => {
    onStateChange(selectedState);
    onCityChange(selectedCity);
    setOpen(false);
  };

  return (
    <div ref={ref} className="relative" onMouseEnter={() => setOpen(true)} onMouseLeave={() => setOpen(false)}>
      <label className="block text-xs text-gray-500 mb-1">{label}</label>
      <div
        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm bg-white cursor-pointer flex items-center justify-between hover:border-green-500 transition-colors"
        onClick={() => setOpen(!open)}
      >
        <span className={state && city ? 'text-gray-800' : 'text-gray-400'}>
          {state && city ? `${city}, ${state}` : 'Hover to select state & city'}
        </span>
        <svg className={`w-4 h-4 text-gray-400 transition-transform ${open ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {open && (
        <div className="absolute z-50 top-full left-0 mt-1 w-full min-w-[340px] bg-white border border-gray-200 rounded-xl shadow-2xl flex overflow-hidden"
          style={{ maxHeight: '280px' }}>
          {/* States column */}
          <div className="w-1/2 overflow-y-auto border-r border-gray-100 bg-gray-50">
            <p className="text-[10px] font-semibold text-gray-400 uppercase px-3 pt-2 pb-1 sticky top-0 bg-gray-50">States</p>
            {STATES.map((s) => (
              <div
                key={s}
                className={`px-3 py-1.5 text-xs cursor-pointer transition-colors ${
                  hoveredState === s
                    ? 'bg-green-50 text-green-700 font-semibold'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
                onMouseEnter={() => setHoveredState(s)}
                onClick={() => { onStateChange(s); onCityChange(''); }}
              >
                {s}
              </div>
            ))}
          </div>

          {/* Cities column */}
          <div className="w-1/2 overflow-y-auto">
            <p className="text-[10px] font-semibold text-gray-400 uppercase px-3 pt-2 pb-1 sticky top-0 bg-white">Cities / Districts</p>
            {(INDIA_LOCATIONS[hoveredState] || []).map((c) => (
              <div
                key={c}
                className={`px-3 py-1.5 text-xs cursor-pointer transition-colors ${
                  city === c && state === hoveredState
                    ? 'bg-green-100 text-green-800 font-semibold'
                    : 'text-gray-700 hover:bg-green-50 hover:text-green-700'
                }`}
                onClick={() => handleSelectCity(hoveredState, c)}
              >
                {c}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
