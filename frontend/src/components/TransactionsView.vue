<!-- src/components/TransactionsView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto pb-24">

    <!-- 第一层：页面大标题 -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
          <span>📋</span> {{ tExt.pageTitle }}
        </h2>
        <p class="text-xs text-slate-500 mt-1">查看所有历史进销存单据、出入库明细及退款记录。</p>
      </div>
    </div>

    <!-- 第二层：顶部指标卡片（数据来自后端 summary，不再本地 reduce） -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.totalTx }}</p>
        <h3 class="text-2xl font-black text-blue-600 font-mono" data-testid="tx-total">
          {{ meta.total || 0 }} <span class="text-sm">{{ tExt.unit }}</span>
        </h3>
      </div>
      <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.totalOut }}</p>
        <h3 class="text-2xl font-black text-amber-600 font-mono" data-testid="tx-sum-out">
          $ {{ Number(meta.summary?.out_total || 0).toFixed(2) }}
        </h3>
      </div>
      <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.totalIn }}</p>
        <h3 class="text-2xl font-black text-emerald-600 font-mono" data-testid="tx-sum-in">
          $ {{ Number(meta.summary?.in_total || 0).toFixed(2) }}
        </h3>
      </div>
    </div>

    <!-- 第三层：操作工具栏 -->
    <div class="bg-white p-4 md:p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-2 bg-slate-100 p-1.5 rounded-xl">
        <button
          data-testid="tx-tab-all"
          @click="switchTab('ALL')"
          :class="currentTab === 'ALL' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
          class="px-4 py-2 rounded-lg text-sm font-bold transition-all cursor-pointer"
        >
          {{ tExt.tabAll }}
        </button>
        <button
          data-testid="tx-tab-out"
          @click="switchTab('OUT')"
          :class="currentTab === 'OUT' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
          class="px-4 py-2 rounded-lg text-sm font-bold transition-all cursor-pointer"
        >
          {{ tExt.tabOut }}
        </button>
        <button
          data-testid="tx-tab-in"
          @click="switchTab('IN')"
          :class="currentTab === 'IN' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'"
          class="px-4 py-2 rounded-lg text-sm font-bold transition-all cursor-pointer"
        >
          {{ tExt.tabIn }}
        </button>
      </div>

      <div class="flex gap-3">
        <button @click="$emit('export-transactions')" class="flex items-center gap-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200/80 px-4 py-2.5 rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer">
          📥 {{ tExt.exportExcel }}
        </button>
        <button @click="$emit('open-tx-modal')" class="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer">
          ➕ {{ tExt.newTx }}
        </button>
      </div>
    </div>

    <!-- 第四层：数据表格（直接用服务端返回的当前页，不再本地 filter） -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase tracking-wider">
              <th class="py-4 px-6 w-12 text-center">
                <input type="checkbox" class="rounded border-slate-300 text-blue-600 w-4 h-4 pointer-events-none" />
              </th>
              <th class="py-4 px-6">{{ tExt.colTime }}</th>
              <th class="py-4 px-6">{{ tExt.colOem }}</th>
              <th class="py-4 px-6">{{ tExt.colName }}</th>
              <th class="py-4 px-6">{{ tExt.colType }}</th>
              <th class="py-4 px-6">{{ tExt.colQty }}</th>
              <th class="py-4 px-6">{{ tExt.colPrice }}</th>
              <th class="py-4 px-6">{{ tExt.colTotal }}</th>
              <th class="py-4 px-6">{{ tExt.colTarget }}</th>
              <th class="py-4 px-6 text-center">{{ tExt.colActions }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="tx in transactionsList" :key="tx.id" class="hover:bg-blue-50/30 transition-colors cursor-pointer group" @click="openDetailDrawer(tx)">
              <td class="py-4 px-6 text-center" @click.stop>
                <input type="checkbox" class="rounded border-slate-300 text-blue-600 w-4 h-4" />
              </td>
              <td class="py-4 px-6 text-xs text-slate-500 font-mono">{{ tx.timestamp }}</td>
              <td class="py-4 px-6 font-mono font-bold text-blue-600">{{ tx.part_oem }}</td>
              <td class="py-4 px-6 font-bold text-slate-800">{{ tx.part_name }}</td>
              <td class="py-4 px-6">
                <span
                  class="px-2.5 py-1 rounded-md text-xs font-bold border"
                  :class="[
                    tx.type === 'IN' ? 'bg-emerald-50 text-emerald-600' : tx.type === 'REFUND' ? 'bg-rose-50 text-rose-600' : 'bg-amber-50 text-amber-600',
                    tx.type === 'IN' ? 'border-emerald-200/60' : tx.type === 'REFUND' ? 'border-rose-200/60' : 'border-amber-200/60'
                  ]"
                >
                  {{ tx.type === 'IN' ? tExt.typeIn : tx.type === 'REFUND' ? tExt.typeRefund : tExt.typeOut }}
                </span>
              </td>
              <td class="py-4 px-6 font-mono font-bold">{{ tx.quantity }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">$ {{ Number(tx.unit_price || 0).toFixed(2) }}</td>
              <td class="py-4 px-6 font-mono font-bold text-slate-900">$ {{ Number(tx.total_amount || 0).toFixed(2) }}</td>
              <td class="py-4 px-6 text-slate-600">{{ tx.customer_or_supplier || '-' }}</td>
              <td class="py-4 px-6 text-center" @click.stop>
                <button v-if="tx.type !== 'REFUND'" @click="$emit('delete-tx', tx)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1 rounded-lg font-semibold transition-colors cursor-pointer">
                  {{ tExt.btnDelete }}
                </button>
              </td>
            </tr>
            <tr v-if="transactionsList.length === 0">
              <td colspan="10" class="py-16 text-center text-slate-400 text-xs">{{ tExt.emptyData }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页条（内联，跟列表页风格对齐） -->
      <div class="px-6 py-4 border-t border-slate-100 flex flex-wrap items-center justify-between gap-3">
        <p class="text-xs text-slate-500">
          {{ tExt.pageInfo(meta.page || 1, totalPages, meta.total || 0) }}
        </p>
        <div class="flex items-center gap-1.5">
          <button
            data-testid="tx-page-prev"
            @click="gotoPage((meta.page || 1) - 1)"
            :disabled="(meta.page || 1) <= 1"
            class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
          >
            ‹ {{ tExt.prev }}
          </button>
          <button
            v-for="p in pageNumbers"
            :key="p"
            :data-testid="`tx-page-${p}`"
            @click="gotoPage(p)"
            :class="p === (meta.page || 1) ? 'bg-blue-600 text-white border-blue-600' : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'"
            class="min-w-[34px] px-2 py-1.5 text-xs font-bold rounded-lg border transition-colors cursor-pointer"
          >
            {{ p }}
          </button>
          <button
            data-testid="tx-page-next"
            @click="gotoPage((meta.page || 1) + 1)"
            :disabled="(meta.page || 1) >= totalPages"
            class="px-3 py-1.5 text-xs font-semibold rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
          >
            {{ tExt.next }} ›
          </button>
        </div>
      </div>
    </div>

    <!-- ==================== 通用右侧 Drawer（保持原样） ==================== -->
    <SideDrawer
      :visible="detailDrawerVisible"
      :title="tExt.detailTitle"
      icon="🧾"
      @close="closeDrawer"
    >
      <div class="p-6 space-y-6" v-if="currentTx">
        <div class="flex items-center justify-between border-b border-slate-100 pb-4">
          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colTime }}</p>
            <p class="font-mono text-sm font-bold text-slate-800">{{ currentTx.timestamp }}</p>
          </div>
          <span
            class="px-3 py-1.5 rounded-lg text-sm font-bold border"
            :class="[
              currentTx.type === 'IN' ? 'bg-emerald-50 text-emerald-600' : currentTx.type === 'REFUND' ? 'bg-rose-50 text-rose-600' : 'bg-amber-50 text-amber-600',
              currentTx.type === 'IN' ? 'border-emerald-200/60' : currentTx.type === 'REFUND' ? 'border-rose-200/60' : 'border-amber-200/60'
            ]"
          >
            {{ currentTx.type === 'IN' ? tExt.typeIn : currentTx.type === 'REFUND' ? tExt.typeRefund : tExt.typeOut }}
          </span>
        </div>

        <div class="bg-slate-50/50 p-4 rounded-xl border border-slate-100 space-y-3">
          <div class="flex justify-between items-center">
            <span class="text-xs font-semibold text-slate-500">{{ tExt.colOem }}</span>
            <span class="font-mono font-bold text-blue-600">{{ currentTx.part_oem }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-xs font-semibold text-slate-500">{{ tExt.colName }}</span>
            <span class="font-bold text-slate-800">{{ currentTx.part_name }}</span>
          </div>
          <div class="flex justify-between items-center">
            <span class="text-xs font-semibold text-slate-500">{{ tExt.colTarget }}</span>
            <span class="font-bold text-slate-700">{{ currentTx.customer_or_supplier || '-' }}</span>
          </div>
        </div>

        <div class="space-y-3">
          <div class="flex justify-between items-center text-sm">
            <span class="text-slate-500">{{ tExt.colQty }} × {{ tExt.colPrice }}</span>
            <span class="font-mono text-slate-700">{{ currentTx.quantity }} × $ {{ Number(currentTx.unit_price || 0).toFixed(2) }}</span>
          </div>
          <div class="h-px w-full bg-slate-100"></div>
          <div class="flex justify-between items-center">
            <span class="text-sm font-bold text-slate-800">{{ tExt.colTotal }}</span>
            <span class="text-xl font-black font-mono" :class="currentTx.type === 'IN' ? 'text-emerald-600' : 'text-slate-900'">
              $ {{ Number(currentTx.total_amount || 0).toFixed(2) }}
            </span>
          </div>
        </div>

        <div class="pt-6">
          <button
            v-if="currentTx.type !== 'REFUND'"
            @click="handleDeleteFromDrawer"
            class="w-full py-3 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-xl font-bold transition-colors flex justify-center items-center gap-2 cursor-pointer"
          >
            🗑️ {{ tExt.btnDelete }}单据
          </button>
          <p v-else class="text-center text-xs text-slate-400">
            * {{ tExt.refundNoDelete }}
          </p>
        </div>
      </div>
    </SideDrawer>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import SideDrawer from './SideDrawer.vue'

const props = defineProps({
  transactionsList: { type: Array, default: () => [] },
  meta: {
    type: Object,
    default: () => ({ total: 0, page: 1, page_size: 20, summary: { in_total: 0, out_total: 0 } })
  },
})

const emit = defineEmits([
  'export-transactions',
  'open-tx-modal',
  'delete-tx',
  'change-tab',
  'change-page',
])

const { currentLang } = useI18n()

const currentTab = ref('ALL')
const detailDrawerVisible = ref(false)
const currentTx = ref(null)

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    pageTitle: isZh ? '进销存流水' : isEs ? 'Movimientos de Inventario' : 'Inventory Transactions',
    totalTx: isZh ? '总流水单数' : isEs ? 'Total Transacciones' : 'Total Transactions',
    totalOut: isZh ? '出库销售总额' : isEs ? 'Total Ventas' : 'Total Sales',
    totalIn: isZh ? '采购入库总额' : isEs ? 'Total Compras' : 'Total Purchases',
    unit: isZh ? '笔' : isEs ? 'trans.' : 'txns',
    tabAll: isZh ? '全部类型' : isEs ? 'Todos los Tipos' : 'All Types',
    tabOut: isZh ? '出库 (销售)' : isEs ? 'Salida (Venta)' : 'Outbound (Sale)',
    tabIn: isZh ? '采购入库' : isEs ? 'Entrada (Compra)' : 'Inbound (Purchase)',
    exportExcel: isZh ? '导出 Excel' : isEs ? 'Exportar Excel' : 'Export Excel',
    newTx: isZh ? '新增单据' : isEs ? 'Nuevo Registro' : 'New Record',
    colTime: isZh ? '时间' : isEs ? 'Hora' : 'Time',
    colOem: isZh ? '商品编码/OEM' : isEs ? 'Código/OEM' : 'Code/OEM',
    colName: isZh ? '配件名称' : isEs ? 'Repuesto' : 'Part Name',
    colType: isZh ? '类型' : isEs ? 'Tipo' : 'Type',
    colQty: isZh ? '数量' : isEs ? 'Cant.' : 'Qty',
    colPrice: isZh ? '单价' : isEs ? 'Precio Unit.' : 'Unit Price',
    colTotal: isZh ? '总金额' : isEs ? 'Total' : 'Total',
    colTarget: isZh ? '客户 / 供应商' : isEs ? 'Cliente / Proveedor' : 'Customer / Supplier',
    colActions: isZh ? '操作' : isEs ? 'Acciones' : 'Actions',
    typeIn: isZh ? '入库' : isEs ? 'ENTRADA' : 'IN',
    typeOut: isZh ? '出库' : isEs ? 'SALIDA' : 'OUT',
    typeRefund: isZh ? '退款' : isEs ? 'REEMBOLSO' : 'REFUND',
    btnDelete: isZh ? '删除' : isEs ? 'Eliminar' : 'Delete',
    emptyData: isZh ? '没有找到符合条件的进销存单据记录' : isEs ? 'No se encontraron registros de inventario' : 'No inventory records found',
    detailTitle: isZh ? '单据详情' : isEs ? 'Detalle de Transacción' : 'Transaction Details',
    refundNoDelete: isZh ? '退款单据由系统生成，无法直接删除。' : isEs ? 'Los reembolsos generados por el sistema no se pueden eliminar.' : 'System-generated refunds cannot be deleted directly.',
    prev: isZh ? '上一页' : isEs ? 'Anterior' : 'Prev',
    next: isZh ? '下一页' : isEs ? 'Siguiente' : 'Next',
    pageInfo: (p, t, n) =>
      isZh ? `第 ${p} / ${t} 页，共 ${n} 条`
      : isEs ? `Página ${p} de ${t} (${n} registros)`
      : `Page ${p} of ${t} (${n} records)`,
  }
})

const totalPages = computed(() => {
  const ps = props.meta.page_size || 20
  const total = props.meta.total || 0
  return Math.max(1, Math.ceil(total / ps))
})

const pageNumbers = computed(() => {
  const tp = totalPages.value
  const cur = props.meta.page || 1
  const start = Math.max(1, cur - 2)
  const end = Math.min(tp, start + 4)
  const begin = Math.max(1, end - 4)
  const arr = []
  for (let i = begin; i <= end; i++) arr.push(i)
  return arr
})

const switchTab = (tab) => {
  if (tab === currentTab.value) return
  currentTab.value = tab
  emit('change-tab', tab)
}

const gotoPage = (p) => {
  if (p < 1 || p > totalPages.value) return
  if (p === (props.meta.page || 1)) return
  emit('change-page', p)
}

const openDetailDrawer = (tx) => {
  currentTx.value = tx
  detailDrawerVisible.value = true
}

const closeDrawer = () => {
  detailDrawerVisible.value = false
  currentTx.value = null
}

const handleDeleteFromDrawer = () => {
  if (!currentTx.value) return
  emit('delete-tx', currentTx.value)
  closeDrawer()
}
</script>