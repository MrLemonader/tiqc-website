<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'

import { avatarUrl, getMembers } from '@/services/api'

const members = ref([])
const loading = ref(true)
const error = ref('')

async function loadMembers() {
  loading.value = true
  error.value = ''
  try {
    const data = await getMembers()
    members.value = data.members || []
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}

onMounted(loadMembers)
</script>

<template>
  <section>
    <div class="section-heading">
      <div>
        <p class="eyebrow">Directory</p>
        <h1>Active Members</h1>
      </div>
    </div>

    <n-spin :show="loading">
      <p v-if="error" class="error-text">{{ error }}</p>
      <n-empty v-else-if="!members.length" description="No active members yet." />
      <div v-else class="member-grid">
        <RouterLink
          v-for="member in members"
          :key="member.id"
          class="member-card"
          :to="`/members/${member.slug}`"
        >
          <img :src="avatarUrl(member, true)" :alt="`${member.name} avatar`" />
          <div>
            <h2>{{ member.name }}</h2>
            <p class="muted">{{ member.role }}<span v-if="member.title"> · {{ member.title }}</span></p>
            <p v-if="member.bio" class="bio-preview">{{ member.bio }}</p>
          </div>
        </RouterLink>
      </div>
    </n-spin>
  </section>
</template>
