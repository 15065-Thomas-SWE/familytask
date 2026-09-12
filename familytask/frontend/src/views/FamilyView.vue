<script setup>
import { computed, onMounted, ref } from 'vue'
import { apiFetch } from '../api.js'

const member = ref(null)
const members = ref([])
const links = ref([])
const tasks = ref([])
const error = ref('')
const loading = ref(false)
const newName = ref('')
const newLink = ref('')
const newEmail = ref('')
const newPassword = ref('')
const newIsAdmin = ref(false)
const linkToAdd = ref('')

// Indique si le compte affiché est bien administrateur.
const isAdmin = computed(() => Boolean(member.value?.is_admin))

// Charge les membres, les liens et les tâches de la famille connectée.
async function loadFamily() {
  error.value = ''
  loading.value = true

  try {
    const [meResponse, membersResponse, linksResponse, tasksResponse] = await Promise.all([
      apiFetch('/api/me'),
      apiFetch('/api/members'),
      apiFetch('/api/liens'),
      apiFetch('/api/tasks/famille'),
    ])

    if ([meResponse, membersResponse, linksResponse, tasksResponse].some(response => !response.ok)) {
      error.value = 'Impossible de charger les informations de la famille.'
      return
    }

    member.value = await meResponse.json()
    members.value = await membersResponse.json()
    links.value = await linksResponse.json()
    tasks.value = await tasksResponse.json()
  } catch {
    error.value = 'Le serveur est momentanément indisponible.'
  } finally {
    loading.value = false
  }
}

// Crée un compte dans la famille de l'administrateur connecté.
async function addMember() {
  error.value = ''
  const params = new URLSearchParams({
    email: newEmail.value.trim(),
    password: newPassword.value,
    name: newName.value.trim(),
    lien: newLink.value,
    is_admin: String(newIsAdmin.value),
  })
  const response = await apiFetch(`/api/members?${params}`, { method: 'POST' })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    error.value = data.detail || 'Impossible de créer ce compte.'
    return
  }

  newName.value = ''
  newEmail.value = ''
  newPassword.value = ''
  newLink.value = links.value[0] || ''
  newIsAdmin.value = false
  await loadFamily()
}

// Ajoute un nouveau lien de parenté à la liste de la famille.
async function addLink() {
  const label = linkToAdd.value.trim()
  if (!label) return

  error.value = ''
  const params = new URLSearchParams({ label })
  const response = await apiFetch(`/api/liens?${params}`, { method: 'POST' })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    error.value = data.detail || 'Impossible d’ajouter ce lien.'
    return
  }

  links.value = await response.json()
  linkToAdd.value = ''
  if (!newLink.value) newLink.value = links.value[0] || ''
}

// Supprime un membre après confirmation et recharge les données familiales.
async function removeMember(target) {
  if (target.id === member.value?.id) return
  if (!window.confirm(`Supprimer le compte de ${target.name} et ses tâches ?`)) return

  error.value = ''
  const response = await apiFetch(`/api/members/${target.id}`, { method: 'DELETE' })

  if (!response.ok) {
    const data = await response.json().catch(() => ({}))
    error.value = data.detail || 'Impossible de supprimer ce compte.'
    return
  }

  await loadFamily()
}

// Retourne le prénom du membre chargé d'une tâche.
function memberName(memberId) {
  return members.value.find(item => item.id === memberId)?.name || 'Non assignée'
}

// Crée les initiales affichées dans l'avatar d'un membre.
function memberInitials(name) {
  return name.split(' ').map(part => part[0]).join('').slice(0, 2).toUpperCase()
}

// Choisit une couleur stable pour chaque avatar à partir de son identifiant.
function avatarColor(id) {
  return `avatar-color-${(id % 6) + 1}`
}

// Charge les données de la famille à l'ouverture de la vue.
onMounted(async () => {
  await loadFamily()
  newLink.value = links.value[0] || ''
})
</script>

<template>
  <main class="family-page">
    <header class="family-header">
      <p class="eyebrow">ESPACE ADMINISTRATEUR</p>
      <h1>Ma famille</h1>
      <p class="header-subtitle">Gérez les comptes, les liens et les tâches partagées.</p>
    </header>

    <p v-if="error" class="form-error family-error" role="alert">{{ error }}</p>
    <p v-if="loading" class="family-loading">Chargement de la famille...</p>

    <section class="card family-section">
      <div class="section-heading">
        <div>
          <p class="eyebrow">COMPTES</p>
          <h2>Membres de la famille</h2>
        </div>
        <span class="section-count">{{ members.length }}</span>
      </div>

      <ul class="member-list">
        <li v-for="familyMember in members" :key="familyMember.id" class="member-row">
          <span class="member-avatar" :class="avatarColor(familyMember.id)">{{ memberInitials(familyMember.name) }}</span>
          <div>
            <strong>{{ familyMember.name }}</strong>
            <span class="member-detail">{{ familyMember.lien }} · {{ familyMember.email }}</span>
          </div>
          <div class="member-actions">
            <span v-if="familyMember.is_admin" class="admin-badge">admin</span>
            <button v-if="familyMember.id !== member?.id" type="button" class="danger-button" @click="removeMember(familyMember)">Supprimer</button>
          </div>
        </li>
      </ul>
    </section>

    <section class="card family-section">
      <h2>Ajouter un membre</h2>
      <form class="family-form" @submit.prevent="addMember">
        <label for="member-name">Prénom</label>
        <input id="member-name" v-model="newName" required type="text" placeholder="Prénom" />
        <label for="member-link">Lien de parenté</label>
        <select id="member-link" v-model="newLink" required>
          <option v-for="link in links" :key="link" :value="link">{{ link }}</option>
        </select>
        <label for="member-email">Email</label>
        <input id="member-email" v-model="newEmail" required type="email" placeholder="membre@exemple.fr" />
        <label for="member-password">Mot de passe</label>
        <input id="member-password" v-model="newPassword" required type="password" placeholder="Mot de passe" />
        <label class="checkbox-label" for="member-admin">
          <input id="member-admin" v-model="newIsAdmin" type="checkbox" />
          Administrateur
        </label>
        <button type="submit">Ajouter le membre</button>
      </form>
    </section>

    <section class="card family-section">
      <h2>Liens de parenté</h2>
      <form class="inline-form" @submit.prevent="addLink">
        <input v-model="linkToAdd" type="text" placeholder="Ex. cousine" aria-label="Nouveau lien de parenté" />
        <button type="submit">Ajouter</button>
      </form>
      <div class="link-list">
        <span v-for="link in links" :key="link" class="link-chip">{{ link }}</span>
      </div>
    </section>

    <section class="card family-section">
      <div class="section-heading">
        <div>
          <p class="eyebrow">SUIVI</p>
          <h2>Tâches de la famille</h2>
        </div>
        <span class="section-count">{{ tasks.length }}</span>
      </div>
      <ul class="family-task-list">
        <li v-for="task in tasks" :key="task.id">
          <span :class="{ 'task-done': task.done }">{{ task.title }}</span>
          <small>{{ memberName(task.member_id) }}</small>
        </li>
        <li v-if="tasks.length === 0" class="family-empty">Aucune tâche familiale pour le moment.</li>
      </ul>
    </section>
  </main>
</template>
