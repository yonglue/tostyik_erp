// src/composables/useAuth.js
//
// 登录 / 登出 / 重置管理员密码，以及登录态在 localStorage 中的持久化。

import { ref } from 'vue'
import { apiFetch, setToken, clearToken } from '../utils/api'
import { useI18n } from './useI18n'

const LOGGED_IN_KEY = 'tostiyk_logged_in'
const USERNAME_KEY = 'tostiyk_username'
const CURRENT_USER_KEY = 'tostiyk_current_user'

function readStoredUser() {
  try {
    const stored = localStorage.getItem(CURRENT_USER_KEY)
    if (stored) return JSON.parse(stored)
  } catch (e) {}
  return { username: 'admin', role: 'super_admin', permissions: ['*'] }
}

const initialUser = readStoredUser()

const isLoggedIn = ref(localStorage.getItem(LOGGED_IN_KEY) === 'true')
const currentAdminUser = ref(localStorage.getItem(USERNAME_KEY) || 'admin')
const currentUserObj = ref(initialUser)

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

        // 🌟 核心：完整保存后端返回的 role 与 permissions 数组
        const userData = {
          username: data.username,
          role: data.role || 'staff',
          permissions: data.permissions || []
        }

        currentUserObj.value = userData
        setToken(data.access_token)

        localStorage.setItem(LOGGED_IN_KEY, 'true')
        localStorage.setItem(USERNAME_KEY, data.username)
        localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(userData))
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
    currentUserObj.value = { username: 'admin', role: 'super_admin', permissions: ['*'] }
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