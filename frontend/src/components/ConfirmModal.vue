<template>
  <div class="modal-overlay" @click.self="$emit('cancel')" @keydown.esc="$emit('cancel')">
    <div class="modal-content confirm-modal" :class="{ danger }">
      <div class="confirm-icon">{{ danger ? '⚠️' : '❓' }}</div>
      <h3>{{ title }}</h3>
      <p class="confirm-message"><slot>{{ message }}</slot></p>
      <p v-if="danger" class="warning">Это действие нельзя отменить!</p>

      <div class="modal-actions">
        <button
          class="btn"
          :class="danger ? 'btn-danger' : 'btn-primary'"
          @click="$emit('confirm')"
          :disabled="loading"
        >
          {{ loading ? 'Подождите…' : confirmText }}
        </button>
        <button class="btn btn-secondary" @click="$emit('cancel')" :disabled="loading">
          {{ cancelText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: { type: String, default: 'Подтверждение действия' },
  message: { type: String, default: '' },
  confirmText: { type: String, default: 'Удалить' },
  cancelText: { type: String, default: 'Отмена' },
  danger: { type: Boolean, default: true },
  loading: { type: Boolean, default: false }
})

defineEmits(['confirm', 'cancel'])
</script>

<style scoped>
.confirm-modal {
  text-align: center;
  max-width: 420px;
}

.confirm-icon {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}

.confirm-modal h3 {
  margin-bottom: 0.75rem;
}

.confirm-message {
  color: var(--text-secondary);
  line-height: 1.5;
}

.confirm-message strong {
  color: var(--text-primary);
}

.warning {
  color: var(--danger-text);
  font-size: 0.9rem;
  margin-top: 0.75rem;
}

.modal-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.75rem;
}

.modal-actions .btn {
  flex: 1;
}

.btn-danger {
  background: var(--danger-text);
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #c0392b;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
