<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { apiFetch } from '../api.js'

const router = useRouter()
const family = ref('')
const name = ref('')
const lien = ref('parent')
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

// Propose les liens familiaux les plus courants dans le formulaire.
const familyLinks = ['parent', 'mère', 'père', 'fille', 'fils', 'frère', 'sœur', 'autre']

// Crée la famille et connecte immédiatement son administrateur.
async function submit() {
  error.value = ''

  if (!family.value.trim() || !name.value.trim() || !email.value.trim() || !password.value) {
    error.value = 'Renseignez tous les champs obligatoires.'
    return
  }

  loading.value = true

  try {
    const params = new URLSearchParams({
      email: email.value.trim(),
      password: password.value,
      name: name.value.trim(),
      family: family.value.trim(),
      lien: lien.value,
    })
    const response = await apiFetch(`/api/signup?${params}`, { method: 'POST' })
    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      error.value = data.detail || 'Impossible de créer la famille.'
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
      <p class="eyebrow">ORGANISATION FAMILIALE</p>
      <h1>Créer ma famille</h1>
      <p class="auth-intro">Commencez votre espace partagé en quelques secondes.</p>

      <form class="auth-form" @submit.prevent="submit">
        <label for="family">Nom de famille</label>
        <input id="family" v-model="family" type="text" autocomplete="organization" placeholder="Ex. Durand" />

        <label for="name">Prénom</label>
        <input id="name" v-model="name" type="text" autocomplete="given-name" placeholder="Ex. Marie" />

        <label for="lien">Lien de parenté</label>
        <select id="lien" v-model="lien">
          <option v-for="familyLink in familyLinks" :key="familyLink" :value="familyLink">{{ familyLink }}</option>
        </select>

        <label for="email">Email</label>
        <input id="email" v-model="email" type="email" autocomplete="email" placeholder="vous@exemple.fr" />

        <label for="password">Mot de passe</label>
        <input id="password" v-model="password" type="password" autocomplete="new-password" placeholder="Votre mot de passe" />

        <p v-if="error" class="form-error" role="alert">{{ error }}</p>
        <button type="submit" :disabled="loading">{{ loading ? 'Création...' : 'Créer ma famille' }}</button>
      </form>

      <p class="auth-link">Déjà un compte ? <router-link to="/login">Se connecter</router-link></p>
    </section>
  </main>
</template>
