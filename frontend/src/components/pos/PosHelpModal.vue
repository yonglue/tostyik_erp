<!-- src/components/pos/PosHelpModal.vue -->
<template>
  <div v-if="visible" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
    <div class="bg-white/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-4xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
      
      <!-- 顶部标题栏 -->
      <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-white/50 shrink-0">
        <h3 class="font-extrabold text-base text-slate-900 flex items-center gap-2">
          <span>⌨️ 收银台快捷键与操作指南 (Keyboard Shortcuts)</span>
        </h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-700 text-base font-bold p-1 cursor-pointer">✕</button>
      </div>

      <!-- 快捷键内容区 -->
      <div class="flex-1 overflow-y-auto p-6 space-y-4 text-xs bg-white/20">
        
        <!-- 搜索与点选 -->
        <div class="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200/80 space-y-3 shadow-2xs">
          <div class="font-extrabold text-blue-600 uppercase tracking-wider mb-1 text-sm">🔍 商品搜索与点选</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-700">
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">聚焦搜索框</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-blue-600 font-bold">[/] 键</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">搜索结果上下选择</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-blue-600 font-bold">↑ / ↓ 键</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">确认添加商品</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-blue-600 font-bold">Enter 键</span>
            </div>
          </div>
        </div>

        <!-- 购物车与数量 -->
        <div class="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200/80 space-y-3 shadow-2xs">
          <div class="font-extrabold text-indigo-600 uppercase tracking-wider mb-1 text-sm">🛒 购物车与数量操作</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-700">
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">切换选中购物车行</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-indigo-600 font-bold">↑ / ↓ 键</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">当前商品数量加 1</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-indigo-600 font-bold">+ / = 键</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">当前商品数量减 1</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-indigo-600 font-bold">- 键</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">删除选中商品</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-indigo-600 font-bold">Delete / Backspace</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs col-span-2">
              <span class="font-bold">快捷数量乘数语法 (例如: 3个)</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-indigo-600 font-bold">数量输入框支持 "3*" 语法</span>
            </div>
          </div>
        </div>

        <!-- 支付快捷键 -->
        <div class="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200/80 space-y-3 shadow-2xs">
          <div class="font-extrabold text-emerald-600 uppercase tracking-wider mb-1 text-sm">💳 支付通道快速聚焦</div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-slate-700">
            <div class="bg-white p-3 rounded-xl border border-slate-200/80 text-center shadow-2xs">
              <span class="block font-bold text-slate-900 mb-1">美金现金</span>
              <span class="font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-black text-xs">F4 键</span>
            </div>
            <div class="bg-white p-3 rounded-xl border border-slate-200/80 text-center shadow-2xs">
              <span class="block font-bold text-slate-900 mb-1">Bs. 现金</span>
              <span class="font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-black text-xs">F5 键</span>
            </div>
            <div class="bg-white p-3 rounded-xl border border-slate-200/80 text-center shadow-2xs">
              <span class="block font-bold text-slate-900 mb-1">刷卡 POS</span>
              <span class="font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-black text-xs">F6 键</span>
            </div>
            <div class="bg-white p-3 rounded-xl border border-slate-200/80 text-center shadow-2xs">
              <span class="block font-bold text-slate-900 mb-1">Pago Móvil</span>
              <span class="font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-black text-xs">F7 键</span>
            </div>
          </div>
          <div class="bg-white p-3 rounded-xl border border-slate-200/80 text-slate-600 text-center shadow-2xs mt-2">
            💡 提示：在任意支付输入框中按下 <span class="font-mono font-bold text-blue-600">空格键 [Space]</span> 或 <span class="font-mono font-bold text-blue-600">[=] 键</span>，可直接自动填满剩余应付金额！
          </div>
        </div>

        <!-- 常用系统快捷键 -->
        <div class="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200/80 space-y-3 shadow-2xs">
          <div class="font-extrabold text-amber-600 uppercase tracking-wider mb-1 text-sm">⚡ 系统常用快捷键</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-700">
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">快捷选择客户</span>
              <span class="font-mono bg-amber-50 text-amber-700 px-2.5 py-1 rounded font-bold">Ctrl + F</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">云端挂单</span>
              <span class="font-mono bg-amber-50 text-amber-700 px-2.5 py-1 rounded font-bold">Ctrl + H</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">恢复挂单大厅</span>
              <span class="font-mono bg-amber-50 text-amber-700 px-2.5 py-1 rounded font-bold">Ctrl + R</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">清空当前购物车</span>
              <span class="font-mono bg-amber-50 text-amber-700 px-2.5 py-1 rounded font-bold">Ctrl + B</span>
            </div>
          </div>
        </div>

      </div>

      <!-- 底部关闭栏 -->
      <div class="p-5 bg-white/80 backdrop-blur-md border-t border-slate-200/60 flex justify-end shrink-0">
        <button @click="$emit('close')" class="px-6 py-2.5 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 transition-colors cursor-pointer shadow-md">
          我知道了 (关闭)
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
</script>