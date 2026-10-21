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
            <!-- 1. BCV 官方汇率胶囊 (保留炫酷动态，不可点击) -->
            <div class="hidden sm:flex items-center space-x-2 bg-white/70 hover:bg-blue-50/90 border border-slate-200/80 hover:border-blue-300 px-4 py-2 rounded-2xl text-xs font-mono shadow-2xs transition-all duration-200 backdrop-blur-md hover:scale-[1.02] hover:shadow-md">
              <span class="text-slate-500 font-bold">BCV =</span>
              <span class="font-black text-blue-600">{{ bcvRate }}</span>
            </div>

            <!-- 2. 语言切换胶囊 -->
            <select id="app-language-select" name="app-language" v-model="currentLang" class="bg-white/70 hover:bg-blue-500/10 border border-slate-200/80 hover:border-blue-300 text-xs rounded-2xl px-3.5 py-2 outline-none font-semibold text-slate-700 hover:text-blue-700 cursor-pointer shadow-2xs transition-all duration-200 backdrop-blur-md hover:scale-[1.02]">
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
                {{ t.common.logout }}
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
          <GastosView v-else-if="activeTab === 'expenses' && hasPermission('financial:view')" />
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
            @refresh-data="fetchClients"
          />
          <PurchaseOrdersView 
            v-else-if="activeTab === 'procurement' && hasPermission('procurement:view')"
            @navigate="checkAndSwitchTab" 
          />          
          <TransactionsView 
            v-else-if="activeTab === 'transactions' && hasPermission('transactions:history')"
            :transactionsList="transactionsList"
            @export-transactions="exportTransactionsExcel"
            @open-tx-modal="txDialogVisible = true"
            @delete-tx="openDeleteTxModal"
          />
          
          <!-- 🌟 挂载报价单列表 -->
          <QuotationListView 
            v-else-if="activeTab === 'quotations' && hasPermission('pos:access')"
            @convert-to-pos="handleConvertToPos"
            @delete-quote="openDeleteModal"
            @show-toast="(msg, type) => showSuccessModal(msg)"
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
            @exit-pos="handleExitPos" 
            @clear-cart="cartItems = []"
            @refresh-clients="fetchClients"
          />
          <BackupView 
            v-else-if="activeTab === 'backup' && hasPermission('settings:manage')"
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
              <h3 class="font-bold text-lg text-slate-900">{{ tExt.welcomeUser }}，{{ currentUserObj.username }}</h3>
              <p class="text-xs text-slate-500">
                {{ tExt.noPermissionMsg1 }}<strong class="uppercase text-blue-600">{{ currentUserObj.role }}</strong>{{ tExt.noPermissionMsg2 }}
              </p>
            </div>
            <button @click="activeTab = getDefaultAllowedTab()" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/25 transition-all cursor-pointer">
              {{ tExt.goToWorkspace }}
            </button>
          </div>
        </main>
      </div>

    </div>

    <!-- 🌟 新增：手工录入进销存单据弹窗 -->
    <div v-if="txDialogVisible" @click.self="txDialogVisible = false" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4 transition-all">
      <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-100 p-6 space-y-5">
        <div class="flex items-center justify-between border-b border-slate-100 pb-3">
          <div class="flex items-center gap-2">
            <span class="text-xl">📝</span>
            <h3 class="font-bold text-slate-800 text-base">{{ tExt.dialogAddTxTitle }}</h3>
          </div>
          <button @click="txDialogVisible = false" class="text-slate-400 hover:text-slate-700 text-lg font-bold cursor-pointer">✕</button>
        </div>

        <form @submit.prevent="handleAddTx" class="space-y-4">
          <!-- 类型选择 -->
          <div class="flex gap-4">
            <label class="flex-1 cursor-pointer">
              <input type="radio" v-model="newTx.type" value="OUT" class="peer sr-only" />
              <div class="p-3 text-center rounded-xl border border-slate-200 bg-slate-50 peer-checked:border-amber-500 peer-checked:bg-amber-50 peer-checked:text-amber-700 text-slate-600 font-bold transition-all">
                出库 (销售)
              </div>
            </label>
            <label class="flex-1 cursor-pointer">
              <input type="radio" v-model="newTx.type" value="IN" class="peer sr-only" />
              <div class="p-3 text-center rounded-xl border border-slate-200 bg-slate-50 peer-checked:border-emerald-500 peer-checked:bg-emerald-50 peer-checked:text-emerald-700 text-slate-600 font-bold transition-all">
                入库 (采购)
              </div>
            </label>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">OEM 编号</label>
              <input v-model="newTx.part_oem" type="text" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-sm font-mono font-bold outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">配件名称</label>
              <input v-model="newTx.part_name" type="text" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-sm font-medium outline-none focus:border-blue-500" />
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">数量</label>
              <input v-model.number="newTx.quantity" type="number" min="1" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-sm font-bold font-mono outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">单价 ($)</label>
              <input v-model.number="newTx.unit_price" type="number" step="0.01" min="0" required class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-sm font-bold font-mono outline-none focus:border-blue-500" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">客户 / 供应商</label>
            <input v-model="newTx.customer_or_supplier" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-sm outline-none focus:border-blue-500" />
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button type="button" @click="txDialogVisible = false" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">
              {{ t.common.cancel }}
            </button>
            <button type="submit" :disabled="isSubmittingTx" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer disabled:opacity-50">
              {{ isSubmittingTx ? '...' : t.common.save }}
            </button>
          </div>
        </form>
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
            <h3 class="font-bold text-slate-800 text-base">{{ tExt.dialogAddPartTitle }}</h3>
          </div>
          <button @click="dialogVisible = false" class="text-slate-400 hover:text-slate-700 text-lg font-bold cursor-pointer">✕</button>
        </div>

        <form @submit.prevent="handleAddPart" class="space-y-4 max-h-[70vh] overflow-y-auto pr-1">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colOem }}</label>
              <input v-model="newPart.oem" type="text" :placeholder="tExt.placeholderOem" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-mono font-bold outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colName }}</label>
              <input v-model="newPart.name" type="text" :placeholder="tExt.placeholderName" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-medium outline-none focus:border-blue-500" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colCategory }}</label>
              <input v-model="newPart.category" type="text" :placeholder="tExt.placeholderCategory" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colBrand }}</label>
              <input v-model="newPart.brand" type="text" :placeholder="tExt.placeholderBrand" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs outline-none focus:border-blue-500" />
            </div>
          </div>

          <!-- 🌟 修改为三列网格，加入进货价输入框 -->
          <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colStock }}</label>
              <input v-model.number="newPart.stock" type="number" min="0" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold font-mono outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colPriceUsd }}</label>
              <input v-model.number="newPart.price" type="number" step="0.5" min="0" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold font-mono outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-amber-600 mb-1">{{ t.inventory.costPrice }}</label>
              <input v-model.number="newPart.cost_price" type="number" step="0.5" min="0" class="w-full bg-amber-50 border border-amber-200 rounded-xl px-3.5 py-2 text-xs font-bold font-mono text-amber-900 outline-none focus:border-amber-500" />
            </div>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.taxRate }}</label>
              <select v-model.number="newPart.tax_rate" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-bold outline-none focus:border-blue-500 cursor-pointer">
                <option :value="0.16">{{ t.inventory.tax16 }}</option>
                <option :value="0.08">{{ t.inventory.tax8 }}</option>
                <option :value="0.0">{{ t.inventory.tax0 }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1">{{ t.inventory.colBin }}</label>
              <input v-model="newPart.bin_location" type="text" :placeholder="t.inventory.binPlaceholder" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2 text-xs font-mono outline-none focus:border-blue-500" />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">🔗 {{ tExt.labelCrossRef }}</label>
            <textarea 
              v-model="newPart.cross_references" 
              rows="3" 
              :placeholder="tExt.placeholderCrossRef" 
              class="w-full bg-slate-50 border border-slate-200 rounded-xl p-3 text-xs outline-none focus:border-blue-500 font-mono leading-relaxed resize-none"
            ></textarea>
          </div>

          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.labelImages }}</label>
            <input type="file" @change="handleFileChange" accept="image/*" multiple class="w-full text-xs text-slate-500 file:mr-4 file:py-2 file:px-3 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100 cursor-pointer border border-slate-200 rounded-xl p-1.5" />
          </div>

          <div class="flex items-center justify-end gap-3 pt-3 border-t border-slate-100">
            <button type="button" @click="dialogVisible = false" class="px-5 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">
              {{ t.common.cancel }} (ESC)
            </button>
            <button type="submit" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer">
              {{ t.common.save }} (Enter)
            </button>
          </div>
        </form>
      </div>
    </div>

    <div v-if="clientDialogVisible" class="fixed inset-0 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100">
        <div class="px-6 py-5 border-b border-slate-100">
          <h3 class="font-bold text-base text-slate-800">{{ t.clients.addBtn }}</h3>
        </div>
        <div class="p-6 space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.clients.colName }}</label>
            <input v-model="newClient.name" type="text" :placeholder="tExt.placeholderClientName" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.clients.colType }}</label>
              <select v-model="newClient.client_type" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 cursor-pointer">
                <option value="Regular">{{ tExt.optRegular }}</option>
                <option value="Taller">{{ tExt.optTaller }}</option>
                <option value="Mayorista">{{ tExt.optMayorista }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.clients.colPhone }}</label>
              <input v-model="newClient.phone" type="text" placeholder="+58 412..." class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
          </div>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.clients.colAddress }}</label>
              <input v-model="newClient.address" type="text" placeholder="Caracas / Valencia" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
            <div>
              <label class="block text-xs font-semibold text-slate-500 mb-1.5 uppercase">{{ t.clients.colRif }}</label>
              <input v-model="newClient.rif_or_cedula" type="text" placeholder="J-31234567-8" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
            </div>
          </div>
        </div>
        <div class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex justify-end gap-3">
          <button @click="clientDialogVisible = false" class="px-4 py-2 rounded-xl text-sm font-medium text-slate-600 hover:bg-slate-200/60 transition-colors">{{ t.common.cancel }}</button>
          <button @click="handleAddClient" class="px-5 py-2 rounded-xl text-sm font-medium bg-blue-600 text-white hover:bg-blue-700 shadow-md">{{ t.common.save }}</button>
        </div>
      </div>
    </div>

    <div v-if="resetModalVisible" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-2xl shadow-2xl max-w-sm w-full overflow-hidden border border-slate-100 p-6 space-y-5">
        <div class="text-center space-y-1.5">
          <div class="w-12 h-12 rounded-xl bg-amber-500 mx-auto flex items-center justify-center text-white shadow-lg shadow-amber-500/30">
            🔒
          </div>
          <h3 class="font-bold text-base text-slate-900">{{ tExt.resetPinTitle }}</h3>
          <p class="text-xs text-slate-400">{{ tExt.resetPinDesc }}</p>
        </div>

        <div>
          <input 
            v-model="resetPinInput" 
            @keyup.enter="submitResetPassword" 
            type="password" 
            :placeholder="tExt.resetPinPlace" 
            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-3 text-sm outline-none focus:border-amber-500 font-mono text-center tracking-widest"
            autofocus
          />
        </div>

        <div class="flex gap-3 pt-1">
          <button @click="resetModalVisible = false" class="flex-1 px-4 py-2.5 rounded-xl text-xs font-semibold bg-slate-100 text-slate-600 hover:bg-slate-200 transition-colors">
            {{ t.common.cancel }}
          </button>
          <button @click="submitResetPassword" class="flex-1 px-4 py-2.5 rounded-xl text-xs font-semibold bg-amber-600 text-white hover:bg-amber-700 shadow-md transition-colors">
            {{ tExt.btnConfirmReset }}
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
      :title="tExt.confirmDeleteQuote"
      :message="tExt.confirmDeleteQuoteMsg"
      :cancel-text="t.common.cancel"
      :confirm-text="t.common.delete"
      @cancel="deleteModalVisible = false"
      @confirm="confirmDeleteQuotation"
    />

    <ConfirmDialog
      :visible="deletePartModalVisible"
      overlay-class="bg-slate-900/40"
      :title="tExt.confirmDeletePart"
      :cancel-text="t.common.cancel"
      :confirm-text="t.common.delete"
      @cancel="deletePartModalVisible = false"
      @confirm="confirmDeletePart"
    />

    <ConfirmDialog
      :visible="deleteClientModalVisible"
      overlay-class="bg-slate-900/40"
      :title="tExt.confirmDeleteClient"
      :cancel-text="t.common.cancel"
      :confirm-text="t.common.delete"
      @cancel="deleteClientModalVisible = false"
      @confirm="confirmDeleteClient"
    />

    <ConfirmDialog
      :visible="deleteTxModalVisible"
      overlay-class="bg-slate-900/40"
      :title="tExt.confirmDeleteTxTitle"
      :message="tExt.confirmDeleteTxMsg"
      :cancel-text="t.common.cancel"
      :confirm-text="t.common.delete"
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
import { ref, computed, defineAsyncComponent, onMounted, onUnmounted, watch} from 'vue'
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
const QuotationListView = defineAsyncComponent(() => import('./components/QuotationListView.vue'))
const GastosView = defineAsyncComponent(() => import('./components/GastosView.vue'))

import { apiFetch, apiUrl } from './utils/api'
import { useAuth } from './composables/useAuth'
import { useNotifications } from './composables/useNotifications'
import { useInventory } from './composables/useInventory'
import { usePosCart } from './composables/usePosCart'
import { useClock } from './composables/useClock'
import { useGallery } from './composables/useGallery'

const { t, currentLang } = useI18n()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    welcomeUser: isZh ? '欢迎登录' : isEs ? 'Bienvenido' : 'Welcome',
    noPermissionMsg1: isZh ? '当前账号（' : isEs ? 'La cuenta (' : 'Account (',
    noPermissionMsg2: isZh ? '）未授权访问此页面，系统已为您匹配专属工作台。' : isEs ? ') no tiene permiso de acceso. Redirigiendo a su área de trabajo.' : ') is not authorized to access this page. Redirecting to your workspace.',
    goToWorkspace: isZh ? '进入我的可用工作台' : isEs ? 'Ir a mi área de trabajo' : 'Go to my workspace',
    dialogAddPartTitle: isZh ? '录入新汽配档案与多图相册' : isEs ? 'Registrar Nuevo Repuesto' : 'Register New Part',
    placeholderOem: isZh ? '例如: 17801-74060' : isEs ? 'Ej: 17801-74060' : 'E.g. 17801-74060',
    placeholderName: isZh ? '例如: 空气滤清器' : isEs ? 'Ej: Filtro de aire' : 'E.g. Air filter',
    placeholderCategory: isZh ? '滤清器 / 悬挂系统' : isEs ? 'Filtros / Suspensión' : 'Filters / Suspension',
    placeholderBrand: isZh ? 'Toyota / Mack / GENERAL' : isEs ? 'Toyota / Mack / GENERAL' : 'Toyota / Mack / GENERAL',
    labelCrossRef: isZh ? '交叉适配编号与备注' : isEs ? 'Referencias Cruzadas / Notas' : 'Cross-References / Notes',
    placeholderCrossRef: isZh ? '例如: WIX: 51348 / Donaldson: P550020...' : isEs ? 'Ej: WIX: 51348 / Donaldson: P550020...' : 'E.g. WIX: 51348 / Donaldson: P550020...',
    labelImages: isZh ? '配件实物照片 (最多可选 5 张)' : isEs ? 'Fotos del repuesto (Máx. 5)' : 'Part photos (Up to 5)',
    placeholderClientName: isZh ? '例如: Auto Taller Valencia C.A.' : isEs ? 'Ej: Auto Taller Valencia C.A.' : 'E.g. Auto Taller Valencia C.A.',
    optRegular: isZh ? 'Regular (零售)' : isEs ? 'Regular (Minorista)' : 'Regular (Retail)',
    optTaller: isZh ? 'Taller (修理厂)' : isEs ? 'Taller (Mecánico)' : 'Workshop (Mechanic)',
    optMayorista: isZh ? 'Mayorista (批发商)' : isEs ? 'Mayorista (Distribuidor)' : 'Wholesaler',
    resetPinTitle: isZh ? '安全密钥验证' : isEs ? 'Verificación de PIN' : 'Security PIN Verification',
    resetPinDesc: isZh ? '请输入系统最高安全密钥 (Security PIN) 以重置管理员密码' : isEs ? 'Ingrese el PIN de seguridad para restablecer la contraseña del administrador' : 'Enter the Security PIN to reset the admin password',
    resetPinPlace: isZh ? '输入 Security PIN...' : isEs ? 'Ingresar PIN...' : 'Enter PIN...',
    btnConfirmReset: isZh ? '确认重置' : isEs ? 'Confirmar' : 'Confirm Reset',
    confirmDeleteQuote: isZh ? '确认删除报价单' : isEs ? 'Confirmar eliminación de cotización' : 'Confirm Quotation Deletion',
    confirmDeleteQuoteMsg: isZh ? '确定要永久删除这条历史报价单吗？' : isEs ? '¿Eliminar permanentemente esta cotización?' : 'Permanently delete this quotation?',
    confirmDeletePart: isZh ? '确认删除商品' : isEs ? 'Confirmar eliminación de repuesto' : 'Confirm Part Deletion',
    confirmDeleteClient: isZh ? '确认删除客户' : isEs ? 'Confirmar eliminación de cliente' : 'Confirm Client Deletion',
    confirmDeleteTxTitle: isZh ? '确认删除流水单据' : isEs ? 'Confirmar eliminación de transacción' : 'Confirm Transaction Deletion',
    confirmDeleteTxMsg: isZh ? '删除后将自动还原对应的商品库存数量。' : isEs ? 'Se restaurará automáticamente el inventario.' : 'Inventory stock will be automatically restored.',
    toastPosExit: isZh ? '当前仅有收银权限，已安全退出系统。' : isEs ? 'Solo tiene permisos de caja. Cerrando sesión de forma segura.' : 'Only POS permissions. Logging out safely.',
    toastClientDeleted: isZh ? '客户档案已成功删除！' : isEs ? '¡Cliente eliminado con éxito!' : 'Client deleted successfully!',
    toastPartAdded: isZh ? '新汽配商品已成功录入数据库！' : isEs ? '¡Repuesto registrado con éxito!' : 'Part added successfully!',
    toastClientAdded: isZh ? '新客户档案创建成功！' : isEs ? '¡Cliente creado con éxito!' : 'Client created successfully!',
    toastErrorUnknown: isZh ? '未知错误' : isEs ? 'Error desconocido' : 'Unknown error',
    toastServerError: isZh ? '服务器连接异常！' : isEs ? '¡Error de conexión al servidor!' : 'Server connection error!',
    dialogAddTxTitle: isZh ? '手工录入进销存单据' : isEs ? 'Registrar Movimiento' : 'Add Inventory Record',
    toastTxAdded: isZh ? '单据录入成功' : isEs ? 'Registro guardado' : 'Record saved',
  }
})

const {
  successModalVisible, successModalMessage, isErrorMessage,
  showSuccessModal, closeSuccessModal
} = useNotifications()

const {
  isLoggedIn, currentAdminUser, currentUserObj,
  loginForm, loginError, resetMessage,
  resetModalVisible, resetPinInput,
  handleLogin, handleLogout, openResetModal, submitResetPassword, validateSession
} = useAuth()

// 权限校验工具
const hasPermission = (permKey) => {
  if (!currentUserObj.value) return false
  const role = currentUserObj.value.role || 'staff'
  const perms = currentUserObj.value.permissions || []
  if (role === 'super_admin' || role === 'admin' || perms.includes('*')) return true
  return perms.includes(permKey)
}

// 获取用户默认应当进入的页面
const getDefaultAllowedTab = () => {
  const role = currentUserObj.value?.role || 'staff'
  if (role === 'super_admin' || role === 'admin') return 'dashboard'

  if (hasPermission('parts:view')) return 'parts'
  if (hasPermission('clients:view')) return 'clients'
  if (hasPermission('transactions:history')) return 'transactions'
  if (hasPermission('financial:view')) return 'financial'
  if (hasPermission('users:manage')) return 'staff'
  if (hasPermission('pos:access')) return 'desk'
  
  return 'dashboard'
}

// 🌟 核心修复：处理退出 POS 逻辑
const handleExitPos = () => {
  const role = currentUserObj.value?.role || 'staff'
  // 判断是否有除 POS 以外的后台权限
  const hasBackendAccess = hasPermission('parts:view') || 
                           hasPermission('clients:view') || 
                           hasPermission('financial:view') || 
                           hasPermission('settings:manage') || 
                           hasPermission('users:manage') ||
                           role === 'admin' || 
                           role === 'super_admin'

  if (!hasBackendAccess) {
    // 纯收银员，直接登出
    showSuccessModal(tExt.value.toastPosExit)
    setTimeout(() => { handleLogout() }, 1500)
  } else {
    // 有后台权限，回退到他有权限的页面
    activeTab.value = getDefaultAllowedTab()
  }
}

const checkAndSwitchTab = (tab) => {
  activeTab.value = tab
}

const mobileMenuOpen = ref(false)
const activeTab = ref(getDefaultAllowedTab())

watch(isLoggedIn, (newVal) => {
  if (newVal) {
    activeTab.value = getDefaultAllowedTab()
    // 登录成功后按权限加载数据（onMounted 时通常还没登录）
    refreshAll()
  } else {
    activeTab.value = 'dashboard' 
  }
})

watch(currentUserObj, (newUser) => {
  if (isLoggedIn.value && newUser && newUser.username) {
    const defaultTab = getDefaultAllowedTab()
    if (defaultTab !== 'dashboard' || !newUser.permissions || newUser.permissions.length === 0) {
       activeTab.value = defaultTab
    }
  }
}, { deep: true })

const searchQuery = ref('')
const clientSearchQuery = ref('')
const selectedBrand = ref('ALL')

const dialogVisible = ref(false)
const clientDialogVisible = ref(false)
const txDialogVisible = ref(false)
// 🌟 新增手工单据的响应式数据
const isSubmittingTx = ref(false)
const newTx = ref({
  type: 'OUT', // IN 或 OUT
  part_oem: '',
  part_name: '',
  quantity: 1,
  unit_price: 0,
  customer_or_supplier: ''
})

// 🌟 提交手工单据
const handleAddTx = async () => {
  isSubmittingTx.value = true
  try {
    const res = await apiFetch('/api/transactions', {
      method: 'POST',
      body: JSON.stringify(newTx.value)
    })
    if (res.ok) {
      txDialogVisible.value = false
      showSuccessModal('✨ ' + (tExt.value.toastTxAdded || 'Saved'))
      newTx.value = { type: 'OUT', part_oem: '', part_name: '', quantity: 1, unit_price: 0, customer_or_supplier: '' }
      fetchTransactions()
      fetchParts()
      fetchDashboardStats()
    } else {
      const err = await res.json()
      showSuccessModal(`❌ ${t.value.common.error}: ${err.detail || 'Unknown'}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ ' + tExt.value.toastServerError)
  } finally {
    isSubmittingTx.value = false
  }
}
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
  fetchDashboardStats, fetchBcvRate, updateBcvRate, refreshAll // 🌟 确保有 updateBcvRate
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

// 🌟 核心新增：处理从报价单转入 POS
const handleConvertToPos = (data) => {
  // 1. 清空当前购物车
  cartItems.value = []
  
  // 2. 将报价单的明细映射到购物车格式
  data.items.forEach(item => {
    cartItems.value.push({
      oem: item.oem,
      name: item.name,
      brand: item.brand || 'GENERAL',
      price: Number(item.price),
      quantity: Number(item.quantity),
      tax_rate: item.tax_rate ?? 0.16
    })
  })

  // 3. 带上客户名字
  if (data.client_name && data.client_name !== 'Cliente General') {
    quoteClientName.value = data.client_name
  }

  // 4. 跳转到 POS 页面
  activeTab.value = 'desk'
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
      showSuccessModal('🗑️ ' + tExt.value.toastClientDeleted)
    } else {
      const err = await res.json()
      deleteClientModalVisible.value = false
      showSuccessModal(`❌ ${t.common.error}: ${err.detail || tExt.value.toastErrorUnknown}`)
    }
  } catch (e) {
    console.error(e)
    deleteClientModalVisible.value = false
    showSuccessModal('❌ ' + tExt.value.toastServerError)
  }
}

// 🌟 修改：加上进货价初始值
const newPart = ref({ oem: '', name: '', brand: '', category: '', stock: 10, price: 15.00, cost_price: 10.00, tax_rate: 0.16, bin_location: 'Estante A-1', cross_references: '' })
const selectedFiles = ref([])
const handleFileChange = (e) => { selectedFiles.value = Array.from(e.target.files).slice(0, 5) }

const handleAddPart = async () => {
  if (!newPart.value.oem || !newPart.value.name) return
  
  const formData = new FormData()
  formData.append('oem', newPart.value.oem || '')
  formData.append('name', newPart.value.name || '')
  formData.append('brand', newPart.value.brand || 'GENERAL')
  formData.append('category', newPart.value.category || 'Uncategorized')
  formData.append('stock', newPart.value.stock ?? 0)
  formData.append('price', newPart.value.price ?? 0.0)
  formData.append('cost_price', newPart.value.cost_price ?? 0.0) // 🌟 新增：提交进货价
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
      // 🌟 修改：重置表单也带上进货价
      newPart.value = { oem: '', name: '', brand: '', category: '', stock: 10, price: 15.00, cost_price: 10.00, tax_rate: 0.16, bin_location: 'Estante A-1', cross_references: '' }
      selectedFiles.value = []
      fetchParts(); fetchDashboardStats();
      showSuccessModal('✨ ' + tExt.value.toastPartAdded)
    } else {
      const err = await res.json()
      const errorMsg = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail)
      showSuccessModal(`❌ ${t.common.error}: ${errorMsg}`)
    }
  } catch (e) {
    console.error(e)
    showSuccessModal('❌ ' + tExt.value.toastServerError)
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
    showSuccessModal('✨ ' + tExt.value.toastClientAdded)
  }
}

const handleGlobalKeydown = (e) => {
  if (galleryModalVisible.value) {
    if (e.key === 'Escape') {
      e.preventDefault()
      galleryModalVisible.value = false 
      return
    }
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      prevGalleryImage() 
      return
    }
    if (e.key === 'ArrowRight') {
      e.preventDefault()
      nextGalleryImage() 
      return
    }
  }

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

onMounted(async () => {
  window.addEventListener('keydown', handleGlobalKeydown)

  // 未登录时不要发任何受保护请求，避免无 Token 的 401 反过来清空登录态
  if (!isLoggedIn.value) return

  // 刷新页面后先复核 Token；有效再拉业务数据，并同步最新权限
  if (await validateSession()) {
    refreshAll()
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
})
</script>