const DEFAULT_AVATAR = '/static/images/default-avatar.svg'

async function request(path, options = {}) {
  const response = await fetch(path, {
    credentials: 'include',
    ...options,
  })

  const data = await response.json().catch(() => ({}))

  if (!response.ok) {
    const error = new Error(data.error || `Request failed: ${response.status}`)
    error.status = response.status
    error.data = data
    throw error
  }

  return data
}

export function avatarUrl(member, bustCache = false) {
  const url = member?.avatar_url || DEFAULT_AVATAR
  return bustCache && member?.avatar_url ? `${url}?t=${Date.now()}` : url
}

export function getCurrentUser() {
  return request('/api/me')
}

export function login(campusId, password) {
  return request('/api/login', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ campus_id: campusId, password }),
  })
}

export function logout() {
  return request('/api/logout', {
    method: 'POST',
  })
}

export function getMembers() {
  return request('/api/members')
}

export function getMember(slug) {
  return request(`/api/members/${encodeURIComponent(slug)}`)
}

export function getProfile() {
  return request('/api/profile')
}

export function updateProfile(payload) {
  return request('/api/profile', {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function changePassword(payload) {
  return request('/api/password', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export function uploadAvatar(file) {
  const formData = new FormData()
  formData.append('avatar', file)

  return request('/api/profile/avatar', {
    method: 'POST',
    body: formData,
  })
}
