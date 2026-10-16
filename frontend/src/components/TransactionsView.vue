<!-- src/components/TransactionsView.vue -->
<template>
  <div class="space-y-6">
    
    <!-- 🌟 顶部极简统计摘要横幅 -->
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-1">
        <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">今日总流水单数</span>
        <div class="text-2xl font-black text-slate-900 font-mono">{{ transactionsList.length }} 笔</div>
      </div>
      <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-1">
        <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">今日出库销售总额</span>
        <div class="text-2xl font-black text-amber-600 font-mono">$ {{ totalOutAmount.toFixed(2) }}</div>
      </div>
      <div class="bg-white p-5 rounded-2xl border border-slate-200/80 shadow-xs space-y-1">
        <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">今日采购入库总额</span>
        <div class="text-2xl font-black text-emerald-600 font-mono">$ {{ totalInAmount.toFixed(2) }}</div>
      </div>
    </div>

    <!-- 🌟 主表格与筛选操作区 -->
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div class="p-4 md:p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4">
        
        <!-- 类型胶囊快速切换 -->
        <div class="flex items-center gap-1.5 bg-slate-100 p-1 rounded-xl">
          <button 
            @click="filterType = 'ALL'"
            :class="['px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer', filterType === 'ALL' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900']"
          >
            全部类型
          </button>
          <button 
            @click="filterType = 'OUT'"
            :class="['px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer', filterType === 'OUT' ? 'bg-white text-amber-600 shadow-xs' : 'text-slate-600 hover:text-slate-900']"
          >
            📦 出库（销售）
          </button>
          <button 
            @click="filterType = 'IN'"
            :class="['px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer', filterType === 'IN' ? 'bg-white text-emerald-600 shadow-xs' : 'text-slate-600 hover:text-slate-900']"
          >
            📥 采购入库
          </button>
        </div>

        <div class="flex items-center gap-3 w-full md:w-auto flex-wrap justify-end">
          <!-- 🌟 批量删除按钮 -->
          <button 
            v-if="selectedIds.length > 0" 
            @click="batchDeleteModalVisible = true" 
            class="flex items-center gap-2 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200/80 px-4 py-2.5 rounded-xl text-xs font-bold shadow-xs transition-all cursor-pointer"
          >
            <span>🗑️ 批量删除 (已选 {{ selectedIds.length }} 项)</span>
          </button>

          <button
            @click="$emit('export-transactions')"
            class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-emerald-700 hover:bg-emerald-800 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md transition-all cursor-pointer"
          >
            <FileSpreadsheet :size="16" />
            <span>{{ t.exportExcelBtn || '导出 Excel' }}</span>
          </button>
          <button
            @click="$emit('open-tx-modal')"
            class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2.5 rounded-xl font-medium text-sm shadow-md shadow-emerald-500/25 transition-all cursor-pointer"
          >
            <Plus :size="16" />
            <span>{{ t.newTransBtn || '新增单据' }}</span>
          </button>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <!-- 🌟 全选复选框 -->
              <th class="py-3.5 px-4 w-12 text-center">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected" 
                  @change="toggleSelectAll" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </th>
              <th class="py-3.5 px-6">{{ t.txTime || '时间' }}</th>
              <th class="py-3.5 px-6">{{ t.colCode || '商品编码/OEM' }}</th>
              <th class="py-3.5 px-6">{{ t.colName || '配件名称' }}</th>
              <th class="py-3.5 px-6 text-center">{{ t.txType || '类型' }}</th>
              <th class="py-3.5 px-6">{{ t.txQty || '数量' }}</th>
              <th class="py-3.5 px-6">{{ t.txUnitPrice || '单价' }}</th>
              <th class="py-3.5 px-6">{{ t.txTotal || '总金额' }}</th>
              <th class="py-3.5 px-6">{{ t.txTarget || '客户 / 供应商' }}</th>
              <th class="py-3.5 px-6 text-center">{{ t.colActions || '操作' }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-for="tx in filteredTransactions" :key="tx.id" class="hover:bg-slate-50/50 transition-colors">
              <!-- 🌟 单选复选框 -->
              <td class="py-4 px-4 text-center">
                <input 
                  type="checkbox" 
                  :checked="selectedIds.includes(tx.id)" 
                  @change="toggleSelect(tx.id)" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </td>
              <td class="py-4 px-6 text-slate-500 text-xs font-mono">{{ tx.timestamp }}</td>
              <td class="py-4 px-6 font-mono font-bold text-slate-800">{{ tx.part_code || tx.part_oem }}</td>
              <td class="py-4 px-6 font-medium text-slate-900">{{ tx.part_name }}</td>
              <td class="py-4 px-6 text-center">
                <span :class="['inline-flex items-center px-2.5 py-1 rounded-md text-xs font-bold',
                  tx.type === 'IN' ? 'bg-emerald-50 text-emerald-600' : 'bg-amber-50 text-amber-600']">
                  {{ tx.type === 'IN' ? (t.txIn || '采购入库') : (t.txOut || '出库 (销售)') }}
                </span>
              </td>
              <td class="py-4 px-6 font-bold text-slate-800">{{ tx.quantity }}</td>
              <td class="py-4 px-6 text-slate-600 font-mono">
                $ {{ Number(tx.unit_price || 0).toFixed(2) }}
              </td>
              <td class="py-4 px-6 font-mono">
                <div class="font-bold text-slate-900">$ {{ Number(tx.total_amount || 0).toFixed(2) }}</div>
                <div class="text-[11px] text-slate-400 font-medium">Bs. {{ (Number(tx.total_amount || 0) * 36.50).toFixed(2) }}</div>
              </td>
              <td class="py-4 px-6 text-slate-600 font-medium">{{ tx.customer_or_supplier || 'Cliente General' }}</td>
              <td class="py-4 px-6 text-center">
                <button 
                  @click="$emit('delete-tx', tx)" 
                  class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1 rounded-lg font-semibold transition-colors cursor-pointer whitespace-nowrap"
                >
                  {{ t.btnDelete || '删除记录' }}
                </button>
              </td>
            </tr>
            <tr v-if="filteredTransactions.length === 0">
              <td colspan="10" class="py-12 text-center text-slate-400 text-xs">没有找到符合条件的进销存单据记录</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 🌟 现代化批量删除确认弹窗 -->
    <ConfirmDialog
      :visible="batchDeleteModalVisible"
      overlay-class="bg-slate-900/40"
      title="确认批量删除流水单据"
      message="批量删除选中的进销存单据后，将自动还原对应的商品库存数量。"
      cancel-text="取消"
      confirm-text="确认删除"
      @cancel="batchDeleteModalVisible = false"
      @confirm="confirmBatchDelete"
    />

  </div>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { Plus, FileSpreadsheet } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { apiFetch } from '../utils/api'
import { useNotifications } from '../composables/useNotifications'
import ConfirmDialog from './ConfirmDialog.vue'

const props = defineProps({
  transactionsList: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['export-transactions', 'open-tx-modal', 'delete-tx', 'refresh-data'])
const { t } = useI18n()
const { showSuccessModal } = useNotifications()

// 多选与批量删除状态
const selectedIds = ref([])
const batchDeleteModalVisible = ref(false)

// 类型筛选状态 ('ALL' / 'IN' / 'OUT')
const filterType = ref('ALL')

// 切换筛选类型时清空已勾选项
watch(filterType, () => {
  selectedIds.value = []
})

// 根据类型过滤流水
const filteredTransactions = computed(() => {
  if (filterType.value === 'ALL') return props.transactionsList
  return props.transactionsList.filter(tx => tx.type === filterType.value)
})

// 全选与单选逻辑
const isAllSelected = computed(() => {
  if (filteredTransactions.value.length === 0) return false
  return filteredTransactions.value.every(item => selectedIds.value.includes(item.id))
})

const toggleSelectAll = (e) => {
  if (e.target.checked) {
    selectedIds.value = filteredTransactions.value.map(i => i.id)
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

// 确认批量删除
const confirmBatchDelete = async () => {
  try {
    for (const id of selectedIds.value) {
      await apiFetch(`/api/transactions/${id}`, { method: 'DELETE' })
    }
    batchDeleteModalValue.value = false
    selectedIds.value = []
    batchDeleteModalVisible.value = false
    showSuccessModal('🗑️ 批量删除流水单据成功！')
    emit('refresh-data')
  } catch (e) {
    batchDeleteModalVisible.value = false
    showSuccessModal('❌ 批量删除出现异常')
  }
}

// 计算今日出库总金额
const totalOutAmount = computed(() => {
  return props.transactionsList
    .filter(tx => tx.type === 'OUT')
    .reduce((sum, tx) => sum + Number(tx.total_amount || 0), 0)
})

// 计算今日入库总金额
const totalInAmount = computed(() => {
  return props.transactionsList
    .filter(tx => tx.type === 'IN')
    .reduce((sum, tx) => sum + Number(tx.total_amount || 0), 0)
})
</script>