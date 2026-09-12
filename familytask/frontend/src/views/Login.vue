<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '../api.js'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

// Authentifie le membre avec l'API et conserve son token.
async function submit() {
  error.value = ''

  if (!email.value.trim() || !password.value) {
    error.value = 'Saisissez votre email et votre mot de passe.'
    return
  }

  loading.value = true

  try {
    const params = new URLSearchParams({ email: email.value.trim(), password: password.value })
    const response = await apiFetch(`/api/login?${params}`, { method: 'POST' })
    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      error.value = data.detail || 'Email ou mot de passe incorrect.'
      return
    }

    localStorage.setItem('token', data.token)
    await router.push('/tasks')
  } catch {
    error.value = 'Le serveur est momentanément indisponible.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-panel">
      <p class="eyebrow">FAMILYTASK</p>
      <h1>Bon retour</h1>
      <p class="auth-intro">Retrouvez les missions de votre famille.</p>

      <form class="auth-form" @submit.prevent="submit">
        <label for="email">Email</label>
        <input id="email" v-model="email" type="email" autocomplete="email" placeholder="vous@exemple.fr" />

        <label for="password">Mot de passe</label>
        <input id="password" v-model="password" type="password" autocomplete="current-password" placeholder="Votre mot de passe" />

        <p v-if="error" class="form-error" role="alert">{{ error }}</p>
        <button type="submit" :disabled="loading">{{ loading ? 'Connexion...' : 'Se connecter' }}</button>
      </form>

      <p class="auth-link">Pas encore de compte ? <router-link to="/signup">Créer ma famille</router-link></p>
    </section>
  </main>
</template>
