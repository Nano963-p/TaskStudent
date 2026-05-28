import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import TaskList  from '../views/TaskList.vue'
import Login     from '../views/Login.vue'
import Register  from '../views/Register.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/',          redirect: '/dashboard' },
    { path: '/dashboard', component: Dashboard, meta: { requiresAuth: true } },
    { path: '/tasks',     component: TaskList,  meta: { requiresAuth: true } },
    { path: '/login',     component: Login,     meta: { guest: true } },
    { path: '/register',  component: Register,  meta: { guest: true } },
  ],
})

router.beforeEach((to, _from, next) => {
  const token = localStorage.getItem('access_token')
  if (to.meta.requiresAuth && !token) return next('/login')
  if (to.meta.guest && token)         return next('/dashboard')
  next()
})

export default router
