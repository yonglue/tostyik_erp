<!-- src/components/ProcurementCenterView.vue -->
<template>
  <div class="space-y-6">
    <!-- 顶部状态栏 -->
    <div class="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-2 bg-slate-100 p-1.5 rounded-xl">
        <button @click="activeTab = 'orders'; resetOrderPagination()" :class="['px-4 py-2 rounded-lg text-sm font-bold transition-all cursor-pointer', activeTab === 'orders' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']">📦 {{ tExt.tabOrders }}</button>
        <button @click="activeTab = 'suggestions'; resetSuggestionPagination()" :class="['px-4 py-2 rounded-lg text-sm font-bold transition-all cursor-pointer', activeTab === 'suggestions' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']">⚡ {{ tExt.tabSuggestions }}</button>
        <button @click="activeTab = 'suppliers'" :class="['px-4 py-2 rounded-lg text-sm font-bold transition-all cursor-pointer', activeTab === 'suppliers' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']">🏢 {{ tExt.tabSuppliers }}</button>
      </div>
      
      <div class="flex items-center gap-3">
        <button @click="openCreateModal" class="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-bold text-sm shadow-md shadow-blue-500/20 transition-all cursor-pointer">
          <Plus :size="16" /> {{ tExt.newPo }}
        </button>
      </div>
    </div>

    <!-- ================= 模块一：采购订单列表 ================= -->
    <div v-if="activeTab === 'orders'" class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden flex flex-col">
      
      <div class="p-4 md:p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4 bg-white/50 shrink-0">
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-2 bg-slate-100 p-1 rounded-lg">
            <button 
              @click="orderSubTab = 'current'; resetOrderPagination(); clearOrderSelection()"
              :class="['px-3 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer', orderSubTab === 'current' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']"
            >
              {{ tExt.subTabCurrent }}
            </button>
            <button 
              @click="orderSubTab = 'history'; resetOrderPagination(); clearOrderSelection()"
              :class="['px-3 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer', orderSubTab === 'history' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']"
            >
              {{ tExt.subTabHistory }}
            </button>
          </div>
          
          <transition name="fade">
            <div v-if="selectedOrderIds.length > 0" class="flex items-center gap-3">
              <span class="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded-md border border-blue-100">{{ tExt.selected }} {{ selectedOrderIds.length }}</span>
              <button @click="batchCancelOrders" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 px-3.5 py-2 rounded-xl font-bold transition-colors cursor-pointer flex items-center gap-1.5 shadow-sm">
                🗑️ {{ tExt.batchVoid }}
              </button>
              <button @click="clearOrderSelection" class="text-xs text-slate-400 hover:text-slate-600 underline cursor-pointer transition-colors">{{ tExt.deselect }}</button>
            </div>
          </transition>
        </div>

        <button @click="fetchOrders" class="flex items-center gap-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer">
          🔄 {{ t.common.refresh }}
        </button>
      </div>

      <div class="overflow-x-auto flex-1">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-transparent border-b border-slate-200 dark:border-slate-700 text-xs font-black text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              <th class="py-4 px-4 w-12 text-center">
                <input 
                  type="checkbox" 
                  :checked="isAllOrdersSelected" 
                  @change="toggleSelectAllOrders" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </th>
              <th class="py-4 px-4">{{ tExt.colPoNo }}</th>
              <th class="py-4 px-6">{{ tExt.colSupplier }}</th>
              <th class="py-4 px-6 text-rose-600">{{ tExt.colSupplierDebt }}</th>
              <th class="py-4 px-6">{{ tExt.colItems }}</th>
              <th class="py-4 px-6">{{ tExt.colStatus }}</th>
              <th class="py-4 px-6">{{ tExt.colTime }}</th>
              <th class="py-4 px-6 text-right">{{ t.common.actions }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="paginatedOrders.length === 0">
              <td colspan="8" class="py-16 text-center text-slate-400 text-xs">
                {{ orderSubTab === 'current' ? tExt.emptyCurrent : tExt.emptyHistory }}
              </td>
            </tr>
            
            <tr 
              v-for="order in paginatedOrders" 
              :key="order.id" 
              @click="openOrderDrawer(order)"
              :class="[
                'transition-colors cursor-pointer',
                selectedOrderIds.includes(order.id) ? 'bg-blue-50/60 border-blue-200' : 'hover:bg-slate-50/80'
              ]"
            >
              <td class="py-4 px-4 text-center" @click.stop>
                <input 
                  type="checkbox" 
                  :checked="selectedOrderIds.includes(order.id)" 
                  @change="toggleSelectOrder(order)"
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </td>
              <td class="py-4 px-4 font-mono font-bold text-blue-600">{{ order.po_no }}</td>
              <td class="py-4 px-6 font-bold text-slate-800">{{ getSupplierName(order.supplier_id) }}</td>
              <td class="py-4 px-6 font-mono font-bold text-rose-500">$ {{ getSupplierDebt(order.supplier_id).toFixed(2) }}</td>
              <td class="py-4 px-6 text-slate-600">{{ getItemsCount(order.items_json) }} SKUs</td>
              <td class="py-4 px-6">
                <span :class="{
                  'bg-emerald-50 text-emerald-600': order.status === 'received',
                  'bg-amber-50 text-amber-600': order.status === 'PENDING',
                  'bg-slate-100 text-slate-500': order.status === 'CANCELLED'
                }" class="px-2.5 py-1 rounded-lg text-xs font-bold">
                  {{ order.status === 'received' ? tExt.stReceived : order.status === 'PENDING' ? tExt.stPending : tExt.stCancelled }}
                </span>
              </td>
              <td class="py-4 px-6 text-slate-500 font-mono text-xs">{{ formatDate(order.created_at) }}</td>
              <td class="py-4 px-6 text-right space-x-2" @click.stop>
                <button @click="openOrderDrawer(order)" class="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">{{ tExt.btnDetail }}</button>
                <button v-if="order.status === 'PENDING'" @click="cancelOrder(order.id)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">{{ tExt.btnVoid }}</button>
                <button v-if="order.status === 'PENDING'" @click="receiveOrder(order.id)" class="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">{{ tExt.btnReceive }}</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="ordersTotalPages > 1" class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs shrink-0">
        <span class="text-slate-500 font-medium">
          {{ tExt.showing }} <strong class="text-slate-800">{{ (ordersCurrentPage - 1) * ordersPageSize + 1 }}</strong> {{ tExt.to }} 
          <strong class="text-slate-800">{{ Math.min(ordersCurrentPage * ordersPageSize, displayedOrders.length) }}</strong> {{ tExt.of }} 
          <strong class="text-slate-800">{{ displayedOrders.length }}</strong> {{ tExt.items }}.
        </span>
        
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 bg-white border border-slate-200 rounded-xl px-2 py-1 shadow-2xs">
            <span class="text-slate-400 text-[11px]">{{ tExt.jumpTo }}</span>
            <input type="number" min="1" :max="ordersTotalPages" v-model.number="jumpOrdersPageInput" @keyup.enter="handleJumpOrdersPage" class="w-12 text-center font-mono font-bold text-blue-600 bg-slate-50 rounded-lg py-1 outline-none border border-slate-200 focus:border-blue-500 text-xs" />
            <span class="text-slate-400 text-[11px]">/ {{ ordersTotalPages }} {{ tExt.page }}</span>
            <button @click="handleJumpOrdersPage" class="bg-blue-50 hover:bg-blue-100 text-blue-600 px-2.5 py-1 rounded-lg font-bold transition-colors cursor-pointer text-[11px]">{{ tExt.jumpBtn }}</button>
          </div>

          <div class="flex items-center gap-1.5">
            <button @click="ordersCurrentPage--" :disabled="ordersCurrentPage === 1" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">{{ tExt.prevPage }}</button>
            <span class="px-3 py-1 font-mono font-bold text-slate-700">{{ ordersCurrentPage }} / {{ ordersTotalPages }}</span>
            <button @click="ordersCurrentPage++" :disabled="ordersCurrentPage === ordersTotalPages" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">{{ tExt.nextPage }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= 模块二：智能补货 ================= -->
    <div v-if="activeTab === 'suggestions'" class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden flex flex-col">
      
      <div class="p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4 bg-white/50 shrink-0">
        <div class="flex items-center gap-6">
          <div>
            <h3 class="font-bold text-slate-800 text-base">⚡ {{ tExt.suggestionTitle }}</h3>
            <p class="text-xs text-slate-400 mt-1">{{ tExt.suggestionSubtitle }}</p>
          </div>
          
          <transition name="fade">
            <div v-if="selectedSuggestionIds.length > 0" class="flex items-center gap-3">
              <span class="text-xs font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded-md border border-amber-200">{{ tExt.selected }} {{ selectedSuggestionIds.length }}</span>
              <button @click="generatePOFromSuggestions" class="text-xs bg-amber-500 hover:bg-amber-600 text-white px-3.5 py-2 rounded-xl font-bold transition-colors cursor-pointer shadow-sm">
                🛒 {{ tExt.addToPo }}
              </button>
              <button @click="selectedSuggestionIds = []" class="text-xs text-slate-400 hover:text-slate-600 underline cursor-pointer transition-colors">{{ tExt.deselect }}</button>
            </div>
          </transition>
        </div>

        <button @click="fetchSuggestions" class="flex items-center gap-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer">
          🔄 {{ t.common.refresh }}
        </button>
      </div>

      <div class="overflow-x-auto flex-1">
        <table class="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr class="bg-transparent border-b border-slate-200 dark:border-slate-700 text-xs font-black text-slate-600 dark:text-slate-400 uppercase tracking-wider">
              <th class="py-4 px-6 w-12 text-center">
                <input type="checkbox" :checked="isAllSuggestionsSelected" @change="toggleSelectAllSuggestions" class="rounded border-slate-300 text-amber-500 focus:ring-amber-500 w-4 h-4 cursor-pointer" />
              </th>
              <th class="py-4 px-6">{{ tExt.colPart }}</th>
              <th class="py-4 px-6">{{ tExt.colStock }}</th>
              <th class="py-4 px-6">{{ tExt.colSuggestQty }}</th>
              <th class="py-4 px-6">{{ tExt.colLastPrice }}</th>
              <th class="py-4 px-6">{{ tExt.colEstCost }}</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="paginatedSuggestions.length === 0">
              <td colspan="6" class="py-16 text-center text-slate-400 text-xs">👍 {{ tExt.emptySuggestion }}</td>
            </tr>
            
            <tr 
              v-for="item in paginatedSuggestions" 
              :key="item.oem" 
              @click="openSuggestionDrawer(item)"
              :class="[
                'cursor-pointer transition-colors',
                selectedSuggestionIds.includes(item.oem) ? 'bg-amber-50/70 border-amber-200' : 'hover:bg-amber-50/30'
              ]"
            >
              <td class="py-4 px-6 text-center" @click.stop>
                <input type="checkbox" :checked="selectedSuggestionIds.includes(item.oem)" @change="toggleSuggestionSelect(item.oem)" class="rounded border-slate-300 text-amber-500 focus:ring-amber-500 w-4 h-4 cursor-pointer" />
              </td>
              <td class="py-4 px-6">
                <div class="font-bold text-slate-800">{{ item.name }}</div>
                <div class="text-xs text-blue-600 font-mono">{{ item.oem }}</div>
              </td>
              <td class="py-4 px-6"><span class="bg-rose-50 text-rose-600 px-2.5 py-1 rounded-lg text-xs font-bold">{{ item.current_stock }} {{ tExt.unit }}</span></td>
              <td class="py-4 px-6 font-mono font-bold text-emerald-600">+ {{ item.suggested_qty }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">$ {{ Number(item.unit_price).toFixed(2) }}</td>
              <td class="py-4 px-6 font-mono font-bold text-slate-800">$ {{ Number(item.estimated_cost).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 分页 -->
      <div v-if="suggestionsTotalPages > 1" class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs shrink-0">
        <span class="text-slate-500 font-medium">
          {{ tExt.showing }} <strong class="text-slate-800">{{ (suggestionsCurrentPage - 1) * suggestionsPageSize + 1 }}</strong> {{ tExt.to }} 
          <strong class="text-slate-800">{{ Math.min(suggestionsCurrentPage * suggestionsPageSize, suggestionsList.length) }}</strong> {{ tExt.of }} 
          <strong class="text-slate-800">{{ suggestionsList.length }}</strong> {{ tExt.suggestions }}.
        </span>
        
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 bg-white border border-slate-200 rounded-xl px-2 py-1 shadow-2xs">
            <span class="text-slate-400 text-[11px]">{{ tExt.jumpTo }}</span>
            <input type="number" min="1" :max="suggestionsTotalPages" v-model.number="jumpSuggestionsPageInput" @keyup.enter="handleJumpSuggestionsPage" class="w-12 text-center font-mono font-bold text-amber-600 bg-slate-50 rounded-lg py-1 outline-none border border-slate-200 focus:border-amber-500 text-xs" />
            <span class="text-slate-400 text-[11px]">/ {{ suggestionsTotalPages }} {{ tExt.page }}</span>
            <button @click="handleJumpSuggestionsPage" class="bg-amber-50 hover:bg-amber-100 text-amber-600 px-2.5 py-1 rounded-lg font-bold transition-colors cursor-pointer text-[11px]">{{ tExt.jumpBtn }}</button>
          </div>

          <div class="flex items-center gap-1.5">
            <button @click="suggestionsCurrentPage--" :disabled="suggestionsCurrentPage === 1" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">{{ tExt.prevPage }}</button>
            <span class="px-3 py-1 font-mono font-bold text-slate-700">{{ suggestionsCurrentPage }} / {{ suggestionsTotalPages }}</span>
            <button @click="suggestionsCurrentPage++" :disabled="suggestionsCurrentPage === suggestionsTotalPages" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">{{ tExt.nextPage }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= 模块三：供应商管理 ================= -->
    <SuppliersView v-if="activeTab === 'suppliers'" />

    <!-- 🌟 订单详情 Drawer -->
    <SideDrawer :visible="isOrderDrawerVisible" :title="tExt.orderDetailTitle" icon="📄" @close="isOrderDrawerVisible = false">
      <div class="p-6 space-y-6" v-if="currentOrderDetail">
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colSupplier }}</p>
            <p class="font-bold text-slate-800">{{ getSupplierName(currentOrderDetail.supplier_id) }}</p>
          </div>
          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colStatus }}</p>
            <p class="font-bold text-slate-800">{{ currentOrderDetail.status === 'PENDING' ? tExt.stPending : currentOrderDetail.status === 'received' ? tExt.stReceived : tExt.stCancelled }}</p>
          </div>
          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colTime }}</p>
            <p class="font-mono text-slate-700">{{ formatDate(currentOrderDetail.created_at) }}</p>
          </div>
          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">PO NO.</p>
            <p class="font-mono font-bold text-blue-600">{{ currentOrderDetail.po_no }}</p>
          </div>
        </div>

        <div class="bg-slate-50/50 p-4 rounded-xl border border-slate-100 space-y-3">
          <div v-for="(item, idx) in parsedDetailItems" :key="idx" class="flex justify-between items-center text-sm border-b border-slate-100 last:border-0 pb-2 last:pb-0">
            <div>
              <div class="font-bold text-slate-800">{{ item.name }}</div>
              <div class="text-xs font-mono text-slate-500">{{ item.oem }} × {{ item.quantity }}</div>
            </div>
            <div class="font-mono font-bold text-emerald-600">${{ (item.quantity * item.unit_price).toFixed(2) }}</div>
          </div>
        </div>
        
        <div class="flex justify-between items-center pt-4 border-t border-slate-200">
          <span class="text-sm font-bold text-slate-800">{{ tExt.totalAmount }}</span>
          <span class="text-xl font-black font-mono text-blue-600">$ {{ currentOrderDetail.total_amount_usd.toFixed(2) }}</span>
        </div>
      </div>
      <template #footer>
        <div class="px-6 py-4 border-t border-slate-100 flex items-center justify-between gap-3 bg-slate-50/50">
          <!-- 🌟 新增的 A4 打印按钮 -->
          <button @click="printA4PurchaseOrder(currentOrderDetail)" class="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-xl text-xs font-bold shadow-md transition-colors cursor-pointer flex items-center gap-2">
            🖨️ {{ tExt.btnPrintA4 }}
          </button>
          <div v-if="currentOrderDetail?.status === 'PENDING'" class="flex items-center gap-3">
            <button @click="cancelOrder(currentOrderDetail.id)" class="px-5 py-2.5 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">{{ tExt.btnVoid }}</button>
            <button @click="receiveOrder(currentOrderDetail.id)" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold shadow-md transition-colors cursor-pointer">{{ tExt.btnReceive }}</button>
          </div>
        </div>
      </template>
    </SideDrawer>

    <!-- 🌟 补货详情 Drawer -->
    <SideDrawer :visible="isSuggestionDrawerVisible" :title="tExt.suggestionDetailTitle" icon="⚡" @close="isSuggestionDrawerVisible = false">
      <div class="p-6 space-y-5" v-if="currentSuggestion">
        <div class="bg-amber-50/50 p-4 rounded-xl border border-amber-100 space-y-1 text-center">
          <div class="text-xs text-amber-600 font-semibold">{{ tExt.colSuggestQty }}</div>
          <div class="font-black text-amber-600 text-3xl font-mono">+ {{ currentSuggestion.suggested_qty }}</div>
        </div>
        
        <div class="grid grid-cols-2 gap-4 text-sm">
          <div class="col-span-2">
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colPart }}</p>
            <p class="font-bold text-slate-800">{{ currentSuggestion.name }}</p>
            <p class="font-mono text-blue-600 text-xs mt-1">{{ currentSuggestion.oem }}</p>
          </div>
          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colStock }}</p>
            <p class="font-bold text-rose-600">{{ currentSuggestion.current_stock }}</p>
          </div>
          <div>
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colLastPrice }}</p>
            <p class="font-mono font-bold text-slate-800">$ {{ Number(currentSuggestion.unit_price).toFixed(2) }}</p>
          </div>
          <div class="col-span-2">
            <p class="text-[11px] font-semibold text-slate-400 uppercase mb-1">{{ tExt.colEstCost }}</p>
            <p class="font-mono font-bold text-emerald-600 text-lg">$ {{ Number(currentSuggestion.estimated_cost).toFixed(2) }}</p>
          </div>
        </div>
      </div>
      <template #footer>
        <div class="px-6 py-4 border-t border-slate-100 flex items-center justify-end gap-3">
          <button @click="addSuggestionToCart" class="px-6 py-2.5 bg-amber-500 hover:bg-amber-600 text-white rounded-xl text-xs font-bold shadow-md transition-colors cursor-pointer">🛒 {{ tExt.addToPo }}</button>
        </div>
      </template>
    </SideDrawer>

    <!-- 新建采购单弹窗 (保留原版大弹窗，多语言化) -->
    <div v-if="isCreateModalVisible" @click.self="isCreateModalVisible = false" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 transition-all">
      <div class="bg-white rounded-3xl shadow-2xl w-[90vw] max-w-[1000px] h-[85vh] max-h-[850px] border border-slate-100 flex flex-col overflow-visible">
        <div class="flex items-center justify-between border-b border-slate-200/60 p-6 pb-4 shrink-0 bg-slate-50/50 rounded-t-3xl">
          <div class="flex items-center gap-2">
            <span class="text-xl">📝</span>
            <h3 class="font-bold text-slate-800 text-base">{{ tExt.createPoTitle }}</h3>
          </div>
          <button @click="isCreateModalVisible = false" class="text-slate-400 hover:text-slate-700 text-lg font-bold cursor-pointer">✕</button>
        </div>
        <div class="flex-1 p-6 flex flex-col min-h-0 bg-white">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 shrink-0 mb-6">
            <div class="relative">
              <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">{{ tExt.colSupplier }}</label>
              <div class="flex gap-2">
                <div class="relative flex-1">
                  <input v-model="poForm.supplier_name" @focus="showSupplierDropdown = true" @blur="hideSupplierDropdownDelayed" type="text" :placeholder="tExt.phSupplier" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm font-bold outline-none focus:border-blue-500 transition-colors" />
                  <div v-if="showSupplierDropdown" class="absolute top-full left-0 mt-1 w-full bg-white border border-slate-200 rounded-xl shadow-xl z-50 py-1 max-h-48 overflow-y-auto">
                    <div v-for="sup in filteredSuppliers" :key="sup.id" @mousedown.prevent="selectSupplier(sup)" class="px-4 py-2.5 hover:bg-blue-50 cursor-pointer transition-colors flex items-center justify-between border-b border-slate-50 last:border-0">
                      <div class="text-sm font-bold text-slate-800">{{ sup.name }}</div>
                      <div class="text-[10px] text-slate-400 font-mono">{{ tExt.colSupplierDebt }}: ${{ sup.debt_usd || 0 }}</div>
                    </div>
                    <div v-if="poForm.supplier_name.trim() && filteredSuppliers.length === 0" class="px-4 py-3 text-center text-xs text-slate-400">{{ tExt.noSupplierFound }}</div>
                  </div>
                </div>
                <button @click="openSupplierModal" type="button" class="px-4 py-2.5 bg-blue-50 hover:bg-blue-100 text-blue-600 border border-blue-200 rounded-xl text-xs font-bold transition-colors cursor-pointer shrink-0">➕ {{ tExt.newSupBtn }}</button>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">{{ tExt.poRefLabel }}</label>
              <input v-model="poForm.po_no" type="text" :placeholder="tExt.poRefPlaceholder" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm font-mono font-bold outline-none focus:border-blue-500 transition-colors" />
            </div>
          </div>
          <div class="flex-1 flex flex-col min-h-0">
            <div class="flex items-center justify-between border-b border-slate-100 pb-2 shrink-0 mb-3">
              <label class="block text-xs font-bold text-slate-500 uppercase">{{ tExt.poItemsLabel }}</label>
              <div class="flex items-center gap-3">
                <button @click="$emit('navigate', 'parts')" class="text-xs text-amber-600 hover:text-amber-700 hover:underline cursor-pointer">{{ tExt.findPartLink }}</button>
                <button @click="addPOLine" class="text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">➕ {{ tExt.addLineBtn }}</button>
              </div>
            </div>
            <div class="flex-1 overflow-y-auto space-y-3 pr-2 pb-10">
              <div v-for="(item, index) in poForm.items" :key="index" class="grid grid-cols-12 gap-3 items-center bg-slate-50 p-3 rounded-xl border border-slate-200/60 relative">
                <div class="col-span-5 relative">
                  <div @click="openPartDropdown(item)" class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm font-medium outline-none cursor-pointer flex items-center justify-between hover:border-blue-400 transition-colors">
                    <span v-if="item.oem" class="truncate text-slate-800">{{ item.oem }} - {{ item.name }}</span>
                    <span v-else class="text-slate-400">{{ tExt.searchPartPlaceholder }}</span>
                    <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                  </div>
                  <div v-if="item.showDropdown" class="absolute top-full left-0 mt-1 w-[500px] bg-white border border-slate-200 rounded-xl shadow-2xl z-[100] p-2 space-y-2">
                    <div class="relative">
                      <Search class="absolute left-3 top-2.5 text-slate-400" :size="16" />
                      <input v-model="item.searchQuery" type="text" :placeholder="tExt.searchPartDropdown" class="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-sm outline-none focus:border-blue-500 font-bold" @click.stop />
                    </div>
                    <div class="max-h-64 overflow-y-auto space-y-1">
                      <div v-for="p in getFilteredParts(item.searchQuery)" :key="p.id" @click="selectPartForItem(item, p)" class="p-2 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors border border-transparent hover:border-blue-200">
                        <div class="text-sm font-bold text-slate-800">{{ p.oem }} - {{ p.name }}</div>
                        <div class="text-[10px] text-slate-500 font-mono">{{ tExt.stockLabel }}: {{ p.stock }} | {{ tExt.lastPriceLabel }}: ${{ p.cost_price || 0 }}</div>
                      </div>
                      <div v-if="getFilteredParts(item.searchQuery).length === 0" class="text-center py-4 text-xs text-slate-400">{{ tExt.noPartFound }}</div>
                    </div>
                  </div>
                </div>
                <div class="col-span-2"><input v-model.number="item.quantity" type="number" min="1" :placeholder="tExt.qtyLabel" class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm font-mono font-bold outline-none focus:border-blue-500" /></div>
                <div class="col-span-2 relative">
                  <span class="absolute left-2.5 top-2 text-xs text-slate-400 font-bold">$</span>
                  <input v-model.number="item.unit_price" type="number" step="0.01" min="0" :placeholder="tExt.priceLabel" class="w-full bg-white border border-slate-200 rounded-lg pl-6 pr-2 py-2 text-sm font-mono font-bold outline-none focus:border-blue-500" />
                </div>
                <div class="col-span-2 text-right font-mono font-bold text-slate-700">$ {{ ((item.quantity || 0) * (item.unit_price || 0)).toFixed(2) }}</div>
                <div class="col-span-1 text-center"><button @click="removePOLine(index)" class="text-rose-500 hover:bg-rose-50 p-1.5 rounded-lg transition-colors cursor-pointer">🗑️</button></div>
              </div>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-between border-t border-slate-200/60 p-6 pt-4 bg-slate-50/50 shrink-0 rounded-b-3xl">
          <div class="text-sm">{{ tExt.poTotalLabel }}: <span class="font-black text-blue-600 text-xl font-mono">$ {{ totalPOAmount.toFixed(2) }}</span></div>
          <div class="flex items-center gap-3">
            <button @click="isCreateModalVisible = false" class="px-5 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">{{ t.common.cancel }}</button>
            <button @click="submitPO" :disabled="isSubmittingPO" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer disabled:opacity-50">{{ isSubmittingPO ? tExt.creating : tExt.createPoBtn }}</button>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建供应商弹窗 (保留原版，多语言化) -->
    <div v-if="isSupplierModalVisible" @click.self="isSupplierModalVisible = false" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center z-[60] p-6">
      <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100 flex flex-col animate-in zoom-in-95 duration-150">
        <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-slate-50/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900">{{ tExt.newSupTitle }}</h3>
          <button @click="isSupplierModalVisible = false" class="text-slate-400 hover:text-slate-700 font-bold text-base p-1 cursor-pointer">✕</button>
        </div>
        <div class="p-5 space-y-4">
          <div><label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.colSupplier }} *</label><input v-model="newSupplierForm.name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-bold text-slate-900" :placeholder="tExt.phSupplier" /></div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.contactLabel }}</label><input v-model="newSupplierForm.contact_person" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500" :placeholder="tExt.phContact" /></div>
            <div><label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.phoneLabel }}</label><input v-model="newSupplierForm.phone" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" :placeholder="tExt.phPhone" /></div>
          </div>
          <div><label class="block text-xs font-semibold text-slate-500 mb-1">{{ tExt.addressLabel }}</label><input v-model="newSupplierForm.address" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500" :placeholder="tExt.optional" /></div>
        </div>
        <div class="p-5 border-t border-slate-200/60 flex justify-end gap-3 bg-slate-50/50">
          <button @click="isSupplierModalVisible = false" class="px-5 py-2.5 rounded-xl text-xs font-bold bg-slate-200 text-slate-600 hover:bg-slate-300 transition-colors cursor-pointer">{{ t.common.cancel }}</button>
          <button @click="saveNewSupplier" :disabled="isSavingSupplier" class="px-6 py-2.5 rounded-xl text-xs font-bold bg-blue-600 text-white hover:bg-blue-700 shadow-md transition-colors cursor-pointer disabled:opacity-50">{{ isSavingSupplier ? tExt.saving : tExt.saveSupBtn }}</button>
        </div>
      </div>
    </div>

    <!-- 确认弹窗 -->
    <ConfirmDialog
      :visible="isConfirmVisible"
      overlay-class="bg-slate-950/60"
      :title="confirmTitle"
      :message="confirmMessage"
      :cancel-text="t.common.cancel"
      :confirm-text="tExt.confirmBtn"
      @cancel="isConfirmVisible = false"
      @confirm="executeConfirm"
    />
  </div>

  <!-- ==================================================== -->
  <!-- 🌟 核心修复：将 A4 打印区域通过 Teleport 移到 body 下，摆脱所有父级限制 -->
  <!-- ==================================================== -->
  <Teleport to="body">
    <div v-if="a4PrintData" class="a4-print-only" id="a4-print-section">
      <div class="a4-header">
        <div class="company-info">
          <h1>TOSTIYK (TK)</h1>
          <p>RIF: J-31234567-8</p>
          <p>Valera, Estado Trujillo - Venezuela</p>
          <p>Tel: +58 412-0000000</p>
        </div>
        <div class="document-info">
          <h2>采购入库单</h2>
          <p><strong>单号:</strong> {{ a4PrintData.po_no }}</p>
          <p><strong>日期:</strong> {{ formatDate(a4PrintData.created_at) }}</p>
        </div>
      </div>

      <div class="a4-parties">
        <div class="supplier-box">
          <h3>供应商信息</h3>
          <p><strong>名称:</strong> {{ getSupplierName(a4PrintData.supplier_id) }}</p>
          <p><strong>状态:</strong> {{ a4PrintData.status === 'PENDING' ? '待收货' : a4PrintData.status === 'received' ? '已入库' : '已作废' }}</p>
        </div>
      </div>

      <table class="a4-table">
        <thead>
          <tr>
            <th width="5%">#</th>
            <th width="40%">商品名称 / 描述</th>
            <th width="20%">OEM 编号</th>
            <th width="10%">数量</th>
            <th width="12%">单价 (USD)</th>
            <th width="13%">小计 (USD)</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(item, index) in parsedA4DetailItems" :key="index">
            <td>{{ index + 1 }}</td>
            <td>{{ item.name }}</td>
            <td>{{ item.oem }}</td>
            <td>{{ item.quantity }}</td>
            <td>${{ Number(item.unit_price || 0).toFixed(2) }}</td>
            <td>${{ Number((item.quantity * item.unit_price) || 0).toFixed(2) }}</td>
          </tr>
        </tbody>
      </table>

      <div class="a4-totals">
        <div class="total-box">
          <p>总计金额 (USD): <strong>${{ Number(a4PrintData.total_amount_usd || 0).toFixed(2) }}</strong></p>
          <p>总计金额 (VES): <strong>Bs. {{ Number((a4PrintData.total_amount_usd || 0) * bcvRate).toFixed(2) }}</strong></p>
        </div>
      </div>

      <div class="a4-signatures">
        <div class="sign-box">
          <p>交货人签字:</p>
          <div class="sign-line"></div>
        </div>
        <div class="sign-box">
          <p>收货人签字 / 盖章:</p>
          <div class="sign-line"></div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { Plus, Search } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'
import { useInventory } from '../composables/useInventory'
import { useNotifications } from '../composables/useNotifications'
import { apiFetch } from '../utils/api'
import SuppliersView from './SuppliersView.vue'
import ConfirmDialog from './ConfirmDialog.vue'
import SideDrawer from './SideDrawer.vue'

const { t, currentLang } = useI18n()
const { showSuccessModal } = useNotifications()
const { partsList, fetchParts, bcvRate } = useInventory()

const emit = defineEmits(['navigate'])

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  return {
    tabOrders: isZh ? '采购订单' : isEs ? 'Órdenes de Compra' : 'Purchase Orders',
    tabSuggestions: isZh ? '智能补货' : isEs ? 'Reabastecimiento' : 'Smart Restock',
    tabSuppliers: isZh ? '供应商管理' : isEs ? 'Proveedores' : 'Suppliers',
    newPo: isZh ? '新建采购单' : isEs ? 'Nueva Orden' : 'New PO',
    subTabCurrent: isZh ? '当前待处理' : isEs ? 'Pendientes' : 'Pending',
    subTabHistory: isZh ? '历史订单' : isEs ? 'Historial' : 'History',
    selected: isZh ? '已选' : isEs ? 'Seleccionados' : 'Selected',
    batchVoid: isZh ? '批量作废' : isEs ? 'Anular Lote' : 'Batch Void',
    deselect: isZh ? '取消选择' : isEs ? 'Deseleccionar' : 'Deselect',
    colPoNo: isZh ? '订单编号' : isEs ? 'Nro. Orden' : 'PO No.',
    colSupplier: isZh ? '供应商' : isEs ? 'Proveedor' : 'Supplier',
    colSupplierDebt: isZh ? '供应商当前欠款' : isEs ? 'Deuda Proveedor' : 'Supplier Debt',
    colItems: isZh ? '明细' : isEs ? 'Detalle' : 'Items',
    colStatus: isZh ? '状态' : isEs ? 'Estado' : 'Status',
    colTime: isZh ? '时间' : isEs ? 'Hora' : 'Time',
    emptyCurrent: isZh ? '当前没有待处理的采购订单' : isEs ? 'No hay órdenes pendientes' : 'No pending orders',
    emptyHistory: isZh ? '暂无历史采购订单' : isEs ? 'No hay historial de órdenes' : 'No history orders',
    stReceived: isZh ? '已入库' : isEs ? 'Recibido' : 'Received',
    stPending: isZh ? '待收货' : isEs ? 'Pendiente' : 'Pending',
    stCancelled: isZh ? '已作废' : isEs ? 'Anulado' : 'Cancelled',
    btnDetail: isZh ? '详情' : isEs ? 'Detalle' : 'Detail',
    btnVoid: isZh ? '作废' : isEs ? 'Anular' : 'Void',
    btnReceive: isZh ? '确认收货' : isEs ? 'Recibir' : 'Receive',
    showing: isZh ? '显示第' : isEs ? 'Mostrando' : 'Showing',
    to: isZh ? '到' : isEs ? 'a' : 'to',
    of: isZh ? '条，共' : isEs ? 'de' : 'of',
    items: isZh ? '个单据' : isEs ? 'registros' : 'records',
    jumpTo: isZh ? '跳转到' : isEs ? 'Ir a' : 'Go to',
    page: isZh ? '页' : isEs ? 'Página' : 'Page',
    jumpBtn: isZh ? '跳转' : isEs ? 'Ir' : 'Go',
    prevPage: isZh ? '上一页' : isEs ? 'Anterior' : 'Prev',
    nextPage: isZh ? '下一页' : isEs ? 'Siguiente' : 'Next',
    suggestionTitle: isZh ? '智能补货建议' : isEs ? 'Sugerencias de Reabastecimiento' : 'Smart Restock Suggestions',
    suggestionSubtitle: isZh ? '系统自动筛选库存低于 5 个的商品' : isEs ? 'Sistema filtra productos con stock menor a 5' : 'System filters products with stock below 5',
    addToPo: isZh ? '加入采购单' : isEs ? 'Añadir a Orden' : 'Add to PO',
    colPart: isZh ? '配件 (OEM & 名称)' : isEs ? 'Repuesto (OEM & Nombre)' : 'Part (OEM & Name)',
    colStock: isZh ? '当前库存' : isEs ? 'Stock Actual' : 'Current Stock',
    colSuggestQty: isZh ? '建议采购量' : isEs ? 'Cant. Sugerida' : 'Suggested Qty',
    colLastPrice: isZh ? '上次进价' : isEs ? 'Último Costo' : 'Last Price',
    colEstCost: isZh ? '预估采购成本' : isEs ? 'Costo Estimado' : 'Est. Cost',
    emptySuggestion: isZh ? '库存非常健康，暂无需要补货的商品！' : isEs ? '¡Stock saludable, no hay sugerencias!' : 'Stock healthy, no suggestions!',
    unit: isZh ? '个' : isEs ? 'uds' : 'pcs',
    suggestions: isZh ? '项建议' : isEs ? 'sugerencias' : 'suggestions',
    orderDetailTitle: isZh ? '采购单详情' : isEs ? 'Detalle de Orden' : 'PO Details',
    totalAmount: isZh ? '预估总价' : isEs ? 'Costo Total' : 'Total Amount',
    suggestionDetailTitle: isZh ? '补货建议详情' : isEs ? 'Detalle de Reabastecimiento' : 'Restock Details',
    createPoTitle: isZh ? '新建采购订单 (PO)' : isEs ? 'Nueva Orden de Compra (PO)' : 'New Purchase Order (PO)',
    phSupplier: isZh ? '输入或选择供应商...' : isEs ? 'Buscar o seleccionar proveedor...' : 'Search or select supplier...',
    noSupplierFound: isZh ? '未找到该供应商，可点击右侧“+新建”建档' : isEs ? 'No encontrado, use "+Nuevo"' : 'Not found, click "+New"',
    newSupBtn: isZh ? '新建' : isEs ? 'Nuevo' : 'New',
    poRefLabel: isZh ? '采购单号 (参考供应商单据)' : isEs ? 'Nro. de Orden (Ref)' : 'PO Number (Ref)',
    poRefPlaceholder: isZh ? '留空则由系统自动生成' : isEs ? 'Dejar vacío para autogenerar' : 'Leave empty for auto-gen',
    poItemsLabel: isZh ? '采购商品明细' : isEs ? 'Detalle de Productos' : 'Purchase Items',
    findPartLink: isZh ? '找不到商品？去库存页新增' : isEs ? '¿No encuentra? Ir a inventario' : 'Not found? Go to inventory',
    addLineBtn: isZh ? '添加商品行' : isEs ? 'Añadir línea' : 'Add Line',
    searchPartPlaceholder: isZh ? '搜索并选择商品...' : isEs ? 'Buscar y seleccionar...' : 'Search and select...',
    searchPartDropdown: isZh ? '输入 OEM 或名称搜索...' : isEs ? 'Buscar por OEM o nombre...' : 'Search OEM or name...',
    stockLabel: isZh ? '库存' : isEs ? 'Stock' : 'Stock',
    lastPriceLabel: isZh ? '进价' : isEs ? 'Costo' : 'Cost',
    noPartFound: isZh ? '未找到匹配商品' : isEs ? 'No se encontraron productos' : 'No parts found',
    qtyLabel: isZh ? '数量' : isEs ? 'Cantidad' : 'Qty',
    priceLabel: isZh ? '进货价' : isEs ? 'Precio Costo' : 'Cost Price',
    poTotalLabel: isZh ? '预估总价' : isEs ? 'Costo Total' : 'Total Est.',
    creating: isZh ? '创建中...' : isEs ? 'Creando...' : 'Creating...',
    createPoBtn: isZh ? '确认创建采购单' : isEs ? 'Confirmar Orden' : 'Confirm PO',
    newSupTitle: isZh ? '新建供应商档案' : isEs ? 'Nuevo Proveedor' : 'New Supplier',
    contactLabel: isZh ? '联系人' : isEs ? 'Contacto' : 'Contact',
    phoneLabel: isZh ? '联系电话' : isEs ? 'Teléfono' : 'Phone',
    addressLabel: isZh ? '地址' : isEs ? 'Dirección' : 'Address',
    optional: isZh ? '选填' : isEs ? 'Opcional' : 'Optional',
    phContact: isZh ? '张老板' : isEs ? 'Ej: Juan' : 'E.g. John',
    phPhone: isZh ? '例如：+58 412...' : isEs ? 'Ej: +58 412...' : 'E.g. +58 412...',
    saving: isZh ? '保存中...' : isEs ? 'Guardando...' : 'Saving...',
    saveSupBtn: isZh ? '保存供应商' : isEs ? 'Guardar Proveedor' : 'Save Supplier',
    confirmBtn: isZh ? '确认' : isEs ? 'Confirmar' : 'Confirm',
    btnPrintA4: isZh ? '打印 A4 单据' : isEs ? 'Imprimir A4' : 'Print A4',
    confirmVoidTitle: isZh ? '确认作废采购单' : isEs ? 'Confirmar Anulación' : 'Confirm Void',
    confirmVoidMsg: isZh ? '作废后不可恢复，且不会增加库存。确定要作废该采购单吗？' : isEs ? '¿Anular esta orden? No se puede deshacer.' : 'Void this PO? Cannot be undone.',
    confirmReceiveTitle: isZh ? '确认收货入库' : isEs ? 'Confirmar Recepción' : 'Confirm Receipt',
    confirmReceiveMsg: isZh ? '系统将增加库存并自动更新商品最新进价！确定收货吗？' : isEs ? '¿Confirmar recepción? El inventario aumentará.' : 'Confirm receipt? Inventory will increase.',
    toastNoName: isZh ? '请填写供应商名称' : isEs ? 'Ingrese el nombre del proveedor' : 'Enter supplier name',
    toastSupCreated: isZh ? '供应商创建成功' : isEs ? 'Proveedor creado' : 'Supplier created',
    toastOrderVoided: isZh ? '采购单已作废' : isEs ? 'Orden anulada' : 'Order voided',
    toastReceiveSuccess: isZh ? '收货成功' : isEs ? 'Recepción exitosa' : 'Receipt successful',
    toastPoCreated: isZh ? '采购单创建成功' : isEs ? 'Orden creada' : 'PO created',
    toastBatchVoided: isZh ? '成功作废' : isEs ? 'Anulados' : 'Voided'
  }
})

const activeTab = ref('orders')
const ordersList = ref([])
const suppliersList = ref([]) 

// 订单状态与分页
const orderSubTab = ref('current')
const selectedOrderIds = ref([])
const ordersCurrentPage = ref(1)
const ordersPageSize = 10
const jumpOrdersPageInput = ref(1)

const displayedOrders = computed(() => {
  if (orderSubTab.value === 'current') return ordersList.value.filter(o => o.status === 'PENDING')
  return ordersList.value.filter(o => o.status === 'received' || o.status === 'CANCELLED')
})

const ordersTotalPages = computed(() => Math.ceil(displayedOrders.value.length / ordersPageSize) || 1)
const paginatedOrders = computed(() => {
  const start = (ordersCurrentPage.value - 1) * ordersPageSize
  return displayedOrders.value.slice(start, start + ordersPageSize)
})

const resetOrderPagination = () => {
  ordersCurrentPage.value = 1
  jumpOrdersPageInput.value = 1
}

const handleJumpOrdersPage = () => {
  let target = parseInt(jumpOrdersPageInput.value)
  if (isNaN(target)) return
  if (target < 1) target = 1
  if (target > ordersTotalPages.value) target = ordersTotalPages.value
  ordersCurrentPage.value = target
}

const isAllOrdersSelected = computed(() => {
  if (paginatedOrders.value.length === 0) return false
  return paginatedOrders.value.every(o => selectedOrderIds.value.includes(o.id))
})

const toggleSelectAllOrders = (e) => {
  if (e.target.checked) {
    const currentIds = paginatedOrders.value.map(o => o.id)
    selectedOrderIds.value = Array.from(new Set([...selectedOrderIds.value, ...currentIds]))
  } else {
    const currentIds = paginatedOrders.value.map(o => o.id)
    selectedOrderIds.value = selectedOrderIds.value.filter(id => !currentIds.includes(id))
  }
}

const toggleSelectOrder = (order) => {
  if (selectedOrderIds.value.includes(order.id)) {
    selectedOrderIds.value = selectedOrderIds.value.filter(id => id !== order.id)
  } else {
    selectedOrderIds.value.push(order.id)
  }
}

const clearOrderSelection = () => { selectedOrderIds.value = [] }

watch(ordersCurrentPage, (val) => { jumpOrdersPageInput.value = val })

const batchCancelOrders = () => {
  const pendingIds = selectedOrderIds.value.filter(id => {
    const order = ordersList.value.find(o => o.id === id)
    return order && order.status === 'PENDING'
  })
  if (pendingIds.length === 0) return showSuccessModal('❌ ' + tExt.value.emptyCurrent)
  showConfirm(
    tExt.value.confirmVoidTitle,
    tExt.value.confirmVoidMsg,
    async () => {
      let successCount = 0
      for (const id of pendingIds) {
        try {
          const res = await apiFetch(`/api/purchase-orders/${id}/cancel`, { method: 'PUT' })
          if (res.ok) successCount++
        } catch (e) {}
      }
      showSuccessModal(`✅ ${tExt.value.toastBatchVoided} ${successCount}`)
      selectedOrderIds.value = []
      fetchOrders()
    }
  )
}

// 智能补货状态与分页
const suggestionsList = ref([])
const selectedSuggestionIds = ref([])
const suggestionsCurrentPage = ref(1)
const suggestionsPageSize = 10
const jumpSuggestionsPageInput = ref(1)

const suggestionsTotalPages = computed(() => Math.ceil(suggestionsList.value.length / suggestionsPageSize) || 1)
const paginatedSuggestions = computed(() => {
  const start = (suggestionsCurrentPage.value - 1) * suggestionsPageSize
  return suggestionsList.value.slice(start, start + suggestionsPageSize)
})

const resetSuggestionPagination = () => {
  suggestionsCurrentPage.value = 1
  jumpSuggestionsPageInput.value = 1
}

const handleJumpSuggestionsPage = () => {
  let target = parseInt(jumpSuggestionsPageInput.value)
  if (isNaN(target)) return
  if (target < 1) target = 1
  if (target > suggestionsTotalPages.value) target = suggestionsTotalPages.value
  suggestionsCurrentPage.value = target
}

const isAllSuggestionsSelected = computed(() => {
  if (paginatedSuggestions.value.length === 0) return false
  return paginatedSuggestions.value.every(item => selectedSuggestionIds.value.includes(item.oem))
})

const toggleSelectAllSuggestions = (e) => {
  if (e.target.checked) {
    const currentOems = paginatedSuggestions.value.map(item => item.oem)
    selectedSuggestionIds.value = Array.from(new Set([...selectedSuggestionIds.value, ...currentOems]))
  } else {
    const currentOems = paginatedSuggestions.value.map(item => item.oem)
    selectedSuggestionIds.value = selectedSuggestionIds.value.filter(oem => !currentOems.includes(oem))
  }
}

const toggleSuggestionSelect = (oem) => {
  if (selectedSuggestionIds.value.includes(oem)) selectedSuggestionIds.value = selectedSuggestionIds.value.filter(id => id !== oem)
  else selectedSuggestionIds.value.push(oem)
}

watch(suggestionsCurrentPage, (val) => { jumpSuggestionsPageInput.value = val })

// 抽屉与弹窗状态
const isOrderDrawerVisible = ref(false)
const currentOrderDetail = ref(null)

const isSuggestionDrawerVisible = ref(false)
const currentSuggestion = ref(null)

const isCreateModalVisible = ref(false)
const isSubmittingPO = ref(false)
const poForm = ref({ supplier_name: '', po_no: '', items: [] })
const showSupplierDropdown = ref(false)

const isSupplierModalVisible = ref(false)
const isSavingSupplier = ref(false)
const newSupplierForm = ref({ name: '', contact_person: '', phone: '', address: '' })

const isConfirmVisible = ref(false)
const confirmTitle = ref('')
const confirmMessage = ref('')
let confirmCallback = null

const showConfirm = (title, message, action) => {
  confirmTitle.value = title
  confirmMessage.value = message
  confirmCallback = action
  isConfirmVisible.value = true
}

const executeConfirm = async () => {
  if (confirmCallback) await confirmCallback()
  isConfirmVisible.value = false
}

const handleKeydown = (e) => {
  if (e.key === 'Escape') {
    if (isConfirmVisible.value) isConfirmVisible.value = false
    else if (isSupplierModalVisible.value) isSupplierModalVisible.value = false
    else if (isCreateModalVisible.value) isCreateModalVisible.value = false
    else if (isOrderDrawerVisible.value) isOrderDrawerVisible.value = false
    else if (isSuggestionDrawerVisible.value) isSuggestionDrawerVisible.value = false
  }
}

const openOrderDrawer = (order) => {
  currentOrderDetail.value = order
  isOrderDrawerVisible.value = true
}

const openSuggestionDrawer = (item) => {
  currentSuggestion.value = item
  isSuggestionDrawerVisible.value = true
}

const addSuggestionToCart = () => {
  if (!currentSuggestion.value) return
  if (!selectedSuggestionIds.value.includes(currentSuggestion.value.oem)) {
    selectedSuggestionIds.value.push(currentSuggestion.value.oem)
  }
  isSuggestionDrawerVisible.value = false
  showSuccessModal('✅ ' + tExt.value.addToPo)
}

const parsedDetailItems = computed(() => {
  if (!currentOrderDetail.value?.items_json) return []
  try { return JSON.parse(currentOrderDetail.value.items_json) } catch (e) { return [] }
})

const cancelOrder = (id) => {
  showConfirm(
    tExt.value.confirmVoidTitle,
    tExt.value.confirmVoidMsg,
    async () => {
      try {
        const res = await apiFetch(`/api/purchase-orders/${id}/cancel`, { method: 'PUT' })
        if (res.ok) {
          showSuccessModal('🗑️ ' + tExt.value.toastOrderVoided)
          fetchOrders()
          if (currentOrderDetail.value?.id === id) isOrderDrawerVisible.value = false
        }
      } catch (e) { showSuccessModal('❌ Error') }
    }
  )
}

const getSupplierDebt = (id) => {
  const sup = suppliersList.value.find(s => s.id === id)
  return sup ? (sup.debt_usd || 0) : 0
}

const fetchSuppliers = async () => {
  try {
    const res = await apiFetch('/api/suppliers')
    if (res.ok) suppliersList.value = await res.json()
  } catch (e) { console.error(e) }
}

watch(activeTab, (newVal) => {
  if (newVal === 'suggestions') fetchSuggestions()
  else if (newVal === 'orders') fetchOrders()
})

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  return dateStr.replace('T', ' ').substring(0, 16)
}

const getSupplierName = (id) => {
  const sup = suppliersList.value.find(s => s.id === id)
  return sup ? sup.name : `Supplier #${id}`
}

const getItemsCount = (jsonStr) => {
  try { return JSON.parse(jsonStr).length } catch (e) { return 0 }
}

const fetchOrders = async () => {
  try {
    const res = await apiFetch('/api/purchase-orders')
    if (res.ok) {
      ordersList.value = await res.json()
      clearOrderSelection()
      if (ordersCurrentPage.value > ordersTotalPages.value) ordersCurrentPage.value = ordersTotalPages.value
    }
  } catch (e) { console.error(e) }
}

const fetchSuggestions = async () => {
  try {
    const res = await apiFetch('/api/procurement/suggestions')
    if (res.ok) {
      suggestionsList.value = await res.json()
      selectedSuggestionIds.value = []
      resetSuggestionPagination()
    }
  } catch (e) { console.error(e) }
}

const generatePOFromSuggestions = () => {
  if (selectedSuggestionIds.value.length === 0) return
  poForm.value = { supplier_name: '', po_no: '', items: [] }
  selectedSuggestionIds.value.forEach(oem => {
    const item = suggestionsList.value.find(s => s.oem === oem)
    if (item) {
      poForm.value.items.push({
        oem: item.oem, name: item.name, brand: item.brand || 'GENERAL',
        quantity: item.suggested_qty, unit_price: item.unit_price || 0,
        searchQuery: '', showDropdown: false
      })
    }
  })
  showSupplierDropdown.value = false
  isCreateModalVisible.value = true
}

const receiveOrder = (id) => {
  showConfirm(
    tExt.value.confirmReceiveTitle,
    tExt.value.confirmReceiveMsg,
    async () => {
      try {
        const res = await apiFetch(`/api/purchase-orders/${id}/receive`, { method: 'POST' })
        if (res.ok) {
          showSuccessModal('✅ ' + tExt.value.toastReceiveSuccess)
          fetchOrders()
          await fetchParts()
          await fetchSuppliers()
          if (currentOrderDetail.value?.id === id) isOrderDrawerVisible.value = false
        }
      } catch (e) { showSuccessModal('❌ Error') }
    }
  )
}

const openCreateModal = () => {
  poForm.value = { supplier_name: '', po_no: '', items: [] }
  addPOLine()
  showSupplierDropdown.value = false
  isCreateModalVisible.value = true
}

const addPOLine = () => {
  poForm.value.items.push({ oem: '', name: '', brand: '', quantity: 1, unit_price: 0, searchQuery: '', showDropdown: false })
}

const removePOLine = (index) => { poForm.value.items.splice(index, 1) }

const filteredSuppliers = computed(() => {
  const q = poForm.value.supplier_name.trim().toLowerCase()
  if (!q) return suppliersList.value
  return suppliersList.value.filter(s => s.name.toLowerCase().includes(q))
})

const selectSupplier = (sup) => {
  poForm.value.supplier_name = sup.name
  showSupplierDropdown.value = false
}

let blurTimeout = null
const hideSupplierDropdownDelayed = () => {
  blurTimeout = setTimeout(() => { showSupplierDropdown.value = false }, 200)
}

const openPartDropdown = (item) => {
  poForm.value.items.forEach(i => { if (i !== item) i.showDropdown = false })
  item.showDropdown = !item.showDropdown
  item.searchQuery = ''
}

const getFilteredParts = (query) => {
  if (!query || !query.trim()) return partsList.value.slice(0, 10)
  const q = query.toLowerCase().trim()
  return partsList.value.filter(p => p.oem.toLowerCase().includes(q) || p.name.toLowerCase().includes(q)).slice(0, 20)
}

const selectPartForItem = (item, part) => {
  item.oem = part.oem
  item.name = part.name
  item.brand = part.brand
  item.unit_price = part.cost_price || part.price || 0
  item.showDropdown = false
}

const totalPOAmount = computed(() => {
  return poForm.value.items.reduce((sum, item) => sum + (Number(item.quantity) || 0) * (Number(item.unit_price) || 0), 0)
})

const openSupplierModal = () => {
  newSupplierForm.value = { name: '', contact_person: '', phone: '', address: '' }
  isSupplierModalVisible.value = true
}

const saveNewSupplier = async () => {
  if (!newSupplierForm.value.name.trim()) return showSuccessModal('❌ ' + tExt.value.toastNoName)
  isSavingSupplier.value = true
  try {
    const res = await apiFetch('/api/suppliers', { method: 'POST', body: JSON.stringify(newSupplierForm.value) })
    if (res.ok) {
      const data = await res.json()
      showSuccessModal('✅ ' + tExt.value.toastSupCreated)
      await fetchSuppliers()
      poForm.value.supplier_name = data.name
      isSupplierModalVisible.value = false
    }
  } catch (e) { showSuccessModal('❌ Error') } finally { isSavingSupplier.value = false }
}

const submitPO = async () => {
  const finalSupplierName = poForm.value.supplier_name.trim() || 'Default'
  const validItems = poForm.value.items.filter(i => i.oem && i.quantity > 0)
  if (validItems.length === 0) return showSuccessModal('❌ Error')

  isSubmittingPO.value = true
  try {
    const payload = {
      supplier_name: finalSupplierName,
      po_no: poForm.value.po_no.trim() || null,
      items: validItems.map(i => ({ oem: i.oem, name: i.name, brand: i.brand, quantity: Number(i.quantity), unit_price: Number(i.unit_price) }))
    }
    const res = await apiFetch('/api/purchase-orders', { method: 'POST', body: JSON.stringify(payload) })
    if (res.ok) {
      showSuccessModal('✅ ' + tExt.value.toastPoCreated)
      isCreateModalVisible.value = false
      fetchOrders()
      fetchSuppliers()
      fetchSuggestions()
    }
  } catch (e) { showSuccessModal('❌ Error') } finally { isSubmittingPO.value = false }
}

// 🌟 新增：A4 打印控制
const a4PrintData = ref(null)

const parsedA4DetailItems = computed(() => {
  if (!a4PrintData.value?.items_json) return []
  try { return JSON.parse(a4PrintData.value.items_json) } catch (e) { return [] }
})

const printA4PurchaseOrder = (order) => {
  if (!order) return
  a4PrintData.value = order
  // 延迟 100ms 让 Vue 渲染完 A4 DOM，再唤起打印
  setTimeout(() => {
    window.print()
    // 打印完毕/取消后清理，避免占用内存
    setTimeout(() => { a4PrintData.value = null }, 1000)
  }, 100)
}

onMounted(() => { 
  fetchOrders(); 
  fetchSuppliers();
  window.addEventListener('keydown', handleKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeydown)
})
</script>

<style>
/* 🌟 屏幕端永远隐藏打印区域 */
@media screen {
  .a4-print-only {
    display: none !important;
  }
}

/* 🌟 打印端隐藏所有网页元素，只保留打印区域 */
@media print {
  /* 隐藏所有东西 */
  body > * {
    display: none !important;
  }
  
  /* 单独显示打印区域 */
  #a4-print-section {
    display: block !important;
    position: absolute;
    left: 0;
    top: 0;
    width: 100%;
    padding: 20mm;
    background: white;
    font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif;
    color: #000;
  }

  /* 隐藏浏览器自带的页边距 */
  @page {
    margin: 0;
  }

  /* 以下为 A4 表格排版 */
  .a4-header {
    display: flex;
    justify-content: space-between;
    border-bottom: 2px solid #333;
    padding-bottom: 10px;
    margin-bottom: 20px;
  }
  .company-info h1 { font-size: 24px; margin: 0 0 5px 0; }
  .company-info p { font-size: 12px; margin: 2px 0; color: #555; }
  
  .document-info { text-align: right; }
  .document-info h2 { font-size: 20px; margin: 0 0 10px 0; text-transform: uppercase; }
  .document-info p { font-size: 13px; margin: 4px 0; }

  .a4-parties { margin-bottom: 20px; }
  .supplier-box { border: 1px solid #ccc; padding: 10px; border-radius: 4px; }
  .supplier-box h3 { font-size: 14px; margin: 0 0 8px 0; border-bottom: 1px solid #eee; padding-bottom: 4px; }
  .supplier-box p { font-size: 13px; margin: 4px 0; }

  .a4-table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 20px;
  }
  .a4-table th, .a4-table td {
    border: 1px solid #333;
    padding: 8px;
    font-size: 12px;
  }
  .a4-table th {
    background-color: #f0f0f0;
    font-weight: bold;
    text-align: left;
  }
  
  .a4-totals {
    display: flex;
    justify-content: flex-end;
    margin-bottom: 40px;
  }
  .total-box {
    width: 300px;
    border-top: 2px solid #333;
    padding-top: 10px;
  }
  .total-box p {
    display: flex;
    justify-content: space-between;
    font-size: 14px;
    margin: 5px 0;
  }

  .a4-signatures {
    display: flex;
    justify-content: space-between;
    margin-top: 60px;
  }
  .sign-box {
    width: 200px;
    text-align: center;
  }
  .sign-box p { font-size: 13px; font-weight: bold; margin-bottom: 40px; }
  .sign-line { border-bottom: 1px solid #333; }
}
</style>