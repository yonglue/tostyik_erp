// src/composables/useTheme.js
import { ref, computed, watch } from 'vue'

const STORAGE_KEY = 'tostiyk_theme'
const theme = ref(localStorage.getItem(STORAGE_KEY) || 'system')
let mediaQuery = null
let initialized = false

const systemPrefersDark = ref(false)

function updateSystemPref() {
  if (typeof window !== 'undefined' && window.matchMedia) {
    systemPrefersDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
  }
}

function applyTheme() {
  if (typeof document === 'undefined') return
  const isDark =
    theme.value === 'dark' ||
    (theme.value === 'system' && systemPrefersDark.value)
  const root = document.documentElement
  root.classList.toggle('dark', isDark)
  root.style.colorScheme = isDark ? 'dark' : 'light'
}

function initTheme() {
  if (initialized || typeof window === 'undefined') return
  initialized = true

  updateSystemPref()
  applyTheme()

  mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
  const handler = (e) => {
    systemPrefersDark.value = e.matches
    if (theme.value === 'system') applyTheme()
  }
  // 兼容老浏览器
  if (mediaQuery.addEventListener) mediaQuery.addEventListener('change', handler)
  else if (mediaQuery.addListener) mediaQuery.addListener(handler)

  watch(theme, () => {
    localStorage.setItem(STORAGE_KEY, theme.value)
    applyTheme()
  })
}

export function useTheme() {
  initTheme()

  const isDark = computed(
    () => theme.value === 'dark' || (theme.value === 'system' && systemPrefersDark.value)
  )
  const resolvedTheme = computed(() => (isDark.value ? 'dark' : 'light'))

  const setTheme = (next) => {
    if (!['light', 'dark', 'system'].includes(next)) return
    theme.value = next
  }

  const cycleTheme = () => {
    const order = ['light', 'dark', 'system']
    const i = order.indexOf(theme.value)
    setTheme(order[(i + 1) % order.length])
  }

  return { theme, isDark, resolvedTheme, setTheme, cycleTheme }
}