<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink, RouterView, useRoute, useRouter } from 'vue-router'
import { PersonCircleOutline } from '@vicons/ionicons5'

import { getCurrentUser, logout } from '@/services/api'

const route = useRoute()
const router = useRouter()
const user = ref(null)
const loadingUser = ref(true)
const loggingOut = ref(false)

const navItems = [
  { label: 'Home', to: '/' },
  { label: 'Members', to: '/members' },
  { label: 'My Profile', to: '/profile' },
]

const userLabel = computed(() => user.value?.name || 'Not logged in')

async function loadUser() {
  loadingUser.value = true
  try {
    const data = await getCurrentUser()
    user.value = data.user
  } catch (error) {
    user.value = null
  } finally {
    loadingUser.value = false
  }
}

function setUser(nextUser) {
  user.value = nextUser
}

async function logoutUser() {
  loggingOut.value = true
  try {
    await logout()
    user.value = null
    router.push('/')
  } finally {
    loggingOut.value = false
  }
}

onMounted(loadUser)
</script>

<template>
  <n-config-provider>
    <n-message-provider>
      <div class="app-shell">
        <header class="site-header">
          <RouterLink class="brand" to="/">TIQC Lab</RouterLink>
          <nav class="nav-links" aria-label="Primary">
            <RouterLink
              v-for="item in navItems"
              :key="item.to"
              :class="{ active: route.path === item.to }"
              :to="item.to"
            >
              {{ item.label }}
            </RouterLink>
          </nav>
          <div class="header-actions">
            <RouterLink
              v-if="!loadingUser && !user"
              class="login-link"
              :class="{ active: route.path === '/login' }"
              to="/login"
            >
              Login
            </RouterLink>
            <div class="user-pill">
              <n-icon size="18">
                <PersonCircleOutline />
              </n-icon>
              <span>{{ loadingUser ? 'Checking...' : userLabel }}</span>
            </div>
            <n-button
              v-if="user"
              size="small"
              quaternary
              :loading="loggingOut"
              @click="logoutUser"
            >
              Logout
            </n-button>
          </div>
        </header>

        <main class="page-wrap">
          <RouterView v-slot="{ Component }">
            <component
              :is="Component"
              @login-success="setUser"
              @profile-updated="loadUser"
            />
          </RouterView>
        </main>
      </div>
    </n-message-provider>
  </n-config-provider>
</template>
