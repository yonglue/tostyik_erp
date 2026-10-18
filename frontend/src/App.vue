<!-- src/App.vue -->
<template>
  <div class="h-screen w-screen overflow-hidden bg-slate-50 text-slate-900">
    
    <LoginView v-if="!isLoggedIn" />

    <!-- 🌟 ERP 主界面结构 -->
    <div v-else class="flex flex-col md:flex-row h-full w-full overflow-hidden bg-slate-50 text-slate-900">
      
      <Sidebar 
        v-if="activeTab !== 'desk'"
        :activeTab="activeTab" 
        :mobileMenuOpen="mobileMenuOpen"
        :currentDateTime="currentDateTime"
        @update:activeTab="activeTab = $event"
        @update:mobileMenuOpen="mobileMenuOpen = $event"
        @menu-click="handleMenuClick"
      />

      <!-- 右侧主工作区 -->
      <div class="flex-1 flex flex-col min-w-0 overflow-hidden">
        
        <header v-if="activeTab !== 'desk'" class="h-16 bg-white/75 backdrop-blur-xl border-b border-white/60 px-6 flex items-center justify-between shrink-0 shadow-xs transition-all">
          <div class="flex items-center space-x-4">
            <button @click="mobileMenuOpen = !mobileMenuOpen" class="md:hidden p-2 text-slate-600 hover:bg-blue-50/90 rounded-2xl transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" class="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/></svg>
            </button>
          </div>

          <div class="flex items-center space-x-3">
            <!-- 1. BCV 官方汇率胶囊 -->
            <div class="hidden sm:flex items-center space-x-2 bg-white/70 hover:bg-blue-50/90 border border-slate-200/80 hover:border-blue-300 px-4 py-2 rounded-2xl text-xs font-mono shadow-2xs transition-all duration-200 backdrop-blur-md cursor-pointer hover:scale-[1.02]">
              <span class="text-slate-500 font-bold">BCV =</span>
              <span class="font-black text-blue-600">{{ bcvRate }}</span>
              <button @click="fetchBcvRate" title="刷新汇率" class="text-slate-400 hover:text-blue-600 transition-colors cursor-pointer ml-1">
                🔄
              </button>
            </div>

            <!-- 2. 语言切换胶囊 -->
            <select v-model="currentLang" class="bg-white/70 hover:bg-blue-500/10 border border-slate-200/80 hover:border-blue-300 text-xs rounded-2xl px-3.5 py-2 outline-none font-semibold text-slate-700 hover:text-blue-700 cursor-pointer shadow-2xs transition-all duration-200 backdrop-blur-md hover:scale-[1.02]">
              <option value="es">🇪🇸 ES</option>
              <option value="zh">🇨🇳 中文</option>
              <option value="en">🇺🇸 EN</option>
            </select>

            <!-- 用户与登出区域 -->
            <div class="flex items-center gap-3 pl-3 border-l border-slate-200/60">
              <div class="flex items-center gap-2.5 bg-white/70 hover:bg-blue-50/90 border border-slate-200/80 hover:border-blue-300 pl-2 pr-4 py-1.5 rounded-2xl shadow-2xs transition-all duration-200 backdrop-blur-md cursor-pointer hover:scale-[1.02]">
                <div class="relative flex items-center justify-center w-7 h-7 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-black text-xs shadow-md shadow-blue-500/20 uppercase shrink-0">
                  {{ currentUserObj.username ? currentUserObj.username.charAt(0) : 'U' }}
                  <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 border-2 border-white rounded-full"></span>
                </div>
                <div class="text-left">
                  <span class="text-[9px] text-slate-400 block uppercase font-extrabold tracking-wider leading-none">{{ currentUserObj.role }}</span>
                  <span class="text-xs font-bold text-slate-800 tracking-tight leading-tight mt-0.5 block">{{ currentUserObj.username }}</span>
                </div>
              </div>

              <button @click="handleLogout" class="px-4 py-2 bg-white/70 hover:bg-rose-500/15 border border-slate-200/80 hover:border-rose-300 text-rose-600 rounded-2xl text-xs font-bold shadow-2xs transition-all duration-200 cursor-pointer backdrop-blur-md hover:scale-[1.02]">
                {{ t.logoutBtn }}
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
            @navigate="(tab) => checkAndSwitchTab(tab)" 
          />
          <FinancialView v-else-if="activeTab === 'financial' && hasPermission('financial:view')" />
          <StaffManagementView v-else-if="activeTab === 'staff' && hasPermission('users:manage')" />
          <AuditLogsView v-else-if="activeTab === 'audit_logs' && hasPermission('users:manage')" />
          <CashRegisterView v-else-if="activeTab === 'cash_register' && hasPermission('shift:report')" />
          <PartsView 
            v-else-if="activeTab === 'parts' && hasPermission('parts:view')"
            :partsList="partsList"
            v-model:searchQuery="searchQuery"
            v-model:selectedBrand="selectedBrand"
            :brandsList="brandsList"
            :bcvRate="bcvRate"
            @open-add-modal="dialogVisible = true"
            @open-gallery="openGallery"
            @delete-part="openDeletePartModal"
            @refresh-data="fetchParts"
          />
          <ClientsView 
            v-else-if="activeTab === 'clients' && hasPermission('clients:view')"
            :clientsList="clientsList"
            v-model:clientSearchQuery="clientSearchQuery"
            @export-clients="exportClientsExcel"
            @open-add-client="clientDialogVisible = true"
            @delete-client="openDeleteClientModal"
          />
          <PurchaseOrdersView 
            v-else-if="activeTab === 'procurement' && hasPermission('procurement:view')"
          />
          <TransactionsView 
            v-else-if="activeTab === 'transactions' && hasPermission('transactions:history')"
            :transactionsList="transactionsList"
            @export-transactions="exportTransactionsExcel"
            @open-tx-modal="txDialogVisible = true"
            @delete-tx="openDeleteTxModal"
          />
          <QuotationDeskView 
            v-else-if="activeTab === 'desk' && hasPermission('pos:access')"
            :partsList="partsList"
            :clientsList="clientsList"
            :cartItems="cartItems"
            :bcvRate="bcvRate"
            :currentDateTime="currentDateTime"
            :currentUser="currentUserObj"
            @add-to-cart="addToCart"
            @generate-quote="fetchTransactions(); fetchParts(); fetchDashboardStats(); fetchClients()"
            @exit-pos="activeTab = getDefaultAllowedTab()"
            @clear-cart="cartItems = []"
          />
          <BackupView 
            v-else-if="activeTab === 'settings' && hasPermission('settings:manage')"
            @export-parts="exportPartsExcel"
            @import-parts="handleImportParts"
            @export-clients="exportClientsExcel"
            @download-db="downloadDatabaseBackup"
          />
          
          <div v-else class="bg-white p-12 rounded-3xl text-center space-y-4 border border-slate-200 max-w-lg mx-auto mt-12 shadow-sm">
            <div class="w-16 h-16 bg-blue-50 text-blue-600 rounded-2xl mx-auto flex items-center justify-center text-3xl font-bold shadow-inner">
              ✨
            </div>
            <div class="space-y-1">
              <h3 class="font-bold text-lg text-slate-900">欢迎登录，{{ currentUserObj.username }}</h3>
              <p class="text-xs text-slate-500">
                当前账号（<strong class="uppercase text-blue-600">{{ currentUserObj.role }}</strong>）未授权访问此页面，系统已为您匹配专属工作台。
              </p>
            </div>
            <button @click="activeTab = getDefaultAllowedTab()" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/25 transition-all cursor-pointer">
              进入我的可用工作台
            </button>
          </div>
        </main>
      </div>

    </div>

    <!-- 弹窗组件：录入新汽配 -->
    <div 
      v-if="dialogVisible" 
      @click.self="dialogVisible = false" 
      class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4 transition-all"
    >
      <div class="bg-white rounded-3xl shadow-2xl max-w-2xl w-full overflow-hidden border border-slate-100 p-6 space-y-5">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-xl">➕</span>
            <h3 class="font-bold text-slate-800 text-base">{{ t.dialogAddPartTitle || '录入新汽配档案与多图相册' }}</h3>
          </div>
          <button @click="dialogVisible = false" class="text-slate-400 hover:text-slate-700 text-lg font-bold cursor-pointer">✕</button>
        </div>

        <form @submit.prevent="handleAddPart" class="space-y-4 max-h-[70vh] overflow-y-auto pr-1">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">OEM 编号</label>
              <input v-model="newPart.oem" type="text" placeholder="例如: 17801-74060" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-mono font-bold outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">配件名称</label>
              <input v-model="newPart.name" type="text" placeholder="例如: 空气滤清器" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-medium outline-none focus:border-blue-500" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">配件分类</label>
              <input v-model="newPart.category" type="text" placeholder="滤清器 / 悬挂系统" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">适配品牌</label>
              <input v-model="newPart.brand" type="text" placeholder="Toyota / Mack / GENERAL" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs outline-none focus:border-blue-500" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">库存数量</label>
              <input v-model.number="newPart.stock" type="number" min="0" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold font-mono outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">零售价格 (USD)</label>
              <input v-model.number="newPart.price" type="number" step="0.5" min="0" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold font-mono outline-none focus:border-blue-500" />
            </div>
          </div>

          <!-- 🌟 优化：新增商品弹窗支持 16%、8% 和 0% 免税下拉 -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">🌟 SENIAT 税率类型属性 (IVA)</label>
              <select v-model.number="newPart.tax_rate" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold outline-none focus:border-blue-500 cursor-pointer">
                <option :value="0.16">16% 标准增值税 (Alicuota General)</option>
                <option :value="0.08">8% 减免增值税 (Alicuota Reducida)</option>
                <option :value="0.0">0% 免税 (Exento)</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">货架库位 (Bin Location)</label>
              <input v-model="newPart.bin_location" type="text" placeholder="Estante A-1" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-mono outline-none focus:border-blue-500" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">🔗 交叉适配编号与备注 (Cross-References / Notes)</label>
            <textarea 
              v-model="newPart.cross_references" 
              rows="3" 
              placeholder="例如: WIX: 51348 / Donaldson: P550020..." 
              class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs outline-none focus:border-blue-500 font-mono leading-relaxed resize-none"
            ></textarea>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">配件实物照片 (最多可选 5 张)</label>
            <input type="file" @change="handleFileChange" accept="image/*" multiple class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-slate-200 rounded-xl p-1.5" />
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button type="button" @click="dialogVisible = false" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">
              取消 (ESC)
            </button>
            <button type="submit" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer">
              确定保存 (Enter)
            </button>
          </div>
        </form>
      </div>
    </div>

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

import Sidebar from './components/Sidebar.vue'
import LoginView from './components/LoginView.vue'
import ConfirmDialog from './components/ConfirmDialog.vue'
import ImageGalleryModal from './components/ImageGalleryModal.vue'
import GlobalNoticeModal from './components/GlobalNoticeModal.vue'

const DashboardView = defineAsyncComponent(() => import('./components/DashboardView.vue'))
const FinancialView = defineAsyncComponent(() => import('./components/FinancialView.vue'))
const PartsView = defineAsyncComponent(() => import('./components/PartsView.vue'))
const ClientsView = defineAsyncComponent(() => import('./components/ClientsView.vue'))
const TransactionsView = defineAsyncComponent(() => import('./components/TransactionsView.vue'))
const QuotationDeskView = defineAsyncComponent(() => import('./components/QuotationDeskView.vue'))
const BackupView = defineAsyncComponent(() => import('./components/BackupView.vue'))
const AuditLogsView = defineAsyncComponent(() => import('./components/AuditLogsView.vue'))
const PurchaseOrdersView = defineAsyncComponent(() => import('./components/ProcurementCenterView.vue'))

import { apiFetch, apiUrl } from './utils/api'
import { useAuth } from './composables/useAuth'
import { useNotifications } from './composables/useNotifications'
import { useInventory } from './composables/useInventory'
import { usePosCart } from './composables/usePosCart'
import { useClock } from './composables/useClock'
import { useGallery } from './composables/useGallery'

const { t, currentLang } = useI18n()

const {
  successModalVisible, successModalMessage, isErrorMessage,
  showSuccessModal, closeSuccessModal
} = useNotifications()

const {
  isLoggedIn, currentAdminUser, currentUserObj,
  loginForm, loginError, resetMessage,
  resetModalVisible, resetPinInput,
  handleLogin, handleLogout, openResetModal, submitResetPassword
} = useAuth()

const hasPermission = (permKey) => {
  if (!currentUserObj.value) return false
  const role = currentUserObj.value.role || 'staff'
  const perms = currentUserObj.value.permissions || []
  if (role === 'super_admin' || role === 'admin' || perms.includes('*')) return true
  return perms.includes(permKey)
}

const getDefaultAllowedTab = () => {
  const role = currentUserObj.value?.role || 'staff'
  if (role === 'super_admin' || role === 'admin') return 'dashboard'

  if (hasPermission('parts:view')) return 'parts'
  if (hasPermission('pos:access')) return 'desk'
  if (hasPermission('clients:view')) return 'clients'
  if (hasPermission('transactions:history')) return 'transactions'
  if (hasPermission('financial:view')) return 'financial'
  if (hasPermission('users:manage')) return 'staff'

  return 'dashboard'
}

const checkAndSwitchTab = (tab) => {
  activeTab.value = tab
}

const mobileMenuOpen = ref(false)
const activeTab = ref(getDefaultAllowedTab())

const searchQuery = ref('')
const clientSearchQuery = ref('')
const selectedBrand = ref('ALL')

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

const {
  bcvRate, partsList, clientsList, transactionsList, quotationsList,
  stats, brandsList,
  fetchParts, fetchClients, fetchTransactions, fetchQuotations,
  fetchDashboardStats, fetchBcvRate
} = useInventory()

const {
  cartItems, quoteClientName, selectedPaymentMethod, paymentReference, addToCart
} = usePosCart()

const { currentDateTime } = useClock()

const handleMenuClick = (key) => {
  if (key === 'dashboard') fetchDashboardStats()
  if (key === 'clients' || key === 'desk') fetchClients()
  if (key === 'quotations') fetchQuotations()
}

const exportTransactionsExcel = () => window.open(apiUrl('/api/export/transactions'), '_blank')
const exportPartsExcel = () => window.open(apiUrl('/api/export/parts'), '_blank')
const exportClientsExcel = () => window.open(apiUrl('/api/export/clients'), '_blank')
const downloadDatabaseBackup = () => window.open(apiUrl('/api/backup/download'), '_blank')

const handleImportParts = async (e) => {
  const file = e.target.files[0]
  if (!file) return
  const formData = new FormData()
  formData.append('file', file)
  const res = await apiFetch('/api/import/parts', { method: 'POST', body: formData })
  if (res.ok) { fetchParts(); fetchDashboardStats(); }
}

const generateAndArchiveQuote = async () => {
  // 已经由 POS 接口统一处理，这里仅刷新前端视图
  fetchQuotations(); fetchParts(); fetchTransactions(); fetchDashboardStats(); fetchClients();
}

const openDeleteModal = (q) => { targetQuote.value = q; deleteModalVisible.value = true }
const confirmDeleteQuotation = async () => {
  if (!targetQuote.value) return
  if ((await apiFetch(`/api/quotations/${targetQuote.value.id}`, { method: 'DELETE' })).ok) {
    deleteModalVisible.value = false; targetQuote.value = null; fetchQuotations()
  }
}

const openDeleteClientModal = (c) => {
  targetClient.value = c
  deleteClientModalVisible.value = true
}

const confirmDeleteClient = async () => {
  if (!targetClient.value) return
  try {
    const res = await apiFetch(`/api/clients/${targetClient.value.id}`, { method: 'DELETE' })
    if (res.ok) {
      deleteClientModalVisible.value = false
      targetClient.value = null
      fetchClients()
      showSuccessModal('🗑️ 客户档案已成功删除！')
    } else {
      const err = await res.json()
      deleteClientModalVisible.value = false
      showSuccessModal(`❌ 删除失败: ${err.detail || '未知错误'}`)
    }
  } catch (e) {
    console.error(e)
    deleteClientModalVisible.value = false
    showSuccessModal('❌ 服务器连接异常！')
  }
}

const newPart = ref({ oem: '', name: '', brand: '', category: '', stock: 10, price: 15.00, tax_rate: 0.16, bin_location: 'Estante A-1', cross_references: '' })
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
  formData.append('tax_rate', newPart.value.tax_rate ?? 0.16)
  formData.append('bin_location', newPart.value.bin_location || 'Estante A-1')
  formData.append('cross_references', newPart.value.cross_references || '')
  
  selectedFiles.value.forEach(f => formData.append('files', f))
  
  try {
    const res = await apiFetch('/api/parts', {
      method: 'POST',
      body: formData
    })
    
    if (res.ok) {
      dialogVisible.value = false
      newPart.value = { oem: '', name: '', brand: '', category: '', stock: 10, price: 15.00, tax_rate: 0.16, bin_location: 'Estante A-1', cross_references: '' }
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
  // 🌟 1. 当大图预览弹窗（Gallery）打开时，优先拦截处理按键
  if (galleryModalVisible.value) {
    if (e.key === 'Escape') {
      e.preventDefault()
      galleryModalVisible.value = false // 按 Esc 键一键关闭大图弹窗
      return
    }
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      prevGalleryImage() // 按左方向键切换到上一张图片
      return
    }
    if (e.key === 'ArrowRight') {
      e.preventDefault()
      nextGalleryImage() // 按右方向键切换到下一张图片
      return
    }
  }

  // 🌟 2. 现有的 Esc 按键关闭录入弹窗逻辑
  if (e.key === 'Escape') {
    if (dialogVisible.value) { dialogVisible.value = false; return; }
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
  fetchParts(); fetchClients(); fetchTransactions(); fetchQuotations(); fetchDashboardStats(); fetchBcvRate()
  window.addEventListener('keydown', handleGlobalKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>