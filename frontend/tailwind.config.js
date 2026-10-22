/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,ts,jsx,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        agri: {
          green: '#16a34a',
          leaf: '#22c55e',
          soil: '#a16207',
          sky: '#0ea5e9',
          sun: '#f59e0b',
          earth: '#4a3b2a',
        },
      },
      spacing: {
        'safe': 'env(safe-area-inset-bottom)',
      },
    },
  },
  plugins: [],
}