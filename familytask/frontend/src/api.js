// Retourne le token d'authentification conservé dans le navigateur.
export function getToken() {
  return localStorage.getItem('token') || ''
}

// Construit l'en-tête Authorization pour les appels authentifiés.
export function authHeaders() {
  const token = getToken()
  return token ? { Authorization: `Bearer ${token}` } : {}
}

// Centralise les appels API et ajoute automatiquement le token disponible.
export function apiFetch(path, options = {}) {
  return fetch(path, {
    ...options,
    headers: { ...authHeaders(), ...(options.headers || {}) },
  })
}
