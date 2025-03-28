/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./public/**/*.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {},
    screens: {
      xs: '400px',
      sm: '640px',
      // => @media (min-width: 640px) { ... }

      md: '768px',
      // => @media (min-width: 768px) { ... }

      lg: '1024px',
      // => @media (min-width: 1024px) { ... }

      xl: '1280px',
      // => @media (min-width: 1280px) { ... }

      '2xl': '1536px'
      // => @media (min-width: 1536px) { ... }
    }
  },
  plugins: [require('daisyui'), require('@headlessui/vue'), require('@tailwindcss/forms')],
  daisyui: {
    themes: [
      {
        mytheme: {
          primary: '#1c3f68',
          secondary: '#665a36',
          accent: '#647ca4',
          neutral: '#3d4451',
          success: '#61c877',
          'base-100': '#ffffff',
          customedBlack: '#64748b'
        }
      }
    ]
  }
}
