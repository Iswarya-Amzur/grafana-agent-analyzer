/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        grafana: {
          orange: '#FF8800',
          blue: '#1F60C4',
          dark: '#111217',
          gray: '#6C7B7F'
        }
      }
    },
  },
  plugins: [],
}
