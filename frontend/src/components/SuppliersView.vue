<!-- src/components/SuppliersView.vue -->
<template>
  <div class="space-y-6">
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <!-- 顶部操作栏 -->
      <div class="p-4 md:p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4">
        <div class="flex items-center gap-3 w-full md:w-auto">
          <div class="relative w-full md:w-72">
            <Search class="absolute left-3.5 top-3 text-slate-400" :size="16" />
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜索供应商名称 / 电话..."
              class="w-full bg-slate-50 border border-slate-200 text-sm rounded-xl pl-10 pr-4 py-2.5 outline-none focus:border-blue-500 focus:bg-white transition-all font-bold"
            />
          </div>
        </div>

        <div class="flex items-center gap-3">
          <!-- 🌟 统一样式：已选状态、批量删除、取消选择 -->
          <transition name="fade">
            <div v-if="selectedIds.length > 0" class="flex items-center gap-3 mr-2">
              <span class="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded-md border border-blue-100">
                已选 {{ selectedIds.length }} 项
              </span>
              <button 
                @click="batchDeleteModalVisible = true" 
                class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 px-3.5 py-2 rounded-xl font-bold transition-colors cursor-pointer flex items-center gap-1.5 shadow-sm"
              >
                🗑️ 批量删除
              </button>
              <button 
                @click="selectedIds = []" 
                class="text-xs text-slate-400 hover:text-slate-600 underline cursor-pointer transition-colors"
              >
                取消选择
              </button>
            </div>
          </transition>

          <button
            @click="openAddModal"
            class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-bold text-sm shadow-md shadow-blue-500/25 transition-all cursor-pointer"
          >
            <Plus :size="16" />
            <span>新增供应商</span>
          </button>
        </div>
      </div>

      <!-- 列表表格 -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[750px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3.5 px-4 w-12 text-center">
                <input 
                  type="checkbox" 
                  :checked="isAllSelected" 
                  @change="toggleSelectAll" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </th>
              <th class="py-3.5 px-6">供应商名称</th>
              <th class="py-3.5 px-6">联系人</th>
              <th class="py-3.5 px-6">联系电话</th>
              <th class="py-3.5 px-6">应付欠款</th>
              <th class="py-3.5 px-6 text-center">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="filteredSuppliers.length === 0">
              <td colspan="6" class="text-center py-12 text-slate-400 text-xs">暂无符合条件的供应商档案</td>
            </tr>
            
            <!-- 点击整行选中，添加高亮背景 -->
            <tr 
              v-for="s in paginatedSuppliers" 
              :key="s.id" 
              @click="toggleSelect(s.id)"
              :class="[
                'transition-colors cursor-pointer',
                selectedIds.includes(s.id) ? 'bg-blue-50/60 border-blue-200' : 'hover:bg-slate-50/80'
              ]"
            >
              <td class="py-4 px-4 text-center" @click.stop>
                <input 
                  type="checkbox" 
                  :checked="selectedIds.includes(s.id)" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 pointer-events-none" 
                />
              </td>
              <td class="py-4 px-6 font-bold text-slate-900">🏢 {{ s.name }}</td>
              <td class="py-4 px-6 text-slate-600">{{ s.contact_person || '-' }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">{{ s.phone || '-' }}</td>
              <td class="py-4 px-6 font-bold" :class="(s.debt_usd || 0) > 0 ? 'text-rose-600' : 'text-slate-400'">
                $ {{ (s.debt_usd || 0).toFixed(2) }}
              </td>
              <!-- 操作按钮区：阻止冒泡 -->
              <td class="py-4 px-6 text-center" @click.stop>
                <div class="flex items-center justify-center gap-2">
                  <button v-if="(s.debt_usd || 0) > 0" @click="openPayModal(s)" class="text-xs bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">💰 付款</button>
                  <button @click="openEditModal(s)" class="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">编辑</button>
                  <button @click="promptDelete(s)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">删除</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs">
        <span class="text-slate-500 font-medium">
          显示第 <strong class="text-slate-800">{{ (currentPage - 1) * pageSize + 1 }}</strong> 到 
          <strong class="text-slate-800">{{ Math.min(currentPage * pageSize, filteredSuppliers.length) }}</strong> 条，共 
          <strong class="text-slate-800">{{ filteredSuppliers.length }}</strong> 个供应商
        </span>
        
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 bg-white border border-slate-200 rounded-xl px-2 py-1 shadow-2xs">
            <span class="text-slate-400 text-[11px]">跳转到</span>
            <input type="number" min="1" :max="totalPages" v-model.number="jumpPageInput" @keyup.enter="handleJumpPage" class="w-12 text-center font-mono font-bold text-blue-600 bg-slate-50 rounded-lg py-1 outline-none border border-slate-200 focus:border-blue-500 text-xs" />
            <span class="text-slate-400 text-[11px]">/ {{ totalPages }} 页</span>
            <button @click="handleJumpPage" class="bg-blue-50 hover:bg-blue-100 text-blue-600 px-2.5 py-1 rounded-lg font-bold transition-colors cursor-pointer text-[11px]">跳转</button>
          </div>

          <div class="flex items-center gap-1.5">
            <button @click="currentPage--" :disabled="currentPage === 1" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">上一页</button>
            <span class="px-3 py-1 font-mono font-bold text-slate-700">{{ currentPage }} / {{ totalPages }}</span>
            <button @click="currentPage++" :disabled="currentPage === totalPages" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">下一页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 新增/编辑 供应商弹窗 -->
    <div v-if="modalVisible" @click.self="modalVisible = false" class="fixed inset-0 bg-slate-950/60 backdrop-blur-md flex items-center justify-center z-50 p-6">
      <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100 flex flex-col animate-in zoom-in-95 duration-150">
        <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-white/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900">{{ isEditing ? '✏️ 编辑供应商' : '🏢 新增供应商' }}</h3>
          <button @click="modalVisible = false" class="text-slate-400 hover:text-slate-700 font-bold text-base p-1">✕</button>
        </div>
        
        <div class="p-5 space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">供应商名称 *</label>
            <input v-model="formData.name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-bold text-slate-900" placeholder="例如：广州汽配城" />
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">联系人</label>
              <input v-model="formData.contact_person" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500" placeholder="张老板" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">联系电话</label>
              <input v-model="formData.phone" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" placeholder="+58 412..." />
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">地址</label>
            <input v-model="formData.address" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500" placeholder="选填" />
          </div>
        </div>

        <div class="p-5 border-t border-slate-100 flex justify-end gap-3 bg-slate-50/50">
          <button @click="modalVisible = false" class="px-5 py-2.5 rounded-xl text-xs font-bold bg-slate-200 text-slate-600 hover:bg-slate-300 transition-colors cursor-pointer">取消</button>
          <button @click="saveSupplier" :disabled="isSubmitting" class="px-6 py-2.5 rounded-xl text-xs font-bold bg-blue-600 text-white hover:bg-blue-700 shadow-md transition-colors cursor-pointer disabled:opacity-50">
            {{ isSubmitting ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 付款弹窗 -->
    <div v-if="isPayModalVisible" @click.self="isPayModalVisible = false" class="fixed inset-0 bg-slate-950/60 backdrop-blur-md flex items-center justify-center z-[60] p-6">
      <div class="bg-white rounded-3xl shadow-2xl max-w-sm w-full overflow-hidden border border-slate-100 flex flex-col">
        <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-white/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900">💰 供应商付款</h3>
          <button @click="isPayModalVisible = false" class="text-slate-400 hover:text-slate-700 font-bold text-base p-1">✕</button>
        </div>
        <div class="p-5 space-y-4">
          <div class="bg-rose-50/50 p-3 rounded-xl border border-rose-100">
            <div class="text-xs text-rose-500 font-bold">当前应付欠款:</div>
            <div class="text-lg font-black text-rose-600 font-mono">$ {{ currentPaySupplier?.debt_usd.toFixed(2) }}</div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">本次付款金额 *</label>
            <input v-model.number="payForm.amount_paid" type="number" step="0.01" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm font-bold font-mono outline-none focus:border-blue-500" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">支付方式</label>
              <select v-model="payForm.payment_method" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-bold outline-none cursor-pointer">
                <option value="Cash_USD">美元现金</option>
                <option value="Cash_BS">玻利瓦尔现金</option>
                <option value="Bank_Transfer">银行转账</option>
                <option value="Zelle">Zelle</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">回执号</label>
              <input v-model="payForm.reference_no" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs outline-none" placeholder="选填" />
            </div>
          </div>
        </div>
        <div class="p-5 border-t border-slate-100 flex justify-end gap-3 bg-slate-50/50">
          <button @click="isPayModalVisible = false" class="px-5 py-2.5 rounded-xl text-xs font-bold bg-slate-200 text-slate-600 hover:bg-slate-300 transition-colors cursor-pointer">取消</button>
          <button @click="submitPay" :disabled="isSubmittingPay" class="px-6 py-2.5 rounded-xl text-xs font-bold bg-emerald-600 text-white hover:bg-emerald-700 shadow-md transition-colors cursor-pointer disabled:opacity-50">
            {{ isSubmittingPay ? '处理中...' : '确认付款' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 批量删除确认弹窗 -->
    <ConfirmDialog
      :visible="batchDeleteModalVisible"
      overlay-class="bg-slate-950/60"
      title="确认批量删除供应商"
      :message="`确定要批量删除选中的 ${selectedIds.length} 个供应商档案吗？删除后不可恢复。`"
      :cancel-text="'取消'"
      :confirm-text="'确认删除'"
      @cancel="batchDeleteModalVisible = false"
      @confirm="confirmBatchDelete"
    />

    <!-- 单个删除确认弹窗 -->
    <ConfirmDialog
      :visible="isSingleDeleteVisible"
      overlay-class="bg-slate-950/60"
      title="确认删除供应商"
      :message="`确定要删除供应商 '${deleteTarget?.name}' 吗？删除后不可恢复。`"
      :cancel-text="'取消'"
      :confirm-text="'确认删除'"
      @cancel="isSingleDeleteVisible = false"
      @confirm="executeSingleDelete"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { Search, Plus } from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import { useNotifications } from '../composables/useNotifications'
import { useInventory } from '../composables/useInventory'
import ConfirmDialog from './ConfirmDialog.vue'

const { showSuccessModal } = useNotifications()
const { bcvRate } = useInventory()

const suppliersList = ref([])
const searchQuery = ref('')

const modalVisible = ref(false)
const isEditing = ref(false)
const editingId = ref(null)
const isSubmitting = ref(false)

const formData = ref({ name: '', contact_person: '', phone: '', address: '' })

const selectedIds = ref([])
const batchDeleteModalVisible = ref(false)
const pageSize = 10
const currentPage = ref(1)
const jumpPageInput = ref(1)

const isPayModalVisible = ref(false)
const isSubmittingPay = ref(false)
const currentPaySupplier = ref(null)
const payForm = ref({ amount_paid: 0, payment_method: 'Cash_USD', reference_no: '' })

const isSingleDeleteVisible = ref(false)
const deleteTarget = ref(null)

const promptDelete = (sup) => {
  deleteTarget.value = sup
  isSingleDeleteVisible.value = true
}

const executeSingleDelete = async () => {
  if (!deleteTarget.value) return
  try {
    const res = await apiFetch(`/api/suppliers/${deleteTarget.value.id}`, { method: 'DELETE' })
    if (res.ok) {
      showSuccessModal('🗑️ 已删除')
      fetchSuppliers()
    }
    else {
      const err = await res.json()
      showSuccessModal(`❌ 无法删除: ${err.detail}`)
    }
  } catch (e) { showSuccessModal('❌ 网络异常') }
  finally {
    isSingleDeleteVisible.value = false
    deleteTarget.value = null
  }
}

const handleKeydown = (e) => {
  if (e.key === 'Escape') {
    if (isPayModalVisible.value) isPayModalVisible.value = false
    else if (modalVisible.value) modalVisible.value = false
    else if (batchDeleteModalVisible.value) batchDeleteModalVisible.value = false
    else if (isSingleDeleteVisible.value) isSingleDeleteVisible.value = false
  }
}

const fetchSuppliers = async () => {
  try {
    const res = await apiFetch('/api/suppliers')
    if (res.ok) suppliersList.value = await res.json()
  } catch (e) { console.error(e) }
}

const filteredSuppliers = computed(() => {
  if (!searchQuery.value.trim()) return suppliersList.value
  const q = searchQuery.value.toLowerCase().trim()
  return suppliersList.value.filter(s => s.name.toLowerCase().includes(q) || (s.phone && s.phone.includes(q)))
})

const totalPages = computed(() => Math.ceil(filteredSuppliers.value.length / pageSize) || 1)
const paginatedSuppliers = computed(() => filteredSuppliers.value.slice((currentPage.value - 1) * pageSize, currentPage.value * pageSize))

watch(searchQuery, () => { currentPage.value = 1; jumpPageInput.value = 1; selectedIds.value = [] })
watch(currentPage, (val) => { jumpPageInput.value = val })

const handleJumpPage = () => {
  let target = parseInt(jumpPageInput.value)
  if (isNaN(target)) return
  if (target < 1) target = 1
  if (target > totalPages.value) target = totalPages.value
  currentPage.value = target
}

const isAllSelected = computed(() => paginatedSuppliers.value.length > 0 && paginatedSuppliers.value.every(item => selectedIds.value.includes(item.id)))
const toggleSelectAll = (e) => {
  if (e.target.checked) selectedIds.value = Array.from(new Set([...selectedIds.value, ...paginatedSuppliers.value.map(i => i.id)]))
  else selectedIds.value = selectedIds.value.filter(id => !paginatedSuppliers.value.map(i => i.id).includes(id))
}

const toggleSelect = (id) => {
  if (selectedIds.value.includes(id)) selectedIds.value = selectedIds.value.filter(i => i !== id)
  else selectedIds.value.push(id)
}

const openAddModal = () => {
  isEditing.value = false; editingId.value = null; formData.value = { name: '', contact_person: '', phone: '', address: '' }; modalVisible.value = true
}
const openEditModal = (sup) => {
  isEditing.value = true; editingId.value = sup.id; formData.value = { ...sup }; modalVisible.value = true
}

const saveSupplier = async () => {
  if (!formData.value.name.trim()) return showSuccessModal('❌ 请输入供应商名称')
  isSubmitting.value = true
  try {
    const res = await apiFetch(isEditing.value ? `/api/suppliers/${editingId.value}` : '/api/suppliers', {
      method: isEditing.value ? 'PUT' : 'POST',
      body: JSON.stringify(formData.value)
    })
    if (res.ok) { showSuccessModal('✅ 保存成功'); modalVisible.value = false; fetchSuppliers() }
    else { const err = await res.json(); showSuccessModal(`❌ 失败: ${err.detail}`) }
  } catch (e) { showSuccessModal('❌ 网络异常') } finally { isSubmitting.value = false }
}

const confirmBatchDelete = async () => {
  let errs = []
  for (const id of selectedIds.value) {
    const res = await apiFetch(`/api/suppliers/${id}`, { method: 'DELETE' })
    if (!res.ok) { const err = await res.json(); errs.push(err.detail) }
  }
  batchDeleteModalVisible.value = false; selectedIds.value = []; fetchSuppliers()
  if (errs.length > 0) showSuccessModal(`⚠️ 部分失败: ${errs[0]}`)
  else showSuccessModal('🗑️ 批量删除成功')
}

const openPayModal = (sup) => {
  currentPaySupplier.value = sup
  payForm.value = { amount_paid: sup.debt_usd, payment_method: 'Cash_USD', reference_no: '' }
  isPayModalVisible.value = true
}

const submitPay = async () => {
  if (payForm.value.amount_paid <= 0) return showSuccessModal('❌ 金额必须大于 0')
  isSubmittingPay.value = true
  try {
    const res = await apiFetch(`/api/suppliers/${currentPaySupplier.value.id}/pay`, {
      method: 'POST',
      body: JSON.stringify({
        amount_paid: payForm.value.amount_paid,
        currency: payForm.value.payment_method === 'Cash_BS' ? 'BS' : 'USD',
        exchange_rate: bcvRate.value,
        payment_method: payForm.value.payment_method,
        reference_no: payForm.value.reference_no
      })
    })
    if (res.ok) { showSuccessModal('✅ 付款成功'); isPayModalVisible.value = false; fetchSuppliers() }
    else { const err = await res.json(); showSuccessModal(`❌ 失败: ${err.detail}`) }
  } catch (e) { showSuccessModal('❌ 网络异常') } finally { isSubmittingPay.value = false }
}

onMounted(() => { 
  fetchSuppliers() 
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>