import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import LoginView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'signup',
      component: () => import('../views/SignupView.vue')
    },
    {
      path: '/book/:isbn',
      name: 'BookDetail',
      component: () => import('../views/BookDetailView.vue')
    },
    {
    path: '/search',
    name: 'search',
    component: () => import('../views/SearchView.vue')
    },
    {
    path: '/profile',
    name: 'profile',
    component: () => import('../views/ProfileView.vue')
    }
  ]
})

export default router