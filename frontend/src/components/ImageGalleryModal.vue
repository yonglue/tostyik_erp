<!-- src/components/ImageGalleryModal.vue -->
<template>
  <div 
    v-if="visible" 
    @click.self="close" 
    class="fixed inset-0 bg-slate-950/90 backdrop-blur-md flex items-center justify-center z-50 p-4 select-none"
  >
    <!-- 顶部控制工具栏 -->
    <div class="absolute top-6 right-6 flex items-center gap-3 z-10">
      <!-- 缩放控制按钮组 -->
      <div class="flex items-center bg-slate-800/80 border border-slate-700/80 rounded-2xl px-3 py-1.5 backdrop-blur-md text-white text-xs gap-2 shadow-lg">
        <button 
          @click="zoomOut" 
          :title="tExt.zoomOut" 
          class="hover:text-blue-400 transition-colors cursor-pointer px-1.5 py-0.5 font-bold text-sm"
        >
          ➖
        </button>
        <span class="font-mono text-slate-300 w-12 text-center font-bold">{{ Math.round(scale * 100) }}%</span>
        <button 
          @click="zoomIn" 
          :title="tExt.zoomIn" 
          class="hover:text-blue-400 transition-colors cursor-pointer px-1.5 py-0.5 font-bold text-sm"
        >
          ➕
        </button>
        <button 
          @click="resetZoom" 
          :title="tExt.reset" 
          class="hover:text-amber-400 transition-colors cursor-pointer text-[10px] bg-slate-700/60 px-2 py-0.5 rounded-lg font-mono ml-1"
        >
          1:1
        </button>
      </div>

      <!-- 关闭按钮 -->
      <button 
        @click="close" 
        :title="tExt.close"
        class="w-9 h-9 rounded-2xl bg-slate-800/80 border border-slate-700/80 hover:bg-slate-700 text-white flex items-center justify-center text-base font-bold transition-all cursor-pointer shadow-lg"
      >
        ✕
      </button>
    </div>

    <!-- 主图显示区域 -->
    <div 
      class="relative max-w-5xl max-h-[85vh] w-full h-full flex items-center justify-center overflow-hidden"
      @wheel.prevent="handleWheel"
    >
      <img 
        v-if="images && images.length > 0"
        :src="images[index]" 
        :style="{ transform: `scale(${scale})` }"
        class="max-w-full max-h-[80vh] object-contain transition-transform duration-150 ease-out rounded-2xl shadow-2xl border border-slate-800/60"
        :alt="tExt.previewAlt"
      />
    </div>

    <!-- 底部切图指示器与左右切换按钮 -->
    <template v-if="images && images.length > 1">
      <button 
        @click="prev" 
        class="absolute left-6 top-1/2 -translate-y-1/2 w-12 h-12 rounded-2xl bg-slate-800/80 border border-slate-700/80 hover:bg-blue-600 text-white flex items-center justify-center text-xl font-bold transition-all cursor-pointer shadow-lg backdrop-blur-md"
      >
        ❮
      </button>

      <button 
        @click="next" 
        class="absolute right-6 top-1/2 -translate-y-1/2 w-12 h-12 rounded-2xl bg-slate-800/80 border border-slate-700/80 hover:bg-blue-600 text-white flex items-center justify-center text-xl font-bold transition-all cursor-pointer shadow-lg backdrop-blur-md"
      >
        ❯
      </button>

      <div class="absolute bottom-6 left-1/2 -translate-x-1/2 bg-slate-800/80 border border-slate-700/80 px-4 py-1.5 rounded-full text-xs font-mono text-slate-300 backdrop-blur-md">
        {{ index + 1 }} / {{ images.length }}
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from '../composables/useI18n'

const props = defineProps({
  visible: Boolean,
  images: Array,
  index: Number
})

const emit = defineEmits(['close', 'prev', 'next'])
const { currentLang } = useI18n()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    zoomIn: isZh ? '放大 (+)' : isEs ? 'Acercar (+)' : 'Zoom In (+)',
    zoomOut: isZh ? '缩小 (-)' : isEs ? 'Alejar (-)' : 'Zoom Out (-)',
    reset: isZh ? '重置 100%' : isEs ? 'Restablecer 100%' : 'Reset 100%',
    close: isZh ? '关闭' : isEs ? 'Cerrar' : 'Close',
    previewAlt: isZh ? '图片预览' : isEs ? 'Vista previa de imagen' : 'Image Preview'
  }
})

// 缩放状态管理 (1.0 = 100%)
const scale = ref(1.0)

// 切换图片或打开弹窗时重置缩放比例
watch([() => props.index, () => props.visible], () => {
  resetZoom()
})

const zoomIn = () => {
  if (scale.value < 4.0) {
    scale.value = Math.min(4.0, +(scale.value + 0.25).toFixed(2))
  }
}

const zoomOut = () => {
  if (scale.value > 0.5) {
    scale.value = Math.max(0.5, +(scale.value - 0.25).toFixed(2))
  }
}

const resetZoom = () => {
  scale.value = 1.0
}

// 鼠标滚轮缩放
const handleWheel = (e) => {
  if (e.deltaY < 0) {
    zoomIn()
  } else {
    zoomOut()
  }
}

const close = () => {
  resetZoom()
  emit('close')
}

const prev = () => {
  resetZoom()
  emit('prev')
}

const next = () => {
  resetZoom()
  emit('next')
}

// 支持键盘 + / - 快捷键缩放
const handleKeydown = (e) => {
  if (!props.visible) return
  if (e.key === '+' || e.key === '=') {
    zoomIn()
  } else if (e.key === '-' || e.key === '_') {
    zoomOut()
  } else if (e.key === '0') {
    resetZoom()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>