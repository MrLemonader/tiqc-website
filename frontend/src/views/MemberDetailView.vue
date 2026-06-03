<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { avatarUrl, getMember } from '@/services/api'

const route = useRoute()
const member = ref(null)
const loading = ref(true)
const error = ref('')

async function loadMember() {
  loading.value = true
  error.value = ''
  member.value = null
  try {
    const data = await getMember(route.params.slug)
    member.value = data.member
  } catch (err) {
    error.value = err.status === 404 ? 'Member not found.' : err.message
  } finally {
    loading.value = false
  }
}

onMounted(loadMember)
watch(() => route.params.slug, loadMember)
</script>

<template>
  <n-spin :show="loading">
    <p v-if="error" class="error-text">{{ error }}</p>

    <article v-else-if="member" class="detail-layout">
      <aside class="detail-aside">
        <img class="avatar-large" :src="avatarUrl(member, true)" :alt="`${member.name} avatar`" />
        <n-tag type="success">{{ member.role }}</n-tag>
      </aside>

      <section class="detail-main">
        <h1>{{ member.name }}</h1>
        <p class="muted" v-if="member.title">{{ member.title }}</p>
        <p v-if="member.email">
          <a :href="`mailto:${member.email}`">{{ member.email }}</a>
        </p>

        <n-divider />

        <h2>Introduction</h2>
        <p>{{ member.bio || 'No introduction yet.' }}</p>

        <h2>Publication Links</h2>
        <n-empty
          v-if="!member.publication_links?.length"
          description="No publication links yet."
        />
        <n-list v-else>
          <n-list-item
            v-for="publication in member.publication_links"
            :key="publication.id || `${publication.title}-${publication.url}`"
          >
            <a :href="publication.url" target="_blank" rel="noopener">
              {{ publication.title }}
            </a>
            <p class="muted">
              <span v-if="publication.journal">{{ publication.journal }}</span>
              <span v-if="publication.year"> {{ publication.year }}</span>
            </p>
          </n-list-item>
        </n-list>
      </section>
    </article>
  </n-spin>
</template>
