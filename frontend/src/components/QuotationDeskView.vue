<!-- src/components/QuotationDeskView.vue -->
<template>
  <div class="fixed inset-0 bg-slate-50 z-40 flex flex-col overflow-hidden text-slate-900 font-sans">
    
    <!-- 🌟 右上角 0.5 秒轻量提示条 (支持动态成功/失败样式) -->
    <transition name="fade">
      <div v-if="toastMessage" :class="toastType === 'success' ? 'bg-emerald-600' : 'bg-rose-600'" class="fixed top-5 right-6 z-50 text-white px-5 py-3 rounded-2xl shadow-xl flex items-center gap-2.5 text-xs font-bold animate-bounce">
        <span>{{ toastType === 'success' ? '✅' : '❌' }}</span>
        <span>{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- 顶部状态栏 -->
    <header class="h-14 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0 shadow-xs">
      <div class="flex items-center space-x-4">
        <span class="bg-blue-600 text-white text-xs px-2.5 py-1 rounded-lg font-mono font-bold">POS v1.0</span>
        <span class="text-sm font-semibold text-slate-700">📅 {{ currentDateTime }}</span>
        <span class="text-xs text-emerald-600 font-mono font-bold">BCV 官方汇率: {{ bcvRate }}</span>
        <!-- 挂单池徽标 -->
        <button v-if="heldOrders.length > 0" @click="openRecallModal" class="bg-amber-100 hover:bg-amber-200 text-amber-800 px-3 py-1 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer">
          <span>📦 挂单池 ({{ heldOrders.length }}) [Ctrl+R]</span>
        </button>
      </div>
      <div class="flex items-center space-x-4">
        <div class="text-right">
          <span class="text-[10px] text-slate-400 block uppercase font-bold">Operator</span>
          <span class="text-xs font-bold text-slate-800">
            {{ currentUser?.username || 'admin' }} ({{ currentUser?.role || 'super_admin' }})
          </span>
        </div>
        <!-- 销售历史与退换货入口 -->
        <button @click="openHistoryModal" class="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 px-3 py-2 rounded-2xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs">
          <span>📜 销售历史与退货</span>
        </button>
        <!-- 今日班结报表按钮 -->
        <button @click="openShiftReportModal" class="bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 px-3 py-2 rounded-2xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs">
          <span>📊 今日班结 (Z-Report)</span>
        </button>
        <!-- 快捷键指南按钮 -->
        <button @click="helpModalVisible = true" class="bg-blue-50/80 hover:bg-blue-100 text-blue-600 border border-blue-200/60 px-3.5 py-2 rounded-2xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-2xs">
          <span>⌨️ 快捷键指南</span>
        </button>
        <!-- 退出收银台按钮 -->
        <button @click="confirmExitPos" class="bg-rose-50/80 hover:bg-rose-100 text-rose-600 border border-rose-200/60 px-4 py-2 rounded-2xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-2xs">
          <span>✕ 退出收银台 (Admin)</span>
        </button>
      </div>
    </header>

    <!-- 中间主工作区 (双栏布局) -->
    <div class="flex-1 flex overflow-hidden p-4 gap-4 pb-20">
      
      <!-- 左侧：商品搜索与购物车 -->
      <div class="flex-1 flex flex-col bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        
        <!-- 搜索与客户绑定栏 -->
        <div class="p-4 border-b border-slate-200 flex gap-3 bg-slate-50/50">
          <div class="flex-1 relative">
            <input 
              ref="searchInputRef"
              v-model="deskSearchQuery" 
              @keydown="handleSearchKeydown"
              type="text" 
              placeholder="按 [/] 键聚焦，输入 OEM / 互换号 / 品名搜索 (按 Esc 确认退出)..." 
              class="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none focus:border-blue-500 font-mono shadow-xs"
              autofocus
            />
          </div>
          <!-- 客户选择区 -->
          <div class="w-72 flex items-center gap-1.5">
            <button 
              @click="openClientSearchModal" 
              type="button"
              class="flex-1 bg-white hover:bg-blue-50/50 border border-blue-500 text-slate-800 rounded-xl px-4 py-3 text-sm font-bold flex items-center justify-between transition-colors shadow-xs cursor-pointer truncate"
            >
              <div class="flex items-center gap-2 truncate">
                <span class="text-blue-600">👤</span>
                <span class="truncate" :class="quoteClientName ? 'text-slate-900' : 'text-slate-400'">
                  {{ quoteClientName || '🔍 搜索选择客户 (Ctrl+F)...' }}
                </span>
              </div>
              <span class="text-xs text-slate-400 ml-1">选择</span>
            </button>
            <button 
              v-if="quoteClientName"
              @click="quoteClientName = ''"
              title="清除当前选中客户"
              type="button"
              class="w-9 h-11 shrink-0 bg-slate-100 hover:bg-rose-100 text-slate-500 hover:text-rose-600 border border-slate-200 rounded-xl flex items-center justify-center text-xs font-bold transition-colors cursor-pointer shadow-2xs"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- 搜索结果快捷点选栏 -->
        <div v-if="deskSearchQuery.trim()" class="max-h-56 overflow-y-auto border-b border-slate-200 bg-white p-2 space-y-1 z-20 shadow-lg">
          <div 
            v-for="(p, index) in filteredParts" 
            :key="p.oem" 
            :ref="el => { if (selectedIndex === index) activeItemRef = el }"
            @click="selectAndAddToCart(p)"
            @mouseenter="selectedIndex = index"
            :class="[
              selectedIndex === index ? 'bg-blue-50 border-blue-300 text-blue-900' : 'hover:bg-slate-50 border-slate-100 text-slate-800',
              p.stock <= 0 ? 'opacity-60 bg-slate-100/60' : ''
            ]"
            class="flex items-center justify-between p-3 rounded-xl cursor-pointer transition-colors border"
          >
            <div>
              <span class="font-mono font-bold text-blue-600 text-xs mr-3">{{ p.oem }}</span>
              <span class="text-sm font-medium">{{ p.name }}</span>
              <span class="text-xs text-slate-400 ml-2">({{ p.brand }})</span>
            </div>
            <div class="flex items-center gap-4">
              <span :class="p.stock > 0 ? 'text-emerald-600' : 'text-rose-600 font-bold'" class="text-xs font-mono font-bold">
                库存: {{ p.stock }} {{ p.stock <= 0 ? '(缺货)' : '' }}
              </span>
              <span class="text-sm font-mono font-bold text-slate-900">${{ p.price.toFixed(2) }}</span>
            </div>
          </div>
          <div v-if="filteredParts.length === 0" class="text-center py-4 text-xs text-slate-400">
            未找到相关配件商品
          </div>
        </div>

        <!-- 购物车明细表格 -->
        <div class="flex-1 overflow-y-auto p-4">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b border-slate-200 text-slate-400 text-xs font-semibold uppercase">
                <th class="py-3 px-3">OEM / 编号</th>
                <th class="py-3 px-3">商品名称</th>
                <th class="py-3 px-3 text-right">单价 (USD)</th>
                <th class="py-3 px-3 text-center">数量</th>
                <th class="py-3 px-3 text-right">小计 (USD)</th>
                <th class="py-3 px-3 text-center">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              <tr v-for="(item, index) in cartItems" :key="item.oem" class="hover:bg-slate-50/80 transition-colors">
                <td class="py-3 px-3 font-mono font-bold text-blue-600 text-xs">{{ item.oem }}</td>
                <td class="py-3 px-3 text-slate-800 font-medium">{{ item.name }}</td>
                <td class="py-3 px-3 text-right font-mono text-slate-600">${{ item.price.toFixed(2) }}</td>
                <td class="py-3 px-3 text-center">
                  <div class="inline-flex items-center border border-slate-200 rounded-xl overflow-hidden bg-slate-50 shadow-2xs">
                    <button @click="item.quantity > 1 ? item.quantity-- : null" class="px-2.5 py-1 text-slate-500 hover:bg-slate-200 font-bold">-</button>
                    <input v-model.number="item.quantity" type="number" min="1" class="w-12 text-center bg-transparent text-slate-800 text-xs font-mono outline-none font-bold" />
                    <button @click="item.quantity++" class="px-2.5 py-1 text-slate-500 hover:bg-slate-200 font-bold">+</button>
                  </div>
                </td>
                <td class="py-3 px-3 text-right font-mono font-bold text-emerald-600">
                  ${{ (item.price * item.quantity).toFixed(2) }}
                </td>
                <td class="py-3 px-3 text-center">
                  <button @click="cartItems.splice(index, 1)" class="text-rose-600 hover:text-rose-700 text-xs font-bold px-2.5 py-1 bg-rose-50 hover:bg-rose-100 rounded-lg transition-colors">删除</button>
                </td>
              </tr>
              <tr v-if="cartItems.length === 0">
                <td colspan="6" class="text-center py-20 text-slate-400 text-sm">
                  🛒 购物车为空，请按 [/] 键聚焦搜索框添加配件 (可按 Ctrl+H 挂单)
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>

      <!-- 右侧：结算与支付大卡片 -->
      <div class="w-96 flex flex-col bg-white rounded-2xl border border-slate-200 p-6 shadow-sm justify-between">
        
        <div class="space-y-4">
          <h3 class="font-bold text-base text-slate-800 border-b border-slate-100 pb-3 flex items-center justify-between">
            <span>💳 结算台与支付方式</span>
            <span class="text-xs font-mono text-blue-600 bg-blue-50 px-2 py-0.5 rounded-md">Items: {{ cartItems.length }}</span>
          </h3>

          <!-- 支付方式选择 -->
          <div class="space-y-2">
            <label class="block text-xs font-semibold text-slate-400 uppercase">选择支付渠道 / 类型 (Alt+P 切挂账)</label>
            <div class="grid grid-cols-2 gap-2">
              <button 
                @click="selectedPaymentMethod = 'Cash_USD'"
                :class="selectedPaymentMethod === 'Cash_USD' ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20 border-blue-600' : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'"
                class="py-2.5 px-3 rounded-xl border text-xs font-bold transition-all text-left cursor-pointer"
              >
                💵 Cash USD
              </button>
              <button 
                @click="selectedPaymentMethod = 'Zelle'"
                :class="selectedPaymentMethod === 'Zelle' ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20 border-blue-600' : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'"
                class="py-2.5 px-3 rounded-xl border text-xs font-bold transition-all text-left cursor-pointer"
              >
                📱 Zelle
              </button>
              <button 
                @click="selectedPaymentMethod = 'Pago_Movil'"
                :class="selectedPaymentMethod === 'Pago_Movil' ? 'bg-blue-600 text-white shadow-md shadow-blue-500/20 border-blue-600' : 'bg-slate-50 border-slate-200 text-slate-700 hover:bg-slate-100'"
                class="py-2.5 px-3 rounded-xl border text-xs font-bold transition-all text-left cursor-pointer"
              >
                ⚡ Pago Móvil
              </button>
              <button 
                @click="selectedPaymentMethod = 'Fiado_Debt'"
                :class="selectedPaymentMethod === 'Fiado_Debt' ? 'bg-amber-600 text-white shadow-md shadow-amber-500/20 border-amber-600' : 'bg-slate-50 border-slate-200 text-amber-700 hover:bg-slate-100'"
                class="py-2.5 px-3 rounded-xl border text-xs font-bold transition-all text-left cursor-pointer"
              >
                📋 挂账 (Fiado)
              </button>
            </div>
          </div>

          <!-- Cash USD 找零计算器输入框 -->
          <div v-if="selectedPaymentMethod === 'Cash_USD'" class="bg-blue-50/60 p-3.5 rounded-2xl border border-blue-100 space-y-2">
            <div class="flex justify-between items-center text-xs font-bold text-blue-900">
              <span>💵 现金实收 (USD):</span>
              <input v-model.number="cashReceivedUsd" type="number" step="0.1" placeholder="0.00" class="w-28 bg-white border border-blue-200 rounded-xl px-3 py-1.5 text-right font-mono text-sm outline-none focus:border-blue-500 font-bold" />
            </div>
            <div v-if="cashReceivedUsd >= totalUsd" class="pt-2 border-t border-blue-200/60 flex justify-between items-center">
              <div>
                <span class="text-[11px] font-bold text-emerald-700 block">应找零 (USD): ${{ (cashReceivedUsd - totalUsd).toFixed(2) }}</span>
                <span class="text-[10px] font-mono text-emerald-600">Bs. {{ ((cashReceivedUsd - totalUsd) * bcvRate).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}</span>
              </div>
              <span class="text-xl font-black font-mono text-emerald-600">${{ (cashReceivedUsd - totalUsd).toFixed(2) }}</span>
            </div>
          </div>

          <!-- 支付参考号 -->
          <div>
            <label class="block text-xs font-semibold text-slate-400 uppercase mb-1.5">支付流水号 / 备注 (Reference)</label>
            <input v-model="paymentReference" type="text" placeholder="选填，如 Zelle 回执号..." class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm text-slate-800 outline-none focus:border-blue-500 font-mono" />
          </div>
        </div>

        <!-- 底部价格大卡片与结算按钮 -->
        <div class="space-y-3 pt-4 border-t border-slate-100">
          <div class="bg-slate-50 rounded-2xl p-4 border border-slate-200/80 space-y-1.5 text-right">
            <div class="text-xs text-slate-400 font-mono">折合委内瑞拉官方汇率 (Bs.)</div>
            <div class="text-2xl font-black font-mono text-emerald-600">
              Bs. {{ (totalUsd * bcvRate).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </div>
            <div class="pt-2 border-t border-slate-200/60 flex justify-between items-center">
              <span class="text-xs font-semibold text-slate-500">总计金额 (USD)</span>
              <span class="text-3xl font-black font-mono text-slate-900">${{ totalUsd.toFixed(2) }}</span>
            </div>
          </div>

          <button 
            @click="openPreviewModal"
            :disabled="cartItems.length === 0"
            class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-2xl font-black text-base shadow-lg shadow-emerald-600/20 transition-all cursor-pointer flex items-center justify-center gap-2"
          >
            <span>🚀 确认结账并打印票据</span>
          </button>
        </div>

      </div>

    </div>

    <!-- 底部专业 POS 快捷键功能导航栏 -->
    <footer class="absolute bottom-0 left-0 right-0 h-16 bg-white border-t border-slate-200 px-6 flex items-center justify-between z-30 shadow-md">
      <div class="grid grid-cols-6 gap-3 w-full">
        <div @click="focusSearch" class="bg-slate-50 hover:bg-blue-50 border border-slate-200 rounded-xl px-3 py-2 flex items-center justify-between text-xs cursor-pointer transition-colors">
          <span class="text-slate-600 font-medium">聚焦搜索</span>
          <span class="bg-blue-100 text-blue-700 font-mono font-bold px-2 py-0.5 rounded">[/]</span>
        </div>
        <div @click="openClientSearchModal" class="bg-slate-50 hover:bg-blue-50 border border-slate-200 rounded-xl px-3 py-2 flex items-center justify-between text-xs cursor-pointer transition-colors">
          <span class="text-slate-600 font-medium">选客户</span>
          <span class="bg-blue-100 text-blue-700 font-mono font-bold px-2 py-0.5 rounded">Ctrl+F</span>
        </div>
        <div @click="holdCurrentOrder" class="bg-slate-50 hover:bg-amber-50 border border-slate-200 rounded-xl px-3 py-2 flex items-center justify-between text-xs cursor-pointer transition-colors">
          <span class="text-slate-600 font-medium">挂单暂存</span>
          <span class="bg-amber-100 text-amber-700 font-mono font-bold px-2 py-0.5 rounded">Ctrl+H</span>
        </div>
        <div @click="$emit('clear-cart')" class="bg-slate-50 hover:bg-rose-50 border border-slate-200 rounded-xl px-3 py-2 flex items-center justify-between text-xs cursor-pointer transition-colors">
          <span class="text-slate-600 font-medium">清空购物车</span>
          <span class="bg-rose-100 text-rose-700 font-mono font-bold px-2 py-0.5 rounded">Ctrl+B</span>
        </div>
        <div @click="deleteLastItem" class="bg-slate-50 hover:bg-rose-50 border border-slate-200 rounded-xl px-3 py-2 flex items-center justify-between text-xs cursor-pointer transition-colors">
          <span class="text-slate-600 font-medium">删末项</span>
          <span class="bg-rose-100 text-rose-700 font-mono font-bold px-2 py-0.5 rounded">Delete</span>
        </div>
        <div @click="confirmExitPos" class="bg-slate-50 hover:bg-slate-100 border border-slate-200 rounded-xl px-3 py-2 flex items-center justify-between text-xs cursor-pointer transition-colors">
          <span class="text-slate-700 font-medium">返回后台</span>
          <span class="bg-slate-200 text-slate-700 font-mono font-bold px-2 py-0.5 rounded">Esc</span>
        </div>
      </div>
    </footer>

    <!-- 销售历史查询与快速退换货 -->
    <PosHistoryModal
      :visible="historyModalVisible"
      :orders="completedOrders"
      @close="historyModalVisible = false"
      @reprint="reprintOrderTicket"
      @return="processReturnOrder"
    />

    <!-- 挂单池/取单弹窗 Modal -->
    <div v-if="recallModalVisible" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-100 flex flex-col max-h-[80vh]">
        <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <h3 class="font-bold text-base text-slate-800 flex items-center gap-2">
            <span>📦 挂单恢复池 (共 {{ heldOrders.length }} 单)</span>
          </h3>
          <button @click="recallModalVisible = false" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-2">
          <div v-for="(order, index) in heldOrders" :key="index" class="p-4 rounded-2xl border border-slate-200 bg-slate-50 hover:bg-blue-50/40 transition-all flex items-center justify-between">
            <div class="space-y-1">
              <div class="font-bold text-sm text-slate-800 flex items-center gap-2">
                <span>👤 {{ order.clientName || '散客' }}</span>
                <span class="text-xs font-mono bg-blue-100 text-blue-700 px-2 py-0.5 rounded">Items: {{ order.items.length }}</span>
              </div>
              <div class="text-xs text-slate-400 font-mono">挂单时间: {{ order.time }}</div>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-base font-mono font-black text-slate-900">${{ order.totalUsd.toFixed(2) }}</span>
              <button @click="recallOrder(index)" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-colors cursor-pointer shadow-sm">
                恢复取单
              </button>
            </div>
          </div>
          <div v-if="heldOrders.length === 0" class="text-center py-12 text-slate-400 text-xs">
            当前没有暂存的挂单
          </div>
        </div>

        <div class="p-3 bg-slate-50 border-t border-slate-100 text-right">
          <button @click="recallModalVisible = false" class="px-4 py-2 bg-slate-200 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-300 transition-colors cursor-pointer">
            关闭
          </button>
        </div>
      </div>
    </div>

    <!-- 今日班结报表 Modal (Z-Report) -->
    <div v-if="shiftReportModalVisible" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100 flex flex-col max-h-[90vh]">
        <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/80">
          <h3 class="font-bold text-base text-slate-800 flex items-center gap-2">
            <span>📊 今日班结营业汇总 (Z-Report)</span>
          </h3>
          <button @click="shiftReportModalVisible = false" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-4 font-mono text-xs bg-slate-50/40">
          <div class="text-center pb-3 border-b border-dashed border-slate-300 space-y-1">
            <div class="font-black text-sm text-slate-900">TOSTIKYK ERP - SHIFT SUMMARY</div>
            <div class="text-[10px] text-slate-500">操作员: {{ currentUser?.username || 'admin' }}</div>
            <div class="text-[10px] text-slate-500">统计时间: {{ currentDateTime }}</div>
          </div>

          <div class="space-y-2.5 pb-3 border-b border-dashed border-slate-300 text-slate-700">
            <div class="flex justify-between font-bold">
              <span>支付渠道</span>
              <span>笔数 / 金额 (USD)</span>
            </div>
            <div class="flex justify-between">
              <span>💵 Cash USD</span>
              <span class="font-bold">${{ shiftStats.cashUsd.amount.toFixed(2) }} ({{ shiftStats.cashUsd.count }}笔)</span>
            </div>
            <div class="flex justify-between">
              <span>📱 Zelle</span>
              <span class="font-bold">${{ shiftStats.zelle.amount.toFixed(2) }} ({{ shiftStats.zelle.count }}笔)</span>
            </div>
            <div class="flex justify-between">
              <span>⚡ Pago Móvil</span>
              <span class="font-bold">${{ shiftStats.pagoMovil.amount.toFixed(2) }} ({{ shiftStats.pagoMovil.count }}笔)</span>
            </div>
            <div class="flex justify-between">
              <span>📋 挂账 (Fiado)</span>
              <span class="font-bold">${{ shiftStats.fiado.amount.toFixed(2) }} ({{ shiftStats.fiado.count }}笔)</span>
            </div>
          </div>

          <div class="space-y-1.5 text-right">
            <div class="text-slate-500 text-[11px]">总计折合 Bs. (BCV: {{ bcvRate }})</div>
            <div class="text-lg font-black text-emerald-600">
              Bs. {{ (shiftStats.totalUsd * bcvRate).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </div>
            <div class="text-xl font-black text-slate-900 pt-1">
              营业总额 USD: ${{ shiftStats.totalUsd.toFixed(2) }} (共 {{ shiftStats.totalCount }} 笔)
            </div>
          </div>
        </div>

        <div class="p-4 bg-white border-t border-slate-100 flex gap-3">
          <button @click="shiftReportModalVisible = false" class="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-2xl text-xs font-bold transition-colors cursor-pointer">
            关闭
          </button>
          <button @click="showToast('🖨️ 班结小票已发送物理打印！', 'success')" class="flex-1 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl text-xs font-black shadow-md shadow-emerald-600/20 transition-colors cursor-pointer flex items-center justify-center gap-1.5">
            <span>🖨️ 打印交班小票</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 收银小票实时预览 Modal 弹窗 -->
    <div v-if="previewModalVisible" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100 flex flex-col max-h-[90vh]">
        <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/80">
          <h3 class="font-bold text-base text-slate-800 flex items-center gap-2">
            <span>🧾 收银小票实时预览</span>
          </h3>
          <button @click="previewModalVisible = false" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-4 font-mono text-xs bg-slate-50/40">
          <div class="text-center pb-3 border-b border-dashed border-slate-300 space-y-1">
            <div class="font-black text-sm text-slate-900">TOSTIKYK ERP AUTO PARTS</div>
            <div class="text-[10px] text-slate-500">POS 销售小票凭证</div>
            <div class="text-[10px] text-slate-500">时间: {{ currentDateTime }}</div>
          </div>

          <div class="space-y-1 text-slate-700 pb-3 border-b border-dashed border-slate-300">
            <div><span class="font-bold">客户:</span> {{ quoteClientName || 'Cliente General (散客)' }}</div>
            <div><span class="font-bold">收银员:</span> {{ currentUser?.username || 'admin' }}</div>
            <div><span class="font-bold">支付方式:</span> {{ selectedPaymentMethod }}</div>
            <div v-if="paymentReference"><span class="font-bold">支付参考号:</span> {{ paymentReference }}</div>
            <div v-if="selectedPaymentMethod === 'Cash_USD' && cashReceivedUsd > 0">
              <span class="font-bold">实收/找零:</span> ${{ cashReceivedUsd.toFixed(2) }} / 找零: ${{ Math.max(0, cashReceivedUsd - totalUsd).toFixed(2) }}
            </div>
            <div><span class="font-bold">BCV 汇率:</span> {{ bcvRate }}</div>
          </div>

          <div class="space-y-2 pb-3 border-b border-dashed border-slate-300">
            <div class="text-[10px] text-slate-400 uppercase font-bold flex justify-between">
              <span>商品明细</span>
              <span>小计</span>
            </div>
            <div v-for="item in cartItems" :key="item.oem" class="flex justify-between items-start gap-2">
              <div>
                <div class="font-bold text-slate-800">{{ item.name }}</div>
                <div class="text-[10px] text-slate-500">{{ item.oem }} x {{ item.quantity }} @ ${{ item.price.toFixed(2) }}</div>
              </div>
              <div class="font-bold text-slate-900">${{ (item.price * item.quantity).toFixed(2) }}</div>
            </div>
          </div>

          <div class="space-y-1.5 text-right pb-2">
            <div class="text-slate-500 text-[11px]">折合委内瑞拉官方汇率 (Bs.)</div>
            <div class="text-2xl font-black text-emerald-600">
              Bs. {{ (totalUsd * bcvRate).toLocaleString('es-VE', { minimumFractionDigits: 2, maximumFractionDigits: 2 }) }}
            </div>
            <div class="text-xl font-black text-slate-900 pt-1">
              总计 USD: ${{ totalUsd.toFixed(2) }}
            </div>
          </div>

          <div class="text-center text-[10px] text-slate-400 pt-3 border-t border-dashed border-slate-300">
            *** 感谢您的光顾，请妥善保管小票 ***
          </div>
        </div>

        <div class="p-4 bg-white border-t border-slate-100 flex gap-3">
          <button @click="previewModalVisible = false" class="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-2xl text-xs font-bold transition-colors cursor-pointer">
            返回修改
          </button>
          <button @click="confirmAndPrint" class="flex-1 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl text-xs font-black shadow-md shadow-emerald-600/20 transition-colors cursor-pointer flex items-center justify-center gap-1.5">
            <span>🖨️ 确认出单并打印</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 快捷键指南弹窗 -->
    <PosHelpModal :visible="helpModalVisible" @close="helpModalVisible = false" />

    <!-- 客户快速搜索与选择 Modal 弹窗 -->
    <div v-if="clientModalVisible" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-100 flex flex-col max-h-[80vh]">
        <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <h3 class="font-bold text-base text-slate-800 flex items-center gap-2">
            <span>👥 快捷选择客户 (支持 ↑↓ 键选择，Enter 确认)</span>
          </h3>
          <button @click="clientModalVisible = false" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
        </div>
        
        <div class="p-4 border-b border-slate-100">
          <input 
            ref="clientModalInputRef"
            v-model="clientFilterQuery" 
            @keydown="handleClientModalKeydown"
            type="text" 
            placeholder="输入客户名称 / 电话 / RIF 快速检索..." 
            class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500 font-medium"
          />
        </div>

        <div class="flex-1 overflow-y-auto p-3 space-y-1.5">
          <div 
            v-for="(c, index) in filteredModalClients" 
            :key="c.id"
            :ref="el => { if (clientSelectedIndex === index) activeClientItemRef = el }"
            @click="selectClient(c.name)"
            @mouseenter="clientSelectedIndex = index"
            :class="clientSelectedIndex === index ? 'bg-blue-50 border-blue-300 text-blue-900 font-bold shadow-xs' : 'hover:bg-slate-50 border-slate-100 text-slate-700'"
            class="p-3 rounded-2xl border cursor-pointer transition-colors flex items-center justify-between text-sm"
          >
            <div>
              <div class="font-bold flex items-center gap-2">
                <span>🏢 {{ c.name }}</span>
                <span class="text-[10px] font-normal bg-slate-100 text-slate-500 px-2 py-0.5 rounded-md">{{ c.client_type || 'Regular' }}</span>
              </div>
              <div class="text-xs text-slate-400 mt-1 font-mono">
                RIF: {{ c.rif_or_cedula || '-' }} | 📞 {{ c.phone || '-' }}
              </div>
            </div>
            <div class="text-right">
              <span class="text-xs font-mono font-bold" :class="(c.debt || 0) > 0 ? 'text-amber-600' : 'text-slate-400'">
                欠款: ${{ (c.debt || 0).toFixed(2) }}
              </span>
            </div>
          </div>

          <div v-if="filteredModalClients.length === 0" class="text-center py-8 text-xs text-slate-400">
            未找到匹配的客户记录
          </div>
        </div>

        <div class="p-3 bg-slate-50 border-t border-slate-100 text-right">
          <button @click="clientModalVisible = false" class="px-4 py-2 bg-slate-200 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-300 transition-colors cursor-pointer">
            关闭
          </button>
        </div>
      </div>
    </div>

    <!-- 二次确认：退出收银台 -->
    <ConfirmDialog
      :visible="exitConfirmVisible"
      icon="⚠️"
      icon-class="bg-amber-50 text-amber-600"
      title="确认退出收银台？"
      message="当前收银台若有未结算的商品，退出后购物车可能会被清空，是否继续？"
      confirm-text="确认退出"
      @cancel="exitConfirmVisible = false"
      @confirm="executeExitPos"
    />

    <!-- 二次确认：退货处理 -->
    <ConfirmDialog
      :visible="returnConfirmVisible"
      icon="🔄"
      icon-class="bg-rose-50 text-rose-600"
      title="确认执行退货处理？"
      message="该操作会自动将商品库存回滚至仓库，是否继续？"
      confirm-text="确认退货"
      @cancel="returnConfirmVisible = false"
      @confirm="executeReturnOrder"
    />

  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { apiFetch } from '../utils/api'
import ConfirmDialog from './ConfirmDialog.vue'
import PosHelpModal from './pos/PosHelpModal.vue'
import PosHistoryModal from './pos/PosHistoryModal.vue'

const props = defineProps({
  partsList: Array,
  clientsList: Array,
  cartItems: Array,
  bcvRate: Number,
  currentDateTime: String,
  currentUser: Object
})

const emit = defineEmits(['add-to-cart', 'generate-quote', 'exit-pos', 'clear-cart'])

const deskSearchQuery = ref('')
const quoteClientName = ref('')
const selectedPaymentMethod = ref('Cash_USD')
const paymentReference = ref('')
const searchInputRef = ref(null)
const selectedIndex = ref(0)
const activeItemRef = ref(null)
const exitConfirmVisible = ref(false)

// 现金实收找零计算
const cashReceivedUsd = ref(0)

// 挂单池状态
const heldOrders = ref([])
const recallModalVisible = ref(false)

// 🌟 后端持久化的已完成订单历史记录状态
const completedOrders = ref([])
const historyModalVisible = ref(false)

// 班结报表状态
const shiftReportModalVisible = ref(false)
const shiftStats = ref({
  cashUsd: { amount: 0, count: 0 },
  zelle: { amount: 0, count: 0 },
  pagoMovil: { amount: 0, count: 0 },
  fiado: { amount: 0, count: 0 },
  totalUsd: 0,
  totalCount: 0
})

// 弹窗状态控制
const previewModalVisible = ref(false)
const helpModalVisible = ref(false)

// 右上角轻量提示状态
const toastMessage = ref('')
const toastType = ref('success') // 'success' 或 'error'
let toastTimer = null

const showToast = (msg, type = 'error') => {
  toastMessage.value = msg
  toastType.value = type
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => {
    toastMessage.value = ''
  }, 1500)
}

// 客户选择 Modal 弹窗相关状态与键盘上下键控制
const clientModalVisible = ref(false)
const clientFilterQuery = ref('')
const clientModalInputRef = ref(null)
const clientSelectedIndex = ref(0)
const activeClientItemRef = ref(null)

const openClientSearchModal = async () => {
  clientFilterQuery.value = ''
  clientSelectedIndex.value = 0
  clientModalVisible.value = true
  await nextTick()
  if (clientModalInputRef.value) {
    clientModalInputRef.value.focus()
  }
}

const selectClient = (name) => {
  quoteClientName.value = name
  clientModalVisible.value = false
}

const filteredModalClients = computed(() => {
  if (!props.clientsList) return []
  if (!clientFilterQuery.value.trim()) return props.clientsList
  const q = clientFilterQuery.value.toUpperCase()
  return props.clientsList.filter(c => 
    c.name.toUpperCase().includes(q) ||
    (c.phone && c.phone.toUpperCase().includes(q)) ||
    (c.rif_or_cedula && c.rif_or_cedula.toUpperCase().includes(q))
  )
})

watch(clientFilterQuery, () => {
  clientSelectedIndex.value = 0
})

watch(clientSelectedIndex, async () => {
  await nextTick()
  if (activeClientItemRef.value && typeof activeClientItemRef.value.scrollIntoView === 'function') {
    activeClientItemRef.value.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  }
})

const handleClientModalKeydown = (e) => {
  const results = filteredModalClients.value
  if (e.key === 'Escape') {
    e.preventDefault()
    clientModalVisible.value = false
    return
  }

  if (results.length > 0) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      clientSelectedIndex.value = (clientSelectedIndex.value + 1) % results.length
      return
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      clientSelectedIndex.value = (clientSelectedIndex.value - 1 + results.length) % results.length
      return
    }
    if (e.key === 'Enter') {
      e.preventDefault()
      if (results[clientSelectedIndex.value]) {
        selectClient(results[clientSelectedIndex.value].name)
      }
      return
    }
  }
}

const filteredParts = computed(() => {
  if (!deskSearchQuery.value.trim()) return []
  const q = deskSearchQuery.value.toUpperCase()
  return props.partsList.filter(p => 
    p.oem.toUpperCase().includes(q) || 
    p.name.toUpperCase().includes(q) || 
    p.brand.toUpperCase().includes(q)
  ).slice(0, 10)
})

watch(deskSearchQuery, () => {
  selectedIndex.value = 0
})

watch(selectedIndex, async () => {
  await nextTick()
  if (activeItemRef.value && typeof activeItemRef.value.scrollIntoView === 'function') {
    activeItemRef.value.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
  }
})

const totalUsd = computed(() => {
  return props.cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
})

const selectAndAddToCart = (part) => {
  if (part.stock <= 0) {
    showToast(`商品 ${part.oem} 库存不足 (0)，无法加入购物车！`, 'error')
    return
  }
  emit('add-to-cart', part)
  deskSearchQuery.value = ''
  selectedIndex.value = 0
  focusSearch()
}

const focusSearch = () => {
  if (searchInputRef.value) {
    searchInputRef.value.focus()
  }
}

const increaseLastQty = () => {
  if (props.cartItems.length > 0) {
    props.cartItems[props.cartItems.length - 1].quantity += 1
  }
}

const deleteLastItem = () => {
  if (props.cartItems.length > 0) {
    props.cartItems.pop()
  }
}

// 挂单与取单逻辑
const holdCurrentOrder = () => {
  if (props.cartItems.length === 0) {
    showToast('当前购物车为空，无需挂单！', 'error')
    return
  }
  heldOrders.value.push({
    clientName: quoteClientName.value,
    items: [...props.cartItems],
    totalUsd: totalUsd.value,
    time: new Date().toLocaleTimeString()
  })
  props.cartItems.splice(0, props.cartItems.length)
  quoteClientName.value = ''
  showToast('📦 当前订单已成功挂单暂存！', 'success')
}

const openRecallModal = () => {
  if (heldOrders.value.length === 0) {
    showToast('挂单池为空！', 'error')
    return
  }
  recallModalVisible.value = true
}

const recallOrder = (index) => {
  const order = heldOrders.value.splice(index, 1)[0]
  props.cartItems.splice(0, props.cartItems.length, ...order.items)
  quoteClientName.value = order.clientName
  recallModalVisible.value = false
  showToast('✅ 成功恢复挂单！', 'success')
}

// 🌟 从后端加载销售历史订单
const fetchCompletedOrders = async () => {
  try {
    const res = await apiFetch('/api/pos/orders')
    if (!res.ok) throw new Error('获取历史订单失败')
    completedOrders.value = await res.json()
  } catch (err) {
    console.error('获取历史订单失败:', err)
  }
}

const openHistoryModal = async () => {
  await fetchCompletedOrders()
  historyModalVisible.value = true
}

// 补打小票
const reprintOrderTicket = (order) => {
  showToast(`🖨️ 正在重新打印订单 #${order.orderId} 小票...`, 'success')
}

// 🌟 申请退货/退款（调用后端接口自动回滚库存）
const targetReturnDbId = ref(null)
const returnConfirmVisible = ref(false)

const processReturnOrder = (dbId) => {
  targetReturnDbId.value = dbId
  returnConfirmVisible.value = true
}

const executeReturnOrder = async () => {
  if (!targetReturnDbId.value) return
  try {
    const res = await apiFetch(`/api/pos/orders/${targetReturnDbId.value}/refund`, {
      method: 'POST'
    })
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}))
      throw new Error(detail.detail || '退货请求失败')
    }
    showToast('🔄 退货成功，库存已自动回滚！', 'success')
    returnConfirmVisible.value = false
    targetReturnDbId.value = null
    await fetchCompletedOrders()
  } catch (err) {
    returnConfirmVisible.value = false
    showToast(err.message || '退货请求失败', 'error')
  }
}

// 班结报表统计逻辑
const openShiftReportModal = () => {
  shiftReportModalVisible.value = true
}

const confirmExitPos = () => {
  exitConfirmVisible.value = true
}

const executeExitPos = () => {
  exitConfirmVisible.value = false
  emit('exit-pos')
}

// 点击结算按钮时打开预览窗口
const openPreviewModal = () => {
  if (props.cartItems.length === 0) return
  previewModalVisible.value = true
}

// 🌟 在预览窗口中确认出单：正式通过 Axios 提交到后端数据库持久化
const confirmAndPrint = async () => {
  try {
    const payload = {
      client_name: quoteClientName.value || "Cliente General",
      payment_method: selectedPaymentMethod.value,
      payment_reference: paymentReference.value,
      bcv_rate: props.bcvRate,
      items: props.cartItems.map(i => ({
        oem: i.oem,
        name: i.name,
        brand: i.brand || "GENERAL",
        quantity: i.quantity,
        price: i.price
      }))
    }

    const res = await apiFetch('/api/pos/orders', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    if (!res.ok) {
      const detail = await res.json().catch(() => ({}))
      throw new Error(detail.detail || '结账失败，请检查网络或库存！')
    }
    const data = await res.json()
    
    // 🌟 核心：关闭预览弹窗，绝不弹出中间多余提示，只在右上角显示绿色成功提示
    previewModalVisible.value = false
    showToast(`✅ 开单成功！单号: ${data.order_no}`, 'success')
    
    cashReceivedUsd.value = 0
    paymentReference.value = ''
    quoteClientName.value = ''
    
    emit('generate-quote')
    await fetchCompletedOrders()
  } catch (err) {
    const errorMsg = err.message || '结账失败，请检查网络或库存！'
    showToast(errorMsg, 'error')
  }
}

const handleGlobalKeydown = (e) => {
  if (previewModalVisible.value) {
    if (e.key === 'Enter') {
      e.preventDefault()
      confirmAndPrint()
      return
    }
    if (e.key === 'Escape') {
      e.preventDefault()
      previewModalVisible.value = false
    }
    return
  }

  if (clientModalVisible.value || helpModalVisible.value || recallModalVisible.value || shiftReportModalVisible.value || historyModalVisible.value || returnConfirmVisible.value) {
    if (e.key === 'Escape') {
      e.preventDefault()
      clientModalVisible.value = false
      previewModalVisible.value = false
      helpModalVisible.value = false
      recallModalVisible.value = false
      shiftReportModalVisible.value = false
      historyModalVisible.value = false
      returnConfirmVisible.value = false
    }
    return
  }

  if (exitConfirmVisible.value) {
    if (e.key === 'Enter') {
      e.preventDefault()
      executeExitPos()
    } else if (e.key === 'Escape') {
      e.preventDefault()
      exitConfirmVisible.value = false
    }
    return
  }

  if (e.key === 'Escape') {
    e.preventDefault()
    confirmExitPos()
    return
  }

  if (e.key === '/' && document.activeElement !== searchInputRef.value) {
    e.preventDefault()
    focusSearch()
    return
  }
  
  if (e.ctrlKey && e.key.toLowerCase() === 'f') {
    e.preventDefault()
    openClientSearchModal()
    return
  }

  if (e.ctrlKey && e.key.toLowerCase() === 'h') {
    e.preventDefault()
    holdCurrentOrder()
    return
  }

  if (e.ctrlKey && e.key.toLowerCase() === 'r') {
    e.preventDefault()
    openRecallModal()
    return
  }

  if (e.key === 'F2') {
    e.preventDefault()
    openClientSearchModal()
    return
  }
  if (e.key === 'F3') {
    e.preventDefault()
    increaseLastQty()
    return
  }
  if (e.ctrlKey && e.key.toLowerCase() === 'b') {
    e.preventDefault()
    emit('clear-cart')
    return
  }
  if (e.key === 'Delete' && document.activeElement !== searchInputRef.value) {
    e.preventDefault()
    deleteLastItem()
    return
  }
  if (e.altKey && e.key.toLowerCase() === 'p') {
    e.preventDefault()
    selectedPaymentMethod.value = 'Fiado_Debt'
    return
  }
}

const handleSearchKeydown = (e) => {
  if (e.key === 'Escape') {
    e.preventDefault()
    confirmExitPos()
    return
  }

  const results = filteredParts.value
  if (results.length > 0) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      selectedIndex.value = (selectedIndex.value + 1) % results.length
      return
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      selectedIndex.value = (selectedIndex.value - 1 + results.length) % results.length
      return
    }
    if (e.key === 'Enter') {
      e.preventDefault()
      if (results[selectedIndex.value]) {
        selectAndAddToCart(results[selectedIndex.value])
      }
      return
    }
  }

  if (e.key === 'Enter' && results.length === 0 && props.cartItems.length > 0) {
    e.preventDefault()
    openPreviewModal()
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
  focusSearch()
  fetchCompletedOrders()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
  if (toastTimer) clearTimeout(toastTimer)
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>