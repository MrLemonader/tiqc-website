import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import LoginView from '@/views/LoginView.vue'
import MemberDetailView from '@/views/MemberDetailView.vue'
import MembersView from '@/views/MembersView.vue'
import ProfileView from '@/views/ProfileView.vue'
import { getCurrentUser } from '@/services/api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/login', name: 'login', component: LoginView },
    { path: '/members', name: 'members', component: MembersView },
    { path: '/members/:slug', name: 'member-detail', component: MemberDetailView },
    { path: '/profile', name: 'profile', component: ProfileView, meta: { requiresAuth: true } },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth) {
    return true
  }

  try {
    await getCurrentUser()
    return true
  } catch (error) {
    return {
      name: 'login',
      query: { redirect: to.fullPath },
    }
  }
})

export default router
