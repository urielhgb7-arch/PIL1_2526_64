module.exports = {
  content: [
    './*.html',
    './pages/**/*.html',
    './pages/*.html',
    './**/*.html'
  ],
  theme: {
    extend: {
      colors: {
        background: '#08090C',
        foreground: '#FFFFFF',
        card: '#0F111A',
        popover: '#1F2433',
        primary: '#7C6FF7',
        success: '#2DD4A0',
        warning: '#F5A623',
        destructive: '#F97066',
        border: 'rgba(255, 255, 255, 0.08)',
        input: '#1F2433',
        muted: 'rgba(255, 255, 255, 0.6)'
      }
    }
  },
  plugins: []
}
