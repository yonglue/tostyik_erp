// src/composables/useNotifications.js
//
// 全局提示：成功/拦截大弹窗 + 右上角 toast。
// 模块级单例，任何组件调用 useNotifications() 拿到的是同一份提示状态。

import { computed, ref } from 'vue'

const ERROR_KEYWORDS = ['❌', '拒绝', '不足', '失败', '错误']

function looksLikeError(msg) {
  const text = msg || ''
  return ERROR_KEYWORDS.some((kw) => text.includes(kw))
}

// ── 大弹窗（App.vue 使用）──
const successModalVisible = ref(false)
const successModalMessage = ref('')
let successTimer = null

// ── 右上角轻提示（收银台等使用）──
const toastMessage = ref('')
const toastType = ref('success')
let toastTimer = null

export function useNotifications() {
  const isErrorMessage = computed(() => looksLikeError(successModalMessage.value))

  /** 统一提示：错误/拒绝信息常驻，成功信息 2 秒后自动关闭 */
  const showSuccessModal = (msg) => {
    successModalMessage.value = msg
    successModalVisible.value = true
    if (successTimer) clearTimeout(successTimer)

    if (!looksLikeError(msg)) {
      successTimer = setTimeout(() => {
        successModalVisible.value = false
      }, 2000)
    }
  }

  const closeSuccessModal = () => {
    successModalVisible.value = false
  }

  const showToast = (msg, type = 'error') => {
    toastMessage.value = msg
    toastType.value = type
    if (toastTimer) clearTimeout(toastTimer)
    toastTimer = setTimeout(() => {
      toastMessage.value = ''
    }, 2500)
  }

  return {
    successModalVisible,
    successModalMessage,
    isErrorMessage,
    showSuccessModal,
    closeSuccessModal,
    toastMessage,
    toastType,
    showToast
  }
}
