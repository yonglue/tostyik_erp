<!-- src/components/QuotationDeskView.vue -->
<template>
  <div class="fixed inset-0 bg-slate-950/25 backdrop-blur-md z-40 flex flex-col overflow-hidden text-slate-900 font-sans transition-all">
    
    <!-- 右上角提示条 -->
    <transition name="fade">
      <div v-if="toastMessage" :class="toastType === 'success' ? 'bg-emerald-600/90 border-emerald-400/30' : 'bg-rose-600/90 border-rose-400/30'" class="fixed top-2 right-4 z-50 text-white px-4 py-3 rounded-xl shadow-xl backdrop-blur-md border flex items-center gap-2 text-sm font-bold animate-bounce">
        <span>{{ toastType === 'success' ? '✅' : '❌' }}</span>
        <span>{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- 顶部状态栏 -->
    <header class="h-12 bg-white/75 backdrop-blur-xl border-b border-white/60 px-4 flex items-center justify-between shrink-0 shadow-2xs">
      <div class="flex items-center space-x-3">
        <span class="bg-blue-600 text-white text-xs px-2.5 py-1 rounded-lg font-mono font-bold shadow-2xs">POS v2.9</span>
        <span class="text-sm font-bold text-slate-700">📅 {{ currentDateTime }}</span>
        <span class="text-sm text-emerald-600 font-mono font-bold">{{ t.bcvLabel }}: {{ bcvRate }}</span>
        
        <button v-if="heldOrders.length > 0" @click="openRecallModal" class="bg-white/70 hover:bg-amber-500/10 text-amber-800 border border-slate-200 hover:border-amber-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <span>📦 挂单池 ({{ heldOrders.length }}) [Ctrl+R]</span>
        </button>
      </div>
      
      <div class="flex items-center space-x-2.5">
        <button @click="openHistoryModal" class="bg-white/70 hover:bg-white/90 text-indigo-700 border border-slate-200 hover:border-indigo-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <span>📜 销售历史</span>
        </button>
        <button @click="openShiftReportModal" class="bg-white/70 hover:bg-white/90 text-emerald-700 border border-slate-200 hover:border-emerald-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <span>📊 交接班</span>
        </button>
        <button @click="helpModalVisible = true" class="bg-white/70 hover:bg-white/90 text-blue-600 border border-slate-200 hover:border-blue-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <span>⌨️ 快捷键</span>
        </button>

        <div class="flex items-center gap-2.5 pl-2.5 border-l border-slate-200/60">
          <div class="flex items-center gap-2 bg-white/70 hover:bg-blue-50/90 border border-slate-200 hover:border-blue-300 pl-2 pr-3.5 py-1.5 rounded-xl shadow-2xs backdrop-blur-md cursor-pointer transition-all hover:scale-[1.02]">
            <div class="relative flex items-center justify-center w-7 h-7 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-black text-xs uppercase shrink-0 shadow-md shadow-blue-500/20">
              {{ currentUser?.username ? currentUser.username.charAt(0) : 'A' }}
              <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 border-2 border-white rounded-full"></span>
            </div>
            <div class="text-left">
              <span class="text-[9px] text-slate-400 block uppercase font-extrabold tracking-wider leading-none">{{ currentUser?.role || 'super_admin' }}</span>
              <span class="text-xs font-bold text-slate-800 leading-tight block mt-0.5">{{ currentUser?.username || 'admin' }}</span>
            </div>
          </div>
          <button @click="confirmExitPos" class="px-3 py-1.5 bg-white/70 hover:bg-rose-500/15 border border-slate-200 hover:border-rose-300 text-rose-600 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-2xs hover:scale-[1.02]">
            退出
          </button>
        </div>
      </div>
    </header>

    <!-- 中间主工作区 -->
    <div class="flex-1 flex overflow-hidden p-2 gap-2 pb-12">
      
      <!-- 左侧：商品搜索与购物车 -->
      <div class="flex-1 flex flex-col bg-white/75 backdrop-blur-xl rounded-xl border border-white/60 overflow-hidden shadow-lg">
        
        <div class="p-2.5 border-b border-slate-200/60 flex gap-2 bg-white/40 backdrop-blur-md">
          <div class="flex-1 relative">
            <input 
              ref="searchInputRef"
              v-model="deskSearchQuery" 
              @keydown="handleSearchKeydown"
              type="text" 
              placeholder="按 [/] 键聚焦，输入 OEM / 互换号 / 品名搜索..." 
              class="w-full bg-white/90 hover:bg-white focus:bg-white border border-slate-200/80 focus:border-blue-500 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 placeholder-slate-400 outline-none font-mono shadow-2xs transition-all font-bold"
            />
          </div>
          <div class="w-68 flex items-center gap-1.5">
            <button 
              @click="openClientSearchModal" 
              type="button"
              class="flex-1 bg-white/90 hover:bg-blue-50/70 border border-blue-300/60 hover:border-blue-500 text-slate-800 rounded-lg px-3.5 py-2.5 text-xs font-bold flex items-center justify-between transition-all shadow-2xs cursor-pointer truncate"
            >
              <div class="flex items-center gap-2 truncate">
                <span class="text-blue-600 text-sm">👤</span>
                <span class="truncate text-xs font-bold" :class="quoteClientName ? 'text-slate-900' : 'text-slate-400'">
                  {{ quoteClientName || '🔍 选择客户...' }}
                </span>
              </div>
              <span class="text-xs text-slate-400 ml-1">选择</span>
            </button>
            <button 
              v-if="quoteClientName"
              @click="quoteClientName = ''"
              title="清除当前选中客户"
              type="button"
              class="w-8 h-9.5 shrink-0 bg-slate-100 hover:bg-rose-500/20 text-slate-500 hover:text-rose-600 border border-slate-200 rounded-lg flex items-center justify-center text-xs font-bold transition-all cursor-pointer"
            >
              ✕
            </button>
          </div>
        </div>

        <!-- 搜索结果快捷点选栏 -->
        <div v-if="deskSearchQuery.trim()" class="max-h-56 overflow-y-auto border-b border-slate-200/60 bg-white/95 backdrop-blur-md p-2 space-y-1.5 z-20 shadow-xl">
          <div 
            v-for="(p, index) in filteredParts" 
            :key="p.oem" 
            :ref="el => { if (selectedIndex === index) activeItemRef = el }"
            @click="selectAndAddToCart(p)"
            @mouseenter="selectedIndex = index"
            :class="[
              selectedIndex === index ? 'bg-blue-500/15 border-blue-300 text-blue-950 shadow-2xs' : 'hover:bg-slate-100/70 border-slate-100 text-slate-800',
              p.stock <= 0 ? 'opacity-60 bg-slate-100/60' : ''
            ]"
            class="flex items-center justify-between p-2.5 rounded-lg cursor-pointer transition-all border text-sm"
          >
            <div>
              <span class="font-mono font-black text-blue-600 text-sm mr-3">{{ p.oem }}</span>
              <span class="font-bold text-slate-800">{{ p.name }}</span>
              <span class="text-xs text-slate-400 ml-2">({{ p.brand }})</span>
            </div>
            <div class="flex items-center gap-4 text-right">
              <div>
                <span class="text-sm font-mono font-black text-slate-900">${{ p.price.toFixed(2) }}</span>
                <span class="text-xs text-slate-400 font-mono block">Bs. {{ (p.price * bcvRate).toFixed(2) }}</span>
              </div>
              <span :class="p.stock > 0 ? 'text-emerald-600' : 'text-rose-600 font-bold'" class="text-xs font-mono font-black">
                库存: {{ p.stock }}
              </span>
            </div>
          </div>
          <div v-if="filteredParts.length === 0" class="text-center py-4 text-sm text-slate-400 font-bold">
            未找到相关配件商品
          </div>
        </div>

        <!-- 购物车明细表格：带有精美的斑马纹、行底边框与悬停高亮 -->
        <div class="flex-1 overflow-y-auto p-2.5">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b-2 border-slate-200 text-slate-600 text-xs font-extrabold uppercase bg-slate-100/50">
                <th class="py-3 px-3">OEM 编号</th>
                <th class="py-3 px-3">配件名称</th>
                <th class="py-3 px-3 text-right">单价 ($ / Bs.)</th>
                <th class="py-3 px-3 text-center">数量</th>
                <th class="py-3 px-3 text-right">小计 ($ / Bs.)</th>
                <th class="py-3 px-3 text-center">操作</th>
              </tr>
            </thead>
            <tbody class="text-sm font-medium">
              <tr 
                v-for="(item, index) in cartItems" 
                :key="item.oem" 
                :class="index % 2 === 0 ? 'bg-white/80' : 'bg-slate-50/70'"
                class="border-b border-slate-200/70 hover:bg-blue-50/50 transition-all shadow-2xs"
              >
                <td class="py-3 px-3 font-mono font-black text-blue-600 text-sm">{{ item.oem }}</td>
                <td class="py-3 px-3 text-slate-900 font-bold">{{ item.name }}</td>
                <td class="py-3 px-3 text-right font-mono text-slate-700 font-bold">
                  <div>${{ item.price.toFixed(2) }}</div>
                  <div class="text-xs text-slate-400 font-normal">Bs. {{ (item.price * bcvRate).toFixed(2) }}</div>
                </td>
                <td class="py-3 px-3 text-center">
                  <div class="inline-flex items-center border border-slate-300 rounded-lg overflow-hidden bg-white shadow-2xs">
                    <button @click="item.quantity > 1 ? item.quantity-- : null" class="px-2.5 py-1 text-slate-600 hover:bg-slate-200 font-bold text-sm">-</button>
                    <input v-model.number="item.quantity" type="number" min="1" class="w-10 text-center bg-transparent text-slate-900 text-sm font-mono outline-none font-black" />
                    <button @click="item.quantity++" class="px-2.5 py-1 text-slate-600 hover:bg-slate-200 font-bold text-sm">+</button>
                  </div>
                </td>
                <td class="py-3 px-3 text-right font-mono font-black text-emerald-600">
                  <div>${{ (item.price * item.quantity).toFixed(2) }}</div>
                  <div class="text-xs text-emerald-700/80 font-normal">Bs. {{ (item.price * item.quantity * bcvRate).toFixed(2) }}</div>
                </td>
                <td class="py-3 px-3 text-center">
                  <button @click="cartItems.splice(index, 1)" class="text-rose-600 text-xs font-bold px-2.5 py-1 bg-rose-500/10 hover:bg-rose-500/20 rounded-lg transition-all cursor-pointer shadow-2xs">删除</button>
                </td>
              </tr>
              <tr v-if="cartItems.length === 0">
                <td colspan="6" class="text-center py-20 text-slate-400 text-sm font-bold">
                  🛒 购物车为空，请扫码或搜索添加配件商品...
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>

      <!-- 右侧：组合支付面板 -->
      <div class="w-[410px] flex flex-col bg-white/75 backdrop-blur-xl rounded-xl border border-white/60 p-3.5 shadow-lg justify-between shrink-0 overflow-y-auto max-h-full">
        
        <div class="space-y-2.5">
          <div class="flex items-center justify-between border-b border-slate-200/60 pb-2">
            <h3 class="font-bold text-xs text-slate-800 uppercase tracking-wider">💳 多通道组合支付</h3>
            <button 
              @click="toggleMainCurrency" 
              type="button"
              class="bg-blue-500/10 hover:bg-blue-500/20 text-blue-700 border border-blue-200/60 px-2.5 py-1 rounded-lg text-xs font-bold font-mono transition-all cursor-pointer shadow-2xs flex items-center gap-1"
            >
              <span>🔄 主显: {{ primaryCurrency === 'USD' ? '美元 ($)' : 'Bs.' }}</span>
            </button>
          </div>

          <div class="space-y-2 text-sm">
            <!-- 1. Cash USD -->
            <div class="bg-white/70 hover:bg-white p-2 rounded-xl border border-white/90 hover:border-blue-300 transition-all flex items-center justify-between shadow-2xs">
              <div>
                <span class="font-bold text-slate-800 flex items-center gap-1">💵 美金现金 Cash USD <span class="text-[10px] text-blue-600 font-mono">[F4]</span></span>
                <span class="text-xs text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ Bs. ${((Number(paymentSplit.cashUsd) || 0) * bcvRate).toFixed(2)}` : `≈ $${(Number(paymentSplit.cashUsd) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">$</span>
                <input 
                  ref="cashUsdInputRef"
                  v-model.number="paymentSplit.cashUsd" 
                  @keydown="handlePaymentKeydown($event, 'cashUsd')"
                  type="number" step="0.5" placeholder="0.00" 
                  class="w-26 bg-white/90 focus:bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-right font-mono font-black text-slate-900 outline-none focus:border-blue-500 text-sm" 
                />
              </div>
            </div>

            <!-- 2. Efectivo Bs. -->
            <div class="bg-white/70 hover:bg-white p-2 rounded-xl border border-white/90 hover:border-blue-300 transition-all flex items-center justify-between shadow-2xs">
              <div>
                <span class="font-bold text-slate-800 flex items-center gap-1">🇻🇪 玻利瓦尔现金 <span class="text-[10px] text-blue-600 font-mono">[F5]</span></span>
                <span class="text-xs text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.cashBs) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.cashBs) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">Bs.</span>
                <input 
                  ref="cashBsInputRef"
                  v-model.number="paymentSplit.cashBs" 
                  @keydown="handlePaymentKeydown($event, 'cashBs')"
                  type="number" step="10" placeholder="0.00" 
                  class="w-26 bg-white/90 focus:bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-right font-mono font-black text-slate-900 outline-none focus:border-blue-500 text-sm" 
                />
              </div>
            </div>

            <!-- 3. Card POS -->
            <div class="bg-white/70 hover:bg-white p-2 rounded-xl border border-white/90 hover:border-blue-300 transition-all flex items-center justify-between shadow-2xs">
              <div>
                <span class="font-bold text-slate-800 flex items-center gap-1">💳 刷卡 POS (Bs.) <span class="text-[10px] text-blue-600 font-mono">[F6]</span></span>
                <span class="text-xs text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.cardPos) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.cardPos) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">Bs.</span>
                <input 
                  ref="cardPosInputRef"
                  v-model.number="paymentSplit.cardPos" 
                  @keydown="handlePaymentKeydown($event, 'cardPos')"
                  type="number" step="10" placeholder="0.00" 
                  class="w-26 bg-white/90 focus:bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-right font-mono font-black text-slate-900 outline-none focus:border-blue-500 text-sm" 
                />
              </div>
            </div>

            <!-- 4. Pago Móvil -->
            <div class="bg-white/70 hover:bg-white p-2 rounded-xl border border-white/90 hover:border-blue-300 transition-all flex items-center justify-between shadow-2xs">
              <div>
                <span class="font-bold text-slate-800 flex items-center gap-1">⚡ 手机支付 Pago Móvil <span class="text-[10px] text-blue-600 font-mono">[F7]</span></span>
                <span class="text-xs text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.pagoMovil) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.pagoMovil) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">Bs.</span>
                <input 
                  ref="pagoMovilInputRef"
                  v-model.number="paymentSplit.pagoMovil" 
                  @keydown="handlePaymentKeydown($event, 'pagoMovil')"
                  type="number" step="10" placeholder="0.00" 
                  class="w-26 bg-white/90 focus:bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-right font-mono font-black text-slate-900 outline-none focus:border-blue-500 text-sm" 
                />
              </div>
            </div>
          </div>

          <!-- 回执号码：左侧为纯文本标签“回执号码”，右侧为输入框 -->
          <div class="flex items-center gap-2 bg-white/70 hover:bg-white border border-slate-200 hover:border-blue-300 rounded-xl px-3 py-2 shadow-2xs transition-all">
            <span class="w-1/3 text-xs font-black text-slate-700 shrink-0 truncate">回执号码:</span>
            <input 
              v-model="paymentReference" 
              type="text" 
              placeholder="选填，如 Pago Móvil 回执号..." 
              class="w-2/3 bg-transparent text-xs font-bold text-slate-900 outline-none font-mono placeholder-slate-400" 
            />
          </div>
        </div>

        <!-- 底部应付、已付、找零区域 -->
        <div class="space-y-3 pt-3 border-t border-slate-200/60 mt-1">
          <div class="space-y-2">
            <!-- 总应付金额 -->
            <div class="flex justify-between items-start text-base font-bold text-slate-700">
              <span class="font-extrabold text-slate-800">总应付金额:</span>
              <div class="text-right">
                <div class="font-mono text-slate-900 text-lg font-black">{{ primaryCurrency === 'USD' ? `$${totalUsd.toFixed(2)}` : `Bs. ${(totalUsd * bcvRate).toFixed(2)}` }}</div>
                <div class="font-mono text-xs text-slate-400 font-semibold">{{ primaryCurrency === 'USD' ? `Bs. ${(totalUsd * bcvRate).toFixed(2)}` : `$${totalUsd.toFixed(2)}` }}</div>
              </div>
            </div>

            <!-- 已付金额 -->
            <div class="flex justify-between items-start text-base font-bold text-slate-700">
              <span class="font-extrabold text-slate-800">已付金额 (Paid):</span>
              <div class="text-right">
                <div class="font-mono text-emerald-600 text-lg font-black">{{ primaryCurrency === 'USD' ? `$${totalPaidUsd.toFixed(2)}` : `Bs. ${(totalPaidUsd * bcvRate).toFixed(2)}` }}</div>
                <div class="font-mono text-xs text-emerald-700/80 font-semibold">{{ primaryCurrency === 'USD' ? `Bs. ${(totalPaidUsd * bcvRate).toFixed(2)}` : `$${totalPaidUsd.toFixed(2)}` }}</div>
              </div>
            </div>

            <!-- 待付余额 / 找零 -->
            <div class="pt-2 border-t border-slate-200/60 flex justify-between items-start">
              <span class="text-base font-black pt-0.5" :class="balanceRemaining > 0 ? 'text-rose-600' : 'text-emerald-600'">
                {{ balanceRemaining > 0 ? '🔴 待付余额:' : '🟢 找零 (Cambio):' }}
              </span>
              <div class="text-right">
                <div class="text-2xl font-black font-mono leading-tight" :class="balanceRemaining > 0 ? 'text-rose-600' : 'text-emerald-600'">
                  {{ primaryCurrency === 'USD' ? `$${Math.abs(balanceRemaining).toFixed(2)}` : `Bs. ${(Math.abs(balanceRemaining) * bcvRate).toFixed(2)}` }}
                </div>
                <div class="font-mono text-xs font-bold" :class="balanceRemaining > 0 ? 'text-rose-500' : 'text-emerald-500'">
                  {{ primaryCurrency === 'USD' ? `Bs. ${(Math.abs(balanceRemaining) * bcvRate).toFixed(2)}` : `$${Math.abs(balanceRemaining).toFixed(2)}` }}
                </div>
              </div>
            </div>
          </div>

          <button 
            @click="openPreviewModal"
            :disabled="!isFullyPaid || cartItems.length === 0"
            class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl font-black text-sm shadow-md shadow-emerald-600/30 transition-all cursor-pointer flex items-center justify-center gap-1.5"
          >
            <span>🚀 确认收款并出单 ({{ cartItems.length === 0 ? '购物车为空' : (balanceRemaining < 0 ? `找零 $${Math.abs(balanceRemaining).toFixed(2)}` : '已付清') }})</span>
          </button>
        </div>

      </div>

    </div>

    <!-- 底部快捷键导航栏 -->
    <footer class="absolute bottom-0 left-0 right-0 h-11 bg-white/75 backdrop-blur-xl border-t border-white/60 px-3 flex items-center justify-between z-30 shadow-md">
      <div class="grid grid-cols-6 gap-2 w-full">
        <div @click="focusSearch" class="bg-white/70 hover:bg-blue-500/10 border border-slate-200 hover:border-blue-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 font-bold">聚焦搜索 [/]</span>
          <span class="bg-blue-500/15 text-blue-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">F4~F7支付</span>
        </div>
        <div @click="openClientSearchModal" class="bg-white/70 hover:bg-blue-500/10 border border-slate-200 hover:border-blue-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 font-bold">选客户</span>
          <span class="bg-blue-500/15 text-blue-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+F</span>
        </div>
        <div @click="holdCurrentOrder" class="bg-white/70 hover:bg-amber-500/10 border border-slate-200 hover:border-amber-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 font-bold">云端挂单</span>
          <span class="bg-amber-500/15 text-amber-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+H</span>
        </div>
        <div @click="$emit('clear-cart')" class="bg-white/70 hover:bg-rose-500/10 border border-slate-200 hover:border-rose-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 font-bold">清空购物车</span>
          <span class="bg-rose-500/15 text-rose-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+B</span>
        </div>
        <div @click="deleteLastItem" class="bg-white/70 hover:bg-rose-500/10 border border-slate-200 hover:border-rose-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 font-bold">删末项</span>
          <span class="bg-rose-500/15 text-rose-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Delete</span>
        </div>
        <div @click="confirmExitPos" class="bg-white/70 hover:bg-slate-200/80 border border-slate-200 hover:border-slate-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 font-bold">返回后台</span>
          <span class="bg-slate-200 text-slate-800 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Esc</span>
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
    <div v-if="recallModalVisible" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div class="bg-white/85 backdrop-blur-xl rounded-3xl shadow-2xl max-w-xl w-full overflow-hidden border border-white/60 flex flex-col max-h-[80vh]">
        <div class="p-4 border-b border-slate-200/60 flex items-center justify-between bg-white/40">
          <h3 class="font-bold text-sm text-slate-800 flex items-center gap-2">
            <span>📦 云端挂单恢复大厅 (共 {{ heldOrders.length }} 单)</span>
          </h3>
          <button @click="recallModalVisible = false" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-4 space-y-2.5">
          <div v-for="order in heldOrders" :key="order.id" class="p-3.5 rounded-2xl border border-slate-200/60 bg-white/60 hover:bg-blue-500/10 transition-all flex items-center justify-between shadow-2xs hover:scale-[1.01]">
            <div class="space-y-1">
              <div class="font-bold text-xs text-slate-800 flex items-center gap-2">
                <span class="font-mono text-blue-600">{{ order.hold_no }}</span>
                <span>👤 {{ order.client_name || '散客' }}</span>
              </div>
              <div class="text-[11px] text-slate-400 font-mono">挂单时间: {{ order.timestamp }}</div>
            </div>
            <div class="flex items-center gap-3">
              <span class="text-sm font-mono font-black text-slate-900">${{ order.total_amount.toFixed(2) }}</span>
              <button @click="recallOrder(order)" class="px-3.5 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition-all cursor-pointer shadow-sm hover:scale-105">
                恢复取单
              </button>
              <button @click="deleteHeldOrder(order.id)" class="px-2.5 py-1.5 bg-rose-500/10 hover:bg-rose-500/20 text-rose-600 rounded-xl text-xs font-bold transition-all hover:scale-105 cursor-pointer">
                作废
              </button>
            </div>
          </div>
          <div v-if="heldOrders.length === 0" class="text-center py-10 text-slate-400 text-xs">
            当前云端挂单池为空
          </div>
        </div>

        <div class="p-3 bg-white/40 border-t border-slate-200/60 text-right">
          <button @click="recallModalVisible = false" class="px-4 py-1.5 bg-slate-200/80 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-all cursor-pointer">
            取消
          </button>
        </div>
      </div>
    </div>

    <!-- 交接班 Modal -->
    <div v-if="shiftReportModalVisible" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div class="bg-white/85 backdrop-blur-xl rounded-3xl shadow-2xl max-w-2xl w-full overflow-hidden border border-white/60 flex flex-col max-h-[92vh]">
        <div class="p-4 border-b border-slate-200/60 flex items-center justify-between bg-white/40">
          <h3 class="font-bold text-sm text-slate-800 flex items-center gap-2">
            <span>📊 收银交接班与营业汇总 (Shift Handover)</span>
          </h3>
          <button @click="shiftReportModalVisible = false" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-4 text-xs bg-white/30">
          
          <div class="bg-white/70 backdrop-blur-md p-3.5 rounded-2xl border border-white/80 space-y-2 shadow-2xs font-mono">
            <div class="text-[11px] font-bold text-slate-400 uppercase tracking-wider border-b border-slate-200/60 pb-1.5">
              1. 系统统计应收 (SYSTEM SNAPSHOT)
            </div>
            <div class="grid grid-cols-2 gap-x-6 gap-y-1.5">
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
            </div>
            <div class="pt-1.5 border-t border-slate-200/60 flex justify-between items-center text-xs font-black">
              <span class="text-slate-900">系统总营业额 (USD):</span>
              <span class="text-emerald-600 text-sm">${{ shiftStats.totalUsd.toFixed(2) }}</span>
            </div>
          </div>

          <div class="bg-blue-500/10 backdrop-blur-md p-3.5 rounded-2xl border border-blue-200/80 space-y-2.5 font-mono">
            <div class="text-[11px] font-bold text-blue-900 uppercase tracking-wider border-b border-blue-200/60 pb-1.5 flex justify-between items-center">
              <span>2. 收银员实盘录入款项 (ACTUAL COUNT)</span>
              <span class="text-[10px] text-blue-700 font-normal">请录入抽屉及账面实际金额</span>
            </div>

            <div class="grid grid-cols-2 gap-2.5">
              <div class="bg-white/80 p-2 rounded-xl border border-blue-200/60 space-y-1 shadow-2xs">
                <label class="block text-[10px] font-bold text-slate-700">💵 实收美金现金 (USD):</label>
                <div class="flex items-center gap-1">
                  <span class="text-slate-400 font-bold">$</span>
                  <input 
                    v-model.number="actualCounts.cashUsd" 
                    type="number" step="0.5" placeholder="0.00" 
                    class="w-full bg-white border border-slate-200 rounded-lg px-2 py-1 text-right font-mono text-xs outline-none focus:border-blue-500 font-bold text-slate-900"
                  />
                </div>
                <div class="text-[10px] text-right font-bold" :class="cashUsdDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ cashUsdDiff >= 0 ? '+' : '' }}${{ cashUsdDiff.toFixed(2) }}
                </div>
              </div>

              <div class="bg-white/80 p-2 rounded-xl border border-blue-200/60 space-y-1 shadow-2xs">
                <label class="block text-[10px] font-bold text-slate-700">🇻🇪 实收 Bs. 现金 (Bs.):</label>
                <div class="flex items-center gap-1">
                  <span class="text-slate-400 font-bold">Bs.</span>
                  <input 
                    v-model.number="actualCounts.cashBs" 
                    type="number" step="10" placeholder="0.00" 
                    class="w-full bg-white border border-slate-200 rounded-lg px-2 py-1 text-right font-mono text-xs outline-none focus:border-blue-500 font-bold text-slate-900"
                  />
                </div>
                <div class="text-[10px] text-right font-bold" :class="cashBsDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ cashBsDiff >= 0 ? '+' : '' }}Bs. {{ cashBsDiff.toFixed(2) }}
                </div>
              </div>

              <div class="bg-white/80 p-2 rounded-xl border border-blue-200/60 space-y-1 shadow-2xs">
                <label class="block text-[10px] font-bold text-slate-700">💳 实收 POS 刷卡 (Bs.):</label>
                <div class="flex items-center gap-1">
                  <span class="text-slate-400 font-bold">Bs.</span>
                  <input 
                    v-model.number="actualCounts.cardPos" 
                    type="number" step="10" placeholder="0.00" 
                    class="w-full bg-white border border-slate-200 rounded-lg px-2 py-1 text-right font-mono text-xs outline-none focus:border-blue-500 font-bold text-slate-900"
                  />
                </div>
                <div class="text-[10px] text-right font-bold" :class="cardPosDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ cardPosDiff >= 0 ? '+' : '' }}Bs. {{ cardPosDiff.toFixed(2) }}
                </div>
              </div>

              <div class="bg-white/80 p-2 rounded-xl border border-blue-200/60 space-y-1 shadow-2xs">
                <label class="block text-[10px] font-bold text-slate-700">⚡ 实收 Pago Móvil (Bs.):</label>
                <div class="flex items-center gap-1">
                  <span class="text-slate-400 font-bold">Bs.</span>
                  <input 
                    v-model.number="actualCounts.pagoMovil" 
                    type="number" step="10" placeholder="0.00" 
                    class="w-full bg-white border border-slate-200 rounded-lg px-2 py-1 text-right font-mono text-xs outline-none focus:border-blue-500 font-bold text-slate-900"
                  />
                </div>
                <div class="text-[10px] text-right font-bold" :class="pagoMovilDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ pagoMovilDiff >= 0 ? '+' : '' }}Bs. {{ pagoMovilDiff.toFixed(2) }}
                </div>
              </div>
            </div>

            <div class="pt-1.5 border-t border-blue-200/60 flex justify-between items-center text-xs">
              <span class="font-bold text-slate-700">折算总盈亏 (Diferencia Total):</span>
              <span :class="totalUsdDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'" class="font-black font-mono text-sm">
                {{ totalUsdDiff >= 0 ? '+' : '' }}${{ totalUsdDiff.toFixed(2) }}
              </span>
            </div>
          </div>

          <div v-if="totalUsdDiff !== 0" class="space-y-1">
            <label class="block font-semibold text-slate-500 uppercase text-[11px]">盈亏原因备注</label>
            <input v-model="handoverNotes" type="text" placeholder="例如：Bs. 零钱误差 / Pago Móvil 延迟到账..." class="w-full bg-white/80 border border-slate-200 rounded-xl px-3 py-1.5 text-xs outline-none focus:border-blue-500 shadow-2xs" />
          </div>
        </div>

        <div class="p-3.5 bg-white/60 backdrop-blur-md border-t border-slate-200/60 flex gap-2.5">
          <button @click="shiftReportModalVisible = false" class="flex-1 py-2.5 bg-slate-100 hover:bg-slate-200 text-slate-700 rounded-xl text-xs font-bold transition-all cursor-pointer">
            取消
          </button>
          <button @click="submitShiftHandover" class="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black shadow-md shadow-emerald-600/20 transition-all cursor-pointer flex items-center justify-center gap-1.5 hover:scale-[1.01]">
            <span>🔒 确认交班并锁定锁班</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 小票预览 Modal -->
    <div v-if="previewModalVisible" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div class="bg-white/85 backdrop-blur-xl rounded-3xl shadow-2xl max-w-md w-full overflow-hidden border border-white/60 flex flex-col max-h-[90vh]">
        <div class="p-4 border-b border-slate-200/60 flex items-center justify-between bg-white/40">
          <h3 class="font-bold text-sm text-slate-800 flex items-center gap-2">
            <span>🧾 收银小票实时预览 (Pago Mixto)</span>
          </h3>
          <button @click="previewModalVisible = false" class="text-slate-400 hover:text-slate-600 text-sm font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-3 font-mono text-xs bg-white/30">
          <div class="text-center pb-2.5 border-b border-dashed border-slate-300 space-y-1">
            <div class="font-black text-xs text-slate-900">{{ systemConfig.company_name || 'TOSTIYK (TK) - VENEZUELA' }}</div>
            <div class="text-[10px] text-blue-600 font-bold">RIF: {{ systemConfig.rif || 'J-00000000-0' }}</div>
            <div class="text-[10px] text-slate-500">{{ systemConfig.address || 'Valencia, Carabobo' }}</div>
          </div>

          <div class="space-y-1 text-slate-700 pb-2.5 border-b border-dashed border-slate-300">
            <div><span class="font-bold">Client:</span> {{ quoteClientName || 'Cliente General' }}</div>
            <div><span class="font-bold">Operator:</span> {{ currentUser?.username || 'admin' }}</div>
            <div class="font-bold text-blue-600">Payment Breakdown:</div>
            <div v-if="paymentSplit.cashUsd > 0"> - Cash USD: ${{ paymentSplit.cashUsd.toFixed(2) }} (Bs. {{ (paymentSplit.cashUsd * bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.cashBs > 0"> - Efectivo Bs.: Bs. {{ paymentSplit.cashBs.toFixed(2) }} (${{ (paymentSplit.cashBs / bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.cardPos > 0"> - Card POS: Bs. {{ paymentSplit.cardPos.toFixed(2) }} (${{ (paymentSplit.cardPos / bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.pagoMovil > 0"> - Pago Móvil: Bs. {{ paymentSplit.pagoMovil.toFixed(2) }} (${{ (paymentSplit.pagoMovil / bcvRate).toFixed(2) }})</div>
            <div v-if="balanceRemaining < 0"> - cambio (找零): ${{ Math.abs(balanceRemaining).toFixed(2) }} (Bs. {{ (Math.abs(balanceRemaining) * bcvRate).toFixed(2) }})</div>
            <div v-if="paymentReference"><span class="font-bold">Ref:</span> {{ paymentReference }}</div>
          </div>

          <div class="space-y-1.5 pb-2.5 border-b border-dashed border-slate-300">
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

          <div class="space-y-1 text-right pb-1">
            <div class="text-base font-black text-slate-900">Total: ${{ totalUsd.toFixed(2) }} / Bs. {{ (totalUsd * bcvRate).toFixed(2) }}</div>
          </div>
        </div>

        <div class="p-3.5 bg-white/60 backdrop-blur-md border-t border-slate-200/60 flex gap-2.5">
          <button @click="previewModalVisible = false" class="flex-1 py-2.5 bg-slate-100 text-slate-700 rounded-xl text-xs font-bold hover:bg-slate-200 transition-all">返回修改</button>
          <button @click="confirmAndPrint" class="flex-1 py-2.5 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black shadow-md shadow-emerald-600/20 transition-all hover:scale-[1.01]">确认出单并打印</button>
        </div>
      </div>
    </div>

    <!-- 快捷键指南弹窗 -->
    <PosHelpModal :visible="helpModalVisible" @close="helpModalVisible = false" />

    <!-- 客户快速搜索 Modal -->
    <div v-if="clientModalVisible" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-4">
      <div class="bg-white/85 backdrop-blur-xl rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden border border-white/60 flex flex-col max-h-[80vh]">
        <div class="p-4 border-b border-slate-200/60 flex items-center justify-between bg-white/40">
          <h3 class="font-bold text-sm text-slate-800">快捷选择客户</h3>
          <button @click="clientModalVisible = false" class="text-slate-400 font-bold">✕</button>
        </div>
        <div class="p-3.5 border-b border-slate-200/60">
          <input ref="clientModalInputRef" v-model="clientFilterQuery" @keydown="handleClientModalKeydown" type="text" placeholder="搜索客户..." class="w-full bg-white/80 border border-slate-200 rounded-xl px-3.5 py-2 text-xs outline-none focus:border-blue-500 shadow-2xs" />
        </div>
        <div class="flex-1 overflow-y-auto p-2.5 space-y-1.5">
          <div v-for="c in filteredModalClients" :key="c.id" @click="selectClient(c.name)" class="p-2.5 rounded-xl border border-slate-200/60 bg-white/50 cursor-pointer hover:bg-blue-500/10 hover:border-blue-300 transition-all flex items-center justify-between text-xs shadow-2xs hover:scale-[1.01]">
            <div><div class="font-bold">🏢 {{ c.name }}</div><div class="text-[11px] text-slate-400 font-mono">RIF: {{ c.rif_or_cedula || '-' }}</div></div>
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

const paymentSplit = ref({
  cashUsd: 0,
  cashBs: 0,
  cardPos: 0,
  pagoMovil: 0
})

const totalUsd = computed(() => {
  return props.cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
})

const totalPaidUsd = computed(() => {
  const cUsd = Number(paymentSplit.value.cashUsd) || 0
  const cBs = Number(paymentSplit.value.cashBs) || 0
  const cCard = Number(paymentSplit.value.cardPos) || 0
  const cPago = Number(paymentSplit.value.pagoMovil) || 0

  const rate = props.bcvRate || 1
  const paidInUsd = cUsd + (cBs / rate) + (cCard / rate) + (cPago / rate)
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
      pagoMovil: 0
    }
  } else {
    paymentSplit.value = { cashUsd: 0, cashBs: 0, cardPos: 0, pagoMovil: 0 }
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
  totalUsd: 0,
  totalCount: 0
})

const actualCounts = ref({
  cashUsd: 0,
  cashBs: 0,
  cardPos: 0,
  pagoMovil: 0
})
const handoverNotes = ref('')

const cashUsdDiff = computed(() => Number(((actualCounts.value.cashUsd || 0) - shiftStats.value.cashUsd.amount).toFixed(2)))
const cashBsDiff = computed(() => Number(((actualCounts.value.cashBs || 0) - (shiftStats.value.cashBs.amount * (props.bcvRate || 1))).toFixed(2)))
const cardPosDiff = computed(() => Number(((actualCounts.value.cardPos || 0) - (shiftStats.value.cardPos.amount * (props.bcvRate || 1))).toFixed(2)))
const pagoMovilDiff = computed(() => Number(((actualCounts.value.pagoMovil || 0) - (shiftStats.value.pagoMovil.amount * (props.bcvRate || 1))).toFixed(2)))

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
      system_debt_usd: 0,
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
  selectedIndex.value = 0
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
    let cUsd = 0, cBs = 0, cardAmt = 0, pUsd = 0, tUsd = 0
    ordersData.forEach(o => {
      tUsd += o.totalUsd
      if (o.paymentMethod === 'Cash_USD') cUsd += o.totalUsd
      else if (o.paymentMethod === 'Cash_Bs') cBs += o.totalUsd
      else if (o.paymentMethod === 'Card_POS') cardAmt += o.totalUsd
      else if (o.paymentMethod === 'Pago_Movil') pUsd += o.totalUsd
    })
    shiftStats.value = {
      cashUsd: { amount: cUsd, count: ordersData.length },
      cashBs: { amount: cBs, count: 0 },
      cardPos: { amount: cardAmt, count: 0 },
      pagoMovil: { amount: pUsd, count: 0 },
      totalUsd: tUsd,
      totalCount: ordersData.length
    }

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
      payment_method: 'Cash_USD',
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

  if (e.key === '/' && document.activeElement !== searchInputRef.value) { e.preventDefault(); focusSearch(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'f') { e.preventDefault(); openClientSearchModal(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'h') { e.preventDefault(); holdCurrentOrder(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'r') { e.preventDefault(); openRecallModal(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'b') { e.preventDefault(); emit('clear-cart'); return }
}

const handleSearchKeydown = (e) => {
  const results = filteredParts.value
  if (results.length === 0) return

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    selectedIndex.value = (selectedIndex.value + 1) % results.length
    if (activeItemRef.value && typeof activeItemRef.value.scrollIntoView === 'function') {
      activeItemRef.value.scrollIntoView({ block: 'nearest' })
    }
  } else if (e.key === 'ArrowUp') {
    e.preventDefault()
    selectedIndex.value = (selectedIndex.value - 1 + results.length) % results.length
    if (activeItemRef.value && typeof activeItemRef.value.scrollIntoView === 'function') {
      activeItemRef.value.scrollIntoView({ block: 'nearest' })
    }
  } else if (e.key === 'Enter') {
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