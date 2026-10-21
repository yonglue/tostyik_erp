<!-- src/components/ClientsView.vue -->
<template>
  <div class="space-y-6">
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="p-4 md:p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3 w-full md:w-auto">
          <div class="relative w-full md:w-72">
            <Search class="absolute left-3.5 top-3 text-slate-400" :size="16" />
            <input
              :value="clientSearchQuery"
              @input="$emit('update:clientSearchQuery',$event.target.value)"
              type="text"
              :placeholder="t.clients.searchPlaceholder"
              class="w-full bg-slate-50 border border-slate-200 text-sm rounded-xl pl-10 pr-4 py-2.5 outline-none focus:border-blue-500 focus:bg-white transition-all"
            />
          </div>
        </div>

        <div class="flex items-center gap-3 flex-wrap w-full md:w-auto">
          <!-- 🌟 批量删除按钮 -->
          <button 
            v-if="selectedIds.length > 0" 
            @click="batchDeleteModalVisible = true" 
            class="flex items-center gap-2 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200/80 px-4 py-2.5 rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer"
          >
            <span>🗑️ {{ tExt.batchDelete }} ({{ tExt.batchSelected }} {{ selectedIds.length }})</span>
          </button>

          <button
            @click="$emit('export-clients')"
            class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md transition-all"
          >
            <FileSpreadsheet :size="16" />
            <span>{{ tExt.exportClients }}</span>
          </button>
          <button
            @click="$emit('open-add-client')"
            class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md shadow-blue-500/25 transition-all"
          >
            <Plus :size="16" />
            <span>{{ t.clients.addBtn }}</span>
          </button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[750px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <!-- 🌟 全选框 -->
              <th class="py-3.5 px-4 w-12 text-center">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected" 
                  @change="toggleSelectAll" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </th>
              <th class="py-3.5 px-6">{{ t.clients.colName }}</th>
              <th class="py-3.5 px-6">{{ t.clients.colType }}</th>
              <th class="py-3.5 px-6">{{ t.clients.colPhone }}</th>
              <th class="py-3.5 px-6">{{ t.clients.colAddress }}</th>
              <th class="py-3.5 px-6">{{ t.clients.colRif }}</th>
              <th class="py-3.5 px-6">{{ t.clients.colDebt }}</th>
              <th class="py-3.5 px-6 text-center">{{ t.common.actions }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="filteredClients.length === 0">
              <td colspan="8" class="text-center py-12 text-slate-400 text-xs">
                {{ t.clients.empty }}
              </td>
            </tr>
            <tr v-for="c in filteredClients" :key="c.id" class="hover:bg-slate-50/50 transition-colors">
              <!-- 🌟 单选框 -->
              <td class="py-4 px-4 text-center">
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
                  {{ c.client_type }}
                </span>
              </td>
              <td class="py-4 px-6 font-mono text-slate-600">{{ c.phone || '-' }}</td>
              <td class="py-4 px-6 text-slate-600">{{ c.address || '-' }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">{{ c.rif_or_cedula || '-' }}</td>
              <td class="py-4 px-6 font-bold" :class="(c.debt || 0) > 0 ? 'text-rose-600' : 'text-slate-400'">
                $ {{ (c.debt || 0).toFixed(2) }}
              </td>
              <td class="py-4 px-6 text-center">
                <div class="flex items-center justify-center gap-2">
                  <!-- 🌟 新增：收款按钮（只有欠款大于 0 才显示） -->
                  <button 
                    v-if="(c.debt || 0) > 0"
                    @click="openRepayModal(c)" 
                    class="text-xs bg-amber-50 hover:bg-amber-100 text-amber-700 border border-amber-200/80 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer"
                  >
                    💰 {{ tExt.repay || '收款' }}
                  </button>
                  <button @click="$emit('delete-client', c)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-medium transition-colors cursor-pointer">
                    {{ t.common.delete }}
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 🌟 批量删除确认弹窗 -->
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

    <!-- 🌟 新增：客户收款 Modal -->
    <div v-if="repayModalVisible" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100 p-6 space-y-5">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-xl">💰</span>
            <h3 class="font-bold text-slate-800 text-base">{{ tExt.repayTitle || '客户还款收款' }}</h3>
          </div>
          <button @click="repayModalVisible = false" class="text-slate-400 hover:text-slate-700 text-lg font-bold cursor-pointer">✕</button>
        </div>

        <!-- 客户信息与当前欠款 -->
        <div class="bg-rose-50/50 p-4 rounded-xl border border-rose-100 space-y-1">
          <div class="text-xs text-rose-500 font-semibold">{{ tExt.clientName || '客户名称' }}: <span class="font-bold text-slate-800">{{ currentClient?.name }}</span></div>
          <div class="text-xs text-rose-500 font-semibold">
            {{ tExt.currentDebt || '当前欠款' }}: 
            <span class="font-black text-rose-600 text-sm">$ {{ (currentClient?.debt || 0).toFixed(2) }}</span>
            <span class="text-rose-400 font-normal text-[10px]"> (Bs. {{ ((currentClient?.debt || 0) * bcvRate).toFixed(2) }})</span>
          </div>
        </div>

        <div class="space-y-4">
          <!-- 金额与币种 -->
          <div class="flex items-end gap-3">
            <div class="flex-1">
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.amountPaid || '收款金额' }}</label>
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

          <!-- 实时折算提示 -->
          <div class="flex items-center justify-between bg-blue-50/50 p-3 rounded-xl border border-blue-100">
            <span class="text-xs text-blue-700 font-semibold">{{ tExt.usdEquivalent || '折合美元' }}:</span>
            <span class="text-sm font-black text-blue-700 font-mono">
              $ {{ repayForm.currency === 'USD' ? repayForm.amount_paid.toFixed(2) : (repayForm.amount_paid / bcvRate).toFixed(2) }}
            </span>
          </div>

          <!-- 支付方式与回执号 -->
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.payMethod || '支付方式' }}</label>
              <select 
                v-model="repayForm.payment_method"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-bold outline-none focus:border-blue-500 cursor-pointer"
              >
                <option value="Cash_USD">美元现金</option>
                <option value="Cash_BS">玻利瓦尔现金</option>
                <option value="Pago_Movil">Pago Móvil</option>
                <option value="Card_POS">刷卡 (POS)</option>
                <option value="Bank_Transfer">银行转账</option>
                <option value="Zelle">Zelle</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.referenceNo || '回执号码' }}</label>
              <input 
                v-model="repayForm.reference_no" 
                type="text" 
                placeholder="选填"
                class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-xs font-mono outline-none focus:border-blue-500" 
              />
            </div>
          </div>
        </div>

        <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
          <button @click="repayModalVisible = false" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">
            {{ t.common.cancel }}
          </button>
          <button 
            @click="submitRepayment" 
            :disabled="isRepaying"
            class="px-6 py-2.5 bg-amber-500 hover:bg-amber-600 disabled:bg-amber-300 text-white rounded-xl text-xs font-bold shadow-md shadow-amber-500/20 transition-all cursor-pointer"
          >
            {{ isRepaying ? '...' : (tExt.confirmRepay || '确认收款') }}
          </button>
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

const props = defineProps({
  clientsList: Array,
  clientSearchQuery: String
})

const emit = defineEmits(['update:clientSearchQuery', 'open-add-client', 'export-clients', 'delete-client', 'refresh-data'])
const { t, currentLang } = useI18n()
const { showSuccessModal } = useNotifications()
const { bcvRate } = useInventory() // 🌟 引入全局汇率

// 🌟 扩展翻译字典
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
    clientName: isZh ? '客户名称' : isEs ? 'Cliente' : 'Client',
    currentDebt: isZh ? '当前欠款' : isEs ? 'Deuda Actual' : 'Current Debt',
    amountPaid: isZh ? '收款金额' : isEs ? 'Monto a Cobrar' : 'Amount to Pay',
    usdEquivalent: isZh ? '折合美元' : isEs ? 'Equivalente USD' : 'USD Equivalent',
    payMethod: isZh ? '支付方式' : isEs ? 'Método de Pago' : 'Payment Method',
    referenceNo: isZh ? '回执号码' : isEs ? 'Nro. Referencia' : 'Reference No.',
    confirmRepay: isZh ? '确认收款' : isEs ? 'Confirmar Cobro' : 'Confirm Repayment'
  }
})

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

// ================= 收款逻辑 =================

const repayModalVisible = ref(false)
const currentClient = ref(null)
const isRepaying = ref(false)

const repayForm = ref({
  amount_paid: 0,
  currency: 'USD',
  payment_method: 'Cash_USD',
  reference_no: '',
  notes: ''
})

const openRepayModal = (client) => {
  currentClient.value = client
  repayForm.value = {
    amount_paid: client.debt || 0, // 默认填入全部欠款
    currency: 'USD',
    payment_method: 'Cash_USD',
    reference_no: '',
    notes: ''
  }
  repayModalVisible.value = true
}

const submitRepayment = async () => {
  if (repayForm.value.amount_paid <= 0) {
    showSuccessModal('❌ 请输入有效的金额')
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
      showSuccessModal(`✅ 收款成功！折合 $${data.amount_usd_equivalent.toFixed(2)}，剩余欠款 $${data.remaining_debt.toFixed(2)}`)
      repayModalVisible.value = false
      emit('refresh-data') // 让父组件刷新客户列表
    } else {
      const err = await res.json().catch(() => ({}))
      showSuccessModal(`❌ 收款失败: ${err.detail || '未知错误'}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ 网络连接异常')
  } finally {
    isRepaying.value = false
  }
}
</script>