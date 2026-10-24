<!-- src/components/QuotationDeskView.vue -->
<template>
  <div class="fixed inset-0 bg-slate-950/25 backdrop-blur-md z-40 flex flex-col overflow-hidden text-slate-900 dark:text-white font-sans transition-all">
    
    <!-- 结账成功的全屏绿色对勾遮罩 -->
    <div v-if="checkoutSuccessVisible" class="fixed inset-0 z-[100] bg-slate-900/80 backdrop-blur-sm flex items-center justify-center flex-col transition-all duration-300">
      <div class="w-40 h-40 bg-emerald-500 rounded-full flex items-center justify-center shadow-[0_0_60px_rgba(16,185,129,0.6)] animate-pop-in">
        <svg class="w-24 h-24 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="3" d="M5 13l4 4L19 7"></path>
        </svg>
      </div>
      <h2 class="text-white text-2xl font-black mt-8 tracking-widest drop-shadow-lg">{{ tExt.checkoutSuccessTitle }}</h2>
    </div>

    <!-- 右上角提示条 -->
    <transition name="fade">
      <div v-if="toastMessage" :class="toastType === 'success' ? 'bg-emerald-600/90 border-emerald-400/30' : 'bg-rose-600/90 border-rose-400/30'" class="fixed top-2 right-4 z-[100] text-white px-4 py-3 rounded-xl shadow-xl backdrop-blur-md border flex items-center gap-2 text-sm font-bold animate-bounce">
        <span>{{ toastType === 'success' ? '✅' : '❌' }}</span>
        <span>{{ toastMessage }}</span>
      </div>
    </transition>

    <!-- 顶部状态栏 -->
    <header class="h-12 bg-white dark:bg-slate-800/75 backdrop-blur-xl border-b border-white/60 px-4 flex items-center justify-between shrink-0 shadow-2xs">
      <div class="flex items-center space-x-3">
        <span class="text-white text-xs px-2.5 py-1 rounded-lg font-mono font-bold shadow-2xs bg-amber-500">
          QUOTE v1.0
        </span>
        <span class="text-sm font-bold text-slate-700 dark:text-slate-300">📅 {{ currentDateTime }}</span>
        <span class="text-sm text-emerald-600 font-mono font-bold">{{ t.dashboard.bcvLabel }}: {{ bcvRate }}</span>
        
        <button v-if="!isQuoteMode && heldOrders.length > 0" @click="openRecallModal" class="bg-white dark:bg-slate-800/70 hover:bg-amber-500/10 text-amber-800 dark:text-amber-400 border border-slate-200 dark:border-slate-700 hover:border-amber-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <span>📦 {{ t.pos.holdPool }} ({{ heldOrders.length }}) [Ctrl+R]</span>
        </button>
      </div>
      
      <div class="flex items-center space-x-2.5">
        <button v-if="!isQuoteMode" @click="openHistoryModal" class="bg-white dark:bg-slate-800/70 hover:bg-white dark:bg-slate-800/90 text-indigo-700 border border-slate-200 dark:border-slate-700 hover:border-indigo-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <span>📜 {{ t.pos.salesHistory }}</span>
        </button>
        <button v-if="!isQuoteMode" @click="openShiftReportModal" class="bg-white dark:bg-slate-800/70 hover:bg-white dark:bg-slate-800/90 text-emerald-700 border border-slate-200 dark:border-slate-700 hover:border-emerald-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <span>📊 {{ t.pos.shiftReport }}</span>
        </button>
        <button @click="helpModalVisible = true" class="bg-white dark:bg-slate-800/70 hover:bg-white dark:bg-slate-800/90 text-blue-600 border border-slate-200 dark:border-slate-700 hover:border-blue-300 px-3 py-1.5 rounded-xl text-xs font-bold transition-all flex items-center gap-1 cursor-pointer shadow-2xs hover:scale-[1.02]">
          <span>⌨️ {{ t.pos.shortcutGuide }}</span>
        </button>

        <div class="flex items-center gap-2.5 pl-2.5 border-l border-slate-200 dark:border-slate-700/60">
          <div class="flex items-center gap-2 bg-white dark:bg-slate-800/70 hover:bg-blue-50/90 border border-slate-200 dark:border-slate-700 hover:border-blue-300 pl-2 pr-3.5 py-1.5 rounded-xl shadow-2xs backdrop-blur-md cursor-pointer transition-all hover:scale-[1.02]">
            <div class="relative flex items-center justify-center w-7 h-7 rounded-lg bg-gradient-to-tr from-blue-600 to-indigo-600 text-white font-black text-xs uppercase shrink-0 shadow-md shadow-blue-500/20">
              {{ currentUser?.username ? currentUser.username.charAt(0) : 'U' }}
              <span class="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 border-2 border-white rounded-full"></span>
            </div>
            <div class="text-left">
              <span class="text-[9px] text-slate-400 block uppercase font-extrabold tracking-wider leading-none">{{ currentUser?.role || 'staff' }}</span>
              <span class="text-xs font-bold text-slate-800 dark:text-slate-200 leading-tight block mt-0.5">{{ currentUser?.username || 'User' }}</span>
            </div>
          </div>
          <button @click="confirmExitPos" class="px-3 py-1.5 bg-white dark:bg-slate-800/70 hover:bg-rose-500/15 border border-slate-200 dark:border-slate-700 hover:border-rose-300 text-rose-600 rounded-xl text-xs font-bold transition-all cursor-pointer shadow-2xs hover:scale-[1.02]">
            {{ t.pos.exit }}
          </button>
        </div>
      </div>
    </header>

    <!-- 中间主工作区 -->
    <div class="flex-1 flex overflow-hidden p-2 gap-2 pb-12">
      
      <!-- 左侧：商品搜索与购物车 -->
      <div class="flex-1 flex flex-col bg-white dark:bg-slate-800/75 backdrop-blur-xl rounded-xl border border-white/60 overflow-hidden shadow-lg">
        
        <!-- 顶部工具栏 -->
        <div class="p-2.5 border-b border-slate-200 dark:border-slate-700/60 flex gap-2 bg-white dark:bg-slate-800/40 backdrop-blur-md items-center w-full">
          
          <!-- 1. 配件搜索框 -->
          <div class="relative w-1/2">
            <input
              data-testid="quote-search-input" 
              ref="searchInputRef"
              v-model="deskSearchQuery" 
              @keydown="handleSearchKeydown"
              type="text" 
              :placeholder="t.pos.searchPlaceholder" 
              class="w-full bg-white dark:bg-slate-800/90 hover:bg-white dark:bg-slate-800 focus:bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700/80 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/30 rounded-lg px-3.5 py-2.5 text-sm text-slate-900 dark:text-white placeholder-slate-400 outline-none font-mono shadow-2xs transition-all font-bold"
            />
          </div>
          
          <!-- 2. 已选客户信息展示区 -->
          <div class="w-1/4">
            <div v-if="quoteClientName" class="flex items-center justify-between bg-blue-50/80 border border-blue-200/80 px-3 py-1.5 rounded-lg shadow-2xs w-full">
              <div class="flex items-center gap-2 flex-1 truncate">
                <span class="text-blue-600 text-lg">👤</span>
                <div class="truncate">
                  <div class="text-sm font-bold text-slate-800 dark:text-slate-200 leading-tight truncate">{{ quoteClientName }}</div>
                  <div class="text-[10px] text-blue-600/70 font-semibold truncate">{{ tExt.clientSelected }}</div>
                </div>
              </div>
              <button @click="quoteClientName = ''; quoteClientId = null" :title="tExt.clearClient" class="text-slate-400 hover:text-rose-500 hover:bg-rose-100 rounded-md p-1 transition-colors cursor-pointer shrink-0 ml-1">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>
            <div v-else class="flex items-center justify-center border border-dashed border-slate-300 dark:border-slate-600 bg-slate-50 dark:bg-slate-900/50 rounded-lg px-3 py-2.5 text-slate-400 text-xs font-semibold w-full">
              {{ tExt.noClientSelected }}
            </div>
          </div>

          <!-- 3. 搜索/切换客户按钮 -->
          <div class="w-1/4">
            <button 
              @click="openClientSearchModal" 
              type="button"
              class="w-full flex items-center justify-between bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 hover:border-blue-400 hover:bg-blue-50 text-slate-600 dark:text-slate-400 rounded-lg px-3.5 py-2.5 text-xs font-bold transition-all shadow-2xs cursor-pointer"
            >
              <div class="flex items-center gap-1.5 truncate">
                <span class="text-blue-500">🔍</span>
                <span class="truncate">{{ t.pos.selectClient }}</span>
              </div>
              <span class="text-slate-400 font-mono text-[10px] hidden sm:inline">Ctrl+F</span>
            </button>
          </div>
        </div>

        <!-- 购物车明细表格 -->
        <div class="flex-1 overflow-y-auto p-2.5">
          <table data-testid="cart-table" class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b-2 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 text-xs font-extrabold uppercase bg-slate-100 dark:bg-slate-800/50">
                <th class="py-3 px-3">{{ tExt.cartOem }}</th>
                <th class="py-3 px-3">{{ tExt.cartName }}</th>
                <th class="py-3 px-3 text-right">{{ tExt.cartPrice }}</th>
                <th class="py-3 px-3 text-center">{{ tExt.cartQty }}</th>
                <th class="py-3 px-3 text-right">{{ tExt.cartSubtotal }}</th>
                <th class="py-3 px-3 text-center">{{ tExt.cartAction }}</th>
              </tr>
            </thead>
            <tbody class="text-sm font-medium">
              <tr 
                v-for="(item, index) in cartItems" 
                :key="item.oem" 
                @click="selectedCartIndex = index"
                :class="[
                  selectedCartIndex === index ? 'bg-blue-500/15 border-blue-400 ring-1 ring-blue-400' : (index % 2 === 0 ? 'bg-white dark:bg-slate-800/80' : 'bg-slate-50 dark:bg-slate-900/70'),
                  'border-b border-slate-200 dark:border-slate-700/70 hover:bg-blue-50/50 transition-all shadow-2xs cursor-pointer'
                ]"
              >
                <td class="py-3 px-3 font-mono font-black text-blue-600 text-sm">{{ item.oem }}</td>
                <td class="py-3 px-3 text-slate-900 dark:text-white font-bold">{{ item.name }}</td>
                <td class="py-3 px-3 text-right font-mono text-slate-700 dark:text-slate-300 font-bold">
                  <div>${{ item.price.toFixed(2) }}</div>
                  <div class="text-xs text-slate-400 font-normal">Bs. {{ (item.price * bcvRate).toFixed(2) }}</div>
                </td>
                <td class="py-3 px-3 text-center" @click.stop>
                  <div class="inline-flex items-center border border-slate-300 dark:border-slate-600 rounded-lg overflow-hidden bg-white dark:bg-slate-800 shadow-2xs focus-within:ring-2 focus-within:ring-blue-500 focus-within:border-blue-500">
                    <button @click="item.quantity > 1 ? item.quantity-- : null" class="px-2.5 py-1 text-slate-600 dark:text-slate-400 hover:bg-slate-200 font-bold text-sm">-</button>
                    <input 
                      v-model="itemInputQuantities[index]" 
                      @focus="$event.target.select()"
                      @blur="applyMultiplierQuantity(index)"
                      @keydown.enter="applyMultiplierQuantity(index)"
                      type="text" 
                      class="w-12 text-center bg-transparent text-slate-900 dark:text-white text-sm font-mono outline-none font-black" 
                    />
                    <button @click="item.quantity++; itemInputQuantities[index] = item.quantity" class="px-2.5 py-1 text-slate-600 dark:text-slate-400 hover:bg-slate-200 font-bold text-sm">+</button>
                  </div>
                </td>
                <td class="py-3 px-3 text-right font-mono font-black text-emerald-600">
                  <div>${{ (item.price * item.quantity).toFixed(2) }}</div>
                  <div class="text-xs text-emerald-700/80 font-normal">Bs. {{ (item.price * item.quantity * bcvRate).toFixed(2) }}</div>
                </td>
                <td class="py-3 px-3 text-center" @click.stop>
                  <button @click="cartItems.splice(index, 1)" class="text-rose-600 text-xs font-bold px-2.5 py-1 bg-rose-500/10 hover:bg-rose-500/20 rounded-lg transition-all cursor-pointer shadow-2xs">{{ t.common.delete }}</button>
                </td>
              </tr>
              <tr v-if="cartItems.length === 0">
                <td colspan="6" class="text-center py-20 text-slate-400 text-sm font-bold">
                  🛒 {{ tExt.cartEmpty }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- 右侧面板容器 -->
      <div class="w-[410px] flex flex-col bg-white dark:bg-slate-800/75 backdrop-blur-xl rounded-xl border border-white/60 shadow-lg shrink-0 overflow-hidden transition-all">

        <!-- ================= 🌟 报价模式面板 ================= -->
        <div v-if="isQuoteMode" class="flex flex-col h-full w-full p-4 justify-between animate-in fade-in duration-200">
          <div class="space-y-4">
            <div class="flex items-center justify-between border-b border-slate-200 dark:border-slate-700/60 pb-2">
              <h3 class="font-bold text-sm text-slate-800 dark:text-slate-200 flex items-center gap-2">📄 {{ tExt.quoteInfoTitle }}</h3>
              <!-- 🌟 新增：载入历史报价按钮 -->
              <button 
                @click="openHistoryQuotesModal" 
                type="button"
                class="text-xs bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-slate-700 dark:text-slate-300 px-2.5 py-1 rounded-lg font-bold transition-colors cursor-pointer flex items-center gap-1 shadow-2xs"
              >
                📂 载入历史
              </button>
            </div>
            
            <div>
              <label class="block text-xs font-bold text-slate-500 dark:text-slate-400 mb-1">{{ tExt.quoteNotesLabel }}</label>
              <textarea 
                v-model="quoteNotes" 
                class="w-full border border-slate-300 dark:border-slate-600 rounded-lg p-3 text-sm outline-none focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 shadow-inner" 
                rows="6" 
                :placeholder="tExt.quoteNotesPlaceholder"
              ></textarea>
            </div>
            
            <div class="bg-amber-50 dark:bg-amber-900/30/50 p-4 rounded-xl border border-amber-200/60">
              <div class="text-xs text-amber-800 dark:text-amber-400 font-bold mb-1">{{ tExt.quoteTipTitle }}</div>
              <div class="text-xs text-amber-700/80 leading-relaxed">
                {{ tExt.quoteTipText }}
              </div>
            </div>
          </div>

          <div class="p-3 bg-white dark:bg-slate-800/90 backdrop-blur-md border-t border-slate-200 dark:border-slate-700/60 shrink-0 flex flex-col gap-2">
            <button 
              @click="generateQuotationPDF" 
              :disabled="cartItems.length === 0 || isSubmitting"
              class="w-full py-3 bg-amber-500 hover:bg-amber-400 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl font-black text-sm shadow-md shadow-amber-500/30 transition-all cursor-pointer flex items-center justify-center gap-1.5"
            >
              <span>💾 {{ isSubmitting ? tExt.savingQuote : tExt.saveQuoteBtn }}</span>
            </button>
            <!-- 🌟 新增：挂账按钮 -->
            <button 
              data-testid="quote-credit-btn"
              @click="submitOrderAsCredit"
              :disabled="!quoteClientId || cartItems.length === 0 || isSubmitting"
              class="w-full py-3 bg-rose-600 hover:bg-rose-500 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl font-black text-sm shadow-md shadow-rose-500/30 transition-all cursor-pointer flex items-center justify-center gap-1.5"
            >
              <span>📝 确认全单挂账 (Fiado)</span>
            </button>
            <p v-if="!quoteClientId && cartItems.length > 0" class="text-[10px] text-rose-500 text-center font-bold">
              * 挂账前请先在顶部搜索并选择客户
            </p>
          </div>
        </div>

      </div>

    </div>

    <!-- 底部快捷键导航栏 -->
    <footer class="absolute bottom-0 left-0 right-0 h-11 bg-white dark:bg-slate-800/75 backdrop-blur-xl border-t border-white/60 px-3 flex items-center justify-between z-30 shadow-md">
      <div class="grid grid-cols-6 gap-2 w-full">
        <!-- 1. 聚焦搜索 -->
        <div @click="focusSearch" class="bg-white dark:bg-slate-800/70 hover:bg-blue-500/10 border border-slate-200 dark:border-slate-700 hover:border-blue-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ t.pos.keyFocus }} [/]</span>
          <span class="bg-blue-500/15 text-blue-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">搜索</span>
        </div>
        
        <!-- 2. 选客户 -->
        <div @click="openClientSearchModal" class="bg-white dark:bg-slate-800/70 hover:bg-blue-500/10 border border-slate-200 dark:border-slate-700 hover:border-blue-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ t.pos.keyClient }}</span>
          <span class="bg-blue-500/15 text-blue-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+F</span>
        </div>

        <!-- 3. 保存报价快捷键（填补缺失的空位） -->
        <div @click="generateQuotationPDF" class="bg-white dark:bg-slate-800/70 hover:bg-amber-500/10 border border-slate-200 dark:border-slate-700 hover:border-amber-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">保存报价</span>
          <span class="bg-amber-500/15 text-amber-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+S</span>
        </div>

        <!-- 4. 清空购物车 -->
        <div @click="$emit('clear-cart')" class="bg-white dark:bg-slate-800/70 hover:bg-rose-500/10 border border-slate-200 dark:border-slate-700 hover:border-rose-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ t.pos.keyClear }}</span>
          <span class="bg-rose-500/15 text-rose-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Ctrl+B</span>
        </div>

        <!-- 5. 删除项 -->
        <div @click="deleteLastItem" class="bg-white dark:bg-slate-800/70 hover:bg-rose-500/10 border border-slate-200 dark:border-slate-700 hover:border-rose-300 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">{{ t.pos.keyDeleteLast }}</span>
          <span class="bg-rose-500/15 text-rose-700 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Delete</span>
        </div>

        <!-- 6. 退出 -->
        <div @click="confirmExitPos" class="bg-white dark:bg-slate-800/70 hover:bg-slate-200/80 border border-slate-200 dark:border-slate-700 hover:border-slate-300 dark:border-slate-600 rounded-lg px-2.5 py-1.5 flex items-center justify-between text-xs cursor-pointer transition-all shadow-2xs">
          <span class="text-slate-800 dark:text-slate-200 font-bold">退出界面</span>
          <span class="bg-slate-200 text-slate-800 dark:text-slate-200 font-mono font-bold px-1.5 py-0.5 rounded text-[10px]">Esc</span>
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
    <div v-if="recallModalVisible" @click.self="recallModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
      <div class="bg-white dark:bg-slate-800/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-4xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
        <div class="p-5 border-b border-slate-200 dark:border-slate-700/60 flex items-center justify-between bg-white dark:bg-slate-800/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white flex items-center gap-2">
            <span>📦 {{ tExt.recallTitle }} ({{ heldOrders.length }})</span>
          </h3>
          <button @click="recallModalVisible = false" class="text-slate-400 hover:text-slate-700 dark:text-slate-300 text-base font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-3 bg-white dark:bg-slate-800/20 flex flex-col">
          <template v-if="heldOrders.length > 0">
            <div v-for="order in heldOrders" :key="order.id" class="p-4 rounded-2xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-slate-800/80 backdrop-blur-md hover:bg-white dark:bg-slate-800 transition-all flex items-center justify-between shadow-2xs shrink-0">
              <div class="space-y-1">
                <div class="font-bold text-xs text-slate-800 dark:text-slate-200 flex items-center gap-2">
                  <span class="font-mono text-blue-600 font-black text-sm">{{ order.hold_no }}</span>
                  <span class="text-slate-700 dark:text-slate-300">👤 {{ order.client_name || 'Cliente General' }}</span>
                </div>
                <div class="text-[11px] text-slate-400 font-mono">{{ tExt.recallTime }} {{ order.timestamp }}</div>
              </div>
              <div class="flex items-center gap-4">
                <span class="text-base font-mono font-black text-slate-900 dark:text-white">${{ order.total_amount.toFixed(2) }}</span>
                <button @click="recallOrder(order)" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition-all cursor-pointer shadow-sm">
                  {{ tExt.recallBtn }}
                </button>
                <button @click="deleteHeldOrder(order.id)" class="px-3.5 py-2 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 rounded-xl text-xs font-bold transition-all cursor-pointer">
                  {{ tExt.recallVoid }}
                </button>
              </div>
            </div>
          </template>
          <div v-else class="flex-1 flex flex-col items-center justify-center py-20 text-slate-400 text-xs font-bold">
            <span class="text-4xl mb-2">📭</span>
            <span>{{ tExt.recallEmpty }}</span>
          </div>
        </div>

        <div class="p-5 bg-white dark:bg-slate-800/80 backdrop-blur-md border-t border-slate-200 dark:border-slate-700/60 flex items-center justify-between shrink-0">
          <span class="text-xs text-slate-600 dark:text-slate-400 font-mono font-bold">
            {{ tExt.recallFound }}: <strong class="text-slate-900 dark:text-white">{{ heldOrders.length }}</strong>
          </span>
          <button @click="recallModalVisible = false" class="px-6 py-2 bg-slate-200/80 hover:bg-slate-300 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition-colors cursor-pointer">
            {{ t.common.cancel }}
          </button>
        </div>
      </div>
    </div>

    <!-- 交接班 Modal -->
    <div v-if="shiftReportModalVisible" @click.self="shiftReportModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
      <div class="bg-white dark:bg-slate-800/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-4xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
        <div class="p-5 border-b border-slate-200 dark:border-slate-700/60 flex items-center justify-between bg-white dark:bg-slate-800/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white flex items-center gap-2">
            <span>📊 {{ tExt.shiftTitle }}</span>
          </h3>
          <button @click="shiftReportModalVisible = false" class="text-slate-400 hover:text-slate-700 dark:text-slate-300 text-base font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-6 text-sm bg-white dark:bg-slate-800/30">
          <div class="bg-white dark:bg-slate-800/80 backdrop-blur-md p-5 rounded-2xl border border-white/90 space-y-3 shadow-2xs font-mono">
            <div class="text-xs font-black text-slate-400 uppercase tracking-wider border-b border-slate-200 dark:border-slate-700 pb-2 flex justify-between">
              <span>{{ tExt.shiftSystemTitle }}</span>
              <span class="text-[10px] text-emerald-600">{{ tExt.shiftTodayOnly }}</span>
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div class="bg-slate-50 dark:bg-slate-900/80 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700/80">
                <span class="text-slate-500 dark:text-slate-400 block mb-1">💳 {{ t.pos.payCardPos }}:</span>
                <span class="font-black text-blue-600 text-sm">Bs. {{ (shiftStats.cardPos.amount * bcvRate).toFixed(2) }}</span>
              </div>
              <div class="bg-slate-50 dark:bg-slate-900/80 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700/80">
                <span class="text-slate-500 dark:text-slate-400 block mb-1">⚡ {{ t.pos.payPagoMovil }}:</span>
                <span class="font-black text-indigo-600 text-sm">Bs. {{ (shiftStats.pagoMovil.amount * bcvRate).toFixed(2) }}</span>
              </div>
              <div class="bg-slate-50 dark:bg-slate-900/80 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700/80">
                <span class="text-slate-500 dark:text-slate-400 block mb-1">🇻🇪 {{ t.pos.payCashBs }}:</span>
                <span class="font-black text-emerald-600 text-sm">Bs. {{ (shiftStats.cashBs.amount * bcvRate).toFixed(2) }}</span>
              </div>
              <div class="bg-slate-50 dark:bg-slate-900/80 p-3.5 rounded-xl border border-slate-200 dark:border-slate-700/80">
                <span class="text-slate-500 dark:text-slate-400 block mb-1">💵 {{ t.pos.payCashUsd }}:</span>
                <span class="font-black text-slate-900 dark:text-white text-sm">${{ shiftStats.cashUsd.amount.toFixed(2) }}</span>
              </div>
            </div>
            <div class="pt-2 border-t border-slate-200 dark:border-slate-700 flex justify-between items-center text-sm font-black">
              <span class="text-slate-900 dark:text-white">{{ tExt.shiftTotalRevenue }} (USD):</span>
              <span class="text-emerald-600 text-lg">${{ shiftStats.totalUsd.toFixed(2) }}</span>
            </div>
          </div>

          <div class="bg-blue-50/50 backdrop-blur-md p-5 rounded-2xl border border-blue-200/80 space-y-4 font-mono shadow-2xs">
            <div class="text-xs font-black text-blue-900 uppercase tracking-wider border-b border-blue-200 pb-2 flex justify-between items-center">
              <span>{{ tExt.shiftActualTitle }}</span>
              <span class="text-xs text-blue-700 font-normal">{{ tExt.shiftActualDesc }}</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-blue-100 space-y-2 shadow-2xs">
                <label class="block text-xs font-bold text-slate-800 dark:text-slate-200">💳 {{ t.pos.payCardPos }} (Bs.):</label>
                <div class="flex items-center gap-2">
                  <span class="text-slate-400 font-bold text-base">Bs.</span>
                  <input 
                    v-model.number="actualCounts.cardPos" 
                    type="number" step="10" placeholder="0" 
                    class="w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-3.5 py-2.5 text-right font-mono text-base outline-none focus:border-blue-500 font-black text-slate-900 dark:text-white shadow-2xs no-spinner"
                  />
                </div>
                <div class="text-xs text-right font-bold pt-1" :class="cardPosDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  {{ tExt.shiftDiff }}: {{ cardPosDiff >= 0 ? '+' : '' }}Bs. {{ cardPosDiff.toFixed(2) }}
                </div>
              </div>

              <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-blue-100 space-y-2 shadow-2xs">
                <label class="block text-xs font-bold text-slate-800 dark:text-slate-200">⚡ {{ t.pos.payPagoMovil }} (Bs.):</label>
                <div class="flex items-center gap-2">
                  <span class="text-slate-400 font-bold text-base">Bs.</span>
                  <input 
                    v-model.number="actualCounts.pagoMovil" 
                    type="number" step="10" placeholder="0" 
                    class="w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-3.5 py-2.5 text-right font-mono text-base outline-none focus:border-blue-500 font-black text-slate-900 dark:text-white shadow-2xs no-spinner"
                  />
                </div>
                <div class="text-xs text-right font-bold pt-1" :class="pagoMovilDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  {{ tExt.shiftDiff }}: {{ pagoMovilDiff >= 0 ? '+' : '' }}Bs. {{ pagoMovilDiff.toFixed(2) }}
                </div>
              </div>

              <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-blue-100 space-y-2 shadow-2xs">
                <label class="block text-xs font-bold text-slate-800 dark:text-slate-200">🇻🇪 {{ t.pos.payCashBs }} (Bs.):</label>
                <div class="flex items-center gap-2">
                  <span class="text-slate-400 font-bold text-base">Bs.</span>
                  <input 
                    v-model.number="actualCounts.cashBs" 
                    type="number" step="10" placeholder="0" 
                    class="w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-3.5 py-2.5 text-right font-mono text-base outline-none focus:border-blue-500 font-black text-slate-900 dark:text-white shadow-2xs no-spinner"
                  />
                </div>
                <div class="text-xs text-right font-bold pt-1" :class="cashBsDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  {{ tExt.shiftDiff }}: {{ cashBsDiff >= 0 ? '+' : '' }}Bs. {{ cashBsDiff.toFixed(2) }}
                </div>
              </div>

              <div class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-blue-100 space-y-2 shadow-2xs">
                <label class="block text-xs font-bold text-slate-800 dark:text-slate-200">💵 {{ t.pos.payCashUsd }} (USD):</label>
                <div class="flex items-center gap-2">
                  <span class="text-slate-400 font-bold text-base">$</span>
                  <input 
                    v-model.number="actualCounts.cashUsd" 
                    type="number" step="0.5" placeholder="0" 
                    class="w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-3.5 py-2.5 text-right font-mono text-base outline-none focus:border-blue-500 font-black text-slate-900 dark:text-white shadow-2xs no-spinner"
                  />
                </div>
                <div class="text-xs text-right font-bold pt-1" :class="cashUsdDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  {{ tExt.shiftDiff }}: {{ cashUsdDiff >= 0 ? '+' : '' }}${{ cashUsdDiff.toFixed(2) }}
                </div>
              </div>
            </div>

            <div class="pt-3 border-t border-blue-200 flex justify-between items-center text-sm">
              <span class="font-extrabold text-slate-800 dark:text-slate-200">{{ tExt.shiftTotalDiff }}:</span>
              <span :class="totalUsdDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'" class="font-black font-mono text-lg">
                {{ totalUsdDiff >= 0 ? '+' : '' }}${{ totalUsdDiff.toFixed(2) }}
              </span>
            </div>
          </div>

          <div v-if="totalUsdDiff !== 0" class="space-y-2">
            <label class="block font-bold text-slate-600 dark:text-slate-400 uppercase text-xs">{{ tExt.shiftNotes }}</label>
            <input v-model="handoverNotes" type="text" :placeholder="tExt.shiftNotesPlace" class="w-full bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-xl px-4 py-3 text-xs outline-none focus:border-blue-500 font-bold text-slate-900 dark:text-white shadow-2xs" />
          </div>
        </div>

        <div class="p-5 bg-white dark:bg-slate-800/80 backdrop-blur-md border-t border-slate-200 dark:border-slate-700/60 flex items-center justify-between shrink-0">
          <button @click="shiftReportModalVisible = false" class="px-6 py-2.5 bg-slate-200/80 hover:bg-slate-300 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition-colors cursor-pointer">
            {{ t.common.cancel }}
          </button>
          <button @click="submitShiftHandover" class="px-7 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black shadow-lg shadow-emerald-600/30 transition-all cursor-pointer">
            🔒 {{ tExt.shiftConfirm }}
          </button>
        </div>
      </div>
    </div>

    <!-- 小票预览 Modal -->
    <div v-if="previewModalVisible" @click.self="previewModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
      <div class="bg-white dark:bg-slate-800/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-4xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
        <div class="p-5 border-b border-slate-200 dark:border-slate-700/60 flex items-center justify-between bg-white dark:bg-slate-800/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white flex items-center gap-2">
            <span>🧾 {{ tExt.ticketTitle }}</span>
          </h3>
          <button @click="previewModalVisible = false" class="text-slate-400 hover:text-slate-700 dark:text-slate-300 text-base font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-4 font-mono text-xs bg-white dark:bg-slate-800/30 max-w-lg mx-auto w-full my-auto border border-slate-200 dark:border-slate-700/80 rounded-2xl shadow-sm my-6">
          <div class="text-center pb-3 border-b border-dashed border-slate-300 dark:border-slate-600 space-y-1">
            <div class="font-black text-sm text-slate-900 dark:text-white">{{ systemConfig.company_name || 'TOSTIYK (TK) - VENEZUELA' }}</div>
            <div class="text-[11px] text-blue-600 font-bold">RIF: {{ systemConfig.rif || 'J-00000000-0' }}</div>
            <div class="text-[11px] text-slate-500 dark:text-slate-400">{{ systemConfig.address || 'Valencia, Carabobo' }}</div>
          </div>

          <div class="space-y-1 text-slate-700 dark:text-slate-300 pb-3 border-b border-dashed border-slate-300 dark:border-slate-600 font-sans">
            <div><span class="font-bold">{{ tExt.ticketClient }}:</span> {{ quoteClientName || 'Cliente General' }}</div>
            <div><span class="font-bold">{{ tExt.ticketOperator }}:</span> {{ currentUser?.username || 'N/A' }}</div>
            <div class="font-bold text-blue-600 mt-1">{{ tExt.ticketPayment }}:</div>
            <div v-if="paymentSplit.cardPos > 0"> - {{ t.pos.payCardPos }}: Bs. {{ paymentSplit.cardPos.toFixed(2) }} (${{ (paymentSplit.cardPos / bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.pagoMovil > 0"> - {{ t.pos.payPagoMovil }}: Bs. {{ paymentSplit.pagoMovil.toFixed(2) }} (${{ (paymentSplit.pagoMovil / bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.cashBs > 0"> - {{ t.pos.payCashBs }}: Bs. {{ paymentSplit.cashBs.toFixed(2) }} (${{ (paymentSplit.cashBs / bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.cashUsd > 0"> - {{ t.pos.payCashUsd }}: ${{ paymentSplit.cashUsd.toFixed(2) }} (Bs. {{ (paymentSplit.cashUsd * bcvRate).toFixed(2) }})</div>
            <div v-if="balanceRemaining < 0"> - {{ t.pos.changeDue }}: ${{ Math.abs(balanceRemaining).toFixed(2) }} (Bs. {{ (Math.abs(balanceRemaining) * bcvRate).toFixed(2) }})</div>
            <div v-if="paymentReference"><span class="font-bold">Ref:</span> {{ paymentReference }}</div>
          </div>

          <div class="space-y-2 pb-3 border-b border-dashed border-slate-300 dark:border-slate-600">
            <div v-for="item in cartItems" :key="item.oem" class="flex justify-between items-start gap-2">
              <div>
                <div class="font-bold text-slate-800 dark:text-slate-200">{{ item.name }}</div>
                <div class="text-[11px] text-slate-500 dark:text-slate-400">{{ item.oem }} x {{ item.quantity }} @ ${{ item.price.toFixed(2) }}</div>
              </div>
              <div class="font-bold text-slate-900 dark:text-white text-right">
                <div>${{ (item.price * item.quantity).toFixed(2) }}</div>
                <div class="text-[11px] text-slate-500 dark:text-slate-400 font-normal">Bs. {{ (item.price * item.quantity * bcvRate).toFixed(2) }}</div>
              </div>
            </div>
          </div>

          <div class="space-y-1 text-right pb-1 font-bold">
            <div>{{ t.pos.baseImponible }}: ${{ totalBaseUsd.toFixed(2) }}</div>
            <div>{{ t.pos.ivaTax }}: ${{ totalTaxUsd.toFixed(2) }}</div>
            <div class="text-lg font-black text-slate-900 dark:text-white mt-1">{{ tExt.ticketTotal }}: ${{ totalUsd.toFixed(2) }} / Bs. {{ (totalUsd * bcvRate).toFixed(2) }}</div>
          </div>
        </div>

        <div class="p-5 bg-white dark:bg-slate-800/80 backdrop-blur-md border-t border-slate-200 dark:border-slate-700/60 flex gap-4 shrink-0">
          <button @click="previewModalVisible = false" :disabled="isSubmitting" class="flex-1 py-3 bg-slate-200/80 hover:bg-slate-300 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition-all cursor-pointer">{{ t.pos.backToEdit }}</button>
          <button @click="confirmAndPrint" :disabled="isSubmitting" class="flex-1 py-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-300 text-white rounded-xl text-sm font-black shadow-lg shadow-emerald-600/30 transition-all cursor-pointer">
            {{ isSubmitting ? tExt.ticketPrinting : t.pos.confirmAndPrint }}
          </button>
        </div>
      </div>
    </div>

    <!-- 快捷键指南弹窗 -->
    <PosHelpModal :visible="helpModalVisible" @close="helpModalVisible = false" />

    <!-- 🌟 客户快速搜索 & 未找到创建 Modal -->
    <div v-if="clientModalVisible" @click.self="clientModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-4 cursor-pointer">
      <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl max-w-lg w-full h-[600px] max-h-[85vh] overflow-hidden border border-slate-100 dark:border-slate-800 flex flex-col cursor-default animate-in zoom-in-95 duration-150">
        <div class="p-5 border-b border-slate-100 dark:border-slate-800 flex items-center justify-between shrink-0 bg-white dark:bg-slate-800/50">
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white">{{ tExt.clientModalTitle }}</h3>
          <div class="flex items-center gap-2">
            <button @click="prepareCreateClient('')" class="bg-blue-600 hover:bg-blue-700 text-white px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 shadow-md cursor-pointer active:scale-95">
              <span>➕</span> {{ tExt.newClientBtn }}
            </button>
            <button @click="clientModalVisible = false" class="text-slate-400 hover:text-slate-700 dark:text-slate-300 font-bold text-base p-1">✕</button>
          </div>
        </div>
        
        <div class="p-4 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-900/50 shrink-0">
          <input ref="clientModalInputRef" v-model="clientFilterQuery" @keydown="handleClientModalKeydown" type="text" :placeholder="tExt.clientModalSearch" class="w-full bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-xl px-4 py-3 text-sm outline-none focus:border-blue-500 shadow-sm font-bold text-slate-900 dark:text-white" />
        </div>
        
        <div class="flex-1 overflow-y-auto p-3 space-y-2 bg-white dark:bg-slate-800">
          <div v-for="c in filteredModalClients" :key="c.id" @click="selectClient(c)" class="p-3.5 rounded-xl border border-slate-200 dark:border-slate-700/80 bg-white dark:bg-slate-800 cursor-pointer hover:bg-blue-50 hover:border-blue-300 transition-all flex items-center justify-between text-xs shadow-2xs">
            <div>
              <div class="font-black text-slate-900 dark:text-white text-sm">🏢 {{ c.name }}</div>
              <div class="text-xs text-slate-500 dark:text-slate-400 font-mono mt-0.5">RIF: {{ c.rif_or_cedula || '-' }} | 📞 {{ c.phone || tExt.clientNoPhone }}</div>
            </div>
            <span class="text-blue-600 font-bold bg-blue-100/50 px-3 py-1.5 rounded-lg">{{ tExt.clientSelectBtn }} ↵</span>
          </div>
          
          <div v-if="filteredModalClients.length === 0 && clientFilterQuery.trim()" class="flex flex-col items-center justify-center py-12 space-y-4 animate-in fade-in duration-200">
            <div class="text-slate-400 text-sm font-bold text-center">
              {{ tExt.clientNotFound }} <br>
              <span class="text-lg text-slate-800 dark:text-slate-200">"{{ clientFilterQuery }}"</span>
            </div>
            <button @click="prepareCreateClient(clientFilterQuery)" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl text-sm font-black shadow-lg shadow-blue-500/30 transition-all cursor-pointer flex items-center gap-2 hover:scale-105 active:scale-95 w-full justify-center">
              <span>➕</span> {{ tExt.createThisClient }}
            </button>
          </div>
          
          <div v-else-if="filteredModalClients.length === 0 && !clientFilterQuery.trim()" class="text-center py-12 text-slate-400 text-xs font-bold">
            {{ tExt.typeToSearch }}
          </div>
        </div>
        
        <div class="p-4 border-t border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-900 flex justify-end shrink-0">
          <button @click="clientModalVisible = false" class="px-6 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition-all cursor-pointer">
            {{ t.common.cancel }}
          </button>
        </div>
      </div>
    </div>

    <!-- 🌟 新建客户 Modal (完整税务字段版) -->
    <div v-if="newClientModalVisible" @click.self="newClientModalVisible = false" class="fixed inset-0 bg-slate-950/60 backdrop-blur-md flex items-center justify-center z-[60] p-6">
      <div class="bg-white dark:bg-slate-800 rounded-3xl shadow-2xl max-w-lg w-full overflow-hidden border border-slate-100 dark:border-slate-800 flex flex-col animate-in zoom-in-95 duration-150">
        <div class="p-5 border-b border-slate-200 dark:border-slate-700/60 flex items-center justify-between bg-white dark:bg-slate-800/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white">{{ tExt.createClientTitle }}</h3>
          <button @click="newClientModalVisible = false" class="text-slate-400 hover:text-slate-700 dark:text-slate-300 font-bold text-base p-1">✕</button>
        </div>
        <div class="p-5 space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{{ t.clients.colName }} *</label>
            <input v-model="newClientForm.name" type="text" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-bold text-slate-900 dark:text-white" placeholder="Ej: Auto Taller Valencia" />
          </div>
          
          <div class="grid grid-cols-2 gap-4">
            <!-- 🌟 RIF 拆分输入 -->
            <div>
              <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{{ t.clients.colRif }}</label>
              <div class="flex gap-2">
                <select v-model="newClientForm.rif_type" class="w-16 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-2 py-2.5 text-sm outline-none focus:border-blue-500 font-bold text-slate-900 dark:text-white cursor-pointer">
                  <option value="V">V</option>
                  <option value="E">E</option>
                  <option value="J">J</option>
                  <option value="G">G</option>
                </select>
                <input 
                  v-model="newClientForm.rif_number" 
                  @input="formatRifNumber"
                  type="text" 
                  maxlength="9"
                  class="flex-1 w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-mono text-slate-900 dark:text-white" 
                  placeholder="12345678" 
                />
              </div>
            </div>
            
            <!-- 🌟 电话号码强格式化 -->
            <div>
              <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{{ t.clients.colPhone }}</label>
              <div class="flex">
                <span class="inline-flex items-center px-3 rounded-l-xl border border-r-0 border-slate-200 dark:border-slate-700 bg-slate-100 dark:bg-slate-800 text-slate-500 dark:text-slate-400 text-sm font-mono font-bold">
                  +58
                </span>
                <input 
                  v-model="newClientForm.phone" 
                  @input="formatPhoneNumber"
                  type="text" 
                  maxlength="10"
                  class="flex-1 w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-r-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-mono text-slate-900 dark:text-white" 
                  placeholder="4121234567" 
                />
              </div>
            </div>
          </div>
          
          <div>
            <label class="block text-xs font-semibold text-slate-500 dark:text-slate-400 mb-1">{{ t.clients.colType }}</label>
            <select v-model="newClientForm.client_type" class="w-full bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-xl px-3.5 py-2.5 text-sm outline-none focus:border-blue-500 font-semibold text-slate-900 dark:text-white cursor-pointer">
              <option value="Regular">{{ tExt.clientTypeRegular }}</option>
              <option value="Taller">{{ tExt.clientTypeTaller }}</option>
              <option value="Mayorista">{{ tExt.clientTypeMayorista }}</option>
            </select>
          </div>
          
          <!-- 🌟 特殊纳税人复选框 -->
          <div class="flex items-center gap-3 bg-amber-50 dark:bg-amber-900/30 border border-amber-200 p-3 rounded-xl">
            <input type="checkbox" id="specialTax" v-model="newClientForm.is_special_taxpayer" class="w-4 h-4 text-amber-600 rounded border-amber-300 focus:ring-amber-500 cursor-pointer" />
            <label for="specialTax" class="text-xs font-bold text-amber-900 cursor-pointer">
              {{ tExt.isSpecialTaxpayer }}
            </label>
          </div>
        </div>
        <div class="p-5 border-t border-slate-100 dark:border-slate-800 flex justify-end gap-3 bg-slate-50 dark:bg-slate-900/50">
          <button @click="newClientModalVisible = false" class="px-5 py-2.5 rounded-xl text-xs font-bold bg-slate-200 text-slate-600 dark:text-slate-400 hover:bg-slate-300 transition-colors cursor-pointer">{{ t.common.cancel }}</button>
          <button @click="saveNewClient" :disabled="isSavingClient" class="px-6 py-2.5 rounded-xl text-xs font-bold bg-blue-600 text-white hover:bg-blue-700 shadow-md transition-colors cursor-pointer disabled:opacity-50">
            {{ isSavingClient ? '...' : t.common.save }}
          </button>
        </div>
      </div>
    </div>

    <!-- 退出确认 -->
    <ConfirmDialog 
      :visible="exitConfirmVisible" 
      icon="⚠️" 
      :title="tExt.exitTitle" 
      :message="tExt.exitMsg" 
      @cancel="exitConfirmVisible = false" 
      @confirm="executeExitPos" 
    />

    <!-- 🌟 新增：历史报价选择弹窗 -->
    <div v-if="historyQuotesModalVisible" @click.self="historyQuotesModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-[60] p-6 cursor-pointer">
      <div class="bg-white dark:bg-slate-800/95 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-3xl w-full max-h-[80vh] overflow-hidden border border-white/80 flex flex-col cursor-default animate-in zoom-in-95 duration-150">
        <div class="p-5 border-b border-slate-200 dark:border-slate-700/60 flex items-center justify-between bg-white dark:bg-slate-800/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 dark:text-white flex items-center gap-2">
            <span>📂 载入历史报价单</span>
          </h3>
          <button @click="historyQuotesModalVisible = false" class="text-slate-400 hover:text-slate-700 dark:text-slate-300 text-base font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-3 bg-slate-50 dark:bg-slate-900/50">
          <div v-if="isFetchingQuotes" class="text-center py-10 text-slate-400 text-xs">加载中...</div>
          
          <template v-else-if="historyQuotesList.length > 0">
            <div 
              v-for="q in historyQuotesList" 
              :key="q.id" 
              @click="loadQuoteToCart(q)" 
              class="bg-white dark:bg-slate-800 p-4 rounded-2xl border border-slate-200 dark:border-slate-700/80 hover:border-blue-400 hover:shadow-md transition-all cursor-pointer flex items-center justify-between shadow-2xs group"
            >
              <div class="space-y-1">
                <div class="font-black text-sm text-slate-800 dark:text-slate-200 flex items-center gap-2">
                  <span class="text-blue-600 font-mono">{{ q.quotation_no }}</span>
                  <span>👤 {{ q.client_name }}</span>
                </div>
                <div class="text-[11px] text-slate-400 font-mono">创建时间: {{ q.created_at || '历史记录' }}</div>
              </div>
              <div class="flex items-center gap-4">
                <span class="text-base font-mono font-black text-emerald-600">${{ Number(q.total_usd || 0).toFixed(2) }}</span>
                <span class="text-xs font-bold text-blue-500 bg-blue-50 px-3 py-1.5 rounded-lg group-hover:bg-blue-600 group-hover:text-white transition-colors">载入 ↵</span>
              </div>
            </div>
          </template>
          
          <div v-else class="text-center py-20 text-slate-400 text-xs font-bold">
            <span class="text-4xl block mb-2">📭</span>
            暂无历史报价记录
          </div>
        </div>

        <div class="p-4 border-t border-slate-200 dark:border-slate-700/60 bg-white dark:bg-slate-800 flex justify-end shrink-0">
          <button @click="historyQuotesModalVisible = false" class="px-6 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-700 dark:text-slate-300 rounded-xl text-xs font-bold transition-all cursor-pointer">
            取消
          </button>
        </div>
        <!-- 🌟 新增：覆盖购物车确认弹窗 -->
        <ConfirmDialog
          :visible="showLoadConfirm"
          overlay-class="bg-slate-900/60"
          :title="tExt.overwriteCartTitle || '覆盖购物车'"
          :message="tExt.overwriteCartMsg || '载入历史报价将覆盖当前购物车中的商品，是否继续？'"
          :cancel-text="t.common.cancel"
          :confirm-text="t.common.confirm || '确认'"
          @cancel="showLoadConfirm = false; pendingQuoteToLoad = null"
          @confirm="executeLoadQuote(pendingQuoteToLoad)"
        />
      </div>
    </div>

    <!-- ==================================================== -->
    <!-- 🌟 核心新增：隐藏的 80mm 热敏打印区域 (已多语言化)      -->
    <!-- ==================================================== -->
    <div v-if="printData" class="print-only hidden" id="print-section">
      <div class="print-header">
        <h2>{{ systemConfig.company_name || 'TOSTIYK (TK)' }}</h2>
        <p>RIF: {{ systemConfig.rif || 'J-00000000-0' }}</p>
        <p>{{ systemConfig.address || 'Valencia, Carabobo' }}</p>
        <p>Tel: {{ systemConfig.phone || 'N/A' }}</p>
        <p class="divider">--------------------------------</p>
      </div>
      
      <div class="print-meta">
        <p>{{ tExt.printOrderNo }} {{ printData.order_no }}</p>
        <p>{{ tExt.printDate }} {{ printData.date }}</p>
        <p>{{ tExt.printClient }} {{ printData.client_name }}</p>
        <p>{{ tExt.printOperator }} {{ printData.operator }}</p>
        <p class="divider">--------------------------------</p>
      </div>

      <div class="print-items">
        <table>
          <thead>
            <tr>
              <th style="text-align: left;">{{ tExt.printItemsTitle }}</th>
              <th style="text-align: center;">{{ tExt.printQtyTitle }}</th>
              <th style="text-align: right;">{{ tExt.printSubtotalTitle }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in printData.items" :key="item.oem">
              <td style="text-align: left;">{{ item.name }}</td>
              <td style="text-align: center;">{{ item.quantity }}</td>
              <td style="text-align: right;">${{ (item.price * item.quantity).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
        <p class="divider">--------------------------------</p>
      </div>

      <div class="print-totals">
        <p><span>Base Imponible:</span> <span>${{ printData.base_usd.toFixed(2) }}</span></p>
        <p><span>IVA:</span> <span>${{ printData.tax_usd.toFixed(2) }}</span></p>
        <p class="bold"><span>TOTAL USD:</span> <span>${{ printData.total_usd.toFixed(2) }}</span></p>
        <p class="bold"><span>TOTAL VES:</span> <span>Bs. {{ printData.total_bs.toFixed(2) }}</span></p>
        <p class="divider">--------------------------------</p>
      </div>

      <div class="print-payments">
        <p>{{ tExt.printPaymentTitle }}</p>
        <p v-if="printData.payment.cardPos > 0"> - Punto de Venta: Bs. {{ printData.payment.cardPos.toFixed(2) }}</p>
        <p v-if="printData.payment.pagoMovil > 0"> - Pago Móvil: Bs. {{ printData.payment.pagoMovil.toFixed(2) }}</p>
        <p v-if="printData.payment.cashBs > 0"> - Efectivo Bs: Bs. {{ printData.payment.cashBs.toFixed(2) }}</p>
        <p v-if="printData.payment.cashUsd > 0"> - Efectivo USD: ${{ printData.payment.cashUsd.toFixed(2) }}</p>
        <p v-if="printData.reference">Ref: {{ printData.reference }}</p>
      </div>

      <div class="print-footer">
        <p>{{ tExt.printThanks }}</p>
        <p>Tostiyk (TK) ERP</p>
      </div>
    </div>

  </div> <!-- 这是最外层包裹所有界面的 div，只能有一个 -->
</template> <!-- 这是 template 的结束标签，只能有一个 -->

<script setup>

import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { apiFetch } from '../utils/api'
import { useI18n } from '../composables/useI18n'
import ConfirmDialog from './ConfirmDialog.vue'
import PosHelpModal from './pos/PosHelpModal.vue'
import PosHistoryModal from './pos/PosHistoryModal.vue'

const { t, currentLang } = useI18n()

const tExt = computed(() => {
  const isZh = currentLang.value === 'zh'
  const isEs = currentLang.value === 'es'
  
  return {
    switchToCashier: isZh ? '🔄 切换回收银' : isEs ? '🔄 Cambiar a Caja' : '🔄 Switch to Cashier',
    switchToQuote: isZh ? '📄 切换到报价' : isEs ? '📄 Cambiar a Cotización' : '📄 Switch to Quote',
    quoteInfoTitle: isZh ? '报价单信息' : isEs ? 'Información de Cotización' : 'Quotation Info',
    quoteNotesLabel: isZh ? '销售备注' : isEs ? 'Notas de Venta' : 'Sales Notes',
    quoteNotesPlaceholder: isZh ? '填写客户要求、保修说明、交货期等...' : isEs ? 'Requisitos del cliente, garantía, entrega...' : 'Client requirements, warranty, delivery...',
    quoteTipTitle: isZh ? '💡 温馨提示:' : isEs ? '💡 Nota:' : '💡 Tip:',
    quoteTipText: isZh ? '生成报价单不会扣减库存。客户确认购买后，请切回收银模式重新开单收款。' : isEs ? 'Generar cotización no descuenta inventario. Cámbiese a Caja para cobrar.' : 'Quotation does not deduct inventory. Switch to Cashier to charge.',
    savingQuote: isZh ? '正在生成...' : isEs ? 'Generando...' : 'Generating...',
    saveQuoteBtn: isZh ? '保存并生成报价单 PDF' : isEs ? 'Guardar y Generar PDF' : 'Save & Generate PDF',
    genQuoteSuccess: isZh ? '报价单已生成并下载' : isEs ? 'Cotización generada y descargada' : 'Quotation generated and downloaded',
    genQuotePdfError: isZh ? '报价单生成成功，但 PDF 下载失败' : isEs ? 'Cotización generada, pero fallo al descargar PDF' : 'Quotation generated, but PDF download failed',
    genQuoteFail: isZh ? '生成报价单失败' : isEs ? 'Error al generar cotización' : 'Failed to generate quotation',
    toastInvalidRif: isZh ? 'RIF 格式错误：必须是 8 到 9 位数字' : isEs ? 'Formato RIF inválido: 8 a 9 dígitos' : 'Invalid RIF: 8-9 digits',
    toastInvalidPhone: isZh ? '电话号码错误：必须是 10 位数字' : isEs ? 'Teléfono inválido: 10 dígitos' : 'Invalid phone: 10 digits',
    
    clearClient: isZh ? '清除当前选中客户' : isEs ? 'Limpiar cliente' : 'Clear client',
    clientSelected: isZh ? '当前已选客户' : isEs ? 'Cliente Seleccionado' : 'Selected Client',
    noClientSelected: isZh ? '未选择客户' : isEs ? 'Sin cliente' : 'No Client',
    cartOem: isZh ? 'OEM 编号' : isEs ? 'OEM' : 'OEM',
    cartName: isZh ? '配件名称' : isEs ? 'Descripción' : 'Description',
    cartPrice: isZh ? '单价 ($ / Bs.)' : isEs ? 'Precio ($ / Bs.)' : 'Price ($ / Bs.)',
    cartQty: isZh ? '数量' : isEs ? 'Cant.' : 'Qty',
    cartSubtotal: isZh ? '小计 ($ / Bs.)' : isEs ? 'Subtotal ($ / Bs.)' : 'Subtotal ($ / Bs.)',
    cartAction: isZh ? '操作' : isEs ? 'Acción' : 'Action',
    cartEmpty: isZh ? '购物车为空，请按 [/] 键搜索添加...' : isEs ? 'Carrito vacío, presione [/]...' : 'Cart is empty, press [/]...',
    recallTitle: isZh ? '云端挂单恢复大厅' : isEs ? 'Sala de Recuperación de Pedidos' : 'Held Orders Recovery',
    recallBtn: isZh ? '恢复取单' : isEs ? 'Recuperar' : 'Recall',
    recallVoid: isZh ? '作废' : isEs ? 'Anular' : 'Void',
    recallTime: isZh ? '挂单时间:' : isEs ? 'Hora:' : 'Time:',
    recallEmpty: isZh ? '当前云端挂单池为空' : isEs ? 'No hay pedidos en espera' : 'No held orders',
    recallFound: isZh ? '笔挂单' : isEs ? 'pedidos' : 'orders',
    shiftTitle: isZh ? '收银交接班与营业汇总' : isEs ? 'Cierre de Caja y Resumen' : 'Shift Handover & Summary',
    shiftSystemTitle: isZh ? '1. 系统统计应收' : isEs ? '1. Esperado por Sistema' : '1. System Snapshot',
    shiftTodayOnly: isZh ? '仅统计今日订单' : isEs ? 'Solo hoy' : 'Today only',
    shiftTotalRevenue: isZh ? '系统总营业额' : isEs ? 'Total Ventas' : 'Total Revenue',
    shiftActualTitle: isZh ? '2. 收银员实盘录入款项' : isEs ? '2. Conteo Real del Cajero' : '2. Actual Count',
    shiftActualDesc: isZh ? '请仔细清点并录入抽屉及账面实际金额' : isEs ? 'Ingrese el monto real contado' : 'Enter actual counted amount',
    shiftDiff: isZh ? '盈亏' : isEs ? 'Diferencia' : 'Difference',
    shiftTotalDiff: isZh ? '折算总盈亏' : isEs ? 'Diferencia Total' : 'Total Difference',
    shiftNotes: isZh ? '盈亏原因备注' : isEs ? 'Notas de Diferencia' : 'Difference Notes',
    shiftNotesPlace: isZh ? '例如：Bs. 零钱误差...' : isEs ? 'Ej: Error de cambio...' : 'E.g. Change error...',
    shiftConfirm: isZh ? '确认交班并锁定归档' : isEs ? 'Confirmar Cierre' : 'Confirm Shift',
    ticketTitle: isZh ? '收银小票实时预览与出单' : isEs ? 'Vista Previa de Recibo' : 'Ticket Preview',
    ticketClient: isZh ? '客户' : isEs ? 'Cliente' : 'Client',
    ticketOperator: isZh ? '收银员' : isEs ? 'Cajero' : 'Operator',
    ticketPayment: isZh ? '支付明细' : isEs ? 'Desglose de Pago' : 'Payment Breakdown',
    ticketTotal: isZh ? '总计' : isEs ? 'Total' : 'Total',
    ticketPrinting: isZh ? '正在出单...' : isEs ? 'Emitiendo...' : 'Printing...',
    clientModalTitle: isZh ? '快捷选择客户' : isEs ? 'Selección Rápida de Cliente' : 'Quick Client Select',
    clientModalSearch: isZh ? '输入客户名称或电话搜索...' : isEs ? 'Buscar por nombre o teléfono...' : 'Search by name or phone...',
    clientNoPhone: isZh ? '无电话' : isEs ? 'Sin teléfono' : 'No phone',
    clientSelectBtn: isZh ? '选择此客户' : isEs ? 'Seleccionar' : 'Select',
    clientNotFound: isZh ? '未找到客户' : isEs ? 'Cliente no encontrado' : 'Client not found',
    createThisClient: isZh ? '一键新建客户' : isEs ? 'Crear nuevo cliente' : 'Create new client',
    typeToSearch: isZh ? '请输入客户名称进行搜索...' : isEs ? 'Escriba el nombre para buscar...' : 'Type name to search...',
    createClientTitle: isZh ? '快速新建客户档案' : isEs ? 'Creación Rápida de Cliente' : 'Quick Create Client',
    newClientBtn: isZh ? '新建客户' : isEs ? 'Nuevo Cliente' : 'New Client',
    clientTypeRegular: isZh ? 'Regular (零售)' : isEs ? 'Regular (Minorista)' : 'Regular (Retail)',
    clientTypeTaller: isZh ? 'Taller (修理厂)' : isEs ? 'Taller (Mecánico)' : 'Workshop',
    clientTypeMayorista: isZh ? 'Mayorista (批发商)' : isEs ? 'Mayorista (Distribuidor)' : 'Wholesaler',
    isSpecialTaxpayer: isZh ? '标记为特殊纳税人 (需代扣 IVA)' : isEs ? 'Contribuyente Especial (Retención IVA)' : 'Special Taxpayer (VAT withholding)',
    specialTaxpayerNotice: isZh ? '该客户为 SENIAT 特殊纳税人，依法需开具发票并代扣部分 IVA。' : isEs ? 'Cliente Especial (SENIAT). Requiere factura y retención de IVA.' : 'Special Taxpayer (SENIAT). Requires invoice and VAT withholding.',
    exitTitle: isZh ? '确认退出收银台？' : isEs ? '¿Salir de Caja?' : 'Exit POS?',
    exitMsg: isZh ? '当前收银台若有未结算商品，是否继续？' : isEs ? '¿Seguro? El carrito actual se perderá.' : 'Cart will be cleared. Continue?',
    toastStockError: isZh ? '库存不足' : isEs ? 'Stock insuficiente' : 'Insufficient stock',
    toastHoldSuccess: isZh ? '订单已成功挂入云端挂单池！' : isEs ? '¡Pedido pausado exitosamente!' : 'Order held successfully!',
    toastHoldEmpty: isZh ? '当前购物车为空，无需挂单！' : isEs ? 'Carrito vacío' : 'Cart is empty',
    toastRecallSuccess: isZh ? '成功取回挂单' : isEs ? 'Pedido recuperado' : 'Order recalled',
    toastRecallError: isZh ? '解析失败' : isEs ? 'Error al analizar' : 'Parse error',
    toastShiftSuccess: isZh ? '交接班成功，班次已成功锁定归档！' : isEs ? '¡Cierre de caja exitoso!' : 'Shift closed successfully!',
    toastShiftError: isZh ? '交接班归档失败' : isEs ? 'Error al cerrar caja' : 'Shift close failed',
    toastCheckoutSuccess: isZh ? '开单成功！单号:' : isEs ? '¡Venta exitosa! Nro:' : 'Checkout success! No:',
    toastCheckoutError: isZh ? '结账失败' : isEs ? 'Error al cobrar' : 'Checkout failed',
    toastReturnSuccess: isZh ? '退货成功' : isEs ? 'Devolución exitosa' : 'Return successful',
    toastReturnError: isZh ? '退货失败' : isEs ? 'Error en la devolución' : 'Return failed',
    toastReprint: isZh ? '打印小票' : isEs ? 'Reimprimir ticket' : 'Reprint ticket',
    checkoutSuccessTitle: isZh ? '交易完成！' : isEs ? '¡Pago Exitoso!' : 'Payment Successful!',
    toastClientCreated: isZh ? '客户创建成功并已选中！' : isEs ? '¡Cliente creado y seleccionado!' : 'Client created and selected!',
    errorRequired: isZh ? '请输入客户名称' : isEs ? 'Ingrese el nombre del cliente' : 'Enter client name',

    printOrderNo: isZh ? '单号:' : isEs ? 'Nro:' : 'No:',
    printDate: isZh ? '日期:' : isEs ? 'Fecha:' : 'Date:',
    printClient: isZh ? '客户:' : isEs ? 'Cliente:' : 'Client:',
    printOperator: isZh ? '收银:' : isEs ? 'Cajero:' : 'Operator:',
    printItemsTitle: isZh ? '商品' : isEs ? 'Producto' : 'Item',
    printQtyTitle: isZh ? '数量' : isEs ? 'Cant.' : 'Qty',
    printSubtotalTitle: isZh ? '小计' : isEs ? 'Subtotal' : 'Subtotal',
    printPaymentTitle: isZh ? '支付明细:' : isEs ? 'Pagos:' : 'Payments:',
    printThanks: isZh ? '感谢惠顾！' : isEs ? '¡Gracias por su compra!' : 'Thank you!',
  }
})

const props = defineProps({
  partsList: Array,
  clientsList: Array,
  cartItems: Array,
  bcvRate: Number,
  currentDateTime: String,
  currentUser: Object
})

const emit = defineEmits(['add-to-cart', 'generate-quote', 'exit-pos', 'clear-cart', 'refresh-clients'])

const deskSearchQuery = ref('')
const quoteClientName = ref('')
const quoteClientId = ref(null)
const paymentReference = ref('')
const searchInputRef = ref(null)
const selectedIndex = ref(0)
const selectedCartIndex = ref(0)
const activeItemRef = ref(null)
const exitConfirmVisible = ref(false)

const itemInputQuantities = ref([])

watch(() => props.cartItems, (newItems) => {
  itemInputQuantities.value = newItems.map(i => String(i.quantity))
}, { deep: true, immediate: true })

const applyMultiplierQuantity = (index) => {
  const raw = String(itemInputQuantities.value[index] || '').trim()
  const item = props.cartItems[index]
  if (!item) return
  let targetQty = item.quantity
  if (raw.includes('*')) {
    const parts = raw.split('*')
    const multiplier = parseInt(parts[0])
    if (!isNaN(multiplier) && multiplier > 0) targetQty = multiplier
  } else {
    const parsed = parseInt(raw)
    if (!isNaN(parsed) && parsed > 0) targetQty = parsed
  }
  item.quantity = Math.max(1, targetQty)
  itemInputQuantities.value[index] = String(item.quantity)
}

const primaryCurrency = ref('USD')
const toggleMainCurrency = () => {
  primaryCurrency.value = primaryCurrency.value === 'USD' ? 'BS' : 'USD'
}

const cardPosInputRef = ref(null)
const pagoMovilInputRef = ref(null)
const cashBsInputRef = ref(null)
const cashUsdInputRef = ref(null)
const referenceInputRef = ref(null)

const paymentSplit = ref({
  cardPos: 0,
  pagoMovil: 0,
  cashBs: 0,
  cashUsd: 0
})

// 🌟 新增：报价模式开关和备注
const isQuoteMode = ref(true) // 🌟 这个页面永远是报价模式
const quoteNotes = ref('')

const goodsTotalUsd = computed(() => {
  const totalCents = props.cartItems.reduce((sum, item) => {
    return sum + Math.round(item.price * 100) * item.quantity
  }, 0)
  return totalCents / 100
})

const totalBaseUsd = computed(() => {
  let totalCents = 0
  props.cartItems.forEach(item => {
    const rate = item.tax_rate ?? 0.16
    const lineTotalCents = Math.round(item.price * 100) * item.quantity
    if (rate > 0) {
      totalCents += Math.round(lineTotalCents / (1.0 + rate))
    } else {
      totalCents += lineTotalCents
    }
  })
  return totalCents / 100
})

const totalTaxUsd = computed(() => {
  const diffCents = Math.round(goodsTotalUsd.value * 100) - Math.round(totalBaseUsd.value * 100)
  return diffCents / 100
})

const igtfAmountUsd = computed(() => {
  return 0 // 🌟 彻底关闭 3% IGTF
})

const totalUsd = computed(() => {
  const totalCents = Math.round(goodsTotalUsd.value * 100) + Math.round(igtfAmountUsd.value * 100)
  return totalCents / 100
})

const totalPaidUsd = computed(() => {
  const rate = props.bcvRate || 1
  const cCardCents = Math.round((Number(paymentSplit.value.cardPos) || 0) / rate * 100)
  const cPagoCents = Math.round((Number(paymentSplit.value.pagoMovil) || 0) / rate * 100)
  const cBsCents = Math.round((Number(paymentSplit.value.cashBs) || 0) / rate * 100)
  const cUsdCents = Math.round((Number(paymentSplit.value.cashUsd) || 0) * 100)
  
  const paidCents = cCardCents + cPagoCents + cBsCents + cUsdCents
  return paidCents / 100
})

const balanceRemaining = computed(() => {
  const balanceCents = Math.round(totalUsd.value * 100) - Math.round(totalPaidUsd.value * 100)
  return balanceCents / 100
})

const isFullyPaid = computed(() => {
  return totalUsd.value > 0 && totalPaidUsd.value >= totalUsd.value
})

// 🌟 判断当前客户是否为特殊纳税人
const currentClientIsSpecial = computed(() => {
  if (!quoteClientName.value || !props.clientsList) return false
  const client = props.clientsList.find(c =>
    quoteClientId.value ? c.id === quoteClientId.value : c.name === quoteClientName.value
  )
  return client?.is_special_taxpayer || false
})

const handlePaymentKeydown = (e, channelKey) => {
  const orderSequence = ['cardPos', 'pagoMovil', 'cashBs', 'cashUsd', 'reference']
  const currentIndex = orderSequence.indexOf(channelKey)

  if (e.ctrlKey && e.key === 'Enter') {
    e.preventDefault()
    e.stopPropagation()
    if (isFullyPaid.value && props.cartItems.length > 0 && !isSubmitting.value) {
      openPreviewModal()
    }
    return
  }

  if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (currentIndex > 0) {
      const prevKey = orderSequence[currentIndex - 1]
      focusPaymentChannel(prevKey)
    }
    return
  }

  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (currentIndex !== -1 && currentIndex < orderSequence.length - 1) {
      const nextKey = orderSequence[currentIndex + 1]
      focusPaymentChannel(nextKey)
    }
    return
  }

  if (channelKey === 'reference') return

  if (e.key === ' ' || e.key === '=') {
    e.preventDefault()
    const rate = props.bcvRate || 1

    let otherPaidInUsd = 0
    for (const k in paymentSplit.value) {
      if (k !== channelKey) {
        const val = Number(paymentSplit.value[k]) || 0
        if (k === 'cashUsd') {
          otherPaidInUsd += val
        } else {
          otherPaidInUsd += val / rate
        }
      }
    }

    if (channelKey === 'cashUsd') {
      const goodsNeeded = Math.max(0, goodsTotalUsd.value - otherPaidInUsd)
      paymentSplit.value.cashUsd = Number(goodsNeeded.toFixed(2))
    } else {
      const neededUsd = Math.max(0, goodsTotalUsd.value - otherPaidInUsd)
      paymentSplit.value[channelKey] = Number((neededUsd * rate).toFixed(2))
    }
    return
  }

  if (e.key === 'Enter') {
    e.preventDefault()
    if (isFullyPaid.value && !isSubmitting.value) {
      openPreviewModal()
      return
    }
    if (currentIndex !== -1 && currentIndex < orderSequence.length - 1) {
      const nextKey = orderSequence[currentIndex + 1]
      focusPaymentChannel(nextKey)
    }
  }
}

const focusPaymentChannel = (key) => {
  if (key === 'cardPos' && cardPosInputRef.value) cardPosInputRef.value.focus()
  else if (key === 'pagoMovil' && pagoMovilInputRef.value) pagoMovilInputRef.value.focus()
  else if (key === 'cashBs' && cashBsInputRef.value) cashBsInputRef.value.focus()
  else if (key === 'cashUsd' && cashUsdInputRef.value) cashUsdInputRef.value.focus()
  else if (key === 'reference' && referenceInputRef.value) referenceInputRef.value.focus()
}

watch(goodsTotalUsd, (newVal) => {
  const rate = props.bcvRate || 1
  if (newVal > 0) {
    paymentSplit.value = {
      cardPos: Number((newVal * rate).toFixed(2)),
      pagoMovil: 0,
      cashBs: 0,
      cashUsd: 0
    }
  } else {
    paymentSplit.value = { cardPos: 0, pagoMovil: 0, cashBs: 0, cashUsd: 0 }
  }
}, { immediate: true })

watch(() => props.cartItems.length, (newLen) => {
  if (newLen === 0) {
    selectedCartIndex.value = 0
  } else if (selectedCartIndex.value >= newLen) {
    selectedCartIndex.value = newLen - 1
  }
})

const systemConfig = ref({ company_name: 'TOSTIYK (TK) - VENEZUELA', rif: 'J-00000000-0', address: 'Valencia, Carabobo' })

const fetchSystemSettings = async () => {
  try {
    const res = await apiFetch('/api/settings')
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
  cardPos: { amount: 0, count: 0 },
  pagoMovil: { amount: 0, count: 0 },
  cashBs: { amount: 0, count: 0 },
  cashUsd: { amount: 0, count: 0 },
  baseUsd: 0,
  taxUsd: 0,
  igtfUsd: 0,
  totalUsd: 0,
  totalCount: 0
})

const actualCounts = ref({
  cardPos: 0,
  pagoMovil: 0,
  cashBs: 0,
  cashUsd: 0
})
const handoverNotes = ref('')

const cardPosDiff = computed(() => Number(((actualCounts.value.cardPos || 0) - (shiftStats.value.cardPos.amount * (props.bcvRate || 1))).toFixed(2)))
const pagoMovilDiff = computed(() => Number(((actualCounts.value.pagoMovil || 0) - (shiftStats.value.pagoMovil.amount * (props.bcvRate || 1))).toFixed(2)))
const cashBsDiff = computed(() => Number(((actualCounts.value.cashBs || 0) - (shiftStats.value.cashBs.amount * (props.bcvRate || 1))).toFixed(2)))
const cashUsdDiff = computed(() => Number(((actualCounts.value.cashUsd || 0) - shiftStats.value.cashUsd.amount).toFixed(2)))

const totalUsdDiff = computed(() => {
  const rate = props.bcvRate || 1
  const diffInUsd = (cardPosDiff.value / rate) + (pagoMovilDiff.value / rate) + (cashBsDiff.value / rate) + cashUsdDiff.value
  return Number(diffInUsd.toFixed(2))
})

const submitShiftHandover = async () => {
  try {
    const rate = Number(props.bcvRate) || 0
    if (rate <= 0) {
      showToast('❌ ' + tExt.value.toastShiftError, 'error')
      return
    }

    const money = (n) => Number((Number(n) || 0).toFixed(2))
    const payload = {
      bcv_rate: rate,

      system_base_amount_usd: money(shiftStats.value.baseUsd),
      system_tax_amount_usd: money(shiftStats.value.taxUsd),
      system_igtf_amount_usd: money(shiftStats.value.igtfUsd),

      system_card_pos_bs: money(shiftStats.value.cardPos.amount * rate),
      system_pago_movil_bs: money(shiftStats.value.pagoMovil.amount * rate),
      system_cash_bs: money(shiftStats.value.cashBs.amount * rate),
      system_cash_usd: money(shiftStats.value.cashUsd.amount),
      system_zelle_usd: 0,
      system_transfer_bs: 0,
      system_usdt_usd: 0,
      system_total_usd: money(shiftStats.value.totalUsd),

      actual_card_pos_bs: money(actualCounts.value.cardPos),
      actual_pago_movil_bs: money(actualCounts.value.pagoMovil),
      actual_cash_bs: money(actualCounts.value.cashBs),
      actual_cash_usd: money(actualCounts.value.cashUsd),
      actual_zelle_usd: 0,
      actual_transfer_bs: 0,
      actual_usdt_usd: 0,

      notes: handoverNotes.value || ''
    }
    const res = await apiFetch('/api/pos/shift-handover', { method: 'POST', body: JSON.stringify(payload) })
    if (!res.ok) throw new Error(tExt.value.toastShiftError)
    showToast('🔒 ' + tExt.value.toastShiftSuccess, 'success')
    shiftReportModalVisible.value = false
  } catch (err) { showToast('❌ ' + err.message, 'error') }
}

const previewModalVisible = ref(false)
const pendingRequestId = ref(null)
const makeRequestId = () => {
  try {
    return crypto.randomUUID()
  } catch (e) {
    return `req-${Date.now()}-${Math.random().toString(16).slice(2)}`
  }
}
// 关闭预览（返回修改/成功/取消）即视为放弃本次幂等键；
// 停留在预览页重试时则复用同一个 request_id，避免重复扣库存。
watch(previewModalVisible, (visible) => {
  if (!visible) pendingRequestId.value = null
})
const isPreviewReady = ref(false)
const helpModalVisible = ref(false)
const toastMessage = ref('')
const toastType = ref('success')
const checkoutSuccessVisible = ref(false)
let toastTimer = null

const showToast = (msg, type = 'error') => {
  toastMessage.value = msg
  toastType.value = type
  if (toastTimer) clearTimeout(toastTimer)
  toastTimer = setTimeout(() => { toastMessage.value = '' }, 1500)
}

// 🌟 客户弹窗逻辑
const clientModalVisible = ref(false)
const clientFilterQuery = ref('')
const clientModalInputRef = ref(null)

const openClientSearchModal = async () => {
  clientFilterQuery.value = quoteClientName.value || ''
  clientModalVisible.value = true
  await nextTick()
  if (clientModalInputRef.value) {
    clientModalInputRef.value.focus()
    clientModalInputRef.value.select()
  }
}

const selectClient = (client) => {
  quoteClientName.value = client?.name || ''
  quoteClientId.value = client?.id ?? null
  clientModalVisible.value = false
}

const handleClientModalKeydown = (e) => {
  if (e.key === 'Enter') {
    const matched = filteredModalClients.value
    if (matched.length > 0) {
      selectClient(matched[0])
    } else if (clientFilterQuery.value.trim()) {
      prepareCreateClient(clientFilterQuery.value)
    }
  }
}

const filteredModalClients = computed(() => {
  if (!props.clientsList) return []
  if (!clientFilterQuery.value.trim()) return props.clientsList
  const q = clientFilterQuery.value.toUpperCase()
  return props.clientsList.filter(c => c.name.toUpperCase().includes(q) || (c.phone && c.phone.toUpperCase().includes(q)))
})

// 🌟 新建客户逻辑
const newClientModalVisible = ref(false)
const isSavingClient = ref(false)
// 细化字段
const newClientForm = ref({
  name: '',
  rif_type: 'V',     // V, E, J, G
  rif_number: '',    // 仅数字部分
  phone: '',         // 仅10位数字部分
  client_type: 'Regular',
  address: '',
  notes: '',
  is_special_taxpayer: false
})

// 格式化手机号输入
const formatPhoneNumber = (e) => {
  let val = e.target.value.replace(/\D/g, '')
  if (val.length > 10) val = val.slice(0, 10)
  newClientForm.value.phone = val
}

// 格式化 RIF 输入
const formatRifNumber = (e) => {
  let val = e.target.value.replace(/\D/g, '')
  if (val.length > 9) val = val.slice(0, 9)
  newClientForm.value.rif_number = val
}

const prepareCreateClient = (nameToCreate) => {
  newClientForm.value = { 
    name: nameToCreate || '', 
    rif_type: 'V',
    rif_number: '', 
    phone: '', 
    client_type: 'Regular', 
    address: '', 
    notes: '',
    is_special_taxpayer: false
  }
  clientModalVisible.value = false 
  newClientModalVisible.value = true 
}

const saveNewClient = async () => {
  if (!newClientForm.value.name.trim()) {
    showToast(tExt.value.errorRequired, 'error')
    return
  }

  // 🌟 新增：前端 RIF 格式拦截
  if (newClientForm.value.rif_number && !/^\d{8,9}$/.test(newClientForm.value.rif_number)) {
    showToast('❌ ' + tExt.value.toastInvalidRif, 'error')
    return
  }

  // 🌟 新增：前端电话格式拦截
  if (newClientForm.value.phone && newClientForm.value.phone.length !== 10) {
    showToast('❌ ' + tExt.value.toastInvalidPhone, 'error')
    return
  }
  
  // 组装提交格式
  const finalRif = newClientForm.value.rif_number ? `${newClientForm.value.rif_type}-${newClientForm.value.rif_number}` : ""
  const finalPhone = newClientForm.value.phone ? `+58${newClientForm.value.phone}` : ""
  
  const payload = {
    name: newClientForm.value.name,
    rif_or_cedula: finalRif,
    phone: finalPhone,
    client_type: newClientForm.value.client_type,
    address: newClientForm.value.address,
    notes: newClientForm.value.notes,
    is_special_taxpayer: newClientForm.value.is_special_taxpayer
  }

  isSavingClient.value = true
  try {
    const res = await apiFetch('/api/clients', {
      method: 'POST',
      body: JSON.stringify(payload)
    })
    if (res.ok) {
      const data = await res.json()
      newClientModalVisible.value = false
      quoteClientName.value = data.name
      quoteClientId.value = data.id ?? null
      
      // 🌟 核心修复：清空搜索词，并关闭可能还开着的选择弹窗
      clientFilterQuery.value = ''
      clientModalVisible.value = false
      
      showToast('✅ ' + tExt.value.toastClientCreated, 'success')
      
      emit('refresh-clients')
    } else {
      // 🌟 修复：安全地解析错误信息，防止数组导致的崩溃
      let errorMsg = 'Unknown Error'
      try {
        const err = await res.json()
        if (typeof err.detail === 'string') errorMsg = err.detail
        else if (Array.isArray(err.detail)) errorMsg = err.detail[0]?.msg || 'Validation Error'
      } catch (e) {}
      showToast(`❌ ${errorMsg}`, 'error')
    }
  } catch (e) {
    showToast('❌ ' + t.common.error, 'error')
  } finally {
    isSavingClient.value = false
  }
}

// ==================== 历史报价联动 ====================
const historyQuotesModalVisible = ref(false)
const showLoadConfirm = ref(false)
const pendingQuoteToLoad = ref(null)
const historyQuotesList = ref([])
const isFetchingQuotes = ref(false)

const openHistoryQuotesModal = async () => {
  historyQuotesModalVisible.value = true
  isFetchingQuotes.value = true
  try {
    const res = await apiFetch('/api/quotations')
    if (res.ok) {
      historyQuotesList.value = await res.json()
    }
  } catch (e) {
    showToast('❌ 获取历史报价失败', 'error')
  } finally {
    isFetchingQuotes.value = false
  }
}

const loadQuoteToCart = (quote) => {
  if (props.cartItems.length > 0) {
    // 🌟 新增：先关掉历史列表弹窗
    historyQuotesModalVisible.value = false 
    
    // 再触发确认
    pendingQuoteToLoad.value = quote
    showLoadConfirm.value = true
    return
  }
  executeLoadQuote(quote)
}

// 🌟 新增：真正执行载入的函数
const executeLoadQuote = (quote) => {
  if (!quote) return
  try {
    const parsedItems = JSON.parse(quote.items_json)
    // 1. 清空当前购物车并载入新商品
    props.cartItems.splice(0, props.cartItems.length, ...parsedItems)
    
    // 2. 载入客户信息
    quoteClientName.value = quote.client_name || ''
    const matchedClient = props.clientsList?.find(c => c.name === quote.client_name)
    quoteClientId.value = matchedClient ? matchedClient.id : null
    
    // 3. 如果后端存了备注，顺便恢复
    if (quote.notes) quoteNotes.value = quote.notes

    historyQuotesModalVisible.value = false
    showLoadConfirm.value = false
    pendingQuoteToLoad.value = null
    showToast('✅ 成功载入历史报价', 'success')
  } catch (e) {
    console.error(e)
    showToast('❌ 解析报价数据失败', 'error')
  }
}



// ---------------- 购物车与搜索 ----------------
const filteredParts = computed(() => {
  const qStr = deskSearchQuery.value.trim().toUpperCase()
  if (!qStr) return []
  return props.partsList.filter(p => p.oem.toUpperCase().includes(qStr) || p.name.toUpperCase().includes(qStr)).slice(0, 10)
})

const selectAndAddToCart = (part) => {
  if (part.stock <= 0) {
    showToast(`${tExt.value.toastStockError}: ${part.oem}`, 'error')
    return
  }
  const existing = props.cartItems.find(i => i.oem === part.oem)
  if (existing) {
    existing.quantity += 1
  } else {
    props.cartItems.push({
      oem: part.oem,
      name: part.name,
      brand: part.brand || 'GENERAL',
      price: part.price,
      tax_rate: part.tax_rate ?? 0.16,
      quantity: 1
    })
  }
  deskSearchQuery.value = ''
  selectedIndex.value = 0
  focusSearch()
}

const handleSearchKeydown = (e) => {
  const results = filteredParts.value
  const hasSearchQuery = deskSearchQuery.value.trim().length > 0

  if (hasSearchQuery && results.length > 0) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      e.stopPropagation()
      selectedIndex.value = (selectedIndex.value + 1) % results.length
      if (activeItemRef.value && typeof activeItemRef.value.scrollIntoView === 'function') {
        activeItemRef.value.scrollIntoView({ block: 'nearest' })
      }
      return
    } else if (e.key === 'ArrowUp') {
      e.preventDefault()
      e.stopPropagation()
      selectedIndex.value = (selectedIndex.value - 1 + results.length) % results.length
      if (activeItemRef.value && typeof activeItemRef.value.scrollIntoView === 'function') {
        activeItemRef.value.scrollIntoView({ block: 'nearest' })
      }
      return
    } else if (e.key === 'Enter') {
      e.preventDefault()
      e.stopPropagation()
      selectAndAddToCart(results[selectedIndex.value] || results[0])
      return
    }
  }

  if (e.key === 'ArrowDown' && (!hasSearchQuery || results.length === 0) && props.cartItems.length > 0) {
    e.preventDefault()
    e.stopPropagation()
    if (searchInputRef.value) searchInputRef.value.blur()
    selectedCartIndex.value = 0
    return
  }

  if (e.key === 'Enter' && results.length > 0) {
    e.preventDefault()
    e.stopPropagation()
    selectAndAddToCart(results[0])
  }
}

const focusSearch = () => { if (searchInputRef.value) searchInputRef.value.focus() }
const deleteLastItem = () => { if (props.cartItems.length > 0) props.cartItems.pop() }

const holdCurrentOrder = async () => {
  if (props.cartItems.length === 0) {
    showToast('📌 ' + tExt.value.toastHoldEmpty, 'error')
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
      quoteClientId.value = null
      showToast('📌 ' + tExt.value.toastHoldSuccess, 'success')
      fetchHeldOrders()
    }
  } catch (e) { showToast('❌ ' + tExt.value.toastHoldEmpty, 'error') }
}

const openRecallModal = async () => {
  await fetchHeldOrders()
  if (heldOrders.value.length === 0) {
    showToast('❌ ' + tExt.value.recallEmpty, 'error')
    return
  }
  recallModalVisible.value = true
}

const recallOrder = (order) => {
  try {
    const parsedItems = JSON.parse(order.items_json)
    props.cartItems.splice(0, props.cartItems.length, ...parsedItems)
    const matchedClient = props.clientsList?.find(c => c.name === order.client_name)
    quoteClientName.value = order.client_name
    quoteClientId.value = matchedClient?.id ?? null
    apiFetch(`/api/held-orders/${order.id}`, { method: 'DELETE' }).then(() => fetchHeldOrders())
    recallModalVisible.value = false
    showToast('✅ ' + tExt.value.toastRecallSuccess, 'success')
  } catch (e) { showToast('❌ ' + tExt.value.toastRecallError, 'error') }
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

    const todayStr = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Caracas' })

    let cardAmtCents = 0, pUsdCents = 0, cBsCents = 0, cUsdCents = 0, tUsdCents = 0
    let baseCents = 0, taxCents = 0, igtfCents = 0
    let todayOrderCount = 0

    ordersData.forEach(o => {
      // 已退货订单不计入班结营收/支付渠道统计
      if (o.status === 'REFUNDED') return
      if (o.time && o.time.startsWith(todayStr)) {
        const amtCents = Math.round(o.totalUsd * 100)
        tUsdCents += amtCents
        baseCents += Math.round((o.baseAmountUsd || 0) * 100)
        taxCents += Math.round((o.taxAmountUsd || 0) * 100)
        igtfCents += Math.round((o.igtfAmountUsd || 0) * 100)
        todayOrderCount++
        if (o.paymentMethod === 'Card_POS') cardAmtCents += amtCents
        else if (o.paymentMethod === 'Pago_Movil') pUsdCents += amtCents
        else if (o.paymentMethod === 'Cash_Bs') cBsCents += amtCents
        else if (o.paymentMethod === 'Cash_USD') cUsdCents += amtCents
      }
    })

    shiftStats.value = {
      cardPos: { amount: cardAmtCents / 100, count: 0 },
      pagoMovil: { amount: pUsdCents / 100, count: 0 },
      cashBs: { amount: cBsCents / 100, count: 0 },
      cashUsd: { amount: cUsdCents / 100, count: todayOrderCount },
      baseUsd: baseCents / 100,
      taxUsd: taxCents / 100,
      igtfUsd: igtfCents / 100,
      totalUsd: tUsdCents / 100,
      totalCount: todayOrderCount
    }

    actualCounts.value = {
      cardPos: Number(((cardAmtCents / 100) * (props.bcvRate || 1)).toFixed(2)),
      pagoMovil: Number(((pUsdCents / 100) * (props.bcvRate || 1)).toFixed(2)),
      cashBs: Number(((cBsCents / 100) * (props.bcvRate || 1)).toFixed(2)),
      cashUsd: cUsdCents / 100
    }
  } catch (e) { console.error(e) }
}

const openHistoryModal = async () => { await fetchCompletedOrders(); historyModalVisible.value = true }
const openShiftReportModal = async () => { await fetchCompletedOrders(); shiftReportModalVisible.value = true }
const reprintOrderTicket = (order) => { showToast(`🖨️ ${tExt.value.toastReprint} #${order.orderId}`, 'success') }
const processReturnOrder = async (dbId) => {
  try {
    const res = await apiFetch(`/api/pos/orders/${dbId}/refund`, { method: 'POST' })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      showToast('❌ ' + (err.detail || tExt.value.toastReturnError), 'error')
      return
    }
    showToast('🔄 ' + tExt.value.toastReturnSuccess, 'success')
    fetchCompletedOrders()
  } catch (e) {
    showToast('❌ ' + tExt.value.toastReturnError, 'error')
  }
}

const confirmExitPos = () => { exitConfirmVisible.value = true }
const executeExitPos = () => { exitConfirmVisible.value = false; emit('exit-pos') }

const openPreviewModal = () => { 
  if (props.cartItems.length === 0 || !isFullyPaid.value || isSubmitting.value) return
  if (!pendingRequestId.value) pendingRequestId.value = makeRequestId()
  previewModalVisible.value = true
  isPreviewReady.value = false
  setTimeout(() => {
    isPreviewReady.value = true
  }, 300)
}

const isSubmitting = ref(false)
const printData = ref(null)

const generateQuotationPDF = async () => {
  if (props.cartItems.length === 0) return
  isSubmitting.value = true
  
  try {
    const payload = {
      client_name: quoteClientName.value || "Cliente General",
      payment_method: "quotation",
      lang: currentLang.value,
      items: props.cartItems.map(i => ({ 
        oem: i.oem, name: i.name, brand: i.brand || "GENERAL", 
        quantity: i.quantity, price: i.price 
      }))
    }

    const res = await apiFetch('/api/quotations/generate', { 
      method: 'POST', 
      body: JSON.stringify(payload) 
    })

    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || tExt.value.genQuoteFail)
    }
    
    // 🌟 核心修改：不再在前端请求 PDF 并下载
    // 直接触发全屏绿色对勾动画
    checkoutSuccessVisible.value = true
    setTimeout(() => { checkoutSuccessVisible.value = false }, 1500)
    
    // 提示成功
    showToast('✅ ' + tExt.value.genQuoteSuccess, 'success')
    
    // 清空当前状态
    emit('clear-cart')
    quoteClientName.value = ''
    quoteClientId.value = null
    quoteNotes.value = ''
    
  } catch (err) {
    showToast('❌ ' + err.message, 'error')
  } finally {
    isSubmitting.value = false
  }
}

const downloadPdf = async (quotationNo) => {
  try {
    // 🌟 核心修改：在 URL 末尾加上了 &lang=${currentLang.value}
    const res = await apiFetch(`/api/quotation/pdf/download?quotation_no=${quotationNo}&lang=${currentLang.value}`)
    
    if (!res.ok) throw new Error('PDF 获取失败')
    
    const blob = await res.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `Quotation_${quotationNo}.pdf`
    document.body.appendChild(a)
    a.click()
    a.remove()
    window.URL.revokeObjectURL(url)
    emit('show-toast', '✅ PDF 下载成功', 'success')
  } catch (err) {
    console.error(err)
    emit('show-toast', '❌ PDF 下载失败', 'error')
  }
}

// 🌟 新增：全单挂账函数
const submitOrderAsCredit = async () => {
  if (!quoteClientId.value) {
    showToast('❌ 必须先选中具体客户才能挂账！', 'error')
    return
  }
  if (props.cartItems.length === 0) return

  isSubmitting.value = true
  try {
    const payload = {
      client_name: quoteClientName.value,
      client_id: quoteClientId.value, // 必须有 ID，后端要用它记账
      request_id: makeRequestId(),
      payment_method: 'Fiado_USD', // 关键！告诉后端这是挂账
      payment_reference: '全单挂账',
      bcv_rate: props.bcvRate,
      igtf_amount: 0,
      items: props.cartItems.map(i => ({ 
        oem: i.oem, name: i.name, brand: i.brand || "GENERAL", 
        quantity: i.quantity, price: i.price 
      }))
    }

    const res = await apiFetch('/api/pos/orders', { method: 'POST', body: JSON.stringify(payload) })
    if (!res.ok) {
      const err = await res.json().catch(() => ({}))
      throw new Error(err.detail || '挂账失败')
    }
    
    const data = await res.json()
    
    // 成功提示
    checkoutSuccessVisible.value = true
    setTimeout(() => { checkoutSuccessVisible.value = false }, 1500)
    showToast(`✅ 挂账成功！单号: ${data.order_no}`, 'success')

    // 清空状态
    paymentReference.value = ''
    quoteClientName.value = ''
    quoteClientId.value = null

    // 🌟 终极修复：强制清空购物车
    props.cartItems.splice(0, props.cartItems.length)
    
    emit('generate-quote')
    
    // 通知父组件刷新（包括购物车和客户数据）
    emit('generate-quote')
    fetchCompletedOrders()

  } catch (err) {
    showToast('❌ ' + err.message, 'error')
  } finally {
    isSubmitting.value = false
  }
}

const confirmAndPrint = async () => {
  if (isSubmitting.value) return 
  isSubmitting.value = true

  try {
    let dominantMethod = 'Cash_USD'
    const split = paymentSplit.value
    if ((split.cardPos || 0) > 0) dominantMethod = 'Card_POS'
    if ((split.pagoMovil || 0) > 0) dominantMethod = 'Pago_Movil'
    if ((split.cashBs || 0) > 0) dominantMethod = 'Cash_Bs'
    if ((split.cashUsd || 0) > 0) dominantMethod = 'Cash_USD'

    const activeChannelsCount = Object.values(split).filter(v => Number(v) > 0).length
    if (activeChannelsCount > 1) {
      dominantMethod = 'Pago_Mixto'
    }

    const payload = {
      client_name: quoteClientName.value || "Cliente General",
      client_id: quoteClientId.value || null,
      request_id: pendingRequestId.value || makeRequestId(),
      payment_method: dominantMethod,
      payment_reference: paymentReference.value,
      bcv_rate: props.bcvRate,
      igtf_amount: igtfAmountUsd.value,
      items: props.cartItems.map(i => ({ oem: i.oem, name: i.name, brand: i.brand || "GENERAL", quantity: i.quantity, price: i.price }))
    }

    const res = await apiFetch('/api/pos/orders', { method: 'POST', body: JSON.stringify(payload) })
    if (!res.ok) throw new Error(tExt.value.toastCheckoutError)
    const data = await res.json()
    
    previewModalVisible.value = false
    checkoutSuccessVisible.value = true
    setTimeout(() => { checkoutSuccessVisible.value = false }, 1500)

    showToast(`✅ ${tExt.value.toastCheckoutSuccess} ${data.order_no}`, 'success')

    // 如果本次 POS 是从报价单转入的，标记该报价为已转订单
    const pendingQid = localStorage.getItem('pending_quotation_id')
    if (pendingQid && data.order_id) {
      try {
        await apiFetch(`/api/quotations/${pendingQid}/mark-converted`, {
          method: 'POST',
          body: JSON.stringify({ order_id: data.order_id })
        })
      } catch (e) {
        console.warn('mark-converted 失败（不影响 POS 结账）', e)
      }
      localStorage.removeItem('pending_quotation_id')
    }

    // 🌟 核心新增：组装打印数据
    printData.value = {
      order_no: data.order_no,
      date: new Date().toLocaleString(),
      client_name: quoteClientName.value || 'Cliente General',
      operator: props.currentUser?.username || 'Admin',
      items: [...props.cartItems], // 深拷贝，防止清空后打印数据丢失
      base_usd: totalBaseUsd.value,
      tax_usd: totalTaxUsd.value,
      total_usd: totalUsd.value,
      total_bs: totalUsd.value * props.bcvRate,
      payment: { ...paymentSplit.value },
      reference: paymentReference.value
    }

    // 清空状态
    paymentReference.value = ''
    quoteClientName.value = ''
    quoteClientId.value = null
    emit('generate-quote')
    fetchCompletedOrders()

    // 🌟 核心新增：延迟 500ms 确保 DOM 更新完毕，然后调起打印机
    setTimeout(() => {
      window.print()
    }, 500)

  } catch (err) { 
    showToast(err.message || tExt.value.toastCheckoutError, 'error') 
  } finally {
    setTimeout(() => {
      isSubmitting.value = false
    }, 1000)
  }
}

const handleGlobalKeydown = (e) => {
  if (previewModalVisible.value || newClientModalVisible.value) {
    if (e.key === 'Enter') { 
      e.preventDefault() 
      e.stopPropagation() 
      if (previewModalVisible.value && isPreviewReady.value && !isSubmitting.value) { 
        confirmAndPrint() 
      } else if (newClientModalVisible.value) {
        saveNewClient()
      }
      return 
    }
    if (e.key === 'Escape') { 
      e.preventDefault() 
      e.stopPropagation()
      previewModalVisible.value = false 
      newClientModalVisible.value = false
      return 
    }
    return
  }

  if (e.ctrlKey && e.key === 'Enter' && !isQuoteMode.value) {
    e.preventDefault()
    e.stopPropagation()
    if (isFullyPaid.value && props.cartItems.length > 0 && !previewModalVisible.value && !isSubmitting.value) {
      openPreviewModal()
    }
    return
  }

  if (clientModalVisible.value || helpModalVisible.value || recallModalVisible.value || shiftReportModalVisible.value || historyModalVisible.value || exitConfirmVisible.value) {
    if (e.key === 'Escape') {
      e.preventDefault()
      e.stopPropagation()
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
      e.stopPropagation()
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

  // 在 handleGlobalKeydown 里加上这段
  if (e.ctrlKey && e.key.toLowerCase() === 's') {
    e.preventDefault()
    if (props.cartItems.length > 0 && !isSubmitting.value) {
      generateQuotationPDF()
    }
    return
  }

  const activeEl = document.activeElement
  const isInputActive = activeEl && (activeEl.tagName === 'INPUT' || activeEl.tagName === 'TEXTAREA')
  const isSearchFocused = activeEl === searchInputRef.value
  const hasSearchQuery = deskSearchQuery.value.trim().length > 0

  if (isSearchFocused && hasSearchQuery && (e.key === 'ArrowDown' || e.key === 'ArrowUp')) {
    return
  }

  if (!isInputActive && props.cartItems.length > 0) {
    if (e.key === 'ArrowDown') {
      e.preventDefault()
      selectedCartIndex.value = (selectedCartIndex.value + 1) % props.cartItems.length
      return
    }
    if (e.key === 'ArrowUp') {
      e.preventDefault()
      selectedCartIndex.value = (selectedCartIndex.value - 1 + props.cartItems.length) % props.cartItems.length
      return
    }
    if (e.key === '+' || e.key === '=' || e.code === 'NumpadAdd') {
      e.preventDefault()
      if (props.cartItems[selectedCartIndex.value]) {
        props.cartItems[selectedCartIndex.value].quantity++
        itemInputQuantities.value[selectedCartIndex.value] = String(props.cartItems[selectedCartIndex.value].quantity)
      }
      return
    }
    if (e.key === '-' || e.code === 'NumpadSubtract') {
      e.preventDefault()
      if (props.cartItems[selectedCartIndex.value] && props.cartItems[selectedCartIndex.value].quantity > 1) {
        props.cartItems[selectedCartIndex.value].quantity--
        itemInputQuantities.value[selectedCartIndex.value] = String(props.cartItems[selectedCartIndex.value].quantity)
      }
      return
    }
    if (e.key === 'Delete' || e.key === 'Backspace') {
      e.preventDefault()
      if (props.cartItems[selectedCartIndex.value]) {
        props.cartItems.splice(selectedCartIndex.value, 1)
        if (selectedCartIndex.value >= props.cartItems.length) {
          selectedCartIndex.value = Math.max(0, props.cartItems.length - 1)
        }
      }
      return
    }
  }

  // 快捷键仅在POS模式生效
  if (!isQuoteMode.value) {
    if (e.key === 'F4') { e.preventDefault(); if (cardPosInputRef.value) cardPosInputRef.value.focus(); return }
    if (e.key === 'F5') { e.preventDefault(); if (pagoMovilInputRef.value) pagoMovilInputRef.value.focus(); return }
    if (e.key === 'F6') { e.preventDefault(); if (cashBsInputRef.value) cashBsInputRef.value.focus(); return }
    if (e.key === 'F7') { e.preventDefault(); if (cashUsdInputRef.value) cashUsdInputRef.value.focus(); return }
  }

  if (e.key === '/' && document.activeElement !== searchInputRef.value) { e.preventDefault(); focusSearch(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'f') { e.preventDefault(); openClientSearchModal(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'h' && !isQuoteMode.value) { e.preventDefault(); holdCurrentOrder(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'r' && !isQuoteMode.value) { e.preventDefault(); openRecallModal(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'b') { e.preventDefault(); emit('clear-cart'); return }
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

input.no-spinner::-webkit-outer-spin-button,
input.no-spinner::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
input[type=number].no-spinner {
  -moz-appearance: textfield;
}

@keyframes popIn {
  0% { transform: scale(0.5); opacity: 0; }
  70% { transform: scale(1.1); opacity: 1; }
  100% { transform: scale(1); opacity: 1; }
}
.animate-pop-in {
  animation: popIn 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275) forwards;
}

/* ==================================================== */
/* 🌟 核心新增：热敏小票打印 CSS 样式                    */
/* ==================================================== */
@media print {
  /* 隐藏整个 Vue 应用的主体，只显示 #print-section */
  body * {
    visibility: hidden;
  }
  #print-section, #print-section * {
    visibility: visible;
  }
  
  /* 定位到左上角，去掉默认边距 */
  #print-section {
    position: absolute;
    left: 0;
    top: 0;
    width: 80mm; /* 80mm 热敏纸宽度，如果是 58mm 请改为 58mm */
    margin: 0;
    padding: 5px;
    font-family: 'Courier New', Courier, monospace; /* 等宽字体，小票标准 */
    font-size: 12px;
    color: #000;
    background: #fff;
    line-height: 1.2;
  }

  /* 强制页面无背景，取消所有阴影 */
  @page {
    size: auto; /* 自动适应打印机尺寸 */
    margin: 0mm; 
  }

  .print-header, .print-footer {
    text-align: center;
  }
  .print-header h2 {
    font-size: 16px;
    margin: 0 0 4px 0;
  }
  .print-header p, .print-footer p {
    margin: 0;
    font-size: 10px;
  }
  
  .divider {
    text-align: center;
    margin: 4px 0;
    overflow: hidden;
    white-space: nowrap;
  }

  .print-meta p {
    margin: 2px 0;
    font-size: 11px;
  }

  .print-items table {
    width: 100%;
    border-collapse: collapse;
  }
  .print-items th, .print-items td {
    padding: 2px 0;
    font-size: 11px;
  }
  .print-items th {
    border-bottom: 1px dashed #000;
  }

  .print-totals p {
    display: flex;
    justify-content: space-between;
    margin: 2px 0;
    font-size: 11px;
  }
  .print-totals .bold {
    font-weight: bold;
    font-size: 13px;
  }

  .print-payments p {
    margin: 2px 0;
    font-size: 10px;
  }

  .print-footer {
    margin-top: 10px;
  }
}
</style>