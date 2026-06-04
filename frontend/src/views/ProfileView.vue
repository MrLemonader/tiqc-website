<script setup>
import { computed, onMounted, ref } from 'vue'

import { avatarUrl, getCurrentUser, getProfile, updateProfile, uploadAvatar } from '@/services/api'

const emit = defineEmits(['profile-updated'])

const user = ref(null)
const member = ref(null)
const loading = ref(true)
const saving = ref(false)
const uploading = ref(false)
const loginRequired = ref(false)
const avatarInput = ref(null)
const avatarVersion = ref(Date.now())
const statusMessage = ref('')
const statusType = ref('info')
const currentYear = new Date().getFullYear()
const profileForm = ref(null)
const formRules = {
  email: {
    type: 'email',
    required: false,
    message: 'Please enter a valid email address.',
    trigger: ['blur', 'input'],
  },
}
const form = ref({
  email: '',
  bio: '',
  publication_links: [],
})

const previewAvatar = computed(() => {
  if (!member.value?.avatar_url) {
    return avatarUrl(member.value)
  }
  return `${member.value.avatar_url}?t=${avatarVersion.value}`
})

function setStatus(text, type = 'info') {
  statusMessage.value = text
  statusType.value = type
}

function syncForm(nextMember) {
  form.value = {
    email: nextMember.email || '',
    bio: nextMember.bio || '',
    publication_links: (nextMember.publication_links || []).map((link, index) => ({
      title: link.title || '',
      journal: link.journal || '',
      year: link.year || null,
      url: link.url || '',
      display_order: link.display_order || (index + 1) * 10,
    })),
  }
}

async function loadProfile() {
  loading.value = true
  loginRequired.value = false
  setStatus('')
  try {
    const [meData, profileData] = await Promise.all([getCurrentUser(), getProfile()])
    user.value = meData.user
    member.value = profileData.member
    avatarVersion.value = Date.now()
    syncForm(profileData.member)
  } catch (error) {
    if (error.status === 401) {
      loginRequired.value = true
    } else {
      setStatus(error.message, 'error')
    }
  } finally {
    loading.value = false
  }
}

function addPublication() {
  form.value.publication_links.push({
    title: '',
    journal: '',
    year: null,
    url: '',
    display_order: (form.value.publication_links.length + 1) * 10,
  })
  setStatus('New publication link added. Fill in title and URL, then save profile.', 'info')
}

function removePublication(index) {
  form.value.publication_links.splice(index, 1)
}

function normalizeYear(value) {
  if (value === null || value === undefined || value === '') {
    return null
  }
  const year = Number(value)
  return Number.isFinite(year) ? year : null
}

function cleanPublicationLinks() {
  return form.value.publication_links
    .map((link, index) => ({
      title: link.title.trim(),
      journal: link.journal?.trim() || null,
      year: normalizeYear(link.year),
      url: link.url.trim(),
      display_order: (index + 1) * 10,
    }))
    .filter((link) => link.title || link.url)
}

function validatePublicationLinks(links) {
  const incompleteIndex = links.findIndex((link) => !link.title || !link.url)
  if (incompleteIndex !== -1) {
    throw new Error(`Publication link ${incompleteIndex + 1} requires title and URL.`)
  }
}

async function saveProfile() {
  saving.value = true
  try {
    await profileForm.value?.validate()
    const publicationLinks = cleanPublicationLinks()
    validatePublicationLinks(publicationLinks)
    const data = await updateProfile({
      email: form.value.email,
      bio: form.value.bio,
      publication_links: publicationLinks,
    })
    member.value = data.member
    syncForm(data.member)
    setStatus('Profile saved.', 'success')
    emit('profile-updated')
  } catch (error) {
    setStatus(error.message, 'error')
  } finally {
    saving.value = false
  }
}

function triggerAvatarPicker() {
  avatarInput.value?.click()
}

async function handleAvatarChange(event) {
  const rawFile = event.target.files?.[0]
  if (!rawFile) return

  uploading.value = true
  try {
    const data = await uploadAvatar(rawFile)
    member.value = {
      ...member.value,
      avatar_url: data.avatar_url,
    }
    avatarVersion.value = Date.now()
    setStatus('Avatar uploaded.', 'success')
  } catch (error) {
    setStatus(error.message, 'error')
  } finally {
    uploading.value = false
    event.target.value = ''
  }
}

onMounted(loadProfile)
</script>

<template>
  <div v-if="loading" class="loading-panel">
    <n-spin />
  </div>

  <template v-else>
    <section v-if="loginRequired" class="notice-panel">
      <h1>Login required</h1>
      <p>Login with your campus ID before editing your profile.</p>
      <div class="button-row">
        <RouterLink class="primary-link" to="/login?redirect=/profile">
          Login
        </RouterLink>
      </div>
    </section>

    <section v-else-if="member" class="profile-grid">
      <div class="section-heading full-span">
        <div>
          <p class="eyebrow">Self service</p>
          <h1>My Profile</h1>
        </div>
      </div>

      <n-card title="Basic information">
        <dl class="info-list">
          <dt>Name</dt>
          <dd>{{ member.name }}</dd>
          <dt>Role</dt>
          <dd>{{ member.role }}</dd>
          <dt>Title</dt>
          <dd>{{ member.title || '-' }}</dd>
          <dt>Campus ID</dt>
          <dd>{{ member.campus_id }}</dd>
          <dt>Account</dt>
          <dd>{{ user?.role || 'member' }}</dd>
        </dl>
      </n-card>

      <n-card title="Avatar">
        <div class="avatar-uploader">
          <img class="avatar-large" :src="previewAvatar" :alt="`${member.name} avatar`" />
          <input
            ref="avatarInput"
            class="visually-hidden-file"
            type="file"
            accept=".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp"
            :disabled="uploading"
            @change="handleAvatarChange"
          />
          <n-button :loading="uploading" @click="triggerAvatarPicker">
            Upload avatar
          </n-button>
          <p v-if="uploading" class="muted">Uploading avatar...</p>
        </div>
      </n-card>

      <n-card class="full-span" title="Profile details">
        <n-alert
          v-if="statusMessage"
          class="profile-alert"
          :type="statusType"
          role="status"
        >
          {{ statusMessage }}
        </n-alert>
        <n-form
          ref="profileForm"
          :model="form"
          :rules="formRules"
          label-placement="top"
          @submit.prevent="saveProfile"
        >
          <n-form-item label="Email">
            <n-input v-model:value="form.email" placeholder="name@example.edu" />
          </n-form-item>
          <n-form-item label="Bio">
            <n-input
              v-model:value="form.bio"
              type="textarea"
              :autosize="{ minRows: 5, maxRows: 10 }"
              show-count
              placeholder="Write a short personal introduction shown on your member detail page."
            />
          </n-form-item>

          <div class="form-section-title">
            <div>
              <h2>Publication Links</h2>
              <p class="section-note">Add lightweight links to papers, preprints, profiles, or project pages.</p>
            </div>
            <n-button type="primary" secondary size="small" @click="addPublication">
              Add link
            </n-button>
          </div>

          <n-empty
            v-if="!form.publication_links.length"
            description="No publication links yet."
          />
          <div
            v-for="(publication, index) in form.publication_links"
            v-else
            :key="index"
            class="publication-editor-row"
          >
            <n-card embedded :bordered="false" class="publication-editor-card">
              <div class="publication-editor-fields">
                <n-form-item label="Title" :show-feedback="false">
                  <n-input v-model:value="publication.title" placeholder="Required" />
                </n-form-item>
                <n-form-item label="Journal" :show-feedback="false">
                  <n-input v-model:value="publication.journal" placeholder="Optional" />
                </n-form-item>
                <n-form-item label="Year" :show-feedback="false">
                  <n-input-number
                    v-model:value="publication.year"
                    :min="1900"
                    :max="currentYear + 1"
                    :show-button="false"
                    clearable
                    placeholder="Optional"
                  />
                </n-form-item>
                <n-form-item label="URL" :show-feedback="false">
                  <n-input v-model:value="publication.url" placeholder="Required" />
                </n-form-item>
                <div class="publication-actions">
                  <n-popconfirm
                    positive-text="Delete"
                    negative-text="Cancel"
                    @positive-click="removePublication(index)"
                  >
                    <template #trigger>
                      <n-button type="error" ghost>
                        Delete
                      </n-button>
                    </template>
                    Delete this publication link?
                  </n-popconfirm>
                </div>
              </div>
            </n-card>
          </div>

          <div class="save-row">
            <n-button type="primary" :loading="saving" @click="saveProfile">
              {{ saving ? 'Saving...' : 'Save profile' }}
            </n-button>
          </div>
        </n-form>
      </n-card>
    </section>
  </template>
</template>
