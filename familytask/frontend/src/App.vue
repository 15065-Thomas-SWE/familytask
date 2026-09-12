<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { apiFetch, getToken } from './api.js'

const route = useRoute()
const router = useRouter()
const member = ref(null)

// Récupère le membre connecté à partir du token conservé dans le navigateur.
async function loadMember() {
  const token = getToken()

  if (!token) {
    member.value = null
    return
  }

  const response = await apiFetch('/api/me')

  if (response.ok) {
    member.value = await response.json()
    return
  }

  localStorage.removeItem('token')
  member.value = null
}

// Demande la déconnexion au serveur, puis termine toujours la session locale.
async function logout() {
  try {
    await apiFetch('/api/logout', { method: 'POST' })
  } catch {
    // La session locale est tout de même supprimée si le serveur est indisponible.
  } finally {
    localStorage.removeItem('token')
    member.value = null
    await router.push('/login')
  }
}

// Charge le membre au démarrage puis après chaque navigation.
onMounted(loadMember)
watch(() => route.fullPath, loadMember)
</script>

<template>
  <div class="app-shell">
    <header v-if="member" class="top-bar">
      <div class="top-bar-identity">
        <span class="top-bar-mark">F</span>
        <span>Bonjour <strong>{{ member.name }}</strong></span>
      </div>
      <button type="button" @click="logout">Se déconnecter</button>
    </header>

    <!-- Affiche la vue correspondant à l'URL courante. -->
    <router-view />

    <nav v-if="member" class="bottom-tabs" aria-label="Navigation principale">
      <router-link to="/tasks" class="bottom-tab"><span class="tab-icon">✓</span><span>Tâches</span></router-link>
      <router-link v-if="member.is_admin" to="/famille" class="bottom-tab"><span class="tab-icon">⌂</span><span>Famille</span></router-link>
    </nav>
  </div>
</template>
