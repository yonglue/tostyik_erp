<!-- src/components/ProcurementCenterView.vue -->
<template>
  <div class="space-y-6">
    <!-- 顶部状态栏 -->
    <div class="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
      <div class="flex items-center gap-2 bg-slate-100 p-1.5 rounded-xl">
        <button @click="activeTab = 'orders'; resetOrderPagination()" :class="['px-4 py-2 rounded-lg text-sm font-bold transition-all cursor-pointer', activeTab === 'orders' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']">📦 采购订单</button>
        <button @click="activeTab = 'suggestions'; resetSuggestionPagination()" :class="['px-4 py-2 rounded-lg text-sm font-bold transition-all cursor-pointer', activeTab === 'suggestions' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']">⚡ 智能补货</button>
        <button @click="activeTab = 'suppliers'" :class="['px-4 py-2 rounded-lg text-sm font-bold transition-all cursor-pointer', activeTab === 'suppliers' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']">🏢 供应商管理</button>
      </div>
      
      <div class="flex items-center gap-3">
        <button @click="openCreateModal" class="flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-xl font-bold text-sm shadow-md shadow-blue-500/20 transition-all cursor-pointer">
          <Plus :size="16" /> 新建采购单
        </button>
      </div>
    </div>

    <!-- ================= 模块一：采购订单列表 ================= -->
    <div v-if="activeTab === 'orders'" class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden flex flex-col">
      
      <!-- 顶部：切换与批量操作 (保持左侧布局) -->
      <div class="p-4 md:p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4 bg-white/50 shrink-0">
        <div class="flex items-center gap-6">
          <div class="flex items-center gap-2 bg-slate-100 p-1 rounded-lg">
            <button 
              @click="orderSubTab = 'current'; resetOrderPagination(); clearOrderSelection()"
              :class="['px-3 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer', orderSubTab === 'current' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']"
            >
              当前待处理
            </button>
            <button 
              @click="orderSubTab = 'history'; resetOrderPagination(); clearOrderSelection()"
              :class="['px-3 py-1.5 rounded-md text-xs font-bold transition-all cursor-pointer', orderSubTab === 'history' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700']"
            >
              历史订单
            </button>
          </div>
          
          <transition name="fade">
            <div v-if="selectedOrderIds.length > 0" class="flex items-center gap-3">
              <span class="text-xs font-bold text-blue-600 bg-blue-50 px-2 py-1 rounded-md border border-blue-100">已选 {{ selectedOrderIds.length }} 单</span>
              <button @click="batchCancelOrders" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 px-3.5 py-2 rounded-xl font-bold transition-colors cursor-pointer flex items-center gap-1.5 shadow-sm">
                🗑️ 批量作废
              </button>
              <button @click="clearOrderSelection" class="text-xs text-slate-400 hover:text-slate-600 underline cursor-pointer transition-colors">取消选择</button>
            </div>
          </transition>
        </div>

        <button @click="fetchOrders" class="flex items-center gap-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer">
          🔄 刷新列表
        </button>
      </div>

      <div class="overflow-x-auto flex-1">
        <table class="w-full text-left border-collapse min-w-[900px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase">
              <th class="py-4 px-4 w-12 text-center">
                <input 
                  type="checkbox" 
                  :checked="isAllOrdersSelected" 
                  @change="toggleSelectAllOrders" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 cursor-pointer" 
                />
              </th>
              <th class="py-4 px-4">订单编号</th>
              <th class="py-4 px-6">供应商</th>
              <th class="py-4 px-6 text-rose-600">供应商当前欠款</th>
              <th class="py-4 px-6">明细</th>
              <th class="py-4 px-6">状态</th>
              <th class="py-4 px-6">时间</th>
              <th class="py-4 px-6 text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="paginatedOrders.length === 0">
              <td colspan="8" class="py-16 text-center text-slate-400 text-xs">
                {{ orderSubTab === 'current' ? '当前没有待处理的采购订单' : '暂无历史采购订单' }}
              </td>
            </tr>
            
            <!-- 🌟 循环 paginatedOrders -->
            <tr 
              v-for="order in paginatedOrders" 
              :key="order.id" 
              @click="toggleSelectOrder(order)"
              :class="[
                'transition-colors cursor-pointer',
                selectedOrderIds.includes(order.id) ? 'bg-blue-50/60 border-blue-200' : 'hover:bg-slate-50/80'
              ]"
            >
              <td class="py-4 px-4 text-center" @click.stop>
                <input 
                  type="checkbox" 
                  :checked="selectedOrderIds.includes(order.id)" 
                  class="rounded border-slate-300 text-blue-600 focus:ring-blue-500 w-4 h-4 pointer-events-none" 
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
                  {{ order.status === 'received' ? '已入库' : order.status === 'PENDING' ? '待收货' : '已作废' }}
                </span>
              </td>
              <td class="py-4 px-6 text-slate-500 font-mono text-xs">{{ formatDate(order.created_at) }}</td>
              <td class="py-4 px-6 text-right space-x-2" @click.stop>
                <button @click="openDetailModal(order)" class="text-xs bg-slate-100 hover:bg-slate-200 text-slate-700 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">详情</button>
                <button v-if="order.status === 'PENDING'" @click="cancelOrder(order.id)" class="text-xs bg-rose-50 hover:bg-rose-100 text-rose-600 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">作废</button>
                <button v-if="order.status === 'PENDING'" @click="receiveOrder(order.id)" class="text-xs bg-blue-600 hover:bg-blue-700 text-white px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">确认收货</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 🌟 采购订单 分页栏 -->
      <div v-if="ordersTotalPages > 1" class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs shrink-0">
        <span class="text-slate-500 font-medium">
          显示第 <strong class="text-slate-800">{{ (ordersCurrentPage - 1) * ordersPageSize + 1 }}</strong> 到 
          <strong class="text-slate-800">{{ Math.min(ordersCurrentPage * ordersPageSize, displayedOrders.length) }}</strong> 条，共 
          <strong class="text-slate-800">{{ displayedOrders.length }}</strong> 个单据
        </span>
        
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 bg-white border border-slate-200 rounded-xl px-2 py-1 shadow-2xs">
            <span class="text-slate-400 text-[11px]">跳转到</span>
            <input type="number" min="1" :max="ordersTotalPages" v-model.number="jumpOrdersPageInput" @keyup.enter="handleJumpOrdersPage" class="w-12 text-center font-mono font-bold text-blue-600 bg-slate-50 rounded-lg py-1 outline-none border border-slate-200 focus:border-blue-500 text-xs" />
            <span class="text-slate-400 text-[11px]">/ {{ ordersTotalPages }} 页</span>
            <button @click="handleJumpOrdersPage" class="bg-blue-50 hover:bg-blue-100 text-blue-600 px-2.5 py-1 rounded-lg font-bold transition-colors cursor-pointer text-[11px]">跳转</button>
          </div>

          <div class="flex items-center gap-1.5">
            <button @click="ordersCurrentPage--" :disabled="ordersCurrentPage === 1" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">上一页</button>
            <span class="px-3 py-1 font-mono font-bold text-slate-700">{{ ordersCurrentPage }} / {{ ordersTotalPages }}</span>
            <button @click="ordersCurrentPage++" :disabled="ordersCurrentPage === ordersTotalPages" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">下一页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= 模块二：智能补货 ================= -->
    <div v-if="activeTab === 'suggestions'" class="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden flex flex-col">
      
      <!-- 顶部操作栏 -->
      <div class="p-6 border-b border-slate-100 flex flex-wrap items-center justify-between gap-4 bg-white/50 shrink-0">
        <div class="flex items-center gap-6">
          <div>
            <h3 class="font-bold text-slate-800 text-base">⚡ 智能补货建议</h3>
            <p class="text-xs text-slate-400 mt-1">系统自动筛选库存低于 5 个的商品</p>
          </div>
          
          <transition name="fade">
            <div v-if="selectedSuggestionIds.length > 0" class="flex items-center gap-3">
              <span class="text-xs font-bold text-amber-600 bg-amber-50 px-2 py-1 rounded-md border border-amber-200">已选 {{ selectedSuggestionIds.length }} 项</span>
              <button @click="generatePOFromSuggestions" class="text-xs bg-amber-500 hover:bg-amber-600 text-white px-3.5 py-2 rounded-xl font-bold transition-colors cursor-pointer shadow-sm">
                🛒 一键加入采购单
              </button>
              <button @click="selectedSuggestionIds = []" class="text-xs text-slate-400 hover:text-slate-600 underline cursor-pointer transition-colors">取消选择</button>
            </div>
          </transition>
        </div>

        <button @click="fetchSuggestions" class="flex items-center gap-2 bg-white border border-slate-200 hover:bg-slate-50 text-slate-700 px-4 py-2 rounded-xl text-xs font-bold transition-all cursor-pointer">
          🔄 刷新建议
        </button>
      </div>

      <div class="overflow-x-auto flex-1">
        <table class="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr class="bg-slate-50 border-b border-slate-100 text-xs font-bold text-slate-500 uppercase">
              <th class="py-4 px-6 w-12 text-center">
                <input type="checkbox" :checked="isAllSuggestionsSelected" @change="toggleSelectAllSuggestions" class="rounded border-slate-300 text-amber-500 focus:ring-amber-500 w-4 h-4 cursor-pointer" />
              </th>
              <th class="py-4 px-6">配件 (OEM & 名称)</th>
              <th class="py-4 px-6">当前库存</th>
              <th class="py-4 px-6">建议采购量</th>
              <th class="py-4 px-6">上次进价</th>
              <th class="py-4 px-6">预估采购成本</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="paginatedSuggestions.length === 0">
              <td colspan="6" class="py-16 text-center text-slate-400 text-xs">👍 库存非常健康，暂无需要补货的商品！</td>
            </tr>
            
            <!-- 🌟 循环 paginatedSuggestions -->
            <tr 
              v-for="item in paginatedSuggestions" 
              :key="item.oem" 
              @click="toggleSuggestionSelect(item.oem)"
              :class="[
                'cursor-pointer transition-colors',
                selectedSuggestionIds.includes(item.oem) ? 'bg-amber-50/70 border-amber-200' : 'hover:bg-amber-50/30'
              ]"
            >
              <td class="py-4 px-6 text-center" @click.stop>
                <input type="checkbox" :checked="selectedSuggestionIds.includes(item.oem)" class="rounded border-slate-300 text-amber-500 focus:ring-amber-500 w-4 h-4 pointer-events-none" />
              </td>
              <td class="py-4 px-6">
                <div class="font-bold text-slate-800">{{ item.name }}</div>
                <div class="text-xs text-blue-600 font-mono">{{ item.oem }}</div>
              </td>
              <td class="py-4 px-6"><span class="bg-rose-50 text-rose-600 px-2.5 py-1 rounded-lg text-xs font-bold">{{ item.current_stock }} 个</span></td>
              <td class="py-4 px-6 font-mono font-bold text-emerald-600">+ {{ item.suggested_qty }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">$ {{ Number(item.unit_price).toFixed(2) }}</td>
              <td class="py-4 px-6 font-mono font-bold text-slate-800">$ {{ Number(item.estimated_cost).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- 🌟 智能补货 分页栏 -->
      <div v-if="suggestionsTotalPages > 1" class="px-6 py-4 bg-slate-50 border-t border-slate-100 flex flex-wrap items-center justify-between gap-4 text-xs shrink-0">
        <span class="text-slate-500 font-medium">
          显示第 <strong class="text-slate-800">{{ (suggestionsCurrentPage - 1) * suggestionsPageSize + 1 }}</strong> 到 
          <strong class="text-slate-800">{{ Math.min(suggestionsCurrentPage * suggestionsPageSize, suggestionsList.length) }}</strong> 条，共 
          <strong class="text-slate-800">{{ suggestionsList.length }}</strong> 项建议
        </span>
        
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-1.5 bg-white border border-slate-200 rounded-xl px-2 py-1 shadow-2xs">
            <span class="text-slate-400 text-[11px]">跳转到</span>
            <input type="number" min="1" :max="suggestionsTotalPages" v-model.number="jumpSuggestionsPageInput" @keyup.enter="handleJumpSuggestionsPage" class="w-12 text-center font-mono font-bold text-amber-600 bg-slate-50 rounded-lg py-1 outline-none border border-slate-200 focus:border-amber-500 text-xs" />
            <span class="text-slate-400 text-[11px]">/ {{ suggestionsTotalPages }} 页</span>
            <button @click="handleJumpSuggestionsPage" class="bg-amber-50 hover:bg-amber-100 text-amber-600 px-2.5 py-1 rounded-lg font-bold transition-colors cursor-pointer text-[11px]">跳转</button>
          </div>

          <div class="flex items-center gap-1.5">
            <button @click="suggestionsCurrentPage--" :disabled="suggestionsCurrentPage === 1" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">上一页</button>
            <span class="px-3 py-1 font-mono font-bold text-slate-700">{{ suggestionsCurrentPage }} / {{ suggestionsTotalPages }}</span>
            <button @click="suggestionsCurrentPage++" :disabled="suggestionsCurrentPage === suggestionsTotalPages" class="px-3 py-1.5 rounded-lg border border-slate-200 bg-white font-semibold text-slate-600 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-100 transition-colors cursor-pointer">下一页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- ================= 模块三：供应商管理 ================= -->
    <SuppliersView v-if="activeTab === 'suppliers'" />

    <!-- 订单详情弹窗、新建采购单弹窗、新建供应商弹窗 (原样保留) -->
    <!-- ... -->
    <div v-if="isDetailModalVisible" @click.self="isDetailModalVisible = false" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center z-50 p-6 transition-all">
      <div class="bg-white rounded-3xl shadow-2xl max-w-2xl w-full border border-slate-100 flex flex-col">
        <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-slate-50/50 shrink-0 rounded-t-3xl">
          <h3 class="font-extrabold text-base text-slate-900">📄 采购单详情 - {{ currentOrderDetail?.po_no }}</h3>
          <button @click="isDetailModalVisible = false" class="text-slate-400 hover:text-slate-700 font-bold text-lg p-1 cursor-pointer">✕</button>
        </div>
        <div class="p-6 space-y-4 max-h-[70vh] overflow-y-auto">
          <div class="grid grid-cols-2 gap-4 text-sm mb-4">
            <div><span class="text-slate-500">供应商:</span> <span class="font-bold text-slate-800">{{ getSupplierName(currentOrderDetail?.supplier_id) }}</span></div>
            <div><span class="text-slate-500">状态:</span> <span class="font-bold text-slate-800">{{ currentOrderDetail?.status === 'PENDING' ? '待收货' : currentOrderDetail?.status === 'received' ? '已入库' : '已作废' }}</span></div>
          </div>
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="bg-slate-50 text-xs font-bold text-slate-500 border-b">
                <th class="py-2 px-3">OEM</th>
                <th class="py-2 px-3">名称</th>
                <th class="py-2 px-3 text-right">数量</th>
                <th class="py-2 px-3 text-right">单价</th>
                <th class="py-2 px-3 text-right">小计</th>
              </tr>
            </thead>
            <tbody class="text-sm">
              <tr v-for="(item, idx) in parsedDetailItems" :key="idx" class="border-b border-slate-100">
                <td class="py-2 px-3 font-mono font-bold">{{ item.oem }}</td>
                <td class="py-2 px-3">{{ item.name }}</td>
                <td class="py-2 px-3 text-right font-mono">{{ item.quantity }}</td>
                <td class="py-2 px-3 text-right font-mono">${{ Number(item.unit_price).toFixed(2) }}</td>
                <td class="py-2 px-3 text-right font-mono font-bold text-emerald-600">${{ (item.quantity * item.unit_price).toFixed(2) }}</td>
              </tr>
            </tbody>
          </table>
          <div class="text-right text-lg font-black text-blue-600 font-mono mt-4">
            预估总价: $ {{ currentOrderDetail?.total_amount_usd.toFixed(2) }}
          </div>
        </div>
        <div class="p-4 border-t border-slate-200/60 bg-slate-50/50 flex justify-end rounded-b-3xl">
           <button @click="isDetailModalVisible = false" class="px-5 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">关闭 (ESC)</button>
        </div>
      </div>
    </div>

    <div v-if="isCreateModalVisible" @click.self="isCreateModalVisible = false" class="fixed inset-0 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center z-50 p-4 transition-all">
      <!-- 原样保留 -->
      <div class="bg-white rounded-3xl shadow-2xl w-[90vw] max-w-[1000px] h-[85vh] max-h-[850px] border border-slate-100 flex flex-col overflow-visible">
        <div class="flex items-center justify-between border-b border-slate-200/60 p-6 pb-4 shrink-0 bg-slate-50/50 rounded-t-3xl">
          <div class="flex items-center gap-2">
            <span class="text-xl">📝</span>
            <h3 class="font-bold text-slate-800 text-base">新建采购订单 (PO)</h3>
          </div>
          <button @click="isCreateModalVisible = false" class="text-slate-400 hover:text-slate-700 text-lg font-bold cursor-pointer">✕</button>
        </div>
        <div class="flex-1 p-6 flex flex-col min-h-0 bg-white">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4 shrink-0 mb-6">
            <div class="relative">
              <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">供应商名称</label>
              <div class="flex gap-2">
                <div class="relative flex-1">
                  <input v-model="poForm.supplier_name" @focus="showSupplierDropdown = true" @blur="hideSupplierDropdownDelayed" type="text" placeholder="输入或选择供应商..." class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm font-bold outline-none focus:border-blue-500 transition-colors" />
                  <div v-if="showSupplierDropdown" class="absolute top-full left-0 mt-1 w-full bg-white border border-slate-200 rounded-xl shadow-xl z-50 py-1 max-h-48 overflow-y-auto">
                    <div v-for="sup in filteredSuppliers" :key="sup.id" @mousedown.prevent="selectSupplier(sup)" class="px-4 py-2.5 hover:bg-blue-50 cursor-pointer transition-colors flex items-center justify-between border-b border-slate-50 last:border-0">
                      <div class="text-sm font-bold text-slate-800">{{ sup.name }}</div>
                      <div class="text-[10px] text-slate-400 font-mono">欠款: ${{ sup.debt_usd || 0 }}</div>
                    </div>
                    <div v-if="poForm.supplier_name.trim() && filteredSuppliers.length === 0" class="px-4 py-3 text-center text-xs text-slate-400">未找到该供应商，可点击右侧“+新建”建档</div>
                  </div>
                </div>
                <button @click="openSupplierModal" type="button" class="px-4 py-2.5 bg-blue-50 hover:bg-blue-100 text-blue-600 border border-blue-200 rounded-xl text-xs font-bold transition-colors cursor-pointer shrink-0">➕ 新建</button>
              </div>
            </div>
            <div>
              <label class="block text-xs font-bold text-slate-500 mb-1.5 uppercase">采购单号 (参考供应商单据)</label>
              <input v-model="poForm.po_no" type="text" placeholder="留空则由系统自动生成" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm font-mono font-bold outline-none focus:border-blue-500 transition-colors" />
            </div>
          </div>
          <div class="flex-1 flex flex-col min-h-0">
            <div class="flex items-center justify-between border-b border-slate-100 pb-2 shrink-0 mb-3">
              <label class="block text-xs font-bold text-slate-500 uppercase">采购商品明细</label>
              <div class="flex items-center gap-3">
                <button @click="$emit('navigate', 'parts')" class="text-xs text-amber-600 hover:text-amber-700 hover:underline cursor-pointer">找不到商品？去库存页新增</button>
                <button @click="addPOLine" class="text-xs bg-blue-50 hover:bg-blue-100 text-blue-600 px-3 py-1.5 rounded-lg font-bold transition-colors cursor-pointer">➕ 添加商品行</button>
              </div>
            </div>
            <div class="flex-1 overflow-y-auto space-y-3 pr-2 pb-10">
              <div v-for="(item, index) in poForm.items" :key="index" class="grid grid-cols-12 gap-3 items-center bg-slate-50 p-3 rounded-xl border border-slate-200/60 relative">
                <div class="col-span-5 relative">
                  <div @click="openPartDropdown(item)" class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm font-medium outline-none cursor-pointer flex items-center justify-between hover:border-blue-400 transition-colors">
                    <span v-if="item.oem" class="truncate text-slate-800">{{ item.oem }} - {{ item.name }}</span>
                    <span v-else class="text-slate-400">搜索并选择商品...</span>
                    <svg class="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                  </div>
                  <div v-if="item.showDropdown" class="absolute top-full left-0 mt-1 w-[500px] bg-white border border-slate-200 rounded-xl shadow-2xl z-[100] p-2 space-y-2">
                    <div class="relative">
                      <Search class="absolute left-3 top-2.5 text-slate-400" :size="16" />
                      <input v-model="item.searchQuery" type="text" placeholder="输入 OEM 或名称搜索..." class="w-full bg-slate-50 border border-slate-200 rounded-lg pl-9 pr-3 py-2 text-sm outline-none focus:border-blue-500 font-bold" @click.stop />
                    </div>
                    <div class="max-h-64 overflow-y-auto space-y-1">
                      <div v-for="p in getFilteredParts(item.searchQuery)" :key="p.id" @click="selectPartForItem(item, p)" class="p-2 rounded-lg hover:bg-blue-50 cursor-pointer transition-colors border border-transparent hover:border-blue-200">
                        <div class="text-sm font-bold text-slate-800">{{ p.oem }} - {{ p.name }}</div>
                        <div class="text-[10px] text-slate-500 font-mono">Stock: {{ p.stock }} | 进价: ${{ p.cost_price || 0 }}</div>
                      </div>
                      <div v-if="getFilteredParts(item.searchQuery).length === 0" class="text-center py-4 text-xs text-slate-400">未找到匹配商品</div>
                    </div>
                  </div>
                </div>
                <div class="col-span-2"><input v-model.number="item.quantity" type="number" min="1" placeholder="数量" class="w-full bg-white border border-slate-200 rounded-lg px-3 py-2 text-sm font-mono font-bold outline-none focus:border-blue-500" /></div>
                <div class="col-span-2 relative">
                  <span class="absolute left-2.5 top-2 text-xs text-slate-400 font-bold">$</span>
                  <input v-model.number="item.unit_price" type="number" step="0.01" min="0" placeholder="进货价" class="w-full bg-white border border-slate-200 rounded-lg pl-6 pr-2 py-2 text-sm font-mono font-bold outline-none focus:border-blue-500" />
                </div>
                <div class="col-span-2 text-right font-mono font-bold text-slate-700">$ {{ ((item.quantity || 0) * (item.unit_price || 0)).toFixed(2) }}</div>
                <div class="col-span-1 text-center"><button @click="removePOLine(index)" class="text-rose-500 hover:bg-rose-50 p-1.5 rounded-lg transition-colors cursor-pointer">🗑️</button></div>
              </div>
            </div>
          </div>
        </div>
        <div class="flex items-center justify-between border-t border-slate-200/60 p-6 pt-4 bg-slate-50/50 shrink-0 rounded-b-3xl">
          <div class="text-sm">预估总价: <span class="font-black text-blue-600 text-xl font-mono">$ {{ totalPOAmount.toFixed(2) }}</span></div>
          <div class="flex items-center gap-3">
            <button @click="isCreateModalVisible = false" class="px-5 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">取消 (ESC)</button>
            <button @click="submitPO" :disabled="isSubmittingPO" class="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-sm font-bold shadow-md shadow-blue-500/20 transition-all cursor-pointer disabled:opacity-50">{{ isSubmittingPO ? '创建中...' : '确认创建采购单' }}</button>
          </div>
        </div>
      </div>
    </div>

    <div v-if="isSupplierModalVisible" @click.self="isSupplierModalVisible = false" class="fixed inset-0 bg-slate-950/60 backdrop-blur-sm flex items-center justify-center z-[60] p-6">
      <!-- 原样保留 -->
      <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100 flex flex-col animate-in zoom-in-95 duration-150">
        <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-slate-50/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900">🏢 新建供应商档案</h3>
          <button @click="isSupplierModalVisible = false" class="text-slate-400 hover:text-slate-700 font-bold text-base p-1 cursor-pointer">✕</button>
        </div>
        <div class="p-5 space-y-4">
          <div><label class="block text-xs font-semibold text-slate-500 mb-1">供应商名称 *</label><input v-model="newSupplierForm.name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-bold text-slate-900" placeholder="例如：广州汽配城" /></div>
          <div class="grid grid-cols-2 gap-4">
            <div><label class="block text-xs font-semibold text-slate-500 mb-1">联系人</label><input v-model="newSupplierForm.contact_person" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500" placeholder="张老板" /></div>
            <div><label class="block text-xs font-semibold text-slate-500 mb-1">联系电话</label><input v-model="newSupplierForm.phone" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-mono" placeholder="+58 412..." /></div>
          </div>
          <div><label class="block text-xs font-semibold text-slate-500 mb-1">地址</label><input v-model="newSupplierForm.address" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500" placeholder="选填" /></div>
        </div>
        <div class="p-5 border-t border-slate-200/60 flex justify-end gap-3 bg-slate-50/50">
          <button @click="isSupplierModalVisible = false" class="px-5 py-2.5 rounded-xl text-xs font-bold bg-slate-200 text-slate-600 hover:bg-slate-300 transition-colors cursor-pointer">取消 (ESC)</button>
          <button @click="saveNewSupplier" :disabled="isSavingSupplier" class="px-6 py-2.5 rounded-xl text-xs font-bold bg-blue-600 text-white hover:bg-blue-700 shadow-md transition-colors cursor-pointer disabled:opacity-50">{{ isSavingSupplier ? '保存中...' : '保存供应商' }}</button>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :visible="isConfirmVisible"
      overlay-class="bg-slate-950/60"
      :title="confirmTitle"
      :message="confirmMessage"
      :cancel-text="'取消'"
      :confirm-text="'确认'"
      @cancel="isConfirmVisible = false"
      @confirm="executeConfirm"
    />
  </div>
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

const { currentLang } = useI18n()
const { showSuccessModal } = useNotifications()
const { partsList, fetchParts } = useInventory()

const emit = defineEmits(['navigate'])

const activeTab = ref('orders')
const ordersList = ref([])
const suppliersList = ref([]) 

// 🌟 订单状态与分页逻辑
const orderSubTab = ref('current')
const selectedOrderIds = ref([])
const ordersCurrentPage = ref(1)
const ordersPageSize = 10
const jumpOrdersPageInput = ref(1)

const displayedOrders = computed(() => {
  if (orderSubTab.value === 'current') {
    return ordersList.value.filter(o => o.status === 'PENDING')
  } else {
    return ordersList.value.filter(o => o.status === 'received' || o.status === 'CANCELLED')
  }
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

// 🌟 分页后，全选仅作用于当前页
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

const clearOrderSelection = () => {
  selectedOrderIds.value = []
}

// 监听分页变化，更新跳转框
watch(ordersCurrentPage, (val) => { jumpOrdersPageInput.value = val })

// 🌟 批量作废
const batchCancelOrders = () => {
  const pendingIds = selectedOrderIds.value.filter(id => {
    const order = ordersList.value.find(o => o.id === id)
    return order && order.status === 'PENDING'
  })
  
  if (pendingIds.length === 0) {
    return showSuccessModal('❌ 选中的订单中没有可作废的待处理单据')
  }

  showConfirm(
    '批量作废采购单',
    `确定要作废选中的 ${pendingIds.length} 个待处理单据吗？非待处理单据将被自动忽略。`,
    async () => {
      let successCount = 0
      for (const id of pendingIds) {
        try {
          const res = await apiFetch(`/api/purchase-orders/${id}/cancel`, { method: 'PUT' })
          if (res.ok) successCount++
        } catch (e) {}
      }
      showSuccessModal(`✅ 成功作废 ${successCount} 个单据`)
      selectedOrderIds.value = []
      fetchOrders()
    }
  )
}

// 🌟 智能补货状态与分页逻辑
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

// 🌟 分页后，全选仅作用于当前页
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

// 监听分页变化，更新跳转框
watch(suggestionsCurrentPage, (val) => { jumpSuggestionsPageInput.value = val })

// 后续变量
const isCreateModalVisible = ref(false)
const isSubmittingPO = ref(false)
const poForm = ref({ supplier_name: '', po_no: '', items: [] })
const showSupplierDropdown = ref(false)

const isSupplierModalVisible = ref(false)
const isSavingSupplier = ref(false)
const newSupplierForm = ref({ name: '', contact_person: '', phone: '', address: '' })

const isDetailModalVisible = ref(false)
const currentOrderDetail = ref(null)

// 确认弹窗
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
  if (confirmCallback) {
    await confirmCallback()
  }
  isConfirmVisible.value = false
}

// ESC 关闭
const handleKeydown = (e) => {
  if (e.key === 'Escape') {
    if (isConfirmVisible.value) {
      isConfirmVisible.value = false
    } else if (isDetailModalVisible.value) {
      isDetailModalVisible.value = false
    } else if (isSupplierModalVisible.value) {
      isSupplierModalVisible.value = false
    } else if (isCreateModalVisible.value) {
      isCreateModalVisible.value = false
    }
  }
}

const openDetailModal = (order) => {
  currentOrderDetail.value = order
  isDetailModalVisible.value = true
}

const parsedDetailItems = computed(() => {
  if (!currentOrderDetail.value?.items_json) return []
  try { return JSON.parse(currentOrderDetail.value.items_json) } catch (e) { return [] }
})

const cancelOrder = (id) => {
  showConfirm(
    '确认作废采购单',
    '作废后不可恢复，且不会增加库存。确定要作废该采购单吗？',
    async () => {
      try {
        const res = await apiFetch(`/api/purchase-orders/${id}/cancel`, { method: 'PUT' })
        if (res.ok) {
          showSuccessModal('🗑️ 采购单已作废')
          fetchOrders()
        } else {
          const err = await res.json()
          showSuccessModal(`❌ 失败: ${err.detail}`)
        }
      } catch (e) { showSuccessModal('❌ 网络异常') }
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
      // 如果当前页超出了总页数，退回到最后一页
      if (ordersCurrentPage.value > ordersTotalPages.value) {
        ordersCurrentPage.value = ordersTotalPages.value
      }
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
    '确认收货入库',
    '系统将增加库存并自动更新商品最新进价！确定收货吗？',
    async () => {
      try {
        const res = await apiFetch(`/api/purchase-orders/${id}/receive`, { method: 'POST' })
        if (res.ok) {
          showSuccessModal('✅ 收货成功')
          fetchOrders()
          await fetchParts()
          await fetchSuppliers()
        } else {
          const err = await res.json()
          showSuccessModal(`❌ 失败: ${err.detail}`)
        }
      } catch (e) { showSuccessModal('❌ 网络异常') }
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
  if (!newSupplierForm.value.name.trim()) return showSuccessModal('❌ 请填写供应商名称')
  isSavingSupplier.value = true
  try {
    const res = await apiFetch('/api/suppliers', { method: 'POST', body: JSON.stringify(newSupplierForm.value) })
    if (res.ok) {
      const data = await res.json()
      showSuccessModal('✅ 供应商创建成功')
      await fetchSuppliers()
      poForm.value.supplier_name = data.name
      isSupplierModalVisible.value = false
    } else {
      const err = await res.json()
      showSuccessModal(`❌ 创建失败: ${err.detail}`)
    }
  } catch (e) { showSuccessModal('❌ 网络异常') } finally { isSavingSupplier.value = false }
}

const submitPO = async () => {
  const finalSupplierName = poForm.value.supplier_name.trim() || '默认供应商 / 散客'
  const validItems = poForm.value.items.filter(i => i.oem && i.quantity > 0)
  if (validItems.length === 0) return showSuccessModal('❌ 请至少添加一个有效商品')

  isSubmittingPO.value = true
  try {
    const payload = {
      supplier_name: finalSupplierName,
      po_no: poForm.value.po_no.trim() || null,
      items: validItems.map(i => ({ oem: i.oem, name: i.name, brand: i.brand, quantity: Number(i.quantity), unit_price: Number(i.unit_price) }))
    }
    const res = await apiFetch('/api/purchase-orders', { method: 'POST', body: JSON.stringify(payload) })
    if (res.ok) {
      showSuccessModal('✅ 采购单创建成功')
      isCreateModalVisible.value = false
      fetchOrders()
      fetchSuppliers()
      fetchSuggestions()
    } else {
      const err = await res.json()
      showSuccessModal(`❌ 创建失败: ${err.detail}`)
    }
  } catch (e) { showSuccessModal('❌ 网络异常') } finally { isSubmittingPO.value = false }
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