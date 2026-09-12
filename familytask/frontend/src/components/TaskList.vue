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
      ><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M3 6h18"/><path d="M8 6V4h8v2"/><path d="m19 6-1 15H6L5 6"/><path d="M10 11v6"/><path d="M14 11v6"/></svg></button>
    </li>
    <li v-if="tasks.length === 0" class="empty-state">
      <span class="empty-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m12 3-1.2 4.3L7 8.5l3.8 1.2L12 14l1.2-4.3L17 8.5l-3.8-1.2L12 3Z"/><path d="m19 14-.7 2.3L16 17l2.3.7L19 20l.7-2.3L22 17l-2.3-.7L19 14Z"/></svg></span>
      <span>Tout est fait pour le moment !</span>
      <small>Ajoute une tâche quand une nouvelle mission arrive.</small>
    </li>
  </ul>
</template>
