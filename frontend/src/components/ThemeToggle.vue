<template>
  <button class="theme-toggle" @click="themeStore.toggleTheme" :title="themeStore.isDark ? 'Светлая тема' : 'Темная тема'">
    <span class="toggle-slider">
      <span class="toggle-icon sun">☀️</span>
      <span class="toggle-icon moon">🌙</span>
    </span>
    <span class="toggle-switch" :class="{ active: themeStore.isDark }"></span>
  </button>
</template>

<script setup>
import { useThemeStore } from '../stores/theme'

const themeStore = useThemeStore()
</script>

<style scoped>
.theme-toggle {
  position: relative;
  width: 60px;
  height: 32px;
  background: var(--bg-tertiary);
  border-radius: 40px;
  border: none;
  cursor: pointer;
  padding: 0;
  transition: all 0.3s;
  overflow: hidden;
}

.toggle-slider {
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

.toggle-icon {
  font-size: 14px;
  z-index: 1;
  transition: opacity 0.3s;
}

.sun {
  opacity: 1;
}

.moon {
  opacity: 0.6;
}

.toggle-switch {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 28px;
  height: 28px;
  background: white;
  border-radius: 50%;
  transition: transform 0.3s;
  box-shadow: 0 1px 3px rgba(0,0,0,0.2);
}

.toggle-switch.active {
  transform: translateX(28px);
}

.theme-toggle:hover {
  opacity: 0.9;
}

/* Темная тема для кнопки */
[data-theme="dark"] .toggle-switch {
  background: #2ecc71;
}

[data-theme="dark"] .sun {
  opacity: 0.6;
}

[data-theme="dark"] .moon {
  opacity: 1;
}
</style>