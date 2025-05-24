/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'osrs-gold': '#FFD700',
        'osrs-brown': '#8B4513',
        'osrs-green': '#228B22',
        'osrs-red': '#DC143C',
      }
    },
  },
  plugins: [],
} 