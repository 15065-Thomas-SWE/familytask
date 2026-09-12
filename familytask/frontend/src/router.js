import { createRouter, createWebHistory } from 'vue-router'
import { apiFetch } from './api.js'
import Login from './views/Login.vue'
import Signup from './views/Signup.vue'
import TasksView from './views/TasksView.vue'
import FamilyView from './views/FamilyView.vue'

// Décrit les écrans accessibles dans l'application.
const routes = [
  { path: '/', redirect: '/tasks' },
  { path: '/login', component: Login },
  { path: '/signup', component: Signup },
  { path: '/tasks', component: TasksView, meta: { requiresAuth: true } },
  { path: '/famille', component: FamilyView, meta: { requiresAuth: true, requiresAdmin: true } },
  { path: '/taches', redirect: '/tasks' },
]

// Crée le routeur avec des URLs normales compatibles avec le serveur web.
const router = createRouter({
  history: createWebHistory(),
  routes,
})

// Empêche l'accès aux écrans privés sans token d'authentification.
router.beforeEach(async (to) => {
  const hasToken = Boolean(localStorage.getItem('token'))

  if (to.meta.requiresAuth && !hasToken) return '/login'
  if ((to.path === '/login' || to.path === '/signup') && hasToken) return '/tasks'

  if (to.meta.requiresAdmin) { // Vérifie le statut administrateur avant d'ouvrir l'écran famille.
    const response = await apiFetch('/api/me') // Demande au backend le membre authentifié.
    if (!response.ok) return '/login' // Redirige vers la connexion si le token n'est plus valide.
    const member = await response.json() // Lit les informations du membre connecté.
    if (!member.is_admin) return '/tasks' // Redirige les membres non administrateurs vers leurs tâches.
  }

  return true
})

export default router
