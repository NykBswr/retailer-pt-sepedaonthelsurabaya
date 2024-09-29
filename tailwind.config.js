/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './static/**/*.js',
  ],
  theme: {
    extend: {
      colors: {
        primary: "#2D3945",
        secondary: "#819EB9",
        white: "#FFFFFF",
        // F5EDED
        dark: "#1A1A1A",
        tertiary: "#1B80A0",
      },
    },
  },
  plugins: [],
}
