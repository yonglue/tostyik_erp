<!-- src/components/ClientsView.vue -->
<template>
  <div class="space-y-6 max-w-11xl mx-auto pb-24">
    
    <!-- ==================== 第一层：页面大标题 ==================== -->
    <div class="flex flex-wrap items-center justify-between gap-4">
      <div>
        <h2 class="text-xl font-bold text-slate-800 flex items-center gap-2">
          <span>👥</span> {{ t.clients.title }}
        </h2>
        <p class="text-xs text-slate-500 mt-1">管理客户资料、赊账额度以及回款核销。</p>
      </div>
    </div>

    <!-- ==================== 第二层：操作工具栏 ==================== -->
    <div class="bg-white p-4 md:p-6 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      
      <!-- 左侧：搜索框 -->
      <div class="flex items-center gap-3 w-full md:w-auto">
        <div class="relative w-full md:w-80">
          <Search class="absolute left-3.5 top-3 text-slate-400" :size="16" />
          <input
            :value="clientSearchQuery"
            @input="$emit('update:clientSearchQuery',$event.target.value)"
            type="text"
            :placeholder="t.clients.searchPlaceholder"
            class="w-full bg-slate-50 border border-slate-200 text-sm rounded-xl pl-10 pr-4 py-2.5 outline-none focus:border-blue-500 focus:bg-white transition-all font-bold"
          />
        </div>
      </div>

      <!-- 右侧：操作按钮组 -->
      <div class="flex items-center gap-3 flex-wrap w-full md:w-auto">
        <!-- 批量删除按钮 -->
        <button 
          v-if="selectedIds.length > 0" 
          @click="batchDeleteModalVisible = true" 
          class="flex items-center gap-2 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200/80 px-4 py-2.5 rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer"
        >
          <span>🗑️ {{ tExt.batchDelete }} ({{ tExt.batchSelected }} {{ selectedIds.length }})</span>
        </button>

        <button
          @click="$emit('export-clients')"
          class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200/80 px-4 py-2.5 rounded-xl font-bold text-sm shadow-xs transition-all cursor-pointer"
        >
          <FileSpreadsheet :size="16" />
          <span>{{ tExt.exportClients }}</span>
        </button>
        <button
          @click="$emit('open-add-client')"
          class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-bold text-sm shadow-md shadow-blue-500/20 transition-all cursor-pointer"
        >
          <Plus :size="16" />
          <span>{{ t.clients.addBtn }}</span>
        </button>
      </div>
    </div>

    <!-- ==================== 第三层：数据表格 ==================== -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase tracking-wider">
              <th class="py-4 px-4 w-12 text-center">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected" 
                  @change="toggleSelectAll" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </th>
              <th class="py-4 px-6">{{ t.clients.colName }}</th>
              <th class="py-4 px-6">{{ t.clients.colType }}</th>
              <th class="py-4 px-6">{{ t.clients.colPhone }}</th>
              <th class="py-4 px-6">{{ t.clients.colAddress }}</th>
              <th class="py-4 px-6">{{ t.clients.colRif }}</th>
              <th class="py-4 px-6">{{ t.clients.colDebt }}</th>
              <th class="py-4 px-6 text-center">{{ t.common.actions }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="filteredClients.length === 0">
              <td colspan="8" class="text-center py-16 text-slate-400 text-xs font-bold">
                <span class="text-4xl block mb-3">📭</span>
                {{ t.clients.empty }}
              </td>
            </tr>
            <tr 
              v-for="c in filteredClients" 
              :key="c.id" 
              class="hover:bg-blue-50/30 transition-colors cursor-pointer group"
              @click="openDetailDrawer(c)"
            >
              <!-- 单选框 -->
              <td class="py-4 px-4 text-center" @click.stop>
                <input 
                  type="checkbox" 
                  :checked="selectedIds.includes(c.id)" 
                  @change="toggleSelect(c.id)" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </td>
              <td class="py-4 px-6 font-bold text-slate-900">{{ c.name }}</td>
              <td class="py-4 px-6">
                <span :class="['inline-flex px-2.5 py-1 rounded-md text-xs font-semibold',
                  c.client_type === 'Mayorista' ? 'bg-purple-50 text-purple-600' : (c.client_type === 'Taller' ? 'bg-amber-50 text-amber-600' : 'bg-blue-50 text-blue-600')]">
                  {{ getClientTypeLabel(c.client_type) }}
                </span>
              </td>
              <td class="py-4 px-6 font-mono text-slate-600">{{ c.phone || '-' }}</td>
              <td class="py-4 px-6 text-slate-600">{{ c.address || '-' }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">{{ c.rif_or_cedula || '-' }}</td>
              <td class="py-4 px-6 font-bold font-mono" :class="(c.debt || 0) > 0 ? 'text-rose-600' : 'text-slate-400'">
                $ {{ (c.debt || 0).toFixed(2) }}
              </td>
              <!-- 操作列：仅保留删除 -->
              <td class="py-4 px-6 text-center" @click.stop>
                <button @click="$emit('delete-client', c)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer">
                  {{ t.common.delete }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- ==================== 批量删除确认弹窗 ==================== -->
    <ConfirmDialog
      :visible="batchDeleteModalVisible"
      overlay-class="bg-slate-900/40"
      :title="tExt.batchDeleteTitle"
      :message="tExt.batchDeleteMsg"
      :cancel-text="t.common.cancel"
      :confirm-text="t.common.delete"
      @cancel="batchDeleteModalVisible = false"
      @confirm="confirmBatchDelete"
    />

    <!-- ==================== 通用右侧 Drawer ==================== -->
    <SideDrawer 
      :visible="detailDrawerVisible" 
      :title="drawerMode === 'read' ? t.clients.title : tExt.repayTitle" 
      :icon="drawerMode === 'read' ? '👤' : '💰'"
      @close="closeDrawer"
    >
      <!-- 头部操作按钮 -->
      <template #header-actions>
        <template v-if="drawerMode === 'read'">
          <!-- 🌟 新增：对账单按钮 -->
          <button 
            @click="openStatementModal" 
            class="text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 border border-blue-200/80 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer"
          >
            📄 对账单
          </button>
          <button 
            v-if="(currentClient?.debt || 0) > 0"
            @click="switchToRepay" 
            class="text-xs bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200/80 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer"
          >
            💰 {{ tExt.repay }}
          </button>
          <button @click="onDeleteFromDrawer" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer">
            {{ t.common.delete }}
          </button>
        </template>
      </template>

      <!-- 内容区 -->
      <div class="p-6">
        <!-- 只读详情态 -->
        <div v-if="drawerMode === 'read'" class="space-y-5">
          <div class="bg-rose-50/50 p-4 rounded-xl border border-rose-100 space-y-1">
            <div class="text-xs text-rose-500 font-semibold">{{ tExt.currentDebt }}</div>
            <div class="flex items-baseline gap-2">
              <span class="font-black text-rose-600 text-2xl font-mono">$ {{ (currentClient?.debt || 0).toFixed(2) }}</span>
              <span class="text-rose-400 font-medium text-xs"> (Bs. {{ ((currentClient?.debt || 0) * bcvRate).toFixed(2) }})</span>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.clients.colName }}</p>
              <p class="font-bold text-slate-800">{{ currentClient?.name }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.clients.colType }}</p>
              <span :class="['inline-flex px-2.5 py-1 rounded-md text-xs font-semibold',
                currentClient?.client_type === 'Mayorista' ? 'bg-purple-50 text-purple-600' : (currentClient?.client_type === 'Taller' ? 'bg-amber-50 text-amber-600' : 'bg-blue-50 text-blue-600')]">
                {{ getClientTypeLabel(currentClient?.client_type) }}
              </span>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.clients.colPhone }}</p>
              <p class="font-mono text-slate-800">{{ currentClient?.phone || '-' }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.clients.colRif }}</p>
              <p class="font-mono text-slate-800">{{ currentClient?.rif_or_cedula || '-' }}</p>
            </div>
            <div class="col-span-2">
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ t.clients.colAddress }}</p>
              <p class="text-slate-700">{{ currentClient?.address || '-' }}</p>
            </div>
          </div>
        </div>

        <!-- 收款编辑态 -->
        <div v-else-if="drawerMode === 'repay'" class="space-y-5">
          <div class="flex items-end gap-3">
            <div class="flex-1">
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.amountPaid }}</label>
              <input 
                v-model.number="repayForm.amount_paid" 
                type="number" 
                step="0.01" 
                min="0"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-lg font-black font-mono text-slate-800 outline-none focus:border-blue-500 transition-colors" 
              />
            </div>
            <div class="flex bg-slate-100 p-1 rounded-xl shrink-0 mb-0.5">
              <button 
                @click="repayForm.currency = 'USD'"
                :class="repayForm.currency === 'USD' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-700'"
                class="px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer"
              >
                USD ($)
              </button>
              <button 
                @click="repayForm.currency = 'BS'"
                :class="repayForm.currency === 'BS' ? 'bg-white shadow-sm text-blue-600' : 'text-slate-500 hover:text-slate-700'"
                class="px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer"
              >
                Bs.
              </button>
            </div>
          </div>

          <div class="flex items-center justify-between bg-blue-50/50 p-3 rounded-xl border border-blue-100">
            <span class="text-xs text-blue-700 font-semibold">{{ tExt.usdEquivalent }}:</span>
            <span class="text-sm font-black text-blue-700 font-mono">
              $ {{ repayForm.currency === 'USD' ? (repayForm.amount_paid || 0).toFixed(2) : ((repayForm.amount_paid || 0) / bcvRate).toFixed(2) }}
            </span>
          </div>

          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.payMethod }}</label>
              <select 
                v-model="repayForm.payment_method"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-bold outline-none focus:border-blue-500 cursor-pointer"
              >
                <option v-for="pm in paymentMethods" :key="pm.value" :value="pm.value">{{ pm.label }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.referenceNo }}</label>
              <input 
                v-model="repayForm.reference_no" 
                type="text" 
                :placeholder="tExt.optional"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-mono outline-none focus:border-blue-500" 
              />
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作区（仅收款态显示） -->
      <template #footer>
        <div v-if="drawerMode === 'repay'" class="px-6 py-4 border-t border-slate-100 flex items-center justify-end gap-3">
          <button @click="switchToRead" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">
            {{ t.common.cancel }}
          </button>
          <button 
            @click="submitRepayment" 
            :disabled="isRepaying"
            class="px-6 py-2.5 bg-amber-500 hover:bg-amber-600 disabled:bg-amber-300 text-white rounded-xl text-xs font-bold shadow-md shadow-amber-500/20 transition-all cursor-pointer"
          >
            {{ isRepaying ? '...' : tExt.confirmRepay }}
          </button>
        </div>
      </template>
    </SideDrawer>

    <!-- 🌟 新增：客户历史对账单弹窗 -->
    <div v-if="statementModalVisible" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center z-[100] p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-3xl w-full overflow-hidden border border-slate-100 flex flex-col max-h-[90vh]">
        
        <!-- 头部 -->
        <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50 shrink-0">
          <div>
            <h3 class="font-extrabold text-base text-slate-900">客户历史对账单</h3>
            <p class="text-xs text-slate-500 mt-0.5">客户：{{ currentClient?.name }} | RIF: {{ currentClient?.rif_or_cedula || '无' }}</p>
          </div>
          <div class="flex items-center gap-2">
            <button @click="printStatement" class="text-xs bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-bold shadow-md transition-colors cursor-pointer">
              🖨️ 打印对账单
            </button>
            <button @click="statementModalVisible = false" class="text-slate-400 hover:text-slate-700 text-lg font-bold p-1 cursor-pointer">✕</button>
          </div>
        </div>

        <!-- 对账单内容区（可滚动，打印时也靠它） -->
        <div class="flex-1 overflow-y-auto p-6" id="statement-print-area">
          
          <div class="text-center pb-4 border-b border-slate-200 mb-4">
            <h2 class="text-xl font-black text-slate-800">TOSTIKYK ERP - 历史对账单</h2>
            <p class="text-xs text-slate-500 mt-1">生成时间: {{ new Date().toLocaleString() }}</p>
          </div>

          <table class="w-full text-left border-collapse text-sm">
            <thead>
              <tr class="bg-slate-100 border-b border-slate-200 text-xs font-bold text-slate-600">
                <th class="py-2 px-3">日期</th>
                <th class="py-2 px-3">单号</th>
                <th class="py-2 px-3">支付方式</th>
                <th class="py-2 px-3 text-right">发生金额</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100">
              <tr v-for="tx in clientStatementList" :key="tx.orderId || tx.dbId" class="hover:bg-slate-50">
                <td class="py-2 px-3 font-mono text-xs text-slate-500">{{ tx.time ? tx.time.split(' ')[0] : '-' }}</td>
                <td class="py-2 px-3 font-mono font-bold text-blue-600">{{ tx.orderId || tx.dbId }}</td>
                <td class="py-2 px-3 text-xs">{{ tx.paymentMethod }}</td>
                <td class="py-2 px-3 text-right font-mono font-bold" :class="tx.paymentMethod.includes('Fiado') ? 'text-rose-600' : 'text-emerald-600'">
                  $ {{ Number(tx.totalUsd || 0).toFixed(2) }}
                </td>
              </tr>
              <tr v-if="clientStatementList.length === 0">
                <td colspan="4" class="py-10 text-center text-slate-400 text-xs">该客户暂无历史交易记录</td>
              </tr>
            </tbody>
          </table>

          <!-- 底部汇总 -->
          <div class="mt-6 pt-4 border-t-2 border-dashed border-slate-300 flex justify-end">
            <div class="text-right space-y-2">
              <p class="text-sm text-slate-600">当前未结欠款：<span class="font-black text-rose-600 text-lg font-mono">$ {{ (currentClient?.debt || 0).toFixed(2) }}</span></p>
              <p class="text-xs text-slate-400 font-mono">按当前 BCV 折合: Bs. {{ ((currentClient?.debt || 0) * bcvRate).toFixed(2) }}</p>
            </div>
          </div>
        </div>

      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { Search, Plus, FileSpreadsheet } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api'
import { useNotifications } from '../composables/useNotifications'
import { useInventory } from '../composables/useInventory'
import ConfirmDialog from './ConfirmDialog.vue'
import SideDrawer from './SideDrawer.vue'

const props = defineProps({
  clientsList: Array,
  clientSearchQuery: String
})

const emit = defineEmits(['update:clientSearchQuery', 'open-add-client', 'export-clients', 'delete-client', 'refresh-data'])
const { t, currentLang } = useI18n()
const { showSuccessModal } = useNotifications()
const { bcvRate } = useInventory()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    exportClients: isZh ? '导出客户' : isEs ? 'Exportar Clientes' : 'Export Clients',
    batchDelete: isZh ? '批量删除' : isEs ? 'Eliminar Lote' : 'Batch Delete',
    batchSelected: isZh ? '已选' : isEs ? 'seleccionados' : 'selected',
    batchDeleteTitle: isZh ? '确认批量删除客户' : isEs ? 'Confirmar Eliminación de Clientes' : 'Confirm Batch Delete',
    batchDeleteMsg: isZh ? `确定要批量删除选中的 ${selectedIds.value.length} 个客户档案吗？删除后不可恢复。` : isEs ? `¿Eliminar ${selectedIds.value.length} clientes seleccionados? No se puede deshacer.` : `Delete ${selectedIds.value.length} selected clients? Cannot be undone.`,
    repay: isZh ? '收款' : isEs ? 'Cobrar' : 'Repay',
    repayTitle: isZh ? '客户还款收款' : isEs ? 'Cobro de Deuda' : 'Client Debt Collection',
    currentDebt: isZh ? '当前欠款' : isEs ? 'Deuda Actual' : 'Current Debt',
    amountPaid: isZh ? '收款金额' : isEs ? 'Monto a Cobrar' : 'Amount to Pay',
    usdEquivalent: isZh ? '折合美元' : isEs ? 'Equivalente USD' : 'USD Equivalent',
    payMethod: isZh ? '支付方式' : isEs ? 'Método de Pago' : 'Payment Method',
    referenceNo: isZh ? '回执号码' : isEs ? 'Nro. Referencia' : 'Reference No.',
    confirmRepay: isZh ? '确认收款' : isEs ? 'Confirmar Cobro' : 'Confirm Repayment',
    optional: isZh ? '选填' : isEs ? 'Opcional' : 'Optional',
    regular: isZh ? '零售' : isEs ? 'Regular' : 'Retail',
    taller: isZh ? '修理厂' : isEs ? 'Taller' : 'Workshop',
    mayorista: isZh ? '批发商' : isEs ? 'Mayorista' : 'Wholesaler',
    toastInvalidAmount: isZh ? '请输入有效的金额' : isEs ? 'Ingrese un monto válido' : 'Please enter a valid amount',
    toastRepaySuccess: isZh ? '收款成功！' : isEs ? '¡Cobro exitoso!' : 'Repayment successful!',
    toastRepayFailed: isZh ? '收款失败' : isEs ? 'Cobro fallido' : 'Repayment failed',
    toastNetworkError: isZh ? '网络连接异常' : isEs ? 'Error de conexión' : 'Network error'
  }
})

const paymentMethods = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return [
    { value: 'Cash_USD', label: isZh ? '美元现金' : isEs ? 'Efectivo USD' : 'Cash USD' },
    { value: 'Cash_BS', label: isZh ? '玻利瓦尔现金' : isEs ? 'Efectivo Bs.' : 'Cash Bs.' },
    { value: 'Pago_Movil', label: isZh ? 'Pago Móvil' : isEs ? 'Pago Móvil' : 'Pago Móvil' },
    { value: 'Card_POS', label: isZh ? '刷卡 (POS)' : isEs ? 'Punto de Venta' : 'Card POS' },
    { value: 'Bank_Transfer', label: isZh ? '银行转账' : isEs ? 'Transferencia' : 'Bank Transfer' },
    { value: 'Zelle', label: isZh ? 'Zelle' : isEs ? 'Zelle' : 'Zelle' }
  ]
})

const getClientTypeLabel = (type) => {
  if (type === 'Mayorista') return tExt.value.mayorista
  if (type === 'Taller') return tExt.value.taller
  return tExt.value.regular
}

const selectedIds = ref([])
const batchDeleteModalVisible = ref(false)

const filteredClients = computed(() => {
  return props.clientsList.filter(c => {
    return !props.clientSearchQuery ||
      c.name.toLowerCase().includes(props.clientSearchQuery.toLowerCase()) ||
      (c.rif_or_cedula && c.rif_or_cedula.toLowerCase().includes(props.clientSearchQuery.toLowerCase()))
  })
})

const isAllSelected = computed(() => {
  if (filteredClients.value.length === 0) return false
  return filteredClients.value.every(item => selectedIds.value.includes(item.id))
})

const toggleSelectAll = (e) => {
  if (e.target.checked) {
    selectedIds.value = filteredClients.value.map(i => i.id)
  } else {
    selectedIds.value = []
  }
}

const toggleSelect = (id) => {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter(i => i !== id)
  } else {
    selectedIds.value.push(id)
  }
}

const confirmBatchDelete = async () => {
  try {
    for (const id of selectedIds.value) {
      await apiFetch(`/api/clients/${id}`, { method: 'DELETE' })
    }
    batchDeleteModalVisible.value = false
    selectedIds.value = []
    showSuccessModal('🗑️ ' + t.value.common.success)
    emit('refresh-data')
  } catch (e) {
    batchDeleteModalVisible.value = false
    showSuccessModal('❌ ' + t.value.common.error)
  }
}

const detailDrawerVisible = ref(false)
const drawerMode = ref('read')
const currentClient = ref(null)
const isRepaying = ref(false)

const repayForm = ref({
  amount_paid: 0,
  currency: 'USD',
  payment_method: 'Cash_USD',
  reference_no: '',
  notes: ''
})

const openDetailDrawer = (client) => {
  currentClient.value = { ...client }
  drawerMode.value = 'read'
  detailDrawerVisible.value = true
}

const switchToRepay = () => {
  repayForm.value = {
    amount_paid: currentClient.value?.debt || 0,
    currency: 'USD',
    payment_method: 'Cash_USD',
    reference_no: '',
    notes: ''
  }
  drawerMode.value = 'repay'
}

const switchToRead = () => {
  drawerMode.value = 'read'
}

const closeDrawer = () => {
  detailDrawerVisible.value = false
  drawerMode.value = 'read'
}

const onDeleteFromDrawer = () => {
  emit('delete-client', currentClient.value)
  closeDrawer()
}

const submitRepayment = async () => {
  if (repayForm.value.amount_paid <= 0) {
    showSuccessModal('❌ ' + tExt.value.toastInvalidAmount)
    return
  }

  isRepaying.value = true
  try {
    const payload = {
      client_name: currentClient.value.name,
      amount_paid: repayForm.value.amount_paid,
      currency: repayForm.value.currency,
      payment_method: repayForm.value.payment_method,
      reference_no: repayForm.value.reference_no,
      notes: repayForm.value.notes
    }

    const res = await apiFetch('/api/clients/repay', {
      method: 'POST',
      body: JSON.stringify(payload)
    })

    if (res.ok) {
      const data = await res.json()
      showSuccessModal(`✅ ${tExt.value.toastRepaySuccess} 折合 $${data.amount_usd_equivalent.toFixed(2)}，剩余欠款 $${data.remaining_debt.toFixed(2)}`)
      
      if (currentClient.value) {
        currentClient.value.debt = data.remaining_debt
      }
      
      drawerMode.value = 'read'
      emit('refresh-data')
    } else {
      const err = await res.json().catch(() => ({}))
      showSuccessModal(`❌ ${tExt.value.toastRepayFailed}: ${err.detail || t.common.error}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ ' + tExt.value.toastNetworkError)
  } finally {
    isRepaying.value = false
  }
}

// 🌟 新增：对账单逻辑
const statementModalVisible = ref(false)
const clientStatementList = ref([])

const openStatementModal = async () => {
  if (!currentClient.value) return
  statementModalVisible.value = true
  
  try {
    const res = await apiFetch('/api/pos/orders')
    if (res.ok) {
      const allOrders = await res.json()
      // 过滤出属于当前客户的订单
      clientStatementList.value = allOrders.filter(o => 
        o.clientName === currentClient.value.name || 
        o.client_id === currentClient.value.id
      )
      // 按时间倒序
      clientStatementList.value.sort((a, b) => (b.time || '').localeCompare(a.time || ''))
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ 获取历史订单失败')
  }
}

const printStatement = () => {
  window.print()
}
</script>

<style scoped>
/* 🌟 打印对账单专用样式 */
@media print {
  body * {
    visibility: hidden;
  }
  #statement-print-area, #statement-print-area * {
    visibility: visible;
  }
  #statement-print-area {
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    padding: 20px;
    background: white;
  }
  /* 隐藏顶部的按钮区，只打印白纸内容 */
  .fixed > div > .p-5.border-b {
    display: none !important;
  }
}
</style>