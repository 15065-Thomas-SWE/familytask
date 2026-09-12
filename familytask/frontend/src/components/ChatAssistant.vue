<script setup>
import { onBeforeUnmount, ref } from 'vue'
import { apiFetch } from '../api.js'

const emit = defineEmits(['refresh-tasks'])

const message = ref('')
const messages = ref([
  { role: 'assistant', text: 'Bonjour, que puis-je ajouter à la liste de la famille ?' },
])
const loading = ref(false)
const listening = ref(false)
const error = ref('')

let recognition = null

async function sendMessage() {
  const text = message.value.trim()
  if (!text || loading.value) return

  messages.value.push({ role: 'user', text })
  message.value = ''
  error.value = ''
  loading.value = true

  try {
    const params = new URLSearchParams({ message: text })
    const response = await apiFetch(`/api/assistant?${params}`, { method: 'POST' })
    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      error.value = data.detail || 'L’assistant ne peut pas répondre pour le moment.'
      return
    }

    messages.value.push({ role: 'assistant', text: data.reply || 'Je n’ai pas de réponse.' })
    emit('refresh-tasks')
  } catch {
    error.value = 'Le serveur est momentanément indisponible.'
  } finally {
    loading.value = false
  }
}

function toggleVoiceInput() {
  if (listening.value) {
    recognition?.stop()
    return
  }

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
  if (!SpeechRecognition) {
    error.value = 'La dictée vocale n’est pas disponible dans ce navigateur.'
    return
  }

  recognition = new SpeechRecognition()
  recognition.lang = 'fr-FR'
  recognition.interimResults = false
  recognition.continuous = false
  recognition.onstart = () => {
    error.value = ''
    listening.value = true
  }
  recognition.onresult = (event) => {
    message.value = `${message.value} ${event.results[0][0].transcript}`.trim()
  }
  recognition.onerror = () => {
    error.value = 'La dictée vocale n’a pas pu démarrer.'
  }
  recognition.onend = () => {
    listening.value = false
  }
  recognition.start()
}

onBeforeUnmount(() => recognition?.stop())
</script>

<template>
  <section class="assistant-chat" aria-label="Assistant familial">
    <div class="assistant-messages" aria-live="polite">
      <p v-for="(item, index) in messages" :key="index" class="assistant-message" :class="`assistant-message--${item.role}`">
        {{ item.text }}
      </p>
      <p v-if="loading" class="assistant-message assistant-message--assistant assistant-message--loading">L’assistant réfléchit…</p>
    </div>

    <p v-if="error" class="form-error" role="alert">{{ error }}</p>

    <form class="assistant-form" @submit.prevent="sendMessage">
      <input
        v-model="message"
        type="text"
        placeholder="Demander une tâche…"
        aria-label="Message à l’assistant"
        :disabled="loading"
      />
      <button
        class="assistant-mic"
        type="button"
        :class="{ 'assistant-mic--active': listening }"
        :aria-label="listening ? 'Arrêter la dictée' : 'Dicter un message'"
        :title="listening ? 'Arrêter la dictée' : 'Dicter un message'"
        @click="toggleVoiceInput"
      >
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="9" y="2" width="6" height="12" rx="3"/><path d="M5 10a7 7 0 0 0 14 0"/><path d="M12 21v-3"/><path d="M8 21h8"/></svg>
      </button>
      <button type="submit" :disabled="loading || !message.trim()">Envoyer</button>
    </form>
  </section>
</template>
