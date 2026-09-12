<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import TaskList from '../components/TaskList.vue'
import { apiFetch } from '../api.js'

const router = useRouter()
const tasks = ref([])
const members = ref([])
const currentMember = ref(null)
const newTask = ref('')
const assignedMemberId = ref('')
const error = ref('')

const completedTasks = computed(() => tasks.value.filter(task => task.done).length)
const assignableMembers = computed(() => currentMember.value?.is_admin
  ? members.value
  : members.value.filter(familyMember => familyMember.id === currentMember.value?.id))
const progressPercent = computed(() => tasks.value.length
  ? Math.round((completedTasks.value / tasks.value.length) * 100)
  : 0)

// Recharge la liste des tâches depuis le backend.
async function loadTasks() {
  const [response, membersResponse] = await Promise.all([
    apiFetch('/api/tasks'),
    apiFetch('/api/members'),
  ])

  if (!response.ok || !membersResponse.ok) {
    error.value = 'Impossible de charger les tâches.'
    return
  }

  tasks.value = await response.json()
  members.value = await membersResponse.json()
  const meResponse = await apiFetch('/api/me')
  if (meResponse.ok) currentMember.value = await meResponse.json()
  if (currentMember.value) {
    assignedMemberId.value = String(currentMember.value.id)
  }
}

// Ajoute une tâche puis recharge la liste affichée.
async function addTask() {
  const title = newTask.value.trim()
  if (!title) return

  error.value = ''
  const params = new URLSearchParams({ title })
  if (assignedMemberId.value) params.set('member_id', assignedMemberId.value)
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
        <select v-model="assignedMemberId" aria-label="Assigner la tâche à">
          <option v-for="familyMember in assignableMembers" :key="familyMember.id" :value="String(familyMember.id)">
            Pour {{ familyMember.name }}
          </option>
        </select>
        <button type="submit">Ajouter</button>
      </form>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <section class="progress-panel" aria-label="Progression des tâches">
        <div class="progress-heading">
          <div>
            <p class="progress-kicker">AVANCEMENT</p>
            <strong>{{ completedTasks }} sur {{ tasks.length }} tâche{{ tasks.length > 1 ? 's' : '' }} terminée{{ completedTasks > 1 ? 's' : '' }}</strong>
          </div>
          <span class="progress-percent">{{ progressPercent }}%</span>
        </div>
        <div class="progress-track" role="progressbar" :aria-valuenow="progressPercent" aria-valuemin="0" aria-valuemax="100" aria-label="Pourcentage de tâches terminées">
          <div class="progress-fill" :style="{ width: `${progressPercent}%` }"></div>
        </div>
        <p class="progress-message">
          {{ tasks.length === 0 ? 'Ajoutez une tâche pour commencer.' : progressPercent === 100 ? 'Bravo, tout est terminé !' : 'Encore un petit effort, vous avancez bien.' }}
        </p>
      </section>
      <TaskList :tasks="tasks" @toggle="toggle" @remove="remove" />
    </section>
  </main>
</template>
