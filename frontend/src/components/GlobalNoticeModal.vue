<!-- src/components/GlobalNoticeModal.vue -->
<template>
  <!-- 全局智能提示：成功显示绿勾，拒绝/报错自动变红叉 -->
  <div
    v-if="visible"
    class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4 animate-in fade-in duration-200"
  >
    <div class="bg-white rounded-3xl shadow-2xl max-w-sm w-full p-6 text-center space-y-4 border border-slate-100">
      <div
        :class="isError ? 'bg-rose-50 text-rose-600 shadow-rose-500/10' : 'bg-emerald-50 text-emerald-600 shadow-emerald-500/10'"
        class="w-14 h-14 rounded-2xl mx-auto flex items-center justify-center shadow-lg font-bold text-xl"
      >
        {{ isError ? '✕' : '✓' }}
      </div>
      <div>
        <h3 :class="isError ? 'text-rose-600' : 'text-slate-900'" class="font-black text-lg">
          {{ isError ? tExt.errorTitle : tExt.successTitle }}
        </h3>
        <p class="text-xs text-slate-600 mt-1.5 font-mono whitespace-pre-wrap leading-relaxed">{{ message }}</p>
      </div>
      <button
        @click="$emit('close')"
        :class="isError ? 'bg-rose-600 hover:bg-rose-700 shadow-rose-500/25' : 'bg-blue-600 hover:bg-blue-700 shadow-blue-500/25'"
        class="w-full py-3 text-white rounded-2xl font-bold text-xs shadow-md transition-colors cursor-pointer"
      >
        {{ tExt.btnConfirm }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'

defineProps({
  visible: { type: Boolean, default: false },
  message: { type: String, default: '' },
  isError: { type: Boolean, default: false }
})

defineEmits(['close'])

const { currentLang } = useI18n()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    successTitle: isZh ? '操作成功' : isEs ? 'Operación Exitosa' : 'Operation Successful',
    errorTitle: isZh ? '操作拦截 / 提示' : isEs ? 'Acción Bloqueada / Aviso' : 'Action Blocked / Notice',
    btnConfirm: isZh ? '确定' : isEs ? 'Aceptar' : 'Confirm'
  }
})
</script>