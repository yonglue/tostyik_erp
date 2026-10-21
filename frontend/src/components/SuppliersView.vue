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
              :placeholder="tExt.searchPlaceholder"
              class="w-full bg-slate-50 border border-slate-200 text-sm rounded-xl pl-10 pr-4 py-2.5 outline-none focus:border-blue-500 focus:bg-white transition-all font-bold"
            />
          </div>
        </div>

        <div class="flex items-center gap-3">
          <transition name="fade">
            <div v-if="selectedIds.length > 0" class="flex items-center gap-3 mr-2">
              <span class="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded-md border border-blue-100">
                {{ tExt.selected }} {{ selectedIds.length }} {{ tExt.items }}
              </span>
              <button 
                @click="batchDeleteModalVisible = true" 
                class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 px-3.5 py-2 rounded-xl font-bold transition-colors cursor-pointer flex items-center gap-1.5 shadow-sm"
              >
                🗑️ {{ tExt.batchDelete }}
              </button>
              <button 
                @click="selectedIds = []" 
                class="text-xs text-slate-400 hover:text-slate-600 underline cursor-pointer transition-colors"
              >
                {{ tExt.deselect }}
              </button>
            </div>
          </transition>

          <button
            @click="openDetailDrawer(null)"
            class="flex-1 md:flex-none flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-bold text-sm shadow-md shadow-blue-500/25 transition-all cursor-pointer"
          >
            <Plus :size="16" />
            <span>{{ tExt.addBtn }}</span>
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
              <th class="py-3.5 px-6">{{ tExt.colName }}</th>
              <th class="py-3.5 px-6">{{ tExt.colContact }}</th>
              <th class="py-3.5 px-6">{{ tExt.colPhone }}</th>
              <th class="py-3.5 px-6">{{ tExt.colDebt }}</th>
              <th class="py-3.5 px-6 text-center">{{ t.common.actions }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="filteredSuppliers.length === 0">
              <td colspan="6" class="text-center py-12 text-slate-400 text-xs">{{ tExt.emptyData }}</td>
            </tr>
            
            <tr 
              v-for="s in paginatedSuppliers" 
              :key="s.id" 
              @click="openDetailDrawer(s)"
              :class="[
                'transition-colors cursor-pointer',
                selectedIds.includes(s.id) ? 'bg-blue-50/60 border-blue-200' : 'hover:bg-slate-50/80'
              ]"
            >
              <td class="py-4 px-4 text-center" @click.stop>
                <input 
                  type="checkbox" 
                  :checked="selectedIds.includes(s.id)" 
                  @change="toggleSelect(s.id)"
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </td>
              <td class="py-4 px-6 font-bold text-slate-900">🏢 {{ s.name }}</td>
              <td class="py-4 px-6 text-slate-600">{{ s.contact_person || '-' }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">{{ s.phone || '-' }}</td>
              <td class="py-4 px-6 font-bold" :class="(s.debt_usd || 0) > 0 ? 'text-rose-600' : 'text-slate-400'">
                $ {{ (s.debt_usd || 0).toFixed(2) }}
              </td>
              <td class="py-4 px-6 text-center" @click.stop>
                <div class="flex items-center justify-center gap-2">
                  <button v-if="(s.debt_usd || 0) > 0" @click="openDrawerPayMode(s)" class="text-xs bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">💰 {{ tExt.payBtn }}</button>
                  <button @click="openDrawerEditMode(s)" class="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">{{ t.common.edit }}</button>
                  <button @click="promptDelete(s)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">{{ t.common.delete }}</button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="totalPages > 1" class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs">
        <span class="text-slate-500 font-medium">
          {{ tExt.showing }} <strong class="text-slate-800">{{ (currentPage - 1) * pageSize + 1 }}</strong> {{ tExt.to }} 
          <strong class="text-slate-800">{{ Math.min(currentPage * pageSize, filteredSuppliers.length) }}</strong> {{ tExt.of }} 
          <strong class="text-slate-800">{{ filteredSuppliers.length }}</strong> {{ tExt.suppliers }}
        </span>
        
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 bg-white border border-slate-200 rounded-xl px-2 py-1 shadow-2xs">
            <span class="text-slate-400 text-[11px]">{{ tExt.jumpTo }}</span>
            <input type="number" min="1" :max="totalPages" v-model.number="jumpPageInput" @keyup.enter="handleJumpPage" class="w-12 text-center font-mono font-bold text-blue-600 bg-slate-50 rounded-lg py-1 outline-none border border-slate-200 focus:border-blue-500 text-xs" />
            <span class="text-slate-400 text-[11px]">/ {{ totalPages }} {{ tExt.page }}</span>
            <button @click="handleJumpPage" class="bg-blue-50 hover:bg-blue-100 text-blue-600 px-2.5 py-1 rounded-lg font-bold transition-colors cursor-pointer text-[11px]">{{ tExt.jumpBtn }}</button>
          </div>

          <div class="flex items-center gap-1.5">
            <button @click="currentPage--" :disabled="currentPage === 1" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">{{ tExt.prevPage }}</button>
            <span class="px-3 py-1 font-mono font-bold text-slate-700">{{ currentPage }} / {{ totalPages }}</span>
            <button @click="currentPage++" :disabled="currentPage === totalPages" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">{{ tExt.nextPage }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 🌟 通用右侧 Drawer -->
    <SideDrawer 
      :visible="detailDrawerVisible" 
      :title="drawerTitle" 
      :icon="drawerMode === 'read' ? '🏢' : (drawerMode === 'edit' ? '✏️' : '💰')"
      @close="closeDrawer"
    >
      <!-- 只读态：头部操作 -->
      <template #header-actions>
        <template v-if="drawerMode === 'read' && currentSupplier?.id">
          <button 
            v-if="(currentSupplier?.debt_usd || 0) > 0"
            @click="switchToPay" 
            class="text-xs bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200/80 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer"
          >
            💰 {{ tExt.payBtn }}
          </button>
          <button @click="switchToEdit" class="text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer">
            {{ t.common.edit }}
          </button>
          <button @click="promptDelete(currentSupplier)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-semibold transition-colors cursor-pointer">
            {{ t.common.delete }}
          </button>
        </template>
      </template>

      <!-- 内容区 -->
      <div class="p-6">
        <!-- 只读态 -->
        <div v-if="drawerMode === 'read'" class="space-y-5">
          <div v-if="currentSupplier?.id" class="bg-rose-50/50 p-4 rounded-xl border border-rose-100 space-y-1">
            <div class="text-xs text-rose-500 font-semibold">{{ tExt.colDebt }}</div>
            <div class="font-black text-rose-600 text-2xl font-mono">$ {{ (currentSupplier?.debt_usd || 0).toFixed(2) }}</div>
          </div>

          <div class="grid grid-cols-2 gap-4 text-sm">
            <div class="col-span-2">
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colName }}</p>
              <p class="font-bold text-slate-800 text-base">{{ currentSupplier?.name }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colContact }}</p>
              <p class="text-slate-700">{{ currentSupplier?.contact_person || '-' }}</p>
            </div>
            <div>
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colPhone }}</p>
              <p class="font-mono text-slate-700">{{ currentSupplier?.phone || '-' }}</p>
            </div>
            <div class="col-span-2">
              <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colAddress }}</p>
              <p class="text-slate-700">{{ currentSupplier?.address || '-' }}</p>
            </div>
          </div>
        </div>

        <!-- 新增/编辑态 -->
        <div v-else-if="drawerMode === 'edit'" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.colName }} *</label>
            <input v-model="formData.name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-bold text-slate-900" :placeholder="tExt.phName" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.colContact }}</label>
              <input v-model="formData.contact_person" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500" :placeholder="tExt.phContact" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.colPhone }}</label>
              <input v-model="formData.phone" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" :placeholder="tExt.phPhone" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.colAddress }}</label>
            <input v-model="formData.address" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500" :placeholder="tExt.optional" />
          </div>
        </div>

        <!-- 付款态 -->
        <div v-else-if="drawerMode === 'pay'" class="space-y-4">
          <div class="bg-rose-50/50 p-3 rounded-xl border border-rose-100">
            <div class="text-xs text-rose-500 font-bold">{{ tExt.colDebt }}:</div>
            <div class="text-lg font-black text-rose-600 font-mono">$ {{ (currentSupplier?.debt_usd || 0).toFixed(2) }}</div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.amountPaid }} *</label>
            <input v-model.number="payForm.amount_paid" type="number" step="0.01" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm font-bold font-mono outline-none focus:border-blue-500" />
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.payMethod }}</label>
              <select v-model="payForm.payment_method" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs font-bold outline-none cursor-pointer">
                <option value="Cash_USD">{{ tExt.pmCashUsd }}</option>
                <option value="Cash_BS">{{ tExt.pmCashBs }}</option>
                <option value="Bank_Transfer">{{ tExt.pmTransfer }}</option>
                <option value="Zelle">Zelle</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.referenceNo }}</label>
              <input v-model="payForm.reference_no" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-2.5 text-xs outline-none" :placeholder="tExt.optional" />
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作区 -->
      <template #footer>
        <div v-if="drawerMode !== 'read'" class="px-6 py-4 border-t border-slate-100 flex items-center justify-end gap-3">
          <button @click="switchToRead" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">
            {{ t.common.cancel }}
          </button>
          <button v-if="drawerMode === 'edit'" @click="saveSupplier" :disabled="isSubmitting" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md transition-colors cursor-pointer disabled:opacity-50">
            {{ isSubmitting ? tExt.saving : t.common.save }}
          </button>
          <button v-if="drawerMode === 'pay'" @click="submitPay" :disabled="isSubmittingPay" class="px-6 py-2.5 bg-emerald-600 hover:bg-emerald-700 text-white rounded-xl text-xs font-bold shadow-md transition-colors cursor-pointer disabled:opacity-50">
            {{ isSubmittingPay ? tExt.processing : tExt.confirmPay }}
          </button>
        </div>
      </template>
    </SideDrawer>

    <!-- 批量删除确认弹窗 -->
    <ConfirmDialog
      :visible="batchDeleteModalVisible"
      overlay-class="bg-slate-950/60"
      :title="tExt.batchDeleteTitle"
      :message="tExt.batchDeleteMsg"
      :cancel-text="t.common.cancel"
      :confirm-text="t.common.delete"
      @cancel="batchDeleteModalVisible = false"
      @confirm="confirmBatchDelete"
    />

    <!-- 单个删除确认弹窗 -->
    <ConfirmDialog
      :visible="isSingleDeleteVisible"
      overlay-class="bg-slate-950/60"
      :title="tExt.deleteTitle"
      :message="tExt.deleteMsg.replace('{name}', deleteTarget?.name || '')"
      :cancel-text="t.common.cancel"
      :confirm-text="t.common.delete"
      @cancel="isSingleDeleteVisible = false"
      @confirm="executeSingleDelete"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { Search, Plus } from 'lucide-vue-next'
import { apiFetch } from '../utils/api'
import { useNotifications } from '../composables/useNotifications'
import { useInventory } from '../composables/useInventory'
import { useI18n } from '../composables/useI18n'
import ConfirmDialog from './ConfirmDialog.vue'
import SideDrawer from './SideDrawer.vue'

const { t, currentLang } = useI18n()
const { showSuccessModal } = useNotifications()
const { bcvRate } = useInventory()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    searchPlaceholder: isZh ? '搜索供应商名称 / 电话...' : isEs ? 'Buscar proveedor / teléfono...' : 'Search supplier / phone...',
    addBtn: isZh ? '新增供应商' : isEs ? 'Nuevo Proveedor' : 'Add Supplier',
    selected: isZh ? '已选' : isEs ? 'Seleccionados' : 'Selected',
    items: isZh ? '项' : isEs ? 'ítems' : 'items',
    batchDelete: isZh ? '批量删除' : isEs ? 'Eliminar Lote' : 'Batch Delete',
    deselect: isZh ? '取消选择' : isEs ? 'Deseleccionar' : 'Deselect',
    colName: isZh ? '供应商名称' : isEs ? 'Proveedor' : 'Supplier Name',
    colContact: isZh ? '联系人' : isEs ? 'Contacto' : 'Contact Person',
    colPhone: isZh ? '联系电话' : isEs ? 'Teléfono' : 'Phone',
    colDebt: isZh ? '应付欠款' : isEs ? 'Deuda Pendiente' : 'Debt Owed',
    colAddress: isZh ? '地址' : isEs ? 'Dirección' : 'Address',
    emptyData: isZh ? '暂无符合条件的供应商档案' : isEs ? 'No se encontraron proveedores' : 'No suppliers found',
    payBtn: isZh ? '付款' : isEs ? 'Pagar' : 'Pay',
    showing: isZh ? '显示第' : isEs ? 'Mostrando' : 'Showing',
    to: isZh ? '到' : isEs ? 'a' : 'to',
    of: isZh ? '条，共' : isEs ? 'de' : 'of',
    suppliers: isZh ? '个供应商' : isEs ? 'proveedores' : 'suppliers',
    jumpTo: isZh ? '跳转到' : isEs ? 'Ir a' : 'Go to',
    page: isZh ? '页' : isEs ? 'Página' : 'Page',
    jumpBtn: isZh ? '跳转' : isEs ? 'Ir' : 'Go',
    prevPage: isZh ? '上一页' : isEs ? 'Anterior' : 'Prev',
    nextPage: isZh ? '下一页' : isEs ? 'Siguiente' : 'Next',
    addTitle: isZh ? '新增供应商' : isEs ? 'Nuevo Proveedor' : 'Add Supplier',
    editTitle: isZh ? '编辑供应商' : isEs ? 'Editar Proveedor' : 'Edit Supplier',
    payTitle: isZh ? '供应商付款' : isEs ? 'Pago a Proveedor' : 'Supplier Payment',
    amountPaid: isZh ? '本次付款金额' : isEs ? 'Monto a Pagar' : 'Amount to Pay',
    payMethod: isZh ? '支付方式' : isEs ? 'Método de Pago' : 'Payment Method',
    referenceNo: isZh ? '回执号' : isEs ? 'Referencia' : 'Reference No.',
    optional: isZh ? '选填' : isEs ? 'Opcional' : 'Optional',
    saving: isZh ? '保存中...' : isEs ? 'Guardando...' : 'Saving...',
    processing: isZh ? '处理中...' : isEs ? 'Procesando...' : 'Processing...',
    confirmPay: isZh ? '确认付款' : isEs ? 'Confirmar Pago' : 'Confirm Pay',
    pmCashUsd: isZh ? '美元现金' : isEs ? 'Efectivo USD' : 'Cash USD',
    pmCashBs: isZh ? '玻利瓦尔现金' : isEs ? 'Efectivo Bs.' : 'Cash Bs.',
    pmTransfer: isZh ? '银行转账' : isEs ? 'Transferencia' : 'Bank Transfer',
    phName: isZh ? '例如：广州汽配城' : isEs ? 'Ej: Auto Parts CA' : 'E.g. Auto Parts Co.',
    phContact: isZh ? '张老板' : isEs ? 'Ej: Juan' : 'E.g. John',
    phPhone: isZh ? '例如：+58 412...' : isEs ? 'Ej: +58 412...' : 'E.g. +58 412...',
    batchDeleteTitle: isZh ? '确认批量删除供应商' : isEs ? 'Confirmar Eliminación en Lote' : 'Confirm Batch Delete',
    batchDeleteMsg: isZh ? '确定要批量删除选中的供应商档案吗？删除后不可恢复。' : isEs ? '¿Eliminar los proveedores seleccionados? No se puede deshacer.' : 'Delete selected suppliers? Cannot be undone.',
    deleteTitle: isZh ? '确认删除供应商' : isEs ? 'Confirmar Eliminación' : 'Confirm Delete',
    deleteMsg: isZh ? '确定要删除供应商 {name} 吗？删除后不可恢复。' : isEs ? '¿Eliminar al proveedor {name}? No se puede deshacer.' : 'Delete supplier {name}? Cannot be undone.',
    toastNoName: isZh ? '请输入供应商名称' : isEs ? 'Ingrese el nombre del proveedor' : 'Please enter supplier name',
    toastSaved: isZh ? '保存成功' : isEs ? 'Guardado con éxito' : 'Saved successfully',
    toastSaveFailed: isZh ? '保存失败' : isEs ? 'Error al guardar' : 'Save failed',
    toastNetworkError: isZh ? '网络异常' : isEs ? 'Error de conexión' : 'Network error',
    toastDeleted: isZh ? '已删除' : isEs ? 'Eliminado' : 'Deleted',
    toastPaySuccess: isZh ? '付款成功' : isEs ? 'Pago exitoso' : 'Payment successful',
    toastPayFailed: isZh ? '付款失败' : isEs ? 'Pago fallido' : 'Payment failed',
    toastInvalidAmount: isZh ? '金额必须大于 0' : isEs ? 'El monto debe ser mayor a 0' : 'Amount must be greater than 0'
  }
})

const suppliersList = ref([])
const searchQuery = ref('')
const selectedIds = ref([])
const batchDeleteModalVisible = ref(false)
const pageSize = 10
const currentPage = ref(1)
const jumpPageInput = ref(1)

const detailDrawerVisible = ref(false)
const drawerMode = ref('read')
const currentSupplier = ref(null)
const isSubmitting = ref(false)
const isSubmittingPay = ref(false)

const formData = ref({ name: '', contact_person: '', phone: '', address: '' })
const payForm = ref({ amount_paid: 0, payment_method: 'Cash_USD', reference_no: '' })

const isSingleDeleteVisible = ref(false)
const deleteTarget = ref(null)

const drawerTitle = computed(() => {
  if (drawerMode.value === 'read') return currentSupplier.value?.id ? tExt.value.editTitle : tExt.value.addTitle
  if (drawerMode.value === 'edit') return currentSupplier.value?.id ? tExt.value.editTitle : tExt.value.addTitle
  return tExt.value.payTitle
})

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

const promptDelete = (sup) => {
  deleteTarget.value = sup
  isSingleDeleteVisible.value = true
}

const executeSingleDelete = async () => {
  if (!deleteTarget.value) return
  try {
    const res = await apiFetch(`/api/suppliers/${deleteTarget.value.id}`, { method: 'DELETE' })
    if (res.ok) {
      showSuccessModal('🗑️ ' + tExt.value.toastDeleted)
      fetchSuppliers()
      if (currentSupplier.value?.id === deleteTarget.value.id) closeDrawer()
    } else {
      const err = await res.json()
      showSuccessModal(`❌ ${t.common.error}: ${err.detail}`)
    }
  } catch (e) { showSuccessModal('❌ ' + tExt.value.toastNetworkError) }
  finally {
    isSingleDeleteVisible.value = false
    deleteTarget.value = null
  }
}

// ================= Drawer 逻辑 =================
const openDetailDrawer = (sup) => {
  if (sup) {
    currentSupplier.value = { ...sup }
    drawerMode.value = 'read'
  } else {
    currentSupplier.value = {}
    formData.value = { name: '', contact_person: '', phone: '', address: '' }
    drawerMode.value = 'edit'
  }
  detailDrawerVisible.value = true
}

const openDrawerEditMode = (sup) => {
  currentSupplier.value = { ...sup }
  formData.value = { ...sup }
  drawerMode.value = 'edit'
  detailDrawerVisible.value = true
}

const openDrawerPayMode = (sup) => {
  currentSupplier.value = { ...sup }
  payForm.value = { amount_paid: sup.debt_usd, payment_method: 'Cash_USD', reference_no: '' }
  drawerMode.value = 'pay'
  detailDrawerVisible.value = true
}

const switchToEdit = () => { formData.value = { ...currentSupplier.value }; drawerMode.value = 'edit' }
const switchToPay = () => { payForm.value = { amount_paid: currentSupplier.value?.debt_usd || 0, payment_method: 'Cash_USD', reference_no: '' }; drawerMode.value = 'pay' }
const switchToRead = () => { drawerMode.value = 'read' }
const closeDrawer = () => { detailDrawerVisible.value = false; drawerMode.value = 'read' }

const saveSupplier = async () => {
  if (!formData.value.name?.trim()) return showSuccessModal('❌ ' + tExt.value.toastNoName)
  isSubmitting.value = true
  const isEdit = !!currentSupplier.value?.id
  try {
    const res = await apiFetch(isEdit ? `/api/suppliers/${currentSupplier.value.id}` : '/api/suppliers', {
      method: isEdit ? 'PUT' : 'POST',
      body: JSON.stringify(formData.value)
    })
    if (res.ok) {
      showSuccessModal('✅ ' + tExt.value.toastSaved)
      const savedData = await res.json()
      // 本地更新，使 Drawer 切回只读时能显示最新数据
      currentSupplier.value = isEdit ? { ...currentSupplier.value, ...formData.value } : savedData
      drawerMode.value = 'read'
      fetchSuppliers()
    } else {
      const err = await res.json()
      showSuccessModal(`❌ ${tExt.value.toastSaveFailed}: ${err.detail}`)
    }
  } catch (e) { showSuccessModal('❌ ' + tExt.value.toastNetworkError) }
  finally { isSubmitting.value = false }
}

const confirmBatchDelete = async () => {
  let errs = []
  for (const id of selectedIds.value) {
    const res = await apiFetch(`/api/suppliers/${id}`, { method: 'DELETE' })
    if (!res.ok) { const err = await res.json(); errs.push(err.detail) }
  }
  batchDeleteModalVisible.value = false
  selectedIds.value = []
  fetchSuppliers()
  if (errs.length > 0) showSuccessModal(`⚠️ ${errs[0]}`)
  else showSuccessModal('🗑️ ' + tExt.value.toastDeleted)
}

const submitPay = async () => {
  if (payForm.value.amount_paid <= 0) return showSuccessModal('❌ ' + tExt.value.toastInvalidAmount)
  isSubmittingPay.value = true
  try {
    const res = await apiFetch(`/api/suppliers/${currentSupplier.value.id}/pay`, {
      method: 'POST',
      body: JSON.stringify({
        amount_paid: payForm.value.amount_paid,
        currency: payForm.value.payment_method === 'Cash_BS' ? 'BS' : 'USD',
        exchange_rate: bcvRate.value,
        payment_method: payForm.value.payment_method,
        reference_no: payForm.value.reference_no
      })
    })
    if (res.ok) {
      showSuccessModal('✅ ' + tExt.value.toastPaySuccess)
      const data = await res.json()
      // 更新本地欠款
      if (currentSupplier.value) currentSupplier.value.debt_usd = data.remaining_debt || 0
      drawerMode.value = 'read'
      fetchSuppliers()
    } else {
      const err = await res.json()
      showSuccessModal(`❌ ${tExt.value.toastPayFailed}: ${err.detail}`)
    }
  } catch (e) { showSuccessModal('❌ ' + tExt.value.toastNetworkError) }
  finally { isSubmittingPay.value = false }
}

onMounted(() => { fetchSuppliers() })
</script>