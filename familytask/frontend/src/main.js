import { createApp } from 'vue'
import App from './App.vue'
import router from './router.js' // Importe le routeur de l'application.
import './style.css'

createApp(App).use(router).mount('#app') // Monte l'application avec le routeur activé.
