<template>
  <div class="view-toggle">
    <button 
      v-for="option in options" 
      :key="option.value"
      class="toggle-btn"
      :class="{ active: modelValue === option.value }"
      :title="option.title"
      @click="$emit('update:modelValue', option.value)"
    >
      {{ option.icon }}
    </button>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: String,
    default: 'grid-3'
  }
})

defineEmits(['update:modelValue'])

const options = [
  { value: 'grid-3', icon: '▦', title: 'Сетка 3 колонки' },
  { value: 'grid-2', icon: '⊞', title: 'Сетка 2 колонки' },
  { value: 'list', icon: '☰', title: 'Список' }
]
</script>

<style scoped>
@import '@/assets/styles/view-toggle.css';
</style>