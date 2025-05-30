module.exports = {
  content: ['./templates/**/*.html', './static/css/**/*.css'],
  theme: {
    extend: {},
  },
  plugins: [
    require('tailwindcss/plugin')(({ addVariant }) => {
      addVariant('search-cancel', '&::-webkit-search-cancel-button')
    }),
  ],
}
