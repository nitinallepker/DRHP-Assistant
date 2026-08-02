/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        darkBg: "#0B1220",
        darkCard: "#151E2D",
        primaryAccent: "#3B82F6",
        successAccent: "#22C55E",
        warningAccent: "#F59E0B",
        dangerAccent: "#EF4444",
      }
    },
  },
  plugins: [],
}
