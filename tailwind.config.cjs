module.exports = {
    content: ["./src/**/*.{html,js,svelte}"],  theme: {
    extend: {
      fontFamily: {
        "sans": ["Ubuntu", "Segoe UI", "Roboto", "Oxygen", "Cantarell", "Open Sans", "Helvetica Neue", "sans-serif"]
      }
    },
  },
  plugins: [
    require("daisyui")
  ],
}