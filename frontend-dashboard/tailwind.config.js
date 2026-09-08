/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      colors: {
        bg: '#F5F7FA',
        surface: '#FFFFFF',
        'surface-raised': '#FFFFFF',
        ink: '#12181F',
        muted: '#5B6672',
        border: '#E2E6EA',

        navy: {
          50: '#EEF2F7',
          100: '#D6E0EB',
          400: '#3B5D82',
          600: '#1F3A5F',
          700: '#182F4C',
          900: '#0D1B2E',
        },

        risk: {
          low: '#2F7A4F',
          'low-bg': '#E7F3EC',
          medium: '#C77D22',
          'medium-bg': '#FBEEDD',
          high: '#C0392B',
          'high-bg': '#FBE7E4',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'ui-monospace', 'monospace'],
      },
      borderRadius: {
        sm: '4px',
        DEFAULT: '6px',
        lg: '10px',
      },
      boxShadow: {
        card: '0 1px 2px rgba(13, 27, 46, 0.06), 0 1px 8px rgba(13, 27, 46, 0.04)',
      },
    },
  },
  plugins: [],
};
