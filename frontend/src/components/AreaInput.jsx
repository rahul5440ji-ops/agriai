import React, { useState } from 'react';

const HECTARE_TO_ACRE = 2.47105;
const ACRE_TO_HECTARE = 1 / HECTARE_TO_ACRE;

/**
 * AreaInput — Hectare / Acre toggle input.
 *
 * KEY DESIGN: `rawInput` is local state (what the user actually typed).
 * The parent only receives values in HECTARES via onChange.
 * This prevents the "input snaps / can't type" bug caused by
 * converting parent value → display → back → parent on every keystroke.
 */
export default function AreaInput({ onChange, required = false, label = 'Field Area' }) {
  const [unit, setUnit] = useState('hectare');
  const [rawInput, setRawInput] = useState('');

  const handleChange = (e) => {
    const raw = e.target.value;
    setRawInput(raw); // always let user type freely

    if (raw === '') {
      onChange('');
      return;
    }
    const num = parseFloat(raw);
    if (isNaN(num) || num <= 0) return;

    // Push converted-to-hectare value up to parent
    const inHectare = unit === 'hectare' ? raw : String(num * ACRE_TO_HECTARE);
    onChange(inHectare);
  };

  const switchUnit = (newUnit) => {
    if (newUnit === unit) return;
    // Convert the displayed number to the new unit so the field doesn't clear
    const num = parseFloat(rawInput);
    if (!isNaN(num) && num > 0) {
      const converted =
        unit === 'hectare'
          ? (num * HECTARE_TO_ACRE).toFixed(4)
          : (num * ACRE_TO_HECTARE).toFixed(4);
      setRawInput(converted);
    }
    setUnit(newUnit);
  };

  // Conversion hint shown below the input
  const num = parseFloat(rawInput);
  const hint =
    !isNaN(num) && num > 0
      ? unit === 'hectare'
        ? `≈ ${(num * HECTARE_TO_ACRE).toFixed(3)} acres`
        : `≈ ${(num * ACRE_TO_HECTARE).toFixed(4)} hectares`
      : '';

  return (
    <div>
      <div className="flex items-center justify-between mb-1">
        <label className="text-xs text-gray-500">{label}</label>

        {/* Hectare / Acre pill toggle */}
        <div className="flex items-center bg-gray-100 rounded-full p-0.5 gap-0.5">
          {['hectare', 'acre'].map((u) => (
            <button
              key={u}
              type="button"
              onClick={() => switchUnit(u)}
              className={`text-[10px] font-semibold px-2.5 py-0.5 rounded-full transition-all ${
                unit === u
                  ? 'bg-green-600 text-white shadow'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {u === 'hectare' ? 'Hectare' : 'Acre'}
            </button>
          ))}
        </div>
      </div>

      <div className="relative">
        <input
          type="number"
          step="any"
          min="0"
          className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm pr-16 focus:border-green-500 focus:ring-1 focus:ring-green-200 outline-none transition"
          value={rawInput}
          onChange={handleChange}
          placeholder={`e.g. 2.5 ${unit === 'hectare' ? 'hectares' : 'acres'}`}
          required={required}
        />
        <span className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-gray-400 pointer-events-none font-medium">
          {unit === 'hectare' ? 'ha' : 'ac'}
        </span>
      </div>

      {hint && (
        <p className="text-[10px] text-gray-400 mt-0.5">{hint}</p>
      )}
    </div>
  );
}
