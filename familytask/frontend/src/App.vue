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
        <span class="top-bar-mark" aria-hidden="true">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9"/><path d="M9 20v-6h6v6"/></svg>
        </span>
        <span class="top-bar-brand">FamilyTask</span>
        <span class="top-bar-greeting">Bonjour <strong>{{ member.name }}</strong></span>
      </div>
      <button class="logout-icon" type="button" title="Se déconnecter" aria-label="Se déconnecter" @click="logout">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/><path d="M21 19V5a2 2 0 0 0-2-2h-6"/></svg>
      </button>
    </header>

    <!-- Affiche la vue correspondant à l'URL courante. -->
    <router-view />

    <nav v-if="member" class="bottom-tabs" aria-label="Navigation principale">
      <router-link to="/tasks" class="bottom-tab"><span class="tab-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m5 12 4 4L19 6"/></svg></span><span>Tâches</span></router-link>
      <router-link to="/assistant" class="bottom-tab"><span class="tab-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v2"/><path d="M12 19v2"/><path d="m4.22 4.22 1.42 1.42"/><path d="m18.36 18.36 1.42 1.42"/><path d="M3 12h2"/><path d="M19 12h2"/><path d="m4.22 19.78 1.42-1.42"/><path d="m18.36 5.64 1.42-1.42"/><circle cx="12" cy="12" r="3"/></svg></span><span>Assistant</span></router-link>
      <router-link v-if="member.is_admin" to="/famille" class="bottom-tab"><span class="tab-icon" aria-hidden="true"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="m3 10 9-7 9 7"/><path d="M5 9v11h14V9"/><path d="M9 20v-6h6v6"/></svg></span><span>Famille</span></router-link>
    </nav>
  </div>
</template>
