<template>
  <!-- 商品图片灯箱：点击遮罩关闭，左右切换 -->
  <div
    v-if="visible"
    @click="$emit('close')"
    class="fixed inset-0 bg-slate-900/80 backdrop-blur-md flex items-center justify-center z-50 p-4 cursor-pointer"
  >
    <div class="relative bg-white rounded-2xl p-4 max-w-xl w-full shadow-2xl overflow-hidden text-center space-y-3" @click.stop>
      <div class="relative h-[60vh] flex items-center justify-center bg-slate-100 rounded-xl overflow-hidden">
        <img :src="images[index]" class="max-h-full max-w-full object-contain" />
      </div>
      <div class="flex items-center justify-between px-2">
        <button @click="$emit('prev')" class="px-3 py-1.5 bg-slate-200 rounded-lg text-xs font-semibold cursor-pointer">
          ◀ {{ labels.prev }}
        </button>
        <span class="text-xs font-mono text-slate-600">{{ index + 1 }} / {{ images.length }}</span>
        <button @click="$emit('next')" class="px-3 py-1.5 bg-slate-200 rounded-lg text-xs font-semibold cursor-pointer">
          {{ labels.next }} ▶
        </button>
      </div>
      <button
        @click="$emit('close')"
        class="absolute top-3 right-3 bg-slate-900/60 text-white w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold cursor-pointer"
      >
        ✕
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'

defineProps({
  visible: { type: Boolean, default: false },
  images: { type: Array, default: () => [] },
  index: { type: Number, default: 0 }
})

defineEmits(['close', 'prev', 'next'])

const { t } = useI18n()
const labels = computed(() => ({
  prev: t.value.galleryPrev || '上一张',
  next: t.value.galleryNext || '下一张'
}))
</script>
