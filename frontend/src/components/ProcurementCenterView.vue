<!-- src/components/ProcurementCenterView.vue -->
<template>
  <div class="space-y-6">
    <!-- 顶部状态栏 -->
    <div class="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-2 bg-slate-100 p-1.5 rounded-xl">
        <button 
          @click="activeTab = 'orders'"
          :class="['px-4 py-2 rounded-lg text-sm font-bold transition-all cursor-pointer', activeTab === 'orders' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']"
        >
          📦 {{ tExt.tabOrders }}
        </button>
        <button 
          @click="activeTab = 'suggestions'"
          :class="['px-4 py-2 rounded-lg text-sm font-bold transition-all cursor-pointer', activeTab === 'suggestions' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']"
        >
          ⚡ {{ tExt.tabSuggestions }}
        </button>
      </div>
      <div class="flex items-center gap-2 text-xs font-bold">
        <span class="text-slate-400">{{ tExt.supplyChainStatus }}:</span>
        <span class="text-emerald-600 bg-emerald-50 px-2 py-1 rounded-lg border border-emerald-200">{{ tExt.statusOnline }}</span>
      </div>
    </div>

    <!-- 采购订单列表 -->
    <div v-if="activeTab === 'orders'" class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="p-6 border-b border-slate-100 flex items-center justify-between bg-white/50">
        <div>
          <h3 class="font-bold text-slate-800 text-base">{{ tExt.ordersTitle }}</h3>
          <p class="text-xs text-slate-400 mt-1">{{ tExt.ordersSub }}</p>
        </div>
        <button @click="fetchOrders" class="flex items-center gap-2 bg-slate-100 hover:bg-slate-200 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold transition-all">
          🔄 {{ tExt.refreshList }}
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase">
              <th class="py-4 px-6 w-12 text-center">
                <input type="checkbox" class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4" />
              </th>
              <th class="py-4 px-6">{{ tExt.colPoNo }}</th>
              <th class="py-4 px-6">{{ tExt.colSupplier }}</th>
              <th class="py-4 px-6">{{ tExt.colDetails }}</th>
              <th class="py-4 px-6">{{ tExt.colStatus }}</th>
              <th class="py-4 px-6">{{ tExt.colTime }}</th>
              <th class="py-4 px-6 text-right">{{ tExt.colActions }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="order in ordersList" :key="order.id" class="hover:bg-blue-50/30 transition-colors">
              <td class="py-4 px-6 text-center">
                <input type="checkbox" class="rounded border-slate-300 text-blue-600 w-4 h-4" />
              </td>
              <td class="py-4 px-6 font-mono font-bold text-blue-600">{{ order.po_no }}</td>
              <td class="py-4 px-6 font-bold text-slate-800">{{ order.supplier_name }}</td>
              <td class="py-4 px-6 text-slate-600">{{ order.items_count }} SKUs</td>
              <td class="py-4 px-6">
                <span :class="order.status === 'received' ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600'" class="px-2.5 py-1 rounded-lg text-xs font-bold">
                  {{ order.status === 'received' ? tExt.statusReceived : tExt.statusPending }}
                </span>
              </td>
              <td class="py-4 px-6 text-slate-500 font-mono text-xs">{{ order.created_at }}</td>
              <td class="py-4 px-6 text-right">
                <button v-if="order.status !== 'received'" @click="receiveOrder(order.id)" class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg text-xs font-bold transition-colors">
                  {{ tExt.btnReceive }}
                </button>
                <span v-else class="text-slate-400 text-xs font-semibold">{{ tExt.btnCompleted }}</span>
              </td>
            </tr>
            <tr v-if="ordersList.length === 0">
              <td colspan="7" class="py-16 text-center text-slate-400 text-xs">{{ tExt.emptyOrders }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api'

const { currentLang } = useI18n()
const activeTab = ref('orders')
const ordersList = ref([])

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    tabOrders: isZh ? '采购订单与收货管理' : isEs ? 'Pedidos y Recepción' : 'Purchase Orders',
    tabSuggestions: isZh ? '智能补货建议与下单' : isEs ? 'Sugerencias de Compra' : 'Replenishment',
    supplyChainStatus: isZh ? '供应链状态' : isEs ? 'Estado de Suministro' : 'Supply Chain Status',
    statusOnline: isZh ? '在线正常' : isEs ? 'En Línea' : 'Online',
    ordersTitle: isZh ? '采购订单与收货管理' : isEs ? 'Gestión de Órdenes de Compra' : 'Purchase Orders Management',
    ordersSub: isZh ? '管理供应商采购订单，支持一键验货入库、状态流转与商品明细解析' : isEs ? 'Gestione pedidos de proveedores, recepción y detalles' : 'Manage supplier orders, receiving, and details',
    refreshList: isZh ? '刷新订单列表' : isEs ? 'Actualizar Lista' : 'Refresh List',
    colPoNo: isZh ? '订单编号 (PO NO.)' : isEs ? 'Nro. PO' : 'PO No.',
    colSupplier: isZh ? '供应商' : isEs ? 'Proveedor' : 'Supplier',
    colDetails: isZh ? '采购明细解析 (SKU & 数量)' : isEs ? 'Detalles (SKU & Cant.)' : 'Details (SKU & Qty)',
    colStatus: isZh ? '订单状态' : isEs ? 'Estado' : 'Status',
    colTime: isZh ? '创建时间' : isEs ? 'Fecha de Creación' : 'Created At',
    colActions: isZh ? '操作 / 验货入库' : isEs ? 'Acciones / Recibir' : 'Actions / Receive',
    statusReceived: isZh ? '已入库' : isEs ? 'Recibido' : 'Received',
    statusPending: isZh ? '待收货' : isEs ? 'Pendiente' : 'Pending',
    btnReceive: isZh ? '确认收货入库' : isEs ? 'Confirmar Recepción' : 'Confirm Receive',
    btnCompleted: isZh ? '已完成' : isEs ? 'Completado' : 'Completed',
    emptyOrders: isZh ? '暂无采购订单数据，请前往“智能补货建议”生成采购单' : isEs ? 'No hay órdenes de compra. Vaya a "Sugerencias" para crear una.' : 'No purchase orders found. Go to "Suggestions" to create one.'
  }
})

const fetchOrders = async () => {
  try {
    const res = await apiFetch('/api/purchase-orders')
    if (res.ok) {
      ordersList.value = await res.json()
    }
  } catch (e) { console.error(e) }
}

const receiveOrder = async (id) => {
  if (!confirm('¿Confirmar recepción e ingreso de inventario?')) return
  try {
    const res = await apiFetch(`/api/purchase-orders/${id}/receive`, { method: 'POST' })
    if (res.ok) fetchOrders()
  } catch (e) { console.error(e) }
}

onMounted(() => { fetchOrders() })
</script>