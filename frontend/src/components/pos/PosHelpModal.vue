<template>
  <!-- 快捷键指南弹窗（纯静态内容） -->
  <div v-if="visible" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
    <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100 flex flex-col">
      <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
        <h3 class="font-bold text-base text-slate-800 flex items-center gap-2">
          <span>⌨️ POS 收银台快捷键指南</span>
        </h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
      </div>

      <div class="p-6 space-y-3 text-xs text-slate-700">
        <div
          v-for="shortcut in shortcuts"
          :key="shortcut.label"
          class="flex items-center justify-between p-2.5 bg-slate-50 rounded-xl border border-slate-100"
        >
          <span class="font-medium">{{ shortcut.label }}</span>
          <span :class="shortcut.tone" class="font-mono font-bold px-2 py-0.5 rounded">{{ shortcut.keys }}</span>
        </div>
      </div>

      <div class="p-4 bg-slate-50 border-t border-slate-100 text-center">
        <button @click="$emit('close')" class="w-full py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-colors cursor-pointer">
          我知道了
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  visible: { type: Boolean, default: false }
})

defineEmits(['close'])

const shortcuts = [
  { label: '聚焦商品搜索框', keys: '[/]', tone: 'bg-blue-100 text-blue-700' },
  { label: '呼出客户搜索弹窗', keys: 'Ctrl + F / F2', tone: 'bg-blue-100 text-blue-700' },
  { label: '当前订单暂存挂单', keys: 'Ctrl + H', tone: 'bg-amber-100 text-amber-700' },
  { label: '打开挂单取单池', keys: 'Ctrl + R', tone: 'bg-amber-100 text-amber-700' },
  { label: '购物车末项数量加 1', keys: 'F3', tone: 'bg-emerald-100 text-emerald-700' },
  { label: '切换为挂账支付 (Fiado)', keys: 'Alt + P', tone: 'bg-amber-100 text-amber-700' },
  { label: '清空购物车', keys: 'Ctrl + B', tone: 'bg-rose-100 text-rose-700' },
  { label: '删除购物车最后一项商品', keys: 'Delete', tone: 'bg-rose-100 text-rose-700' },
  { label: '确认退出收银台', keys: 'Esc', tone: 'bg-slate-200 text-slate-700' }
]
</script>
