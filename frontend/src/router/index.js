import { createRouter, createWebHistory } from 'vue-router'

import HomeView from '@/views/HomeView.vue'
import MemberDetailView from '@/views/MemberDetailView.vue'
import MembersView from '@/views/MembersView.vue'
import ProfileView from '@/views/ProfileView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'home', component: HomeView },
    { path: '/members', name: 'members', component: MembersView },
    { path: '/members/:slug', name: 'member-detail', component: MemberDetailView },
    { path: '/profile', name: 'profile', component: ProfileView },
  ],
  scrollBehavior() {
    return { top: 0 }
  },
})

export default router
