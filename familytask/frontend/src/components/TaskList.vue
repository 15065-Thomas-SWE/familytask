<script setup>
defineProps({
  tasks: {
    type: Array,
    required: true,
  },
})

const emit = defineEmits(['toggle', 'remove'])
</script>

<template>
  <ul class="task-list">
    <li v-for="task in tasks" :key="task.id" :class="{ completed: task.done }">
      <label>
        <input
          type="checkbox"
          :checked="task.done"
          @change="emit('toggle', task)"
        />
        <span>{{ task.title }}</span>
      </label>
      <button
        type="button"
        class="delete-task"
        title="Supprimer la tâche"
        aria-label="Supprimer la tâche"
        @click="emit('remove', task)"
      >🗑️</button>
    </li>
    <li v-if="tasks.length === 0" class="empty-state">
      <span class="empty-icon">✨</span>
      <span>Tout est fait pour le moment !</span>
      <small>Ajoute une tâche quand une nouvelle mission arrive.</small>
    </li>
  </ul>
</template>
