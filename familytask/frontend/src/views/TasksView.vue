<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import TaskList from '../components/TaskList.vue'
import { apiFetch } from '../api.js'

const router = useRouter()
const tasks = ref([])
const newTask = ref('')
const error = ref('')

// Recharge la liste des tâches depuis le backend.
async function loadTasks() {
  const response = await apiFetch('/api/tasks')

  if (!response.ok) {
    error.value = 'Impossible de charger les tâches.'
    return
  }

  tasks.value = await response.json()
}

// Ajoute une tâche puis recharge la liste affichée.
async function addTask() {
  const title = newTask.value.trim()
  if (!title) return

  error.value = ''
  const params = new URLSearchParams({ title })
  const response = await apiFetch(`/api/tasks?${params}`, { method: 'POST' })

  if (!response.ok) {
    error.value = 'Impossible d’ajouter cette tâche.'
    return
  }

  newTask.value = ''
  await loadTasks()
}

// Bascule l'état d'une tâche puis recharge la liste.
async function toggle(task) {
  const response = await apiFetch(`/api/tasks/${task.id}`, { method: 'PATCH' })

  if (!response.ok) {
    error.value = 'Impossible de modifier cette tâche.'
    return
  }

  await loadTasks()
}

// Supprime une tâche puis recharge la liste.
async function remove(task) {
  const response = await apiFetch(`/api/tasks/${task.id}`, { method: 'DELETE' })

  if (!response.ok) {
    error.value = 'Impossible de supprimer cette tâche.'
    return
  }

  await loadTasks()
}

// Efface le token local et revient à l'écran de connexion.
function logout() {
  localStorage.removeItem('token')
  router.push('/login')
}

// Charge les tâches dès l'ouverture de l'écran privé.
onMounted(loadTasks)
</script>

<template>
  <main class="tasks-page">
    <header class="tasks-header">
      <div>
        <p class="eyebrow">FAMILYTASK</p>
        <h1>Ma liste de tâches</h1>
        <p class="header-subtitle">Les petites choses, en équipe.</p>
      </div>
      <button class="logout-button" type="button" @click="logout">Quitter</button>
    </header>

    <section class="card">
      <form class="task-form" @submit.prevent="addTask">
        <input v-model="newTask" type="text" placeholder="Ajouter une tâche" aria-label="Nouvelle tâche" />
        <button type="submit">Ajouter</button>
      </form>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <TaskList :tasks="tasks" @toggle="toggle" @remove="remove" />
    </section>
  </main>
</template>
