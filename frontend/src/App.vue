<!-- src/App.vue -->
<template>
  <div class="h-screen w-screen overflow-hidden bg-slate-50 text-slate-900">
    
    <LoginView v-if="!isLoggedIn" />

    <!-- 🌟 ERP 主界面结构 -->
    <div v-else class="flex flex-col md:flex-row h-full w-full overflow-hidden bg-slate-50 text-slate-900">
      
      <!-- 左侧固定导航栏 -->
      <Sidebar 
        :activeTab="activeTab" 
        :mobileMenuOpen="mobileMenuOpen"
        @update:activeTab="activeTab = $event"
        @update:mobileMenuOpen="mobileMenuOpen = $event"
        @menu-click="handleMenuClick"
      />

      <!-- 右侧主工作区 -->
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
        
        <!-- 顶部导航栏 -->
        <header class="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0 shadow-xs">
          <div class="flex items-center space-x-4">
            <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2 text-slate-600 hover:bg-slate-100 rounded-xl">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
            </button>
            <div class="flex items-center gap-2">
              <span class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span class="text-xs font-bold text-slate-700 tracking-wide uppercase">系统在线</span>
              <span class="text-xs font-mono text-slate-400">v4.3 Enterprise</span>
            </div>
          </div>

          <div class="flex items-center space-x-4">
            <!-- BCV 官方汇率展示与刷新 -->
            <div class="hidden sm:flex items-center space-x-2 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl text-xs font-mono">
              <span class="text-slate-500">BCV =</span>
              <span class="font-bold text-blue-600">{{ bcvRate }}</span>
              <button @click="fetchBcvRate" title="刷新汇率" class="text-slate-400 hover:text-blue-600 transition-colors cursor-pointer">
                🔄
              </button>
            </div>

            <!-- 实时时间 -->
            <div class="hidden lg:block text-xs font-mono font-semibold text-slate-600 bg-slate-50 border border-slate-200 px-3 py-1.5 rounded-xl">
              📅 {{ currentDateTime }}
            </div>

            <!-- 语言切换 -->
            <select v-model="currentLang" class="bg-slate-50 border border-slate-200 text-xs rounded-xl px-2.5 py-1.5 outline-none font-semibold cursor-pointer">
              <option value="es">🇪🇸 ES</option>
              <option value="zh">🇨🇳 中文</option>
              <option value="en">🇺🇸 EN</option>
            </select>

            <!-- 用户与登出 -->
            <div class="flex items-center gap-3 pl-2 border-l border-slate-200">
              <div class="text-right hidden sm:block">
                <span class="text-[10px] text-slate-400 block uppercase font-bold">{{ currentUserObj.role }}</span>
                <span class="text-xs font-bold text-slate-800">{{ currentUserObj.username }}</span>
              </div>
              <button @click="handleLogout" class="px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">
                退出登录
              </button>
            </div>
          </div>
        </header>

        <!-- 主内容区域 -->
        <main class="flex-1 overflow-y-auto p-4 md:p-8 space-y-6">
          <DashboardView 
            v-if="activeTab === 'dashboard'" 
            :stats="stats" 
            :bcvRate="bcvRate"
            @navigate="(tab) => activeTab = tab" 
          />
          <FinancialView v-else-if="activeTab === 'financial'" />
          <WarehouseView v-else-if="activeTab === 'warehouse'" :partsList="partsList" />
          <StaffManagementView v-else-if="activeTab === 'staff'" />
          <AuditLogsView v-else-if="activeTab === 'audit_logs'" />
          <CashRegisterView v-else-if="activeTab === 'cash_register'" />
          <PartsView 
            v-else-if="activeTab === 'parts'"
            :partsList="partsList"
            v-model:searchQuery="searchQuery"
            v-model:selectedBrand="selectedBrand"
            :brandsList="brandsList"
            :bcvRate="bcvRate"
            @open-add-modal="dialogVisible = true"
            @open-gallery="openGallery"
            @delete-part="openDeletePartModal"
          />
          <ClientsView 
            v-else-if="activeTab === 'clients'"
            :clientsList="clientsList"
            v-model:clientSearchQuery="clientSearchQuery"
            @export-clients="exportClientsExcel"
            @open-add-client="clientDialogVisible = true"
            @delete-client="openDeleteClientModal"
          />
          <!-- 🌟 采购订单与收货管理模块 -->
          <PurchaseOrdersView 
            v-else-if="activeTab === 'procurement'"
          />
          <TransactionsView 
            v-else-if="activeTab === 'transactions'"
            :transactionsList="transactionsList"
            @export-transactions="exportTransactionsExcel"
            @open-tx-modal="txDialogVisible = true"
            @delete-tx="openDeleteTxModal"
          />
          <QuotationDeskView 
            v-else-if="activeTab === 'desk'"
            :partsList="partsList"
            :clientsList="clientsList"
            :cartItems="cartItems"
            :bcvRate="bcvRate"
            :currentDateTime="currentDateTime"
            :currentUser="currentUserObj"
            @add-to-cart="addToCart"
            @generate-quote="generateAndArchiveQuote"
            @exit-pos="activeTab = 'dashboard'"
            @clear-cart="cartItems = []"
          />
          <QuotationsView 
            v-else-if="activeTab === 'quotations'"
            :quotationsList="quotationsList"
            @export-quotations="exportQuotationsExcel"
            @download-pdf="downloadExistingPdf"
            @delete-quote="openDeleteModal"
          />
          <BackupView 
            v-else-if="activeTab === 'backup'"
            @export-parts="exportPartsExcel"
            @import-parts="handleImportParts"
            @export-clients="exportClientsExcel"
            @download-db="downloadDatabaseBackup"
          />
        </main>
      </div>

    </div>

    <!-- 新增商品弹窗 -->
    <div v-if="dialogVisible" class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100">
        <div class="px-6 py-5 border-b border-slate-100">
          <h3 class="font-bold text-base text-slate-800">{{ t.dialogAddPartTitle }}</h3>
        </div>
        <div class="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.colOem }}</label>
            <input v-model="newPart.oem" type="text" placeholder="例如: 17801-74060" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.colName }}</label>
            <input v-model="newPart.name" type="text" placeholder="例如: 空气滤清器" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.colBrand }}</label>
              <input v-model="newPart.brand" type="text" placeholder="Toyota / Mack" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.colCategory }}</label>
              <input v-model="newPart.category" type="text" placeholder="滤清器 / 悬挂系统" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.colStock }}</label>
              <input v-model.number="newPart.stock" type="number" min="0" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.colPriceUsd }}</label>
              <input v-model.number="newPart.price" type="number" step="0.5" min="0" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.uploadImageLabel }}</label>
            <input type="file" @change="handleFileChange" accept="image/*" multiple class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer" />
          </div>
        </div>
        <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
          <button @click="dialogVisible = false" class="px-4 py-2 rounded-xl text-sm font-medium text-slate-600 hover:bg-slate-200/60 transition-colors">{{ t.btnCancel }}</button>
          <button @click="handleAddPart" class="px-5 py-2 rounded-xl text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 shadow-md">{{ t.btnSave }}</button>
        </div>
      </div>
    </div>

    <!-- 客户弹窗 -->
    <div v-if="clientDialogVisible" class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100">
        <div class="px-6 py-5 border-b border-slate-100">
          <h3 class="font-bold text-base text-slate-800">{{ t.dialogAddClientTitle }}</h3>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.clientColName }}</label>
            <input v-model="newClient.name" type="text" placeholder="例如: Auto Taller Valencia C.A." class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.clientColType }}</label>
              <select v-model="newClient.client_type" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 cursor-pointer">
                <option value="Regular">Regular (零售)</option>
                <option value="Taller">Taller (修理厂)</option>
                <option value="Mayorista">Mayorista (批发商)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.clientColPhone }}</label>
              <input v-model="newClient.phone" type="text" placeholder="+58 412..." class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.clientColAddress }}</label>
              <input v-model="newClient.address" type="text" placeholder="Caracas / Valencia" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.clientColRif }}</label>
              <input v-model="newClient.rif_or_cedula" type="text" placeholder="J-31234567-8" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
          </div>
        </div>
        <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
          <button @click="clientDialogVisible = false" class="px-4 py-2 rounded-xl text-sm font-medium text-slate-600 hover:bg-slate-200/60 transition-colors">{{ t.btnCancel }}</button>
          <button @click="handleAddClient" class="px-5 py-2 rounded-xl text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 shadow-md">{{ t.btnSave }}</button>
        </div>
      </div>
    </div>

    <!-- 🔒 重置密码弹窗 -->
    <div v-if="resetModalVisible" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-sm w-full overflow-hidden border border-slate-100 p-6 space-y-5">
        <div class="text-center space-y-1.5">
          <div class="w-12 h-12 rounded-xl bg-amber-500 mx-auto flex items-center justify-center text-white shadow-lg shadow-amber-500/30">
            🔒
          </div>
          <h3 class="font-bold text-base text-slate-900">安全密钥验证</h3>
          <p class="text-xs text-slate-400">请输入系统最高安全密钥 (Security PIN) 以重置管理员密码</p>
        </div>

        <div>
          <input 
            v-model="resetPinInput" 
            @keyup.enter="submitResetPassword" 
            type="password" 
            placeholder="输入 Security PIN..." 
            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm outline-none focus:border-amber-500 font-mono text-center tracking-widest"
            autofocus
          />
        </div>

        <div class="flex gap-3 pt-1">
          <button @click="resetModalVisible = false" class="flex-1 px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors">
            取消
          </button>
          <button @click="submitResetPassword" class="flex-1 px-4 py-2.5 rounded-xl text-xs font-semibold bg-amber-600 text-white hover:bg-amber-700 shadow-md transition-colors">
            确认重置
          </button>
        </div>
      </div>
    </div>

    <ImageGalleryModal
      :visible="galleryModalVisible"
      :images="currentGalleryImages.map(apiUrl)"
      :index="currentGalleryIndex"
      @close="galleryModalVisible = false"
      @prev="prevGalleryImage"
      @next="nextGalleryImage"
    />

    <!-- 删除确认（报价单 / 商品 / 客户 / 流水，统一组件）-->
    <ConfirmDialog
      :visible="deleteModalVisible"
      overlay-class="bg-slate-900/40"
      :title="t.deleteModalTitle"
      :message="t.deleteConfirm"
      :cancel-text="t.btnCancel"
      :confirm-text="t.btnDelete"
      @cancel="deleteModalVisible = false"
      @confirm="confirmDeleteQuotation"
    />

    <ConfirmDialog
      :visible="deletePartModalVisible"
      overlay-class="bg-slate-900/40"
      title="确认删除商品"
      :cancel-text="t.btnCancel"
      :confirm-text="t.btnDelete"
      @cancel="deletePartModalVisible = false"
      @confirm="confirmDeletePart"
    />

    <ConfirmDialog
      :visible="deleteClientModalVisible"
      overlay-class="bg-slate-900/40"
      :title="t.deleteClientModalTitle"
      :cancel-text="t.btnCancel"
      :confirm-text="t.btnDelete"
      @cancel="deleteClientModalVisible = false"
      @confirm="confirmDeleteClient"
    />

    <ConfirmDialog
      :visible="deleteTxModalVisible"
      overlay-class="bg-slate-900/40"
      title="确认删除流水单据"
      message="删除后将自动还原对应的商品库存数量。"
      :cancel-text="t.btnCancel"
      :confirm-text="t.btnDelete"
      @cancel="deleteTxModalVisible = false"
      @confirm="confirmDeleteTx"
    />

    <GlobalNoticeModal
      :visible="successModalVisible"
      :message="successModalMessage"
      :is-error="isErrorMessage"
      @close="closeSuccessModal"
    />

  </div>
</template>

<script setup>
import StaffManagementView from './components/StaffManagementView.vue'
import CashRegisterView from './components/CashRegisterView.vue'
import { ref, computed, defineAsyncComponent, onMounted, onUnmounted } from 'vue'
import { useI18n } from './composables/useI18n'

// 常驻组件：登录页 / 侧边栏 / 全局弹窗，首屏即需要，保持同步加载
import Sidebar from './components/Sidebar.vue'
import LoginView from './components/LoginView.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import ImageGalleryModal from './components/ImageGalleryModal.vue'
import GlobalNoticeModal from './components/GlobalNoticeModal.vue'

// 业务页签：按需加载，各自切分成独立 chunk，首屏不再下载未打开的页面
const DashboardView = defineAsyncComponent(() => import('./components/DashboardView.vue'))
const FinancialView = defineAsyncComponent(() => import('./components/FinancialView.vue'))
const PartsView = defineAsyncComponent(() => import('./components/PartsView.vue'))
const ClientsView = defineAsyncComponent(() => import('./components/ClientsView.vue'))
const TransactionsView = defineAsyncComponent(() => import('./components/TransactionsView.vue'))
const QuotationDeskView = defineAsyncComponent(() => import('./components/QuotationDeskView.vue'))
const QuotationsView = defineAsyncComponent(() => import('./components/QuotationsView.vue'))
const BackupView = defineAsyncComponent(() => import('./components/BackupView.vue'))
const WarehouseView = defineAsyncComponent(() => import('./components/WarehouseView.vue'))
const AuditLogsView = defineAsyncComponent(() => import('./components/AuditLogsView.vue'))
const PurchaseOrdersView = defineAsyncComponent(() => import('./components/PurchaseOrdersView.vue'))
import { apiFetch, apiUrl } from './utils/api'
import { useAuth } from './composables/useAuth'
import { useNotifications } from './composables/useNotifications'
import { useInventory } from './composables/useInventory'
import { usePosCart } from './composables/usePosCart'
import { useClock } from './composables/useClock'
import { useGallery } from './composables/useGallery'

const { t, currentLang } = useI18n()

// ── 全局提示（成功弹窗 / 拦截提示）──
const {
  successModalVisible, successModalMessage, isErrorMessage,
  showSuccessModal, closeSuccessModal
} = useNotifications()

// ── 登录态与账号操作 ──
const {
  isLoggedIn, currentAdminUser, currentUserObj,
  loginForm, loginError, resetMessage,
  resetModalVisible, resetPinInput,
  handleLogin, handleLogout, openResetModal, submitResetPassword
} = useAuth()

const mobileMenuOpen = ref(false)
const activeTab = ref('dashboard')

const searchQuery = ref('')
const clientSearchQuery = ref('')
const deskSearch = ref('')
const selectedBrand = ref('ALL')
const selectedDeskBrand = ref('ALL')

const dialogVisible = ref(false)
const clientDialogVisible = ref(false)
const txDialogVisible = ref(false)
const deleteModalVisible = ref(false)
const deleteClientModalVisible = ref(false)
const deletePartModalVisible = ref(false)
const deleteTxModalVisible = ref(false)

const {
  galleryModalVisible, currentGalleryImages, currentGalleryIndex,
  openGallery, prevGalleryImage, nextGalleryImage
} = useGallery()

const targetQuote = ref(null)
const targetClient = ref(null)
const targetPartForDelete = ref(null)
const targetTxForDelete = ref(null)

const openDeletePartModal = (part) => {
  targetPartForDelete.value = part
  deletePartModalVisible.value = true
}

const confirmDeletePart = async () => {
  if (!targetPartForDelete.value) return
  try {
    const res = await apiFetch(`/api/parts/${targetPartForDelete.value.id}`, { method: 'DELETE' })
    if (res.ok) {
      deletePartModalVisible.value = false
      targetPartForDelete.value = null
      fetchParts(); fetchDashboardStats();
    }
  } catch (e) { console.error(e) }
}

const openDeleteTxModal = (tx) => {
  targetTxForDelete.value = tx
  deleteTxModalVisible.value = true
}

const confirmDeleteTx = async () => {
  if (!targetTxForDelete.value) return
  try {
    const res = await apiFetch(`/api/transactions/${targetTxForDelete.value.id}`, { method: 'DELETE' })
    if (res.ok) {
      deleteTxModalVisible.value = false
      targetTxForDelete.value = null
      fetchTransactions(); fetchParts(); fetchDashboardStats()
    }
  } catch (e) { console.error(e) }
}

// ── 业务数据（库存 / 客户 / 流水 / 报价 / 看板）──
const {
  bcvRate, partsList, clientsList, transactionsList, quotationsList,
  stats, brandsList,
  fetchParts, fetchClients, fetchTransactions, fetchQuotations,
  fetchDashboardStats, fetchBcvRate
} = useInventory()

// ── 开单购物车 ──
const {
  cartItems, quoteClientName, selectedPaymentMethod, paymentReference, addToCart
} = usePosCart()

// ── 顶栏时钟（自行注册生命周期）──
const { currentDateTime } = useClock()

const handleMenuClick = (key) => {
  if (key === 'dashboard') fetchDashboardStats()
  if (key === 'clients' || key === 'desk') fetchClients()
  if (key === 'quotations') fetchQuotations()
}


const exportTransactionsExcel = () => window.open(apiUrl('/api/export/transactions'), '_blank')
const exportQuotationsExcel = () => window.open(apiUrl('/api/export/quotations'), '_blank')
const exportPartsExcel = () => window.open(apiUrl('/api/export/parts'), '_blank')
const exportClientsExcel = () => window.open(apiUrl('/api/export/clients'), '_blank')
const downloadDatabaseBackup = () => window.open(apiUrl('/api/backup/download'), '_blank')
const downloadExistingPdf = () => window.open(apiUrl('/api/quotation/pdf/download'), '_blank')

const handleImportParts = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  const res = await apiFetch('/api/import/parts', { method: 'POST', body: formData })
  if (res.ok) { fetchParts(); fetchDashboardStats(); }
}

// src/App.vue 中的 generateAndArchiveQuote 函数修改
const generateAndArchiveQuote = async () => {
  if (cartItems.value.length === 0) return
  
  try {
    const res = await apiFetch('/api/quotations/generate', {
      method: 'POST',
      body: JSON.stringify({
        client_name: quoteClientName.value || 'Cliente General',
        lang: currentLang.value,
        payment_method: selectedPaymentMethod.value,
        payment_reference: paymentReference.value,
        items: cartItems.value
      })
    })

    if (res.ok) {
      const data = await res.json()
      
      cartItems.value = []
      paymentReference.value = ''
      fetchQuotations(); fetchParts(); fetchTransactions(); fetchDashboardStats(); fetchClients()
      
      // 🌟 彻底移除 App.vue 里的中间大弹窗触发，改为静默完成（由于收银台已经有了右上角提示，这里无需重复弹窗）
    } else {
      const errData = await res.json()
      showSuccessModal(`❌ 拒绝: ${errData.detail || '开单请求失败'}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ 服务器连接异常！')
  }
}

const openDeleteModal = (q) => { targetQuote.value = q; deleteModalVisible.value = true }
const confirmDeleteQuotation = async () => {
  if (!targetQuote.value) return
  if ((await apiFetch(`/api/quotations/${targetQuote.value.id}`, { method: 'DELETE' })).ok) {
    deleteModalVisible.value = false; targetQuote.value = null; fetchQuotations()
  }
}

const openDeleteClientModal = (c) => { targetClient.value = c; deleteClientModalVisible.value = true }
const confirmDeleteClient = async () => {
  if (!targetClient.value) return
  const res = await apiFetch(`/api/clients/${targetClient.value.id}`, { method: 'DELETE' })
  if (res.ok) {
    deleteClientModalVisible.value = false
    targetClient.value = null
    fetchClients()
  }
}

const newPart = ref({ oem: '', name: '', brand: '', category: '', stock: 10, price: 15.00 })
const selectedFiles = ref([])
const handleFileChange = (e) => { selectedFiles.value = Array.from(e.target.files).slice(0, 5) }

const handleAddPart = async () => {
  if (!newPart.value.oem || !newPart.value.name) return
  
  const formData = new FormData()
  formData.append('oem', newPart.value.oem || '')
  formData.append('name', newPart.value.name || '')
  formData.append('brand', newPart.value.brand || 'GENERAL')
  formData.append('category', newPart.value.category || '未分类')
  formData.append('stock', newPart.value.stock ?? 0)
  formData.append('price', newPart.value.price ?? 0.0)
  formData.append('cross_references', newPart.value.cross_references || '')
  
  selectedFiles.value.forEach(f => formData.append('files', f))
  
  try {
    const res = await apiFetch('/api/parts', {
      method: 'POST',
      body: formData
    })
    
    if (res.ok) {
      dialogVisible.value = false
      newPart.value = { oem: '', name: '', brand: '', category: '', stock: 10, price: 15.00 }
      selectedFiles.value = []
      fetchParts(); fetchDashboardStats();
      
      showSuccessModal('新汽配商品已成功录入数据库！')
    } else {
      const err = await res.json()
      const errorMsg = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail)
      showSuccessModal(`❌ 添加失败: ${errorMsg}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ 服务器连接异常！')
  }
}

const newClient = ref({ name: '', phone: '', address: '', rif_or_cedula: '', client_type: 'Regular', notes: '' })
const handleAddClient = async () => {
  if (!newClient.value.name) return
  const res = await apiFetch('/api/clients', {
    method: 'POST',
    body: JSON.stringify(newClient.value)
  })
  if (res.ok) {
    clientDialogVisible.value = false
    newClient.value = { name: '', phone: '', address: '', rif_or_cedula: '', client_type: 'Regular', notes: '' }
    fetchClients()
    showSuccessModal('新客户档案创建成功！')
  }
}

const handleGlobalKeydown = (e) => {
  // 🌟 核心修复：只要当前在收银台页面（desk），所有键盘事件全部交由 QuotationDeskView 内部处理，
  // App.vue 绝不越权拦截或触发任何自动开单！
  if (activeTab.value === 'desk') {
    return
  }

  if (e.key !== 'Enter') return

  if (successModalVisible.value) {
    e.preventDefault()
    successModalVisible.value = false
    return
  }
  if (dialogVisible.value) {
    e.preventDefault()
    handleAddPart()
    return
  }
  if (clientDialogVisible.value) {
    e.preventDefault()
    handleAddClient()
    return
  }
  if (deletePartModalVisible.value) {
    e.preventDefault()
    confirmDeletePart()
    return
  }
  if (deleteClientModalVisible.value) {
    e.preventDefault()
    confirmDeleteClient()
    return
  }
  if (deleteModalVisible.value) {
    e.preventDefault()
    confirmDeleteQuotation()
    return
  }
  if (deleteTxModalVisible.value) {
    e.preventDefault()
    confirmDeleteTx()
    return
  }
}

onMounted(() => {
  // 时钟的 interval 由 useClock 自行注册与清理
  fetchParts(); fetchClients(); fetchTransactions(); fetchQuotations(); fetchDashboardStats(); fetchBcvRate()
  window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>