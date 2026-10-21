<!-- src/components/pos/PosHelpModal.vue -->
<template>
  <div v-if="visible" @click.self="$emit('close')" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
    <div class="bg-white/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-4xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
      
      <!-- 顶部标题栏 -->
      <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-white/50 shrink-0">
        <h3 class="font-extrabold text-base text-slate-900 flex items-center gap-2">
          <span>⌨️ {{ tExt.title }}</span>
        </h3>
        <button @click="$emit('close')" class="text-slate-400 hover:text-slate-700 text-base font-bold p-1 cursor-pointer">✕</button>
      </div>

      <!-- 快捷键内容区 -->
      <div class="flex-1 overflow-y-auto p-6 space-y-4 text-xs bg-white/20">
        
        <!-- 搜索与点选 -->
        <div class="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200/80 space-y-3 shadow-2xs">
          <div class="font-extrabold text-blue-600 uppercase tracking-wider mb-1 text-sm">🔍 {{ tExt.groupSearch }}</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-700">
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">{{ tExt.hkFocus }}</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-blue-600 font-bold">{{ tExt.keySlash }}</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">{{ tExt.hkSelectResult }}</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-blue-600 font-bold">↑ / ↓</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">{{ tExt.hkConfirmAdd }}</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-blue-600 font-bold">{{ tExt.keyEnter }}</span>
            </div>
          </div>
        </div>

        <!-- 购物车与数量 -->
        <div class="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200/80 space-y-3 shadow-2xs">
          <div class="font-extrabold text-indigo-600 uppercase tracking-wider mb-1 text-sm">🛒 {{ tExt.groupCart }}</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-700">
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">{{ tExt.hkSwitchRow }}</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-indigo-600 font-bold">↑ / ↓</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">{{ tExt.hkQtyAdd }}</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-indigo-600 font-bold">+ / =</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">{{ tExt.hkQtySub }}</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-indigo-600 font-bold">-</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">{{ tExt.hkDelete }}</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-indigo-600 font-bold">Delete / Backspace</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs col-span-2">
              <span class="font-bold">{{ tExt.hkMultiplier }}</span>
              <span class="font-mono bg-slate-100 px-2.5 py-1 rounded text-indigo-600 font-bold">"3*" {{ tExt.hkMultiplierTag }}</span>
            </div>
          </div>
        </div>

        <!-- 支付快捷键 -->
        <div class="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200/80 space-y-3 shadow-2xs">
          <div class="font-extrabold text-emerald-600 uppercase tracking-wider mb-1 text-sm">💳 {{ tExt.groupPay }}</div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-slate-700">
            <div class="bg-white p-3 rounded-xl border border-slate-200/80 text-center shadow-2xs">
              <span class="block font-bold text-slate-900 mb-1">{{ tExt.payCash }}</span>
              <span class="font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-black text-xs">F4</span>
            </div>
            <div class="bg-white p-3 rounded-xl border border-slate-200/80 text-center shadow-2xs">
              <span class="block font-bold text-slate-900 mb-1">{{ tExt.payBs }}</span>
              <span class="font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-black text-xs">F5</span>
            </div>
            <div class="bg-white p-3 rounded-xl border border-slate-200/80 text-center shadow-2xs">
              <span class="block font-bold text-slate-900 mb-1">{{ tExt.payPos }}</span>
              <span class="font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-black text-xs">F6</span>
            </div>
            <div class="bg-white p-3 rounded-xl border border-slate-200/80 text-center shadow-2xs">
              <span class="block font-bold text-slate-900 mb-1">{{ tExt.payPago }}</span>
              <span class="font-mono bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded font-black text-xs">F7</span>
            </div>
          </div>
          <div class="bg-white p-3 rounded-xl border border-slate-200/80 text-slate-600 text-center shadow-2xs mt-2">
            💡 {{ tExt.tipAutoFill1 }} <span class="font-mono font-bold text-blue-600">Space</span> {{ tExt.tipAutoFill2 }} <span class="font-mono font-bold text-blue-600">[=]</span> {{ tExt.tipAutoFill3 }}
          </div>
        </div>

        <!-- 常用系统快捷键 -->
        <div class="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-slate-200/80 space-y-3 shadow-2xs">
          <div class="font-extrabold text-amber-600 uppercase tracking-wider mb-1 text-sm">⚡ {{ tExt.groupSys }}</div>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-slate-700">
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">{{ tExt.sysClient }}</span>
              <span class="font-mono bg-amber-50 text-amber-700 px-2.5 py-1 rounded font-bold">Ctrl + F</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">{{ tExt.sysHold }}</span>
              <span class="font-mono bg-amber-50 text-amber-700 px-2.5 py-1 rounded font-bold">Ctrl + H</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">{{ tExt.sysRecall }}</span>
              <span class="font-mono bg-amber-50 text-amber-700 px-2.5 py-1 rounded font-bold">Ctrl + R</span>
            </div>
            <div class="flex justify-between items-center bg-white p-3 rounded-xl border border-slate-200/80 shadow-2xs">
              <span class="font-bold">{{ tExt.sysClear }}</span>
              <span class="font-mono bg-amber-50 text-amber-700 px-2.5 py-1 rounded font-bold">Ctrl + B</span>
            </div>
          </div>
        </div>

      </div>

      <!-- 底部关闭栏 -->
      <div class="p-5 bg-white/80 backdrop-blur-md border-t border-slate-200/60 flex justify-end shrink-0">
        <button @click="$emit('close')" class="px-6 py-2.5 bg-slate-900 text-white rounded-xl text-xs font-bold hover:bg-slate-800 transition-colors cursor-pointer shadow-md">
          {{ tExt.btnClose }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../../composables/useI18n'

defineProps({
  visible: { type: Boolean, default: false }
})
defineEmits(['close'])

const { currentLang } = useI18n()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    title: isZh ? '收银台快捷键与操作指南' : isEs ? 'Guía de Atajos de Teclado POS' : 'POS Keyboard Shortcuts',
    groupSearch: isZh ? '商品搜索与点选' : isEs ? 'Búsqueda de Productos' : 'Product Search',
    groupCart: isZh ? '购物车与数量操作' : isEs ? 'Operaciones de Carrito' : 'Cart & Quantity Ops',
    groupPay: isZh ? '支付通道快速聚焦' : isEs ? 'Enfoque Rápido de Pago' : 'Quick Payment Focus',
    groupSys: isZh ? '系统常用快捷键' : isEs ? 'Atajos del Sistema' : 'System Shortcuts',
    hkFocus: isZh ? '聚焦搜索框' : isEs ? 'Enfocar caja de búsqueda' : 'Focus search box',
    keySlash: isZh ? '[ / ] 键' : isEs ? 'Tecla [ / ]' : '[ / ] Key',
    keyEnter: isZh ? 'Enter 键' : isEs ? 'Tecla Enter' : 'Enter Key',
    hkSelectResult: isZh ? '搜索结果上下选择' : isEs ? 'Seleccionar resultado' : 'Select result',
    hkConfirmAdd: isZh ? '确认添加商品' : isEs ? 'Confirmar agregar' : 'Confirm add',
    hkSwitchRow: isZh ? '切换选中购物车行' : isEs ? 'Cambiar fila del carrito' : 'Switch cart row',
    hkQtyAdd: isZh ? '当前商品数量加 1' : isEs ? 'Aumentar cantidad' : 'Increase qty',
    hkQtySub: isZh ? '当前商品数量减 1' : isEs ? 'Disminuir cantidad' : 'Decrease qty',
    hkDelete: isZh ? '删除选中商品' : isEs ? 'Eliminar artículo' : 'Delete item',
    hkMultiplier: isZh ? '快捷数量乘数语法 (例如: 3个)' : isEs ? 'Multiplicador rápido (ej: 3)' : 'Quick multiplier (e.g. 3)',
    hkMultiplierTag: isZh ? '语法' : isEs ? 'sintaxis' : 'syntax',
    payCash: isZh ? '美金现金' : isEs ? 'Efectivo USD' : 'Cash USD',
    payBs: isZh ? 'Bs. 现金' : isEs ? 'Efectivo Bs.' : 'Cash Bs.',
    payPos: isZh ? '刷卡 POS' : isEs ? 'Punto de Venta' : 'Card POS',
    payPago: isZh ? 'Pago Móvil' : isEs ? 'Pago Móvil' : 'Pago Móvil',
    tipAutoFill1: isZh ? '提示：在任意支付输入框中按下' : isEs ? 'Sugerencia: En cualquier campo de pago, presione' : 'Tip: In any payment input, press',
    tipAutoFill2: isZh ? '或' : isEs ? 'o' : 'or',
    tipAutoFill3: isZh ? '键，可直接自动填满剩余应付金额！' : isEs ? 'para llenar automáticamente el monto restante.' : 'to auto-fill the remaining amount due.',
    sysClient: isZh ? '快捷选择客户' : isEs ? 'Seleccionar Cliente' : 'Select Client',
    sysHold: isZh ? '云端挂单' : isEs ? 'Pausar Orden' : 'Hold Order',
    sysRecall: isZh ? '恢复挂单大厅' : isEs ? 'Recuperar Orden' : 'Recall Order',
    sysClear: isZh ? '清空当前购物车' : isEs ? 'Limpiar Carrito' : 'Clear Cart',
    btnClose: isZh ? '我知道了 (关闭)' : isEs ? 'Entendido (Cerrar)' : 'Got it (Close)'
  }
})
</script>