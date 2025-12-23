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
      name: 'bookdetail',
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

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  const isLoggedIn = !!token

  // 1. 이미 로그인했는데 로그인(/login)이나 회원가입(/signup) 페이지로 가려는 경우
  if (isLoggedIn && (to.name === 'login' || to.name === 'signup')) {
    alert('이미 로그인된 상태입니다.')
    next({ name: 'home' }) // 홈으로 튕겨냄
  } 
  else {
    next() // 그 외의 경우는 정상 이동
  }
})

export default router