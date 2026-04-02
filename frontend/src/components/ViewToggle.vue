<template>
  <div class="view-toggle">
    <button 
      v-for="option in viewOptions" 
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
import { ref } from 'vue'

const props = defineProps({
  modelValue: {
    type: String,
    default: 'grid-3'
  }
})

defineEmits(['update:modelValue'])

// Определяем опции прямо в компоненте, а не передаем извне
const viewOptions = ref([
  { value: 'grid-3', icon: '▦', title: 'Сетка 3 колонки' },
  { value: 'grid-2', icon: '⊞', title: 'Сетка 2 колонки' },
  { value: 'list', icon: '☰', title: 'Список' }
])
</script>

<style scoped>
.view-toggle {
  display: flex;
  gap: 0.25rem;
  background: #f1f5f9;
  padding: 0.25rem;
  border-radius: 10px;
}

.toggle-btn {
  width: 36px;
  height: 36px;
  border: none;
  background: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 1.1rem;
  transition: all 0.2s;
  color: #94a3b8;
}

.toggle-btn:hover {
  background: #e2e8f0;
  color: #2ecc71;
}

.toggle-btn.active {
  background: #2ecc71;
  color: white;
}
</style>
