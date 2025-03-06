module.exports = {
  content: [
    './templates/**/*.html',
    './app.py'
  ],
  theme: {
    extend: {},
  },
  plugins: [require("@tailwindcss/typography"), require("daisyui")],
}