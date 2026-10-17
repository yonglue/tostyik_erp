<!-- src/components/QuotationDeskView.vue -->
<template>
  <div class="fixed inset-0 bg-slate-50 z-40 flex flex-col overflow-hidden text-slate-900 font-sans">
    
    <!-- 右上角提示条 -->
    <transition name="fade">
      <div v-if="toastMessage" :class="toastType === 'success' ? 'bg-emerald-600' : 'bg-rose-600'" class="fixed top-5 right-6 z-50 text-white px-5 py-3 rounded-2xl shadow-xl flex items-center gap-2.5 text-xs font-bold animate-bounce">
        <span>{{ toastType === 'success' ? '✅' : '❌' }}</span>
        <span>{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- 顶部状态栏 -->
    <header class="h-16 bg-white border-b border-slate-200 px-6 flex items-center justify-between shrink-0 shadow-xs">
      <div class="flex items-center space-x-4">
        <span class="bg-blue-600 text-white text-xs px-2.5 py-1 rounded-lg font-mono font-bold">POS v2.9 (Dual View)</span>
        <span class="text-sm font-semibold text-slate-700">📅 {{ currentDateTime }}</span>
        <span class="text-xs text-emerald-600 font-mono font-bold">{{ t.bcvLabel }}: {{ bcvRate }}</span>
        
        <button v-if="heldOrders.length > 0" @click="openRecallModal" class="bg-amber-100 hover:bg-amber-200 text-amber-800 px-3 py-1 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer">
          <span>📦 云端挂单池 ({{ heldOrders.length }}) [Ctrl+R]</span>
        </button>
      </div>
      
      <div class="flex items-center space-x-3">
        <button @click="openHistoryModal" class="bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200 px-3.5 py-2 rounded-2xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs">
          <span>📜 销售历史与退货</span>
        </button>
        <button @click="openShiftReportModal" class="bg-emerald-50 hover:bg-emerald-100 text-emerald-700 border border-emerald-200 px-3.5 py-2 rounded-2xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs">
          <span>📊 收银交接班 (Shift)</span>
        </button>
        <button @click="helpModalVisible = true" class="bg-blue-50/80 hover:bg-blue-100 text-blue-600 border border-blue-200/60 px-3.5 py-2 rounded-2xl text-xs font-bold transition-all flex items-center gap-1.5 cursor-pointer shadow-2xs">
          <span>⌨️ 快捷键指南</span>
        </button>

        <div class="flex items-center gap-3 pl-3 border-l border-slate-200">
          <div class="flex items-center gap-2.5 bg-slate-50 border border-slate-200/70 pl-2 pr-3.5 py-1 rounded-2xl shadow-2xs">
            <div class="relative flex items-center justify-center w-8 h-8 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-black text-xs shadow-md shadow-blue-500/20 uppercase shrink-0">
              {{ currentUser?.username ? currentUser.username.charAt(0) : 'A' }}
              <span class="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 border-2 border-white rounded-full"></span>
            </div>
            <div class="text-left">
              <span class="text-[9px] text-slate-400 block uppercase font-extrabold tracking-wider leading-none">{{ currentUser?.role || 'super_admin' }}</span>
              <span class="text-xs font-bold text-slate-800 tracking-tight leading-tight mt-0.5 block">{{ currentUser?.username || 'admin' }}</span>
            </div>
          </div>
          <button @click="confirmExitPos" class="px-3.5 py-2 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-xl text-xs font-bold transition-colors cursor-pointer shadow-2xs">
            退出收银台
          </button>
        </div>
      </div>
    </header>

    <!-- 中间主工作区 -->
    <div class="flex-1 flex overflow-hidden p-4 gap-4 pb-20">
      
      <!-- 左侧：商品搜索与购物车 -->
      <div class="flex-1 flex flex-col bg-white rounded-2xl border border-slate-200 overflow-hidden shadow-sm">
        
        <div class="p-4 border-b border-slate-200 flex gap-3 bg-slate-50/50">
          <div class="flex-1 relative">
            <input 
              ref="searchInputRef"
              v-model="deskSearchQuery" 
              @keydown="handleSearchKeydown"
              type="text" 
              placeholder="按 [/] 键聚焦，输入 OEM / 互换号 / 品名搜索 (按 Esc 确认退出)..." 
              class="w-full bg-white border border-slate-200 rounded-xl px-4 py-3 text-sm text-slate-900 placeholder-slate-400 outline-none focus:border-blue-500 font-mono shadow-xs"
            />
          </div>
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
            <div class="flex items-center gap-4 text-right">
              <div>
                <span class="text-sm font-mono font-bold text-slate-900">${{ p.price.toFixed(2) }}</span>
                <span class="text-[10px] text-slate-400 font-mono block">Bs. {{ (p.price * bcvRate).toFixed(2) }}</span>
              </div>
              <span :class="p.stock > 0 ? 'text-emerald-600' : 'text-rose-600 font-bold'" class="text-xs font-mono font-bold">
                库存: {{ p.stock }} {{ p.stock <= 0 ? '(缺货)' : '' }}
              </span>
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
                <th class="py-3 px-3">OEM 编号</th>
                <th class="py-3 px-3">配件名称</th>
                <th class="py-3 px-3 text-right">单价 ($ / Bs.)</th>
                <th class="py-3 px-3 text-center">数量</th>
                <th class="py-3 px-3 text-right">小计 ($ / Bs.)</th>
                <th class="py-3 px-3 text-center">操作</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 text-sm">
              <tr v-for="(item, index) in cartItems" :key="item.oem" class="hover:bg-slate-50/80 transition-colors">
                <td class="py-3 px-3 font-mono font-bold text-blue-600 text-xs">{{ item.oem }}</td>
                <td class="py-3 px-3 text-slate-800 font-medium">{{ item.name }}</td>
                <td class="py-3 px-3 text-right font-mono text-slate-600">
                  <div>${{ item.price.toFixed(2) }}</div>
                  <div class="text-[10px] text-slate-400">Bs. {{ (item.price * bcvRate).toFixed(2) }}</div>
                </td>
                <td class="py-3 px-3 text-center">
                  <div class="inline-flex items-center border border-slate-200 rounded-xl overflow-hidden bg-slate-50 shadow-2xs">
                    <button @click="item.quantity > 1 ? item.quantity-- : null" class="px-2.5 py-1 text-slate-500 hover:bg-slate-200 font-bold">-</button>
                    <input v-model.number="item.quantity" type="number" min="1" class="w-12 text-center bg-transparent text-slate-800 text-xs font-mono outline-none font-bold" />
                    <button @click="item.quantity++" class="px-2.5 py-1 text-slate-500 hover:bg-slate-200 font-bold">+</button>
                  </div>
                </td>
                <td class="py-3 px-3 text-right font-mono font-bold text-emerald-600">
                  <div>${{ (item.price * item.quantity).toFixed(2) }}</div>
                  <div class="text-[10px] text-emerald-700/70 font-normal">Bs. {{ (item.price * item.quantity * bcvRate).toFixed(2) }}</div>
                </td>
                <td class="py-3 px-3 text-center">
                  <button @click="cartItems.splice(index, 1)" class="text-rose-600 hover:text-rose-700 text-xs font-bold px-2.5 py-1 bg-rose-50 hover:bg-rose-100 rounded-lg transition-colors">删除</button>
                </td>
              </tr>
              <tr v-if="cartItems.length === 0">
                <td colspan="6" class="text-center py-20 text-slate-400 text-sm">
                  🛒 购物车为空，请扫码或搜索添加配件商品...
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>

      <!-- 右侧：组合支付面板 -->
      <div class="w-[430px] flex flex-col bg-white rounded-2xl border border-slate-200 p-4 shadow-sm justify-between shrink-0 overflow-y-auto max-h-full">
        
        <div class="space-y-3">
          <div class="flex items-center justify-between border-b border-slate-100 pb-2.5">
            <h3 class="font-bold text-sm text-slate-800">💳 多通道组合支付</h3>
            <button 
              @click="toggleMainCurrency" 
              type="button"
              class="bg-blue-50 hover:bg-blue-100 text-blue-700 border border-blue-200 px-2.5 py-1 rounded-lg text-xs font-bold font-mono transition-all cursor-pointer shadow-2xs flex items-center gap-1"
            >
              <span>🔄 主显示: {{ primaryCurrency === 'USD' ? '美元 ($)' : '玻利瓦尔 (Bs.)' }}</span>
            </button>
          </div>

          <div class="space-y-2 text-xs">
            <!-- 1. Cash USD -->
            <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200 flex items-center justify-between">
              <div>
                <span class="font-bold text-slate-700 flex items-center gap-1">💵 美金现金 Cash USD <span class="text-[10px] text-blue-600 font-mono">[F4]</span></span>
                <span class="text-[10px] text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ Bs. ${((Number(paymentSplit.cashUsd) || 0) * bcvRate).toFixed(2)}` : `≈ $${(Number(paymentSplit.cashUsd) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">$</span>
                <input 
                  ref="cashUsdInputRef"
                  v-model.number="paymentSplit.cashUsd" 
                  @keydown="handlePaymentKeydown($event, 'cashUsd')"
                  type="number" step="0.5" placeholder="0.00" 
                  class="w-28 bg-white border border-slate-300 rounded-lg px-2 py-1 text-right font-mono font-bold text-slate-900 outline-none focus:border-blue-500 text-sm" 
                />
              </div>
            </div>

            <!-- 2. Efectivo Bs. -->
            <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200 flex items-center justify-between">
              <div>
                <span class="font-bold text-slate-700 flex items-center gap-1">🇻🇪 玻利瓦尔现金 <span class="text-[10px] text-blue-600 font-mono">[F5]</span></span>
                <span class="text-[10px] text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.cashBs) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.cashBs) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">Bs.</span>
                <input 
                  ref="cashBsInputRef"
                  v-model.number="paymentSplit.cashBs" 
                  @keydown="handlePaymentKeydown($event, 'cashBs')"
                  type="number" step="10" placeholder="0.00" 
                  class="w-28 bg-white border border-slate-300 rounded-lg px-2 py-1 text-right font-mono font-bold text-slate-900 outline-none focus:border-blue-500 text-sm" 
                />
              </div>
            </div>

            <!-- 3. Card POS -->
            <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200 flex items-center justify-between">
              <div>
                <span class="font-bold text-slate-700 flex items-center gap-1">💳 刷卡 POS (Bs.) <span class="text-[10px] text-blue-600 font-mono">[F6]</span></span>
                <span class="text-[10px] text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.cardPos) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.cardPos) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">Bs.</span>
                <input 
                  ref="cardPosInputRef"
                  v-model.number="paymentSplit.cardPos" 
                  @keydown="handlePaymentKeydown($event, 'cardPos')"
                  type="number" step="10" placeholder="0.00" 
                  class="w-28 bg-white border border-slate-300 rounded-lg px-2 py-1 text-right font-mono font-bold text-slate-900 outline-none focus:border-blue-500 text-sm" 
                />
              </div>
            </div>

            <!-- 4. Pago Móvil -->
            <div class="bg-slate-50 p-2.5 rounded-xl border border-slate-200 flex items-center justify-between">
              <div>
                <span class="font-bold text-slate-700 flex items-center gap-1">⚡ 手机支付 Pago Móvil <span class="text-[10px] text-blue-600 font-mono">[F7]</span></span>
                <span class="text-[10px] text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.pagoMovil) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.pagoMovil) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">Bs.</span>
                <input 
                  ref="pagoMovilInputRef"
                  v-model.number="paymentSplit.pagoMovil" 
                  @keydown="handlePaymentKeydown($event, 'pagoMovil')"
                  type="number" step="10" placeholder="0.00" 
                  class="w-28 bg-white border border-slate-300 rounded-lg px-2 py-1 text-right font-mono font-bold text-slate-900 outline-none focus:border-blue-500 text-sm" 
                />
              </div>
            </div>

            <!-- 5. 挂账 (Fiado) -->
            <div class="bg-amber-50/50 p-2.5 rounded-xl border border-amber-200 flex items-center justify-between">
              <div>
                <span class="font-bold text-amber-800 flex items-center gap-1">📋 本单挂账 Fiado <span class="text-[10px] text-amber-600 font-mono">[Alt+P]</span></span>
                <span class="text-[10px] text-amber-600 font-mono font-bold">Bs. {{ ((Number(paymentSplit.fiado) || 0) * bcvRate).toFixed(2) }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-amber-600 font-bold">$</span>
                <input 
                  ref="fiadoInputRef"
                  v-model.number="paymentSplit.fiado" 
                  @keydown="handlePaymentKeydown($event, 'fiado')"
                  type="number" step="0.5" placeholder="0.00" 
                  class="w-28 bg-white border border-amber-300 rounded-lg px-2 py-1 text-right font-mono font-bold text-amber-900 outline-none focus:border-amber-500 text-sm" 
                />
              </div>
            </div>
          </div>

          <div>
            <input v-model="paymentReference" type="text" placeholder="选填，如 Pago Móvil 回执号 / 批次号..." class="w-full bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 text-xs text-slate-800 outline-none focus:border-blue-500 font-mono" />
          </div>
        </div>

        <div class="space-y-2.5 pt-3 border-t border-slate-200 mt-2">
          <div class="space-y-2">
            <div class="flex justify-between items-start text-xs font-bold text-slate-600">
              <span>总应付金额:</span>
              <div class="text-right">
                <div class="font-mono text-slate-900 text-lg font-black">{{ primaryCurrency === 'USD' ? `$${totalUsd.toFixed(2)}` : `Bs. ${(totalUsd * bcvRate).toFixed(2)}` }}</div>
                <div class="font-mono text-[10px] text-slate-400 font-normal">{{ primaryCurrency === 'USD' ? `Bs. ${(totalUsd * bcvRate).toFixed(2)}` : `$${totalUsd.toFixed(2)}` }}</div>
              </div>
            </div>
            <div class="flex justify-between items-start text-xs font-bold text-slate-600">
              <span>已付金额 (Paid):</span>
              <div class="text-right">
                <div class="font-mono text-emerald-600 text-lg font-black">{{ primaryCurrency === 'USD' ? `$${totalPaidUsd.toFixed(2)}` : `Bs. ${(totalPaidUsd * bcvRate).toFixed(2)}` }}</div>
                <div class="font-mono text-[10px] text-emerald-700/70 font-normal">{{ primaryCurrency === 'USD' ? `Bs. ${(totalPaidUsd * bcvRate).toFixed(2)}` : `$${totalPaidUsd.toFixed(2)}` }}</div>
              </div>
            </div>
            <div class="pt-1.5 border-t border-slate-100 flex justify-between items-start">
              <span class="text-xs font-bold pt-1" :class="balanceRemaining > 0 ? 'text-rose-600' : 'text-emerald-600'">
                {{ balanceRemaining > 0 ? '🔴 待付余额 (Pendiente):' : '🟢 找零 (Cambio):' }}
              </span>
              <div class="text-right">
                <div class="text-xl font-black font-mono" :class="balanceRemaining > 0 ? 'text-rose-600' : 'text-emerald-600'">
                  {{ primaryCurrency === 'USD' ? `$${Math.abs(balanceRemaining).toFixed(2)}` : `Bs. ${(Math.abs(balanceRemaining) * bcvRate).toFixed(2)}` }}
                </div>
                <div class="font-mono text-[10px] font-bold" :class="balanceRemaining > 0 ? 'text-rose-500' : 'text-emerald-500'">
                  {{ primaryCurrency === 'USD' ? `Bs. ${(Math.abs(balanceRemaining) * bcvRate).toFixed(2)}` : `$${Math.abs(balanceRemaining).toFixed(2)}` }}
                </div>
              </div>
            </div>
          </div>

          <button 
            @click="openPreviewModal"
            :disabled="!isFullyPaid || cartItems.length === 0"
            class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-2xl font-black text-base shadow-lg shadow-emerald-600/20 transition-all cursor-pointer flex items-center justify-center gap-2"
          >
            <span>🚀 确认收款并出单 ({{ cartItems.length === 0 ? '购物车为空' : (balanceRemaining < 0 ? `找零 $${Math.abs(balanceRemaining).toFixed(2)}` : '已付清') }})</span>
          </button>
        </div>

      </div>

    </div>

    <!-- 底部快捷键导航 -->
    <footer class="absolute bottom-0 left-0 right-0 h-16 bg-white border-t border-slate-200 px-6 flex items-center justify-between z-30 shadow-md">
      <div class="grid grid-cols-6 gap-3 w-full">
        <div @click="focusSearch" class="bg-slate-50 hover:bg-blue-50 border border-slate-200 rounded-xl px-3 py-2 flex items-center justify-between text-xs cursor-pointer transition-colors">
          <span class="text-slate-600 font-medium">聚焦搜索 [/]</span>
          <span class="bg-blue-100 text-blue-700 font-mono font-bold px-2 py-0.5 rounded">F4~F7切换支付</span>
        </div>
        <div @click="openClientSearchModal" class="bg-slate-50 hover:bg-blue-50 border border-slate-200 rounded-xl px-3 py-2 flex items-center justify-between text-xs cursor-pointer transition-colors">
          <span class="text-slate-600 font-medium">选客户</span>
          <span class="bg-blue-100 text-blue-700 font-mono font-bold px-2 py-0.5 rounded">Ctrl+F</span>
        </div>
        <div @click="holdCurrentOrder" class="bg-slate-50 hover:bg-amber-50 border border-slate-200 rounded-xl px-3 py-2 flex items-center justify-between text-xs cursor-pointer transition-colors">
          <span class="text-slate-600 font-medium">云端挂单</span>
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

    <!-- 销售历史弹窗 -->
    <PosHistoryModal
      :visible="historyModalVisible"
      :orders="completedOrders"
      @close="historyModalVisible = false"
      @reprint="reprintOrderTicket"
      @return="processReturnOrder"
    />

    <!-- 云端挂单恢复弹窗 -->
    <div v-if="recallModalVisible" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-xl w-full overflow-hidden border border-slate-100 flex flex-col max-h-[80vh]">
        <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <h3 class="font-bold text-base text-slate-800 flex items-center gap-2">
            <span>📦 云端挂单恢复大厅 (共 {{ heldOrders.length }} 单)</span>
          </h3>
          <button @click="recallModalVisible = false" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-3">
          <div v-for="order in heldOrders" :key="order.id" class="p-4 rounded-2xl border border-slate-200 bg-slate-50 hover:bg-blue-50/40 transition-all flex items-center justify-between">
            <div class="space-y-1">
              <div class="font-bold text-sm text-slate-800 flex items-center gap-2">
                <span class="font-mono text-blue-600">{{ order.hold_no }}</span>
                <span>👤 {{ order.client_name || '散客' }}</span>
              </div>
              <div class="text-xs text-slate-400 font-mono">挂单时间: {{ order.timestamp }}</div>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-base font-mono font-black text-slate-900">${{ order.total_amount.toFixed(2) }}</span>
              <button @click="recallOrder(order)" class="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl text-xs font-bold transition-colors cursor-pointer shadow-sm">
                恢复取单
              </button>
              <button @click="deleteHeldOrder(order.id)" class="px-3 py-2 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-xl text-xs font-bold transition-colors cursor-pointer">
                作废
              </button>
            </div>
          </div>
          <div v-if="heldOrders.length === 0" class="text-center py-12 text-slate-400 text-xs">
            当前云端挂单池为空
          </div>
        </div>

        <div class="p-3 bg-slate-50 border-t border-slate-100 text-right">
          <button @click="recallModalVisible = false" class="px-4 py-2 bg-slate-200 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-300 transition-colors cursor-pointer">
            取消
          </button>
        </div>
      </div>
    </div>

    <!-- 🌟 重构优化：收银交接班与全通道多币种盘点 Modal -->
    <div v-if="shiftReportModalVisible" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-2xl w-full overflow-hidden border border-slate-100 flex flex-col max-h-[92vh]">
        <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/80">
          <h3 class="font-bold text-base text-slate-800 flex items-center gap-2">
            <span>📊 收银交接班与营业汇总 (Shift Handover)</span>
          </h3>
          <button @click="shiftReportModalVisible = false" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-5 text-xs bg-slate-50/40">
          
          <!-- 1. 系统统计应收 (System Snapshot) -->
          <div class="bg-white p-4 rounded-2xl border border-slate-200 space-y-2.5 shadow-2xs font-mono">
            <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-100 pb-2">
              1. 系统统计应收 (SYSTEM SNAPSHOT)
            </div>
            <div class="grid grid-cols-2 gap-x-6 gap-y-2">
              <div class="flex justify-between items-center text-slate-700">
                <span>💵 美金现金 (Cash USD):</span>
                <span class="font-bold text-slate-900">${{ shiftStats.cashUsd.amount.toFixed(2) }}</span>
              </div>
              <div class="flex justify-between items-center text-slate-700">
                <span>🇻🇪 Bs. 现金 (Efectivo Bs.):</span>
                <span class="font-bold text-emerald-600">Bs. {{ (shiftStats.cashBs.amount * bcvRate).toFixed(2) }}</span>
              </div>
              <div class="flex justify-between items-center text-slate-700">
                <span>💳 刷卡 POS (Bs.):</span>
                <span class="font-bold text-blue-600">Bs. {{ (shiftStats.cardPos.amount * bcvRate).toFixed(2) }}</span>
              </div>
              <div class="flex justify-between items-center text-slate-700">
                <span>⚡ Pago Móvil (Bs.):</span>
                <span class="font-bold text-indigo-600">Bs. {{ (shiftStats.pagoMovil.amount * bcvRate).toFixed(2) }}</span>
              </div>
              <div class="flex justify-between items-center text-slate-700 col-span-2">
                <span>📋 本单挂账 (Fiado):</span>
                <span class="font-bold text-amber-600">${{ shiftStats.fiado.amount.toFixed(2) }}</span>
              </div>
            </div>
            <div class="pt-2 border-t border-slate-100 flex justify-between items-center text-sm font-black">
              <span class="text-slate-900">系统总营业额 (USD):</span>
              <span class="text-emerald-600">${{ shiftStats.totalUsd.toFixed(2) }}</span>
            </div>
          </div>

          <!-- 2. 收银员手动输入实盘款项 (BLIND COUNT & ACTUAL VALUES) -->
          <div class="bg-blue-50/60 p-4 rounded-2xl border border-blue-200/80 space-y-3 font-mono">
            <div class="text-[11px] font-bold text-blue-800 uppercase tracking-wider border-b border-blue-200/60 pb-2 flex justify-between items-center">
              <span>2. 收银员实盘录入款项 (ACTUAL COUNT)</span>
              <span class="text-[10px] text-blue-600 font-normal">请录入抽屉及账面实际金额</span>
            </div>

            <div class="grid grid-cols-2 gap-3">
              <!-- 美金现金 -->
              <div class="bg-white p-2.5 rounded-xl border border-blue-200/70 space-y-1">
                <label class="block text-[11px] font-bold text-slate-700">💵 实收美金现金 (USD):</label>
                <div class="flex items-center gap-1">
                  <span class="text-slate-400 font-bold">$</span>
                  <input 
                    v-model.number="actualCounts.cashUsd" 
                    type="number" step="0.5" placeholder="0.00" 
                    class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-right font-mono text-sm outline-none focus:border-blue-500 font-bold text-slate-900"
                  />
                </div>
                <div class="text-[10px] text-right font-bold" :class="cashUsdDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ cashUsdDiff >= 0 ? '+' : '' }}${{ cashUsdDiff.toFixed(2) }}
                </div>
              </div>

              <!-- Bs. 现金 -->
              <div class="bg-white p-2.5 rounded-xl border border-blue-200/70 space-y-1">
                <label class="block text-[11px] font-bold text-slate-700">🇻🇪 实收 Bs. 现金 (Bs.):</label>
                <div class="flex items-center gap-1">
                  <span class="text-slate-400 font-bold">Bs.</span>
                  <input 
                    v-model.number="actualCounts.cashBs" 
                    type="number" step="10" placeholder="0.00" 
                    class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-right font-mono text-sm outline-none focus:border-blue-500 font-bold text-slate-900"
                  />
                </div>
                <div class="text-[10px] text-right font-bold" :class="cashBsDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ cashBsDiff >= 0 ? '+' : '' }}Bs. {{ cashBsDiff.toFixed(2) }}
                </div>
              </div>

              <!-- 刷卡 POS -->
              <div class="bg-white p-2.5 rounded-xl border border-blue-200/70 space-y-1">
                <label class="block text-[11px] font-bold text-slate-700">💳 实收 POS 刷卡 (Bs.):</label>
                <div class="flex items-center gap-1">
                  <span class="text-slate-400 font-bold">Bs.</span>
                  <input 
                    v-model.number="actualCounts.cardPos" 
                    type="number" step="10" placeholder="0.00" 
                    class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-right font-mono text-sm outline-none focus:border-blue-500 font-bold text-slate-900"
                  />
                </div>
                <div class="text-[10px] text-right font-bold" :class="cardPosDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ cardPosDiff >= 0 ? '+' : '' }}Bs. {{ cardPosDiff.toFixed(2) }}
                </div>
              </div>

              <!-- Pago Móvil -->
              <div class="bg-white p-2.5 rounded-xl border border-blue-200/70 space-y-1">
                <label class="block text-[11px] font-bold text-slate-700">⚡ 实收 Pago Móvil (Bs.):</label>
                <div class="flex items-center gap-1">
                  <span class="text-slate-400 font-bold">Bs.</span>
                  <input 
                    v-model.number="actualCounts.pagoMovil" 
                    type="number" step="10" placeholder="0.00" 
                    class="w-full bg-slate-50 border border-slate-200 rounded-lg px-2 py-1 text-right font-mono text-sm outline-none focus:border-blue-500 font-bold text-slate-900"
                  />
                </div>
                <div class="text-[10px] text-right font-bold" :class="pagoMovilDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ pagoMovilDiff >= 0 ? '+' : '' }}Bs. {{ pagoMovilDiff.toFixed(2) }}
                </div>
              </div>
            </div>

            <!-- 综合盈亏汇总折合美元 -->
            <div class="pt-2 border-t border-blue-200/60 flex justify-between items-center text-sm">
              <span class="font-bold text-slate-700">折算总盈亏 (Diferencia Total):</span>
              <span :class="totalUsdDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'" class="font-black font-mono">
                {{ totalUsdDiff >= 0 ? '+' : '' }}${{ totalUsdDiff.toFixed(2) }}
              </span>
            </div>
          </div>

          <div v-if="totalUsdDiff !== 0" class="space-y-1.5">
            <label class="block font-semibold text-slate-500 uppercase">盈亏原因备注</label>
            <input v-model="handoverNotes" type="text" placeholder="例如：Bs. 零钱误差 / Pago Móvil 延迟到账..." class="w-full bg-white border border-slate-200 rounded-xl px-3.5 py-2 text-xs outline-none focus:border-blue-500" />
          </div>
        </div>

        <div class="p-4 bg-white border-t border-slate-100 flex gap-3">
          <button @click="shiftReportModalVisible = false" class="flex-1 py-3 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-2xl text-xs font-bold transition-colors cursor-pointer">
            取消
          </button>
          <button @click="submitShiftHandover" class="flex-1 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl text-xs font-black shadow-md shadow-emerald-600/20 transition-colors cursor-pointer flex items-center justify-center gap-1.5">
            <span>🔒 确认交班并锁定锁班</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 小票预览 Modal -->
    <div v-if="previewModalVisible" class="fixed inset-0 bg-slate-900/60 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-slate-100 flex flex-col max-h-[90vh]">
        <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/80">
          <h3 class="font-bold text-base text-slate-800 flex items-center gap-2">
            <span>🧾 收银小票实时预览 (Pago Mixto)</span>
          </h3>
          <button @click="previewModalVisible = false" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-4 font-mono text-xs bg-slate-50/40">
          <div class="text-center pb-3 border-b border-dashed border-slate-300 space-y-1">
            <div class="font-black text-sm text-slate-900">{{ systemConfig.company_name || 'TOSTIYK (TK) - VENEZUELA' }}</div>
            <div class="text-[10px] text-blue-600 font-bold">RIF: {{ systemConfig.rif || 'J-00000000-0' }}</div>
            <div class="text-[10px] text-slate-500">{{ systemConfig.address || 'Valencia, Carabobo' }}</div>
          </div>

          <div class="space-y-1 text-slate-700 pb-3 border-b border-dashed border-slate-300">
            <div><span class="font-bold">Client:</span> {{ quoteClientName || 'Cliente General' }}</div>
            <div><span class="font-bold">Operator:</span> {{ currentUser?.username || 'admin' }}</div>
            <div class="font-bold text-blue-600">Payment Breakdown:</div>
            <div v-if="paymentSplit.cashUsd > 0"> - Cash USD: ${{ paymentSplit.cashUsd.toFixed(2) }} (Bs. {{ (paymentSplit.cashUsd * bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.cashBs > 0"> - Efectivo Bs.: Bs. {{ paymentSplit.cashBs.toFixed(2) }} (${{ (paymentSplit.cashBs / bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.cardPos > 0"> - Card POS: Bs. {{ paymentSplit.cardPos.toFixed(2) }} (${{ (paymentSplit.cardPos / bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.pagoMovil > 0"> - Pago Móvil: Bs. {{ paymentSplit.pagoMovil.toFixed(2) }} (${{ (paymentSplit.pagoMovil / bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.fiado > 0"> - Fiado (挂账): ${{ paymentSplit.fiado.toFixed(2) }} (Bs. {{ (paymentSplit.fiado * bcvRate).toFixed(2) }})</div>
            <div v-if="balanceRemaining < 0"> - cambio (找零): ${{ Math.abs(balanceRemaining).toFixed(2) }} (Bs. {{ (Math.abs(balanceRemaining) * bcvRate).toFixed(2) }})</div>
            <div v-if="paymentReference"><span class="font-bold">Ref:</span> {{ paymentReference }}</div>
          </div>

          <div class="space-y-2 pb-3 border-b border-dashed border-slate-300">
            <div v-for="item in cartItems" :key="item.oem" class="flex justify-between items-start gap-2">
              <div>
                <div class="font-bold text-slate-800">{{ item.name }}</div>
                <div class="text-[10px] text-slate-500">{{ item.oem }} x {{ item.quantity }} @ ${{ item.price.toFixed(2) }}</div>
              </div>
              <div class="font-bold text-slate-900 text-right">
                <div>${{ (item.price * item.quantity).toFixed(2) }}</div>
                <div class="text-[10px] text-slate-500 font-normal">Bs. {{ (item.price * item.quantity * bcvRate).toFixed(2) }}</div>
              </div>
            </div>
          </div>

          <div class="space-y-1.5 text-right pb-2">
            <div class="text-xl font-black text-slate-900">Total: ${{ totalUsd.toFixed(2) }} / Bs. {{ (totalUsd * bcvRate).toFixed(2) }}</div>
          </div>
        </div>

        <div class="p-4 bg-white border-t border-slate-100 flex gap-3">
          <button @click="previewModalVisible = false" class="flex-1 py-3 bg-slate-100 text-slate-700 rounded-2xl text-xs font-bold">返回修改</button>
          <button @click="confirmAndPrint" class="flex-1 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-2xl text-xs font-black">确认出单并打印</button>
        </div>
      </div>
    </div>

    <!-- 快捷键指南弹窗 -->
    <PosHelpModal :visible="helpModalVisible" @close="helpModalVisible = false" />

    <!-- 客户快速搜索 Modal -->
    <div v-if="clientModalVisible" class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs flex items-center justify-center z-50 p-4">
      <div class="bg-white rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-100 flex flex-col max-h-[80vh]">
        <div class="p-5 border-b border-slate-100 flex items-center justify-between bg-slate-50/50">
          <h3 class="font-bold text-base text-slate-800">快捷选择客户</h3>
          <button @click="clientModalVisible = false" class="text-slate-400 font-bold">✕</button>
        </div>
        <div class="p-4 border-b border-slate-100">
          <input ref="clientModalInputRef" v-model="clientFilterQuery" @keydown="handleClientModalKeydown" type="text" placeholder="搜索客户..." class="w-full bg-slate-50 border border-slate-200 rounded-xl px-4 py-2.5 text-sm outline-none focus:border-blue-500" />
        </div>
        <div class="flex-1 overflow-y-auto p-3 space-y-1.5">
          <div v-for="c in filteredModalClients" :key="c.id" @click="selectClient(c.name)" class="p-3 rounded-2xl border cursor-pointer hover:bg-blue-50 flex items-center justify-between text-sm">
            <div><div class="font-bold">🏢 {{ c.name }}</div><div class="text-xs text-slate-400 font-mono">RIF: {{ c.rif_or_cedula || '-' }}</div></div>
          </div>
        </div>
      </div>
    </div>

    <!-- 退出确认 -->
    <ConfirmDialog :visible="exitConfirmVisible" icon="⚠️" title="确认退出收银台？" message="当前收银台若有未结算商品，是否继续？" @cancel="exitConfirmVisible = false" @confirm="executeExitPos" />
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { apiFetch, apiUrl } from '../utils/api'
import { useI18n } from '../composables/useI18n'
import ConfirmDialog from './ConfirmDialog.vue'
import PosHelpModal from './pos/PosHelpModal.vue'
import PosHistoryModal from './pos/PosHistoryModal.vue'

const { t } = useI18n()

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
const paymentReference = ref('')
const searchInputRef = ref(null)
const selectedIndex = ref(0)
const activeItemRef = ref(null)
const exitConfirmVisible = ref(false)

// 主显示币种切换 ('USD' 或 'BS')
const primaryCurrency = ref('USD')
const toggleMainCurrency = () => {
  primaryCurrency.value = primaryCurrency.value === 'USD' ? 'BS' : 'USD'
}

const cashUsdInputRef = ref(null)
const cashBsInputRef = ref(null)
const cardPosInputRef = ref(null)
const pagoMovilInputRef = ref(null)
const fiadoInputRef = ref(null)

const paymentSplit = ref({
  cashUsd: 0,
  cashBs: 0,
  cardPos: 0,
  pagoMovil: 0,
  fiado: 0
})

const totalUsd = computed(() => {
  return props.cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
})

const totalPaidUsd = computed(() => {
  const cUsd = Number(paymentSplit.value.cashUsd) || 0
  const cBs = Number(paymentSplit.value.cashBs) || 0
  const cCard = Number(paymentSplit.value.cardPos) || 0
  const cPago = Number(paymentSplit.value.pagoMovil) || 0
  const cFiado = Number(paymentSplit.value.fiado) || 0

  const rate = props.bcvRate || 1
  const paidInUsd = cUsd + (cBs / rate) + (cCard / rate) + (cPago / rate) + cFiado
  return Number(paidInUsd.toFixed(2))
})

const balanceRemaining = computed(() => {
  return Number((totalUsd.value - totalPaidUsd.value).toFixed(2))
})

const isFullyPaid = computed(() => {
  return totalUsd.value > 0 && totalPaidUsd.value >= totalUsd.value
})

const handlePaymentKeydown = (e, channelKey) => {
  if (e.key === ' ' || e.key === '=') {
    e.preventDefault()
    let otherPaid = 0
    const rate = props.bcvRate || 1
    for (const k in paymentSplit.value) {
      if (k !== channelKey) {
        const val = Number(paymentSplit.value[k]) || 0
        if (k === 'cashBs' || k === 'cardPos' || k === 'pagoMovil') {
          otherPaid += val / rate
        } else {
          otherPaid += val
        }
      }
    }
    const needed = Math.max(0, totalUsd.value - otherPaid)
    if (channelKey === 'cashBs' || channelKey === 'cardPos' || channelKey === 'pagoMovil') {
      paymentSplit.value[channelKey] = Number((needed * rate).toFixed(2))
    } else {
      paymentSplit.value[channelKey] = Number(needed.toFixed(2))
    }
  }
}

watch(totalUsd, (newVal) => {
  if (newVal > 0) {
    paymentSplit.value = {
      cashUsd: newVal,
      cashBs: 0,
      cardPos: 0,
      pagoMovil: 0,
      fiado: 0
    }
  } else {
    paymentSplit.value = { cashUsd: 0, cashBs: 0, cardPos: 0, pagoMovil: 0, fiado: 0 }
  }
}, { immediate: true })

const systemConfig = ref({ company_name: 'TOSTIYK (TK) - VENEZUELA', rif: 'J-00000000-0', address: 'Valencia, Carabobo' })

const fetchSystemSettings = async () => {
  try {
    const res = await fetch(apiUrl('/api/settings'))
    if (res.ok) {
      const data = await res.json()
      systemConfig.value = { ...systemConfig.value, ...data }
    }
  } catch (e) { console.error(e) }
}

const heldOrders = ref([])
const recallModalVisible = ref(false)
const fetchHeldOrders = async () => {
  try {
    const res = await apiFetch('/api/held-orders')
    if (res.ok) heldOrders.value = await res.json()
  } catch (e) { console.error(e) }
}

const completedOrders = ref([])
const historyModalVisible = ref(false)
const shiftReportModalVisible = ref(false)
const shiftStats = ref({
  cashUsd: { amount: 0, count: 0 },
  cashBs: { amount: 0, count: 0 },
  cardPos: { amount: 0, count: 0 },
  pagoMovil: { amount: 0, count: 0 },
  fiado: { amount: 0, count: 0 },
  totalUsd: 0,
  totalCount: 0
})

// 🌟 新增：收银员交接班多通道实盘录入状态
const actualCounts = ref({
  cashUsd: 0,
  cashBs: 0,
  cardPos: 0,
  pagoMovil: 0
})
const handoverNotes = ref('')

// 各通道差异计算 (系统应收 vs 实收)
const cashUsdDiff = computed(() => Number(((actualCounts.value.cashUsd || 0) - shiftStats.value.cashUsd.amount).toFixed(2)))
const cashBsDiff = computed(() => Number(((actualCounts.value.cashBs || 0) - (shiftStats.value.cashBs.amount * (props.bcvRate || 1))).toFixed(2)))
const cardPosDiff = computed(() => Number(((actualCounts.value.cardPos || 0) - (shiftStats.value.cardPos.amount * (props.bcvRate || 1))).toFixed(2)))
const pagoMovilDiff = computed(() => Number(((actualCounts.value.pagoMovil || 0) - (shiftStats.value.pagoMovil.amount * (props.bcvRate || 1))).toFixed(2)))

// 总折算美元盈亏
const totalUsdDiff = computed(() => {
  const rate = props.bcvRate || 1
  const diffInUsd = cashUsdDiff.value + (cashBsDiff.value / rate) + (cardPosDiff.value / rate) + (pagoMovilDiff.value / rate)
  return Number(diffInUsd.toFixed(2))
})

const submitShiftHandover = async () => {
  try {
    const payload = {
      system_cash_usd: shiftStats.value.cashUsd.amount,
      system_cash_bs: shiftStats.value.cashBs.amount * (props.bcvRate || 1),
      system_card_pos: shiftStats.value.cardPos.amount * (props.bcvRate || 1),
      system_pagomovil_usd: shiftStats.value.pagoMovil.amount * (props.bcvRate || 1),
      system_debt_usd: shiftStats.value.fiado.amount,
      system_total_usd: shiftStats.value.totalUsd,
      
      actual_cash_usd: actualCounts.value.cashUsd || 0,
      actual_cash_bs: actualCounts.value.cashBs || 0,
      actual_card_pos: actualCounts.value.cardPos || 0,
      actual_pago_movil: actualCounts.value.pagoMovil || 0,
      
      notes: handoverNotes.value
    }
    const res = await apiFetch('/api/pos/shift-handover', { method: 'POST', body: JSON.stringify(payload) })
    if (!res.ok) throw new Error('交接班归档失败')
    showToast('🔒 交接班成功，班次已成功锁定归档！', 'success')
    shiftReportModalVisible.value = false
  } catch (err) { showToast('❌ ' + err.message, 'error') }
}

const previewModalVisible = ref(false)
const helpModalVisible = ref(false)
const toastMessage = ref('')
const toastType = ref('success')
let toastTimer = null

const showToast = (msg, type = 'error') => {
  toastMessage.value = msg
  toastType.value = type
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toastMessage.value = '' }, 1500)
}

const clientModalVisible = ref(false)
const clientFilterQuery = ref('')
const clientModalInputRef = ref(null)

const openClientSearchModal = async () => {
  clientFilterQuery.value = ''
  clientModalVisible.value = true
  await nextTick()
  if (clientModalInputRef.value) clientModalInputRef.value.focus()
}

const selectClient = (name) => {
  quoteClientName.value = name
  clientModalVisible.value = false
}

const filteredModalClients = computed(() => {
  if (!props.clientsList) return []
  if (!clientFilterQuery.value.trim()) return props.clientsList
  const q = clientFilterQuery.value.toUpperCase()
  return props.clientsList.filter(c => c.name.toUpperCase().includes(q) || (c.phone && c.phone.toUpperCase().includes(q)))
})

const filteredParts = computed(() => {
  if (!deskSearchQuery.value.trim()) return []
  const q = deskSearchQuery.value.toUpperCase()
  return props.partsList.filter(p => p.oem.toUpperCase().includes(q) || p.name.toUpperCase().includes(q)).slice(0, 10)
})

const selectAndAddToCart = (part) => {
  if (part.stock <= 0) {
    showToast(`商品 ${part.oem} 库存不足`, 'error')
    return
  }
  emit('add-to-cart', part)
  deskSearchQuery.value = ''
  focusSearch()
}

const focusSearch = () => { if (searchInputRef.value) searchInputRef.value.focus() }
const deleteLastItem = () => { if (props.cartItems.length > 0) props.cartItems.pop() }

const holdCurrentOrder = async () => {
  if (props.cartItems.length === 0) {
    showToast('当前购物车为空，无需挂单！', 'error')
    return
  }
  try {
    const res = await apiFetch('/api/held-orders', {
      method: 'POST',
      body: JSON.stringify({
        client_name: quoteClientName.value || 'Cliente General',
        payment_method: 'Pago_Mixto',
        items: props.cartItems,
        total_amount: totalUsd.value
      })
    })
    if (res.ok) {
      props.cartItems.splice(0, props.cartItems.length)
      quoteClientName.value = ''
      showToast('📌 订单已成功挂入云端挂单池！', 'success')
      fetchHeldOrders()
    }
  } catch (e) { showToast('❌ 挂单异常', 'error') }
}

const openRecallModal = async () => {
  await fetchHeldOrders()
  if (heldOrders.value.length === 0) {
    showToast('云端挂单池为空！', 'error')
    return
  }
  recallModalVisible.value = true
}

const recallOrder = (order) => {
  try {
    const parsedItems = JSON.parse(order.items_json)
    props.cartItems.splice(0, props.cartItems.length, ...parsedItems)
    quoteClientName.value = order.client_name
    apiFetch(`/api/held-orders/${order.id}`, { method: 'DELETE' }).then(() => fetchHeldOrders())
    recallModalVisible.value = false
    showToast('✅ 成功取回挂单', 'success')
  } catch (e) { showToast('❌ 解析失败', 'error') }
}

const deleteHeldOrder = async (id) => {
  await apiFetch(`/api/held-orders/${id}`, { method: 'DELETE' })
  fetchHeldOrders()
}

const fetchCompletedOrders = async () => {
  try {
    const res = await apiFetch('/api/pos/orders')
    if (!res.ok) return
    const ordersData = await res.json()
    completedOrders.value = ordersData
    let cUsd = 0, cBs = 0, cardAmt = 0, pUsd = 0, fUsd = 0, tUsd = 0
    ordersData.forEach(o => {
      tUsd += o.totalUsd
      if (o.paymentMethod === 'Cash_USD') cUsd += o.totalUsd
      else if (o.paymentMethod === 'Cash_Bs') cBs += o.totalUsd
      else if (o.paymentMethod === 'Card_POS') cardAmt += o.totalUsd
      else if (o.paymentMethod === 'Pago_Movil') pUsd += o.totalUsd
      else if (o.paymentMethod === 'Fiado_Debt') fUsd += o.totalUsd
    })
    shiftStats.value = {
      cashUsd: { amount: cUsd, count: ordersData.length },
      cashBs: { amount: cBs, count: 0 },
      cardPos: { amount: cardAmt, count: 0 },
      pagoMovil: { amount: pUsd, count: 0 },
      fiado: { amount: fUsd, count: 0 },
      totalUsd: tUsd,
      totalCount: ordersData.length
    }

    // 默认填入系统计算值
    actualCounts.value = {
      cashUsd: cUsd,
      cashBs: Number((cBs * (props.bcvRate || 1)).toFixed(2)),
      cardPos: Number((cardAmt * (props.bcvRate || 1)).toFixed(2)),
      pagoMovil: Number((pUsd * (props.bcvRate || 1)).toFixed(2))
    }
  } catch (e) { console.error(e) }
}

const openHistoryModal = async () => { await fetchCompletedOrders(); historyModalVisible.value = true }
const openShiftReportModal = async () => { await fetchCompletedOrders(); shiftReportModalVisible.value = true }
const reprintOrderTicket = (order) => { showToast(`🖨️ 打印小票 #${order.orderId}`, 'success') }
const processReturnOrder = async (dbId) => {
  await apiFetch(`/api/pos/orders/${dbId}/refund`, { method: 'POST' })
  showToast('🔄 退货成功', 'success')
  fetchCompletedOrders()
}

const confirmExitPos = () => { exitConfirmVisible.value = true }
const executeExitPos = () => { exitConfirmVisible.value = false; emit('exit-pos') }
const openPreviewModal = () => { if (props.cartItems.length === 0 || !isFullyPaid.value) return; previewModalVisible.value = true }

const confirmAndPrint = async () => {
  try {
    const payload = {
      client_name: quoteClientName.value || "Cliente General",
      payment_method: paymentSplit.value.fiado > 0 ? 'Fiado_Debt' : 'Cash_USD',
      payment_reference: paymentReference.value,
      bcv_rate: props.bcvRate,
      items: props.cartItems.map(i => ({ oem: i.oem, name: i.name, brand: i.brand || "GENERAL", quantity: i.quantity, price: i.price }))
    }
    const res = await apiFetch('/api/pos/orders', { method: 'POST', body: JSON.stringify(payload) })
    if (!res.ok) throw new Error('结账失败')
    const data = await res.json()
    previewModalVisible.value = false
    showToast(`✅ 开单成功！单号: ${data.order_no}`, 'success')
    paymentReference.value = ''
    quoteClientName.value = ''
    emit('generate-quote')
    fetchCompletedOrders()
  } catch (err) { showToast(err.message || '结账失败', 'error') }
}

const handleGlobalKeydown = (e) => {
  if (previewModalVisible.value) {
    if (e.key === 'Enter') { e.preventDefault(); confirmAndPrint(); return }
    if (e.key === 'Escape') { e.preventDefault(); previewModalVisible.value = false; return }
    return
  }

  if (clientModalVisible.value || helpModalVisible.value || recallModalVisible.value || shiftReportModalVisible.value || historyModalVisible.value || exitConfirmVisible.value) {
    if (e.key === 'Escape') {
      e.preventDefault()
      if (exitConfirmVisible.value) {
        exitConfirmVisible.value = false
      } else {
        clientModalVisible.value = false
        helpModalVisible.value = false
        recallModalVisible.value = false
        shiftReportModalVisible.value = false
        historyModalVisible.value = false
      }
      return
    }
    if (exitConfirmVisible.value && e.key === 'Enter') {
      e.preventDefault()
      executeExitPos()
      return
    }
    return
  }

  if (e.key === 'Escape') {
    e.preventDefault()
    confirmExitPos()
    return
  }

  if (e.key === 'F4') { e.preventDefault(); if (cashUsdInputRef.value) cashUsdInputRef.value.focus(); return }
  if (e.key === 'F5') { e.preventDefault(); if (cashBsInputRef.value) cashBsInputRef.value.focus(); return }
  if (e.key === 'F6') { e.preventDefault(); if (cardPosInputRef.value) cardPosInputRef.value.focus(); return }
  if (e.key === 'F7') { e.preventDefault(); if (pagoMovilInputRef.value) pagoMovilInputRef.value.focus(); return }
  if (e.altKey && e.key.toLowerCase() === 'p') { e.preventDefault(); if (fiadoInputRef.value) fiadoInputRef.value.focus(); return }

  if (e.key === '/' && document.activeElement !== searchInputRef.value) { e.preventDefault(); focusSearch(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'f') { e.preventDefault(); openClientSearchModal(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'h') { e.preventDefault(); holdCurrentOrder(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'r') { e.preventDefault(); openRecallModal(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'b') { e.preventDefault(); emit('clear-cart'); return }
}

const handleSearchKeydown = (e) => {
  const results = filteredParts.value
  if (results.length > 0 && e.key === 'Enter') {
    e.preventDefault()
    selectAndAddToCart(results[selectedIndex.value] || results[0])
  }
}

onMounted(() => {
  window.addEventListener('keydown', handleGlobalKeydown)
  focusSearch()
  fetchCompletedOrders()
  fetchSystemSettings()
  fetchHeldOrders()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleGlobalKeydown)
  if (toastTimer) clearTimeout(toastTimer)
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease, transform 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; transform: translateY(-10px); }
</style>