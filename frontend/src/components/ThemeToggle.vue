<template>
  <button 
    class="theme-toggle" 
    :class="{ active: themeStore.isDark }"
    @click="themeStore.toggleTheme" 
    :title="themeStore.isDark ? 'Светлая тема' : 'Темная тема'"
  >
    <span class="toggle-icons">
      <span class="icon sun">☀️</span>
      <span class="icon moon">🌙</span>
    </span>
    <span class="toggle-knob"></span>
  </button>
</template>

<script setup>
import { useThemeStore } from '../stores/theme'

const themeStore = useThemeStore()
</script>

<style scoped>
.theme-toggle {
  position: relative;
  width: 64px;
  height: 32px;
  border-radius: 40px;
  background: var(--toggle-bg);
  border: 2px solid #2ecc71;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s ease;
  overflow: hidden;
}

.theme-toggle:hover {
  transform: scale(1.02);
  border-color: var(--primary-color);
}

.toggle-icons {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 8px;
  pointer-events: none;
}

.icon {
  font-size: 14px;
  z-index: 1;
  transition: opacity 0.3s;
}

.sun {
  opacity: 1;
}

.moon {
  opacity: 0.5;
}

.theme-toggle.active .sun {
  opacity: 0.5;
}

.theme-toggle.active .moon {
  opacity: 1;
}

.toggle-knob {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 24px;
  height: 24px;
  background: var(--toggle-knob);
  border-radius: 50%;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.theme-toggle.active .toggle-knob {
  transform: translateX(32px);
  background: var(--toggle-knob-active);
}
</style>
