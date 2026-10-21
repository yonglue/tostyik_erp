<!-- src/components/ThemeSwitcher.vue -->
<template>
  <div
    class="relative inline-flex items-center p-1 rounded-2xl
           bg-white/70 dark:bg-slate-800/70
           border border-slate-200/80 dark:border-slate-700/60
           shadow-2xs backdrop-blur-md
           transition-all duration-200
           hover:scale-[1.02] hover:shadow-md
           hover:border-blue-300 dark:hover:border-blue-500/50"
    role="group"
    aria-label="主题切换"
  >
    <!-- 滑动指示器 -->
    <div
      class="absolute top-1 h-8 w-9 rounded-xl
             bg-gradient-to-tr from-blue-500 to-indigo-500
             shadow-md shadow-blue-500/30
             transition-all duration-300 ease-out"
      :style="{ left: 4 + activeIndex * 36 + 'px' }"
    ></div>

    <button
      v-for="opt in options"
      :key="opt.value"
      @click="setTheme(opt.value)"
      :title="opt.label"
      :aria-pressed="theme === opt.value"
      class="relative z-10 flex items-center justify-center w-9 h-8 rounded-xl
             transition-colors duration-200 cursor-pointer"
      :class="theme === opt.value
        ? 'text-white'
        : 'text-slate-500 dark:text-slate-400 hover:text-slate-800 dark:hover:text-slate-100'"
    >
      <component :is="opt.icon" :size="15" :stroke-width="2.5" />
    </button>
  </div>
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

const activeIndex = computed(() => options.findIndex(o => o.value === theme.value))
</script>