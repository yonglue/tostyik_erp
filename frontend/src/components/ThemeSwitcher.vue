<!-- src/components/ThemeSwitcher.vue -->
<template>
  <button
    @click="toggleTheme"
    class="group relative flex items-center justify-center w-10 h-10 rounded-2xl
           border border-slate-200/80 dark:border-slate-700/60
           shadow-2xs backdrop-blur-md
           transition-all duration-300 ease-out hover:scale-105 active:scale-95"
    :class="{
      'bg-amber-50/80 hover:bg-amber-100 dark:bg-slate-800/70 dark:hover:bg-slate-700/80': theme === 'light',
      'bg-indigo-50/80 hover:bg-indigo-100 dark:bg-indigo-900/40 dark:hover:bg-indigo-800/60': theme === 'dark',
      'bg-sky-50/80 hover:bg-sky-100 dark:bg-slate-800/70 dark:hover:bg-slate-700/80': theme === 'system'
    }"
    :title="`当前: ${currentOption.label}，点击切换`"
  >
    <Transition name="spin-fade" mode="out-in">
      <component 
        :is="currentOption.icon" 
        :size="20" 
        :stroke-width="2.5" 
        :key="currentOption.value"
        :class="{
          'text-amber-500': theme === 'light',
          'text-indigo-500 dark:text-indigo-400': theme === 'dark',
          'text-sky-500': theme === 'system'
        }"
      />
    </Transition>
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { Sun, Moon, MonitorSmartphone } from 'lucide-vue-next'
import { useTheme } from '../composables/useTheme'

const { theme, setTheme } = useTheme()

const options = [
  { value: 'light',  icon: Sun,                label: '白天' },
  { value: 'dark',   icon: Moon,               label: '黑夜' },
  { value: 'system', icon: MonitorSmartphone,  label: '跟随系统' },
]

// 当前选中的选项
const currentOption = computed(() => {
  return options.find(o => o.value === theme.value) || options[0]
})

// 单点循环切换
const toggleTheme = () => {
  const currentIndex = options.findIndex(o => o.value === theme.value)
  const nextIndex = (currentIndex + 1) % options.length
  setTheme(options[nextIndex].value)
}
</script>

<style scoped>
/* 切换时的旋转 + 淡入淡出动画 */
.spin-fade-enter-active,
.spin-fade-leave-active {
  transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
}
.spin-fade-enter-from {
  opacity: 0;
  transform: rotate(-90deg) scale(0.5);
}
.spin-fade-leave-to {
  opacity: 0;
  transform: rotate(90deg) scale(0.5);
}
</style>