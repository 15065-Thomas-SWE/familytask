<script setup>
import ChatAssistant from '../components/ChatAssistant.vue'

const emit = defineEmits(['refresh-tasks'])
</script>

<template>
  <main class="assistant-page">
    <header class="assistant-header">
      <p class="eyebrow">FAMILYTASK</p>
      <h1>Assistant familial</h1>
      <p class="header-subtitle">Ajoutez une tâche en quelques mots.</p>
    </header>

    <section class="card assistant-section">
      <ChatAssistant @refresh-tasks="emit('refresh-tasks')" />
    </section>
  </main>
</template>
