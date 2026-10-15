<template>
  <!-- 通用二次确认弹窗：POS 退出/退货、后台各处删除确认共用。
       icon 留空则不显示图标区，用于后台的轻量删除确认。 -->
  <div
    v-if="visible"
    :class="overlayClass"
    class="fixed inset-0 backdrop-blur-xs flex items-center justify-center z-50 p-4"
  >
    <div class="bg-white rounded-2xl shadow-2xl max-w-sm w-full p-6 text-center space-y-4 border border-slate-100">
      <div
        v-if="icon"
        :class="iconClass"
        class="w-14 h-14 rounded-2xl mx-auto flex items-center justify-center shadow-lg font-bold text-2xl"
      >
        {{ icon }}
      </div>
      <div>
        <h3 class="font-black text-lg text-slate-900">{{ title }}</h3>
        <p v-if="message" class="text-xs text-slate-500 mt-1.5 leading-relaxed">{{ message }}</p>
      </div>
      <div class="flex gap-3 pt-2">
        <button
          @click="$emit('cancel')"
          class="flex-1 px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors cursor-pointer"
        >
          {{ cancelText }}
        </button>
        <button
          @click="$emit('confirm')"
          class="flex-1 px-4 py-2.5 rounded-xl text-xs font-semibold bg-rose-600 text-white hover:bg-rose-700 shadow-md transition-colors cursor-pointer"
        >
          {{ confirmText }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false },
  icon: { type: String, default: '' },
  iconClass: { type: String, default: 'bg-amber-50 text-amber-600' },
  title: { type: String, default: '' },
  message: { type: String, default: '' },
  cancelText: { type: String, default: '取消' },
  confirmText: { type: String, default: '确认' },
  overlayClass: { type: String, default: 'bg-slate-900/50' }
})

defineEmits(['cancel', 'confirm'])
</script>
