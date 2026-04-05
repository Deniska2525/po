import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    isDark: localStorage.getItem('theme') === 'dark' || 
            (window.matchMedia('(prefers-color-scheme: dark)').matches && !localStorage.getItem('theme'))
  }),
  
  actions: {
    toggleTheme() {
      this.isDark = !this.isDark
      this._applyTheme()
    },
    
    setTheme(isDark) {
      this.isDark = isDark
      this._applyTheme()
    },
    
    _applyTheme() {
      if (this.isDark) {
        document.documentElement.setAttribute('data-theme', 'dark')
        localStorage.setItem('theme', 'dark')
      } else {
        document.documentElement.removeAttribute('data-theme')
        localStorage.setItem('theme', 'light')
      }
    },
    
    init() {
      this._applyTheme()
    }
  }
})