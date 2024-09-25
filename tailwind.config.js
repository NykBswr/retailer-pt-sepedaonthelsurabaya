/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./resources/**/*.blade.php",
    "./resources/**/*.js",
    "./resources/**/*.vue",
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

