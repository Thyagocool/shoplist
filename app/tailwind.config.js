/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eef5ff',
          100: '#d9e6ff',
          200: '#b3ccff',
          300: '#80adff',
          400: '#5c95f7',
          500: '#4287f5',
          600: '#3370d9',
          700: '#295bb8',
          800: '#1f4796',
          900: '#173775',
        },
      },
    },
  },
  plugins: [],
}
