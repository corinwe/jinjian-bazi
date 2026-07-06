const API_BASE = '/api/v1'

export async function analyzeRequest(params) {
  const res = await fetch(`${API_BASE}/engine/debug`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `请求失败 (${res.status})`)
  }
  return res.json()
}

export async function register(username, password) {
  const res = await fetch(`${API_BASE}/auth/register`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `注册失败 (${res.status})`)
  }
  return res.json()
}

export async function login(username, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ username, password }),
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({}))
    throw new Error(err.detail || `登录失败 (${res.status})`)
  }
  return res.json()
}

export async function getHistory() {
  const token = localStorage.getItem('token')
  const res = await fetch(`${API_BASE}/analyses`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  if (!res.ok) throw new Error('获取历史失败')
  return res.json()
}

export async function getAnalysis(id) {
  const token = localStorage.getItem('token')
  const res = await fetch(`${API_BASE}/analyses/${id}`, {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
  })
  if (!res.ok) throw new Error('获取分析失败')
  return res.json()
}

export async function saveAnalysis(data) {
  const token = localStorage.getItem('token')
  const res = await fetch(`${API_BASE}/analyses`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(data),
  })
  if (!res.ok) throw new Error('保存失败')
  return res.json()
}
