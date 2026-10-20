<!-- src/components/TransactionsView.vue -->
<template>
  <div class="space-y-6">
    <!-- 顶部指标卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.totalTx }}</p>
        <h3 class="text-2xl font-black text-blue-600 font-mono">{{ transactionsList.length }} <span class="text-sm">{{ tExt.unit }}</span></h3>
      </div>
      <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.totalOut }}</p>
        <h3 class="text-2xl font-black text-amber-600 font-mono">$ 0.00</h3>
      </div>
      <div class="bg-white/75 backdrop-blur-xl p-6 rounded-2xl border border-white/80 shadow-lg space-y-2">
        <p class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ tExt.totalIn }}</p>
        <h3 class="text-2xl font-black text-emerald-600 font-mono">$ 0.00</h3>
      </div>
    </div>

    <!-- 主列表 -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="p-4 md:p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-2 bg-slate-100 p-1.5 rounded-xl">
          <button class="px-4 py-2 rounded-lg text-sm font-bold bg-white text-blue-600 shadow-sm cursor-pointer">{{ tExt.tabAll }}</button>
          <button class="px-4 py-2 rounded-lg text-sm font-bold text-slate-500 hover:text-slate-700 cursor-pointer">{{ tExt.tabOut }}</button>
          <button class="px-4 py-2 rounded-lg text-sm font-bold text-slate-500 hover:text-slate-700 cursor-pointer">{{ tExt.tabIn }}</button>
        </div>
        <div class="flex gap-3">
          <button @click="$emit('export-transactions')" class="flex items-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-md transition-all">
            📥 {{ tExt.exportExcel }}
          </button>
          <button @click="$emit('open-tx-modal')" class="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl text-xs font-bold shadow-md transition-all">
            ➕ {{ tExt.newTx }}
          </button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase tracking-wider">
              <th class="py-4 px-6 w-12 text-center">
                <input type="checkbox" class="rounded border-slate-300 text-blue-600 w-4 h-4" />
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
            <tr v-for="tx in transactionsList" :key="tx.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="py-4 px-6 text-center">
                <input type="checkbox" class="rounded border-slate-300 text-blue-600 w-4 h-4" />
              </td>
              <td class="py-4 px-6 text-xs text-slate-500 font-mono">{{ tx.timestamp }}</td>
              <td class="py-4 px-6 font-mono font-bold text-blue-600">{{ tx.part_oem }}</td>
              <td class="py-4 px-6 font-bold text-slate-800">{{ tx.part_name }}</td>
              <td class="py-4 px-6">
                <span :class="tx.type === 'IN' ? 'bg-emerald-50 text-emerald-600' : tx.type === 'REFUND' ? 'bg-rose-50 text-rose-600' : 'bg-amber-50 text-amber-600'" class="px-2.5 py-1 rounded-md text-xs font-bold">
                  {{ tx.type === 'IN' ? tExt.typeIn : tx.type === 'REFUND' ? tExt.typeRefund : tExt.typeOut }}
                </span>
              </td>
              <td class="py-4 px-6 font-mono font-bold">{{ tx.quantity }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">$ {{ Number(tx.unit_price || 0).toFixed(2) }}</td>
              <td class="py-4 px-6 font-mono font-bold text-slate-900">$ {{ Number(tx.total_amount || 0).toFixed(2) }}</td>
              <td class="py-4 px-6 text-slate-600">{{ tx.customer_or_supplier || '-' }}</td>
              <td class="py-4 px-6 text-center">
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
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'

const props = defineProps({
  transactionsList: { type: Array, default: () => [] }
})
defineEmits(['export-transactions', 'open-tx-modal', 'delete-tx'])

const { currentLang } = useI18n()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    totalTx: isZh ? '今日总流水单数' : isEs ? 'Total de Transacciones (Hoy)' : 'Total Transactions (Today)',
    totalOut: isZh ? '今日出库销售总额' : isEs ? 'Total Ventas (Hoy)' : 'Total Sales (Today)',
    totalIn: isZh ? '今日采购入库总额' : isEs ? 'Total Compras (Hoy)' : 'Total Purchases (Today)',
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
    emptyData: isZh ? '没有找到符合条件的进销存单据记录' : isEs ? 'No se encontraron registros de inventario' : 'No inventory records found'
  }
})
</script>