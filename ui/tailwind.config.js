/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,jsx}'],
  theme: {
    extend: {
      fontFamily: {
        display: ['"Plus Jakarta Sans"', 'sans-serif'],
        body: ['Inter', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      colors: {
        teal: {
          400: '#2DD4BF',
          500: '#14B8A6',
          600: '#0D9488',
          700: '#0F766E',
        },
        amber: {
          400: '#FBBF24',
          500: '#F59E0B',
          600: '#D97706',
        },
        danger: '#DC2626',
        success: '#059669',
        'bg-dark': '#020617',
        'bg-mid': '#0F172A',
        'bg-card': 'rgba(15, 23, 42, 0.55)',
        'bg-elevated': 'rgba(30, 41, 59, 0.50)',
        text: '#F1F5F9',
        'text-muted': '#94A3B8',
        'text-subtle': '#64748B',
        border: '#1E293B',
        'border-hover': '#334155',
      },
      animation: {
        'pulse-glow': 'pulse-glow 3s ease-in-out infinite',
        'fade-up': 'fade-up 0.6s ease-out forwards',
      },
      keyframes: {
        'pulse-glow': { '0%, 100%': { opacity: '0.4' }, '50%': { opacity: '0.8' } },
        'fade-up': { from: { opacity: '0', transform: 'translateY(24px)' }, to: { opacity: '1', transform: 'translateY(0)' } },
      },
    },
  },
  plugins: [],
}
