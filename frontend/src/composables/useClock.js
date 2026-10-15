// src/composables/useClock.js
//
// 顶栏时钟。自行注册/清理定时器，调用方无需关心生命周期。

import { onMounted, onUnmounted, ref } from 'vue'

export function useClock() {
  const currentDateTime = ref('')
  let timer = null

  const updateClock = () => {
    const now = new Date()
    const yy = String(now.getFullYear()).slice(-2)
    const mm = String(now.getMonth() + 1).padStart(2, '0')
    const dd = String(now.getDate()).padStart(2, '0')
    const hh = String(now.getHours()).padStart(2, '0')
    const min = String(now.getMinutes()).padStart(2, '0')
    const ss = String(now.getSeconds()).padStart(2, '0')
    currentDateTime.value = `${dd}/${mm}/${yy} ${hh}:${min}:${ss}`
  }

  onMounted(() => {
    updateClock()
    timer = setInterval(updateClock, 1000)
  })

  onUnmounted(() => {
    if (timer) clearInterval(timer)
  })

  return { currentDateTime, updateClock }
}
