<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { getCurrentUser, login } from '@/services/api'

const emit = defineEmits(['login-success'])

const route = useRoute()
const router = useRouter()
const campusId = ref('')
const loading = ref(false)
const checking = ref(true)
const error = ref('')

function redirectTarget() {
  const target = route.query.redirect
  return typeof target === 'string' && target.startsWith('/') ? target : '/profile'
}

async function submitLogin() {
  error.value = ''
  const trimmedCampusId = campusId.value.trim()
  if (!trimmedCampusId) {
    error.value = 'Campus ID is required.'
    return
  }

  loading.value = true
  try {
    const data = await login(trimmedCampusId)
    emit('login-success', data.user)
    router.push(redirectTarget())
  } catch (err) {
    error.value = err.data?.error === 'invalid_campus_id'
      ? 'No account was found for that campus ID.'
      : err.message
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    const data = await getCurrentUser()
    emit('login-success', data.user)
    router.push(redirectTarget())
  } catch (err) {
    // Visitor mode is expected here.
  } finally {
    checking.value = false
  }
})
</script>

<template>
  <section class="auth-panel">
    <div class="section-heading">
      <div>
        <p class="eyebrow">Member access</p>
        <h1>Login</h1>
      </div>
    </div>

    <n-spin :show="checking">
      <n-alert v-if="error" class="profile-alert" type="error" role="alert">
        {{ error }}
      </n-alert>

      <n-form label-placement="top" @submit.prevent="submitLogin">
        <n-form-item label="Campus ID">
          <n-input
            v-model:value="campusId"
            autofocus
            placeholder="20240001"
            @keyup.enter="submitLogin"
          />
        </n-form-item>

        <div class="save-row">
          <n-button type="primary" :loading="loading" @click="submitLogin">
            {{ loading ? 'Logging in...' : 'Login' }}
          </n-button>
        </div>
      </n-form>
    </n-spin>
  </section>
</template>
