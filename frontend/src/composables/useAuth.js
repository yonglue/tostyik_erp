// src/composables/useAuth.js
//
// 登录 / 登出 / 重置管理员密码，以及登录态在 localStorage 中的持久化。
// 从 App.vue 抽出：Header、Sidebar 等组件也能复用同一份状态来源。

import { ref } from 'vue'
import { apiFetch, setToken, clearToken } from '../utils/api'
import { useI18n } from './useI18n'

const LOGGED_IN_KEY = 'tostiyk_logged_in'
const USERNAME_KEY = 'tostiyk_username'
const CURRENT_USER_KEY = 'tostiyk_current_user'

function readStoredRole() {
  try {
    const stored = localStorage.getItem(CURRENT_USER_KEY)
    if (stored) return JSON.parse(stored).role
  } catch (e) {
    // 本地数据损坏时忽略，回落到默认角色
  }
  return 'super_admin'
}

// ── 模块级单例状态：多处调用 useAuth() 共享同一份登录态 ──
const isLoggedIn = ref(localStorage.getItem(LOGGED_IN_KEY) === 'true')
const currentAdminUser = ref(localStorage.getItem(USERNAME_KEY) || 'admin')
const currentUserObj = ref({
  username: localStorage.getItem(USERNAME_KEY) || 'admin',
  role: readStoredRole()
})

const loginForm = ref({ username: '', password: '' })
const loginError = ref('')
const resetMessage = ref('')
const resetModalVisible = ref(false)
const resetPinInput = ref('')

export function useAuth() {
  const { t } = useI18n()

  const handleLogin = async () => {
    loginError.value = ''
    resetMessage.value = ''
    if (!loginForm.value.username || !loginForm.value.password) {
      loginError.value = '请输入账号和密码'
      return
    }
    try {
      const res = await apiFetch('/api/auth/login', {
        method: 'POST',
        body: JSON.stringify(loginForm.value)
      })
      if (res.ok) {
        const data = await res.json()
        isLoggedIn.value = true
        currentAdminUser.value = data.username

        // 同步更新响应式用户对象，让收银台和顶部栏瞬间刷新
        currentUserObj.value = {
          username: data.username,
          role: data.role || 'super_admin'
        }

        // 保存访问令牌：之后所有 apiFetch 会自动带 Authorization 头
        setToken(data.access_token)

        localStorage.setItem(LOGGED_IN_KEY, 'true')
        localStorage.setItem(USERNAME_KEY, data.username)
        localStorage.setItem(CURRENT_USER_KEY, JSON.stringify({
          username: data.username,
          role: data.role || 'super_admin'
        }))
      } else {
        const errData = await res.json()
        loginError.value = errData.detail || '登录失败'
      }
    } catch (e) {
      loginError.value = '服务器连接失败'
    }
  }

  const handleLogout = () => {
    isLoggedIn.value = false
    currentUserObj.value = { username: 'admin', role: 'super_admin' }
    clearToken()
    localStorage.removeItem(LOGGED_IN_KEY)
    localStorage.removeItem(USERNAME_KEY)
    localStorage.removeItem(CURRENT_USER_KEY)
    loginForm.value.username = ''
    loginForm.value.password = ''
  }

  const openResetModal = () => {
    loginError.value = ''
    resetMessage.value = ''
    resetPinInput.value = ''
    resetModalVisible.value = true
  }

  const submitResetPassword = async () => {
    loginError.value = ''
    resetMessage.value = ''
    if (!resetPinInput.value) return

    try {
      const res = await apiFetch('/api/auth/reset-admin', {
        method: 'POST',
        body: JSON.stringify({ security_pin: resetPinInput.value })
      })
      if (res.ok) {
        resetModalVisible.value = false
        resetMessage.value = t.value.resetSuccess || "密码已成功重置为 'tostiyk2026'"
      } else {
        const errData = await res.json()
        loginError.value = errData.detail || '安全密钥验证失败'
        resetModalVisible.value = false
      }
    } catch (e) {
      loginError.value = '服务器连接失败'
      resetModalVisible.value = false
    }
  }

  return {
    isLoggedIn,
    currentAdminUser,
    currentUserObj,
    loginForm,
    loginError,
    resetMessage,
    resetModalVisible,
    resetPinInput,
    handleLogin,
    handleLogout,
    openResetModal,
    submitResetPassword
  }
}
