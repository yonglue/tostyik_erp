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
              <span :class="p.tax_rate > 0 ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-slate-100 text-slate-600 border-slate-200'" class="text-[10px] px-1.5 py-0.5 rounded border font-bold">
                {{ p.tax_rate > 0 ? '16% IVA' : '免税' }}
              </span>
              <span :class="p.stock > 0 ? 'text-emerald-600' : 'text-rose-600 font-bold'" class="text-xs font-mono font-black">
                库存: {{ p.stock }}
              </span>
            </div>
          </div>
          <div v-if="filteredParts.length === 0" class="text-center py-4 text-sm text-slate-400 font-bold">
            未找到相关配件商品
          </div>
        </div>

        <!-- 购物车明细表格 -->
        <div class="flex-1 overflow-y-auto p-2.5">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr class="border-b-2 border-slate-200 text-slate-600 text-xs font-extrabold uppercase bg-slate-100/50">
                <th class="py-3 px-3">OEM 编号</th>
                <th class="py-3 px-3">配件名称</th>
                <th class="py-3 px-3">税率属性 (IVA)</th>
                <th class="py-3 px-3 text-right">单价 ($ / Bs.)</th>
                <th class="py-3 px-3 text-center">数量 (支持 3* 语法)</th>
                <th class="py-3 px-3 text-right">小计 ($ / Bs.)</th>
                <th class="py-3 px-3 text-center">操作</th>
              </tr>
            </thead>
            <tbody class="text-sm font-medium">
              <tr 
                v-for="(item, index) in cartItems" 
                :key="item.oem" 
                @click="selectedCartIndex = index"
                :class="[
                  selectedCartIndex === index ? 'bg-blue-500/15 border-blue-400 ring-1 ring-blue-400' : (index % 2 === 0 ? 'bg-white/80' : 'bg-slate-50/70'),
                  'border-b border-slate-200/70 hover:bg-blue-50/50 transition-all shadow-2xs cursor-pointer'
                ]"
              >
                <td class="py-3 px-3 font-mono font-black text-blue-600 text-sm">{{ item.oem }}</td>
                <td class="py-3 px-3 text-slate-900 font-bold">{{ item.name }}</td>
                <td class="py-3 px-3">
                  <span :class="(item.tax_rate ?? 0.16) > 0 ? 'bg-amber-50 text-amber-700 border-amber-200' : 'bg-slate-100 text-slate-600 border-slate-200'" class="inline-flex items-center px-2 py-0.5 rounded text-[11px] font-bold border">
                    {{ (item.tax_rate ?? 0.16) > 0 ? '16% IVA' : '0% 免税' }}
                  </span>
                </td>
                <td class="py-3 px-3 text-right font-mono text-slate-700 font-bold">
                  <div>${{ item.price.toFixed(2) }}</div>
                  <div class="text-xs text-slate-400 font-normal">Bs. {{ (item.price * bcvRate).toFixed(2) }}</div>
                </td>
                <td class="py-3 px-3 text-center" @click.stop>
                  <div class="inline-flex items-center border border-slate-300 rounded-lg overflow-hidden bg-white shadow-2xs">
                    <button @click="item.quantity > 1 ? item.quantity-- : null" class="px-2.5 py-1 text-slate-600 hover:bg-slate-200 font-bold text-sm">-</button>
                    <input 
                      v-model="itemInputQuantities[index]" 
                      @blur="applyMultiplierQuantity(index)"
                      @keydown.enter="applyMultiplierQuantity(index)"
                      type="text" 
                      placeholder="1" 
                      class="w-12 text-center bg-transparent text-slate-900 text-sm font-mono outline-none font-black" 
                    />
                    <button @click="item.quantity++; itemInputQuantities[index] = item.quantity" class="px-2.5 py-1 text-slate-600 hover:bg-slate-200 font-bold text-sm">+</button>
                  </div>
                </td>
                <td class="py-3 px-3 text-right font-mono font-black text-emerald-600">
                  <div>${{ (item.price * item.quantity).toFixed(2) }}</div>
                  <div class="text-xs text-emerald-700/80 font-normal">Bs. {{ (item.price * item.quantity * bcvRate).toFixed(2) }}</div>
                </td>
                <td class="py-3 px-3 text-center" @click.stop>
                  <button @click="cartItems.splice(index, 1)" class="text-rose-600 text-xs font-bold px-2.5 py-1 bg-rose-500/10 hover:bg-rose-500/20 rounded-lg transition-all cursor-pointer shadow-2xs">删除</button>
                </td>
              </tr>
              <tr v-if="cartItems.length === 0">
                <td colspan="7" class="text-center py-20 text-slate-400 text-sm font-bold">
                  🛒 购物车为空，请按 [/] 键搜索添加配件商品...
                </td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>

      <!-- 右侧：组合支付面板（顺序：刷卡 POS ➔ Pago Móvil ➔ 玻利瓦尔现金 ➔ 美金现金） -->
      <div class="w-[410px] flex flex-col bg-white/75 backdrop-blur-xl rounded-xl border border-white/60 shadow-lg shrink-0 overflow-hidden">
        
        <!-- 内部滚动区域 -->
        <div class="flex-1 overflow-y-auto p-3.5 space-y-3">
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
            <!-- 1. Card POS [F4] -->
            <div class="bg-white/70 hover:bg-white p-2 rounded-xl border border-white/90 hover:border-blue-300 transition-all flex items-center justify-between shadow-2xs">
              <div>
                <span class="font-bold text-slate-800 flex items-center gap-1">💳 刷卡 POS (Bs.) <span class="text-[10px] text-blue-600 font-mono">[F4]</span></span>
                <span class="text-xs text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.cardPos) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.cardPos) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">Bs.</span>
                <input 
                  ref="cardPosInputRef"
                  v-model.number="paymentSplit.cardPos" 
                  @keydown="handlePaymentKeydown($event, 'cardPos')"
                  type="number" step="10" placeholder="0" 
                  class="w-28 bg-white/90 focus:bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-right font-mono font-black text-slate-900 outline-none focus:border-blue-500 text-sm no-spinner" 
                />
              </div>
            </div>

            <!-- 2. Pago Móvil [F5] -->
            <div class="bg-white/70 hover:bg-white p-2 rounded-xl border border-white/90 hover:border-blue-300 transition-all flex items-center justify-between shadow-2xs">
              <div>
                <span class="font-bold text-slate-800 flex items-center gap-1">⚡ 手机支付 Pago Móvil <span class="text-[10px] text-blue-600 font-mono">[F5]</span></span>
                <span class="text-xs text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.pagoMovil) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.pagoMovil) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">Bs.</span>
                <input 
                  ref="pagoMovilInputRef"
                  v-model.number="paymentSplit.pagoMovil" 
                  @keydown="handlePaymentKeydown($event, 'pagoMovil')"
                  type="number" step="10" placeholder="0" 
                  class="w-28 bg-white/90 focus:bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-right font-mono font-black text-slate-900 outline-none focus:border-blue-500 text-sm no-spinner" 
                />
              </div>
            </div>

            <!-- 3. Efectivo Bs. [F6] -->
            <div class="bg-white/70 hover:bg-white p-2 rounded-xl border border-white/90 hover:border-blue-300 transition-all flex items-center justify-between shadow-2xs">
              <div>
                <span class="font-bold text-slate-800 flex items-center gap-1">🇻🇪 玻利瓦尔现金 <span class="text-[10px] text-blue-600 font-mono">[F6]</span></span>
                <span class="text-xs text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ $${((Number(paymentSplit.cashBs) || 0) / (bcvRate || 1)).toFixed(2)}` : `Bs. ${(Number(paymentSplit.cashBs) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">Bs.</span>
                <input 
                  ref="cashBsInputRef"
                  v-model.number="paymentSplit.cashBs" 
                  @keydown="handlePaymentKeydown($event, 'cashBs')"
                  type="number" step="10" placeholder="0" 
                  class="w-28 bg-white/90 focus:bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-right font-mono font-black text-slate-900 outline-none focus:border-blue-500 text-sm no-spinner" 
                />
              </div>
            </div>

            <!-- 4. Cash USD [F7] -->
            <div class="bg-white/70 hover:bg-white p-2 rounded-xl border border-white/90 hover:border-blue-300 transition-all flex items-center justify-between shadow-2xs">
              <div>
                <span class="font-bold text-slate-800 flex items-center gap-1">💵 美金现金 Cash USD <span class="text-[10px] text-blue-600 font-mono">[F7]</span></span>
                <span class="text-xs text-emerald-600 font-mono font-bold">{{ primaryCurrency === 'USD' ? `≈ Bs. ${((Number(paymentSplit.cashUsd) || 0) * bcvRate).toFixed(2)}` : `≈ $${(Number(paymentSplit.cashUsd) || 0).toFixed(2)}` }}</span>
              </div>
              <div class="flex items-center gap-1">
                <span class="text-slate-400 font-bold">$</span>
                <input 
                  ref="cashUsdInputRef"
                  v-model.number="paymentSplit.cashUsd" 
                  @keydown="handlePaymentKeydown($event, 'cashUsd')"
                  type="number" step="0.5" placeholder="0" 
                  class="w-28 bg-white/90 focus:bg-white border border-slate-300 rounded-lg px-2.5 py-1 text-right font-mono font-black text-slate-900 outline-none focus:border-blue-500 text-sm no-spinner" 
                />
              </div>
            </div>
          </div>

          <!-- 回执号码 -->
          <div class="flex items-center gap-2 bg-white/70 hover:bg-white border border-slate-200 hover:border-blue-300 rounded-xl px-3 py-2 shadow-2xs transition-all">
            <span class="w-1/3 text-xs font-black text-slate-700 shrink-0 truncate">回执号码:</span>
            <input 
              ref="referenceInputRef"
              v-model="paymentReference" 
              @keydown="handlePaymentKeydown($event, 'reference')"
              type="text" 
              placeholder="选填，如 Pago Móvil 回执号..." 
              class="w-2/3 bg-transparent text-xs font-bold text-slate-900 outline-none font-mono placeholder-slate-400" 
            />
          </div>

          <!-- 底部应付、已付、找零汇总区 -->
          <div class="space-y-2.5 pt-2 border-t border-slate-200/60">
            <!-- 1. 不含税总额 (Base Imponible) -->
            <div class="flex justify-between items-start text-sm font-bold text-slate-600">
              <span class="font-bold pt-0.5">不含税总额 (Base Imponible):</span>
              <div class="text-right">
                <div class="font-mono text-slate-800 font-extrabold text-sm">
                  {{ primaryCurrency === 'USD' ? `$${totalBaseUsd.toFixed(2)}` : `Bs. ${(totalBaseUsd * bcvRate).toFixed(2)}` }}
                </div>
                <div class="font-mono text-[11px] text-slate-400 font-semibold">
                  {{ primaryCurrency === 'USD' ? `Bs. ${(totalBaseUsd * bcvRate).toFixed(2)}` : `$${totalBaseUsd.toFixed(2)}` }}
                </div>
              </div>
            </div>

            <!-- 2. 增值税 (IVA 16% 混合) -->
            <div class="flex justify-between items-start text-sm font-bold text-slate-600">
              <span class="font-bold pt-0.5">增值税 (IVA 16% 混合):</span>
              <div class="text-right">
                <div class="font-mono text-slate-800 font-extrabold text-sm">
                  {{ primaryCurrency === 'USD' ? `$${totalTaxUsd.toFixed(2)}` : `Bs. ${(totalTaxUsd * bcvRate).toFixed(2)}` }}
                </div>
                <div class="font-mono text-[11px] text-slate-400 font-semibold">
                  {{ primaryCurrency === 'USD' ? `Bs. ${(totalTaxUsd * bcvRate).toFixed(2)}` : `$${totalTaxUsd.toFixed(2)}` }}
                </div>
              </div>
            </div>

            <!-- 3. 外汇交易税 (IGTF 3%) -->
            <div v-if="igtfAmountUsd > 0" class="flex justify-between items-start text-sm font-bold text-amber-700 border-b border-slate-200/60 pb-1.5">
              <span class="font-bold pt-0.5">大额交易税 (IGTF 3%):</span>
              <div class="text-right">
                <div class="font-mono font-extrabold text-sm">
                  {{ primaryCurrency === 'USD' ? `$${igtfAmountUsd.toFixed(2)}` : `Bs. ${(igtfAmountUsd * bcvRate).toFixed(2)}` }}
                </div>
                <div class="font-mono text-[11px] font-semibold">
                  {{ primaryCurrency === 'USD' ? `Bs. ${(igtfAmountUsd * bcvRate).toFixed(2)}` : `$${igtfAmountUsd.toFixed(2)}` }}
                </div>
              </div>
            </div>

            <!-- 4. 总应付金额 -->
            <div class="flex justify-between items-start text-sm font-bold text-slate-700">
              <span class="font-extrabold text-slate-800 pt-0.5">总应付金额:</span>
              <div class="text-right">
                <div class="font-mono text-slate-900 text-base font-black">
                  {{ primaryCurrency === 'USD' ? `$${totalUsd.toFixed(2)}` : `Bs. ${(totalUsd * bcvRate).toFixed(2)}` }}
                </div>
                <div class="font-mono text-[11px] text-slate-400 font-semibold">
                  {{ primaryCurrency === 'USD' ? `Bs. ${(totalUsd * bcvRate).toFixed(2)}` : `$${totalUsd.toFixed(2)}` }}
                </div>
              </div>
            </div>

            <!-- 5. 已付金额 (Paid) -->
            <div class="flex justify-between items-start text-sm font-bold text-slate-700">
              <span class="font-extrabold text-slate-800 pt-0.5">已付金额 (Paid):</span>
              <div class="text-right">
                <div class="font-mono text-emerald-600 text-base font-black">
                  {{ primaryCurrency === 'USD' ? `$${totalPaidUsd.toFixed(2)}` : `Bs. ${(totalPaidUsd * bcvRate).toFixed(2)}` }}
                </div>
                <div class="font-mono text-[11px] text-emerald-700/80 font-semibold">
                  {{ primaryCurrency === 'USD' ? `Bs. ${(totalPaidUsd * bcvRate).toFixed(2)}` : `$${totalPaidUsd.toFixed(2)}` }}
                </div>
              </div>
            </div>

            <!-- 6. 待付余额 / 找零 -->
            <div class="pt-2 border-t border-slate-200/60 flex justify-between items-start">
              <span class="text-sm font-black pt-0.5" :class="balanceRemaining > 0 ? 'text-rose-600' : 'text-emerald-600'">
                {{ balanceRemaining > 0 ? '🔴 待付余额:' : '🟢 找零 (Cambio):' }}
              </span>
              <div class="text-right">
                <div class="text-xl font-black font-mono leading-tight" :class="balanceRemaining > 0 ? 'text-rose-600' : 'text-emerald-600'">
                  {{ primaryCurrency === 'USD' ? `$${Math.abs(balanceRemaining).toFixed(2)}` : `Bs. ${(Math.abs(balanceRemaining) * bcvRate).toFixed(2)}` }}
                </div>
                <div class="font-mono text-[11px] font-bold" :class="balanceRemaining > 0 ? 'text-rose-500' : 'text-emerald-500'">
                  {{ primaryCurrency === 'USD' ? `Bs. ${(Math.abs(balanceRemaining) * bcvRate).toFixed(2)}` : `$${Math.abs(balanceRemaining).toFixed(2)}` }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 底部固定吸底的出单按钮区 -->
        <div class="p-3 bg-white/90 backdrop-blur-md border-t border-slate-200/60 shrink-0">
          <button 
            @click="openPreviewModal"
            :disabled="!isFullyPaid || cartItems.length === 0"
            class="w-full py-3.5 bg-emerald-600 hover:bg-emerald-500 disabled:bg-slate-200 disabled:text-slate-400 text-white rounded-xl font-black text-sm shadow-md shadow-emerald-600/30 transition-all cursor-pointer flex items-center justify-center gap-1.5"
          >
            <span>🚀 确认收款并出单 ({{ cartItems.length === 0 ? '购物车为空' : (balanceRemaining < 0 ? `找零 $${Math.abs(balanceRemaining).toFixed(2)}` : '已付清') }}) [Ctrl+Enter]</span>
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
    <div v-if="recallModalVisible" @click.self="recallModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
      <div class="bg-white/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-4xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
        <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-white/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 flex items-center gap-2">
            <span>📦 云端挂单恢复大厅 (共 {{ heldOrders.length }} 单)</span>
          </h3>
          <button @click="recallModalVisible = false" class="text-slate-400 hover:text-slate-700 text-base font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-5 space-y-3 bg-white/20 flex flex-col">
          <template v-if="heldOrders.length > 0">
            <div v-for="order in heldOrders" :key="order.id" class="p-4 rounded-2xl border border-slate-200/80 bg-white/80 backdrop-blur-md hover:bg-white transition-all flex items-center justify-between shadow-2xs shrink-0">
              <div class="space-y-1">
                <div class="font-bold text-xs text-slate-800 flex items-center gap-2">
                  <span class="font-mono text-blue-600 font-black text-sm">{{ order.hold_no }}</span>
                  <span class="text-slate-700">👤 {{ order.client_name || '散客' }}</span>
                </div>
                <div class="text-[11px] text-slate-400 font-mono">挂单时间: {{ order.timestamp }}</div>
              </div>
              <div class="flex items-center gap-4">
                <span class="text-base font-mono font-black text-slate-900">${{ order.total_amount.toFixed(2) }}</span>
                <button @click="recallOrder(order)" class="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition-all cursor-pointer shadow-sm">
                  恢复取单
                </button>
                <button @click="deleteHeldOrder(order.id)" class="px-3.5 py-2 bg-rose-50 hover:bg-rose-100 text-rose-600 border border-rose-200 rounded-xl text-xs font-bold transition-all cursor-pointer">
                  作废
                </button>
              </div>
            </div>
          </template>
          <div v-else class="flex-1 flex flex-col items-center justify-center py-20 text-slate-400 text-xs font-bold">
            <span class="text-4xl mb-2">📭</span>
            <span>当前云端挂单池为空</span>
          </div>
        </div>

        <div class="p-5 bg-white/80 backdrop-blur-md border-t border-slate-200/60 flex items-center justify-between shrink-0">
          <span class="text-xs text-slate-600 font-mono font-bold">
            共找到 <strong class="text-slate-900">{{ heldOrders.length }}</strong> 笔挂单
          </span>
          <button @click="recallModalVisible = false" class="px-6 py-2 bg-slate-200/80 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">
            关闭
          </button>
        </div>
      </div>
    </div>

    <!-- 交接班 Modal -->
    <div v-if="shiftReportModalVisible" @click.self="shiftReportModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
      <div class="bg-white/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-4xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
        <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-white/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 flex items-center gap-2">
            <span>📊 收银交接班与营业汇总 (Shift Handover)</span>
          </h3>
          <button @click="shiftReportModalVisible = false" class="text-slate-400 hover:text-slate-700 text-base font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-6 text-sm bg-white/30">
          <div class="bg-white/80 backdrop-blur-md p-5 rounded-2xl border border-white/90 space-y-3 shadow-2xs font-mono">
            <div class="text-xs font-black text-slate-400 uppercase tracking-wider border-b border-slate-200 pb-2">
              1. 系统统计应收 (SYSTEM SNAPSHOT)
            </div>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-xs">
              <div class="bg-slate-50/80 p-3.5 rounded-xl border border-slate-200/80">
                <span class="text-slate-500 block mb-1">💳 刷卡 POS:</span>
                <span class="font-black text-blue-600 text-sm">Bs. {{ (shiftStats.cardPos.amount * bcvRate).toFixed(2) }}</span>
              </div>
              <div class="bg-slate-50/80 p-3.5 rounded-xl border border-slate-200/80">
                <span class="text-slate-500 block mb-1">⚡ Pago Móvil:</span>
                <span class="font-black text-indigo-600 text-sm">Bs. {{ (shiftStats.pagoMovil.amount * bcvRate).toFixed(2) }}</span>
              </div>
              <div class="bg-slate-50/80 p-3.5 rounded-xl border border-slate-200/80">
                <span class="text-slate-500 block mb-1">🇻🇪 Bs. 现金:</span>
                <span class="font-black text-emerald-600 text-sm">Bs. {{ (shiftStats.cashBs.amount * bcvRate).toFixed(2) }}</span>
              </div>
              <div class="bg-slate-50/80 p-3.5 rounded-xl border border-slate-200/80">
                <span class="text-slate-500 block mb-1">💵 美金现金:</span>
                <span class="font-black text-slate-900 text-sm">${{ shiftStats.cashUsd.amount.toFixed(2) }}</span>
              </div>
            </div>
            <div class="pt-2 border-t border-slate-200 flex justify-between items-center text-sm font-black">
              <span class="text-slate-900">系统总营业额 (Total USD):</span>
              <span class="text-emerald-600 text-lg">${{ shiftStats.totalUsd.toFixed(2) }}</span>
            </div>
          </div>

          <div class="bg-blue-50/50 backdrop-blur-md p-5 rounded-2xl border border-blue-200/80 space-y-4 font-mono shadow-2xs">
            <div class="text-xs font-black text-blue-900 uppercase tracking-wider border-b border-blue-200 pb-2 flex justify-between items-center">
              <span>2. 收银员实盘录入款项 (ACTUAL COUNT)</span>
              <span class="text-xs text-blue-700 font-normal">请仔细清点并录入抽屉及账面实际金额</span>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="bg-white p-4 rounded-2xl border border-blue-100 space-y-2 shadow-2xs">
                <label class="block text-xs font-bold text-slate-800">💳 实收 POS 刷卡 (Bs.):</label>
                <div class="flex items-center gap-2">
                  <span class="text-slate-400 font-bold text-base">Bs.</span>
                  <input 
                    v-model.number="actualCounts.cardPos" 
                    type="number" step="10" placeholder="0" 
                    class="w-full bg-white border border-slate-300 rounded-xl px-3.5 py-2.5 text-right font-mono text-base outline-none focus:border-blue-500 font-black text-slate-900 shadow-2xs no-spinner"
                  />
                </div>
                <div class="text-xs text-right font-bold pt-1" :class="cardPosDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ cardPosDiff >= 0 ? '+' : '' }}Bs. {{ cardPosDiff.toFixed(2) }}
                </div>
              </div>

              <div class="bg-white p-4 rounded-2xl border border-blue-100 space-y-2 shadow-2xs">
                <label class="block text-xs font-bold text-slate-800">⚡ 实收 Pago Móvil (Bs.):</label>
                <div class="flex items-center gap-2">
                  <span class="text-slate-400 font-bold text-base">Bs.</span>
                  <input 
                    v-model.number="actualCounts.pagoMovil" 
                    type="number" step="10" placeholder="0" 
                    class="w-full bg-white border border-slate-300 rounded-xl px-3.5 py-2.5 text-right font-mono text-base outline-none focus:border-blue-500 font-black text-slate-900 shadow-2xs no-spinner"
                  />
                </div>
                <div class="text-xs text-right font-bold pt-1" :class="pagoMovilDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ pagoMovilDiff >= 0 ? '+' : '' }}Bs. {{ pagoMovilDiff.toFixed(2) }}
                </div>
              </div>

              <div class="bg-white p-4 rounded-2xl border border-blue-100 space-y-2 shadow-2xs">
                <label class="block text-xs font-bold text-slate-800">🇻🇪 实收 Bs. 现金 (Bs.):</label>
                <div class="flex items-center gap-2">
                  <span class="text-slate-400 font-bold text-base">Bs.</span>
                  <input 
                    v-model.number="actualCounts.cashBs" 
                    type="number" step="10" placeholder="0" 
                    class="w-full bg-white border border-slate-300 rounded-xl px-3.5 py-2.5 text-right font-mono text-base outline-none focus:border-blue-500 font-black text-slate-900 shadow-2xs no-spinner"
                  />
                </div>
                <div class="text-xs text-right font-bold pt-1" :class="cashBsDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ cashBsDiff >= 0 ? '+' : '' }}Bs. {{ cashBsDiff.toFixed(2) }}
                </div>
              </div>

              <div class="bg-white p-4 rounded-2xl border border-blue-100 space-y-2 shadow-2xs">
                <label class="block text-xs font-bold text-slate-800">💵 实收美金现金 (USD):</label>
                <div class="flex items-center gap-2">
                  <span class="text-slate-400 font-bold text-base">$</span>
                  <input 
                    v-model.number="actualCounts.cashUsd" 
                    type="number" step="0.5" placeholder="0" 
                    class="w-full bg-white border border-slate-300 rounded-xl px-3.5 py-2.5 text-right font-mono text-base outline-none focus:border-blue-500 font-black text-slate-900 shadow-2xs no-spinner"
                  />
                </div>
                <div class="text-xs text-right font-bold pt-1" :class="cashUsdDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'">
                  盈亏: {{ cashUsdDiff >= 0 ? '+' : '' }}${{ cashUsdDiff.toFixed(2) }}
                </div>
              </div>
            </div>

            <div class="pt-3 border-t border-blue-200 flex justify-between items-center text-sm">
              <span class="font-extrabold text-slate-800">折算总盈亏 (Diferencia Total):</span>
              <span :class="totalUsdDiff >= 0 ? 'text-emerald-600' : 'text-rose-600'" class="font-black font-mono text-lg">
                {{ totalUsdDiff >= 0 ? '+' : '' }}${{ totalUsdDiff.toFixed(2) }}
              </span>
            </div>
          </div>

          <div v-if="totalUsdDiff !== 0" class="space-y-2">
            <label class="block font-bold text-slate-600 uppercase text-xs">盈亏原因备注</label>
            <input v-model="handoverNotes" type="text" placeholder="例如：Bs. 零钱误差 / Pago Móvil 延迟到账..." class="w-full bg-white border border-slate-300 rounded-xl px-4 py-3 text-xs outline-none focus:border-blue-500 font-bold text-slate-900 shadow-2xs" />
          </div>
        </div>

        <div class="p-5 bg-white/80 backdrop-blur-md border-t border-slate-200/60 flex items-center justify-between shrink-0">
          <button @click="shiftReportModalVisible = false" class="px-6 py-2.5 bg-slate-200/80 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-colors cursor-pointer">
            取消
          </button>
          <button @click="submitShiftHandover" class="px-7 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-xs font-black shadow-lg shadow-emerald-600/30 transition-all cursor-pointer">
            🔒 确认交班并锁定归档
          </button>
        </div>
      </div>
    </div>

    <!-- 小票预览 Modal -->
    <div v-if="previewModalVisible" @click.self="previewModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
      <div class="bg-white/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-4xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
        <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-white/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900 flex items-center gap-2">
            <span>🧾 收银小票实时预览与出单</span>
          </h3>
          <button @click="previewModalVisible = false" class="text-slate-400 hover:text-slate-700 text-base font-bold p-1 cursor-pointer">✕</button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 space-y-4 font-mono text-xs bg-white/30 max-w-lg mx-auto w-full my-auto border border-slate-200/80 rounded-2xl shadow-sm my-6">
          <div class="text-center pb-3 border-b border-dashed border-slate-300 space-y-1">
            <div class="font-black text-sm text-slate-900">{{ systemConfig.company_name || 'TOSTIYK (TK) - VENEZUELA' }}</div>
            <div class="text-[11px] text-blue-600 font-bold">RIF: {{ systemConfig.rif || 'J-00000000-0' }}</div>
            <div class="text-[11px] text-slate-500">{{ systemConfig.address || 'Valencia, Carabobo' }}</div>
          </div>

          <div class="space-y-1 text-slate-700 pb-3 border-b border-dashed border-slate-300 font-sans">
            <div><span class="font-bold">Client:</span> {{ quoteClientName || 'Cliente General' }}</div>
            <div><span class="font-bold">Operator:</span> {{ currentUser?.username || 'admin' }}</div>
            <div class="font-bold text-blue-600 mt-1">Payment Breakdown:</div>
            <div v-if="paymentSplit.cardPos > 0"> - Card POS: Bs. {{ paymentSplit.cardPos.toFixed(2) }} (${{ (paymentSplit.cardPos / bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.pagoMovil > 0"> - Pago Móvil: Bs. {{ paymentSplit.pagoMovil.toFixed(2) }} (${{ (paymentSplit.pagoMovil / bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.cashBs > 0"> - Efectivo Bs.: Bs. {{ paymentSplit.cashBs.toFixed(2) }} (${{ (paymentSplit.cashBs / bcvRate).toFixed(2) }})</div>
            <div v-if="paymentSplit.cashUsd > 0"> - Cash USD: ${{ paymentSplit.cashUsd.toFixed(2) }} (Bs. {{ (paymentSplit.cashUsd * bcvRate).toFixed(2) }})</div>
            <div v-if="balanceRemaining < 0"> - cambio (找零): ${{ Math.abs(balanceRemaining).toFixed(2) }} (Bs. {{ (Math.abs(balanceRemaining) * bcvRate).toFixed(2) }})</div>
            <div v-if="paymentReference"><span class="font-bold">Ref:</span> {{ paymentReference }}</div>
          </div>

          <div class="space-y-2 pb-3 border-b border-dashed border-slate-300">
            <div v-for="item in cartItems" :key="item.oem" class="flex justify-between items-start gap-2">
              <div>
                <div class="font-bold text-slate-800">{{ item.name }}</div>
                <div class="text-[11px] text-slate-500">{{ item.oem }} x {{ item.quantity }} @ ${{ item.price.toFixed(2) }}</div>
              </div>
              <div class="font-bold text-slate-900 text-right">
                <div>${{ (item.price * item.quantity).toFixed(2) }}</div>
                <div class="text-[11px] text-slate-500 font-normal">Bs. {{ (item.price * item.quantity * bcvRate).toFixed(2) }}</div>
              </div>
            </div>
          </div>

          <div class="space-y-1 text-right pb-1 font-bold">
            <div>Base Imponible: ${{ totalBaseUsd.toFixed(2) }}</div>
            <div>IVA (16%): ${{ totalTaxUsd.toFixed(2) }}</div>
            <div v-if="igtfAmountUsd > 0">IGTF (3%): ${{ igtfAmountUsd.toFixed(2) }}</div>
            <div class="text-lg font-black text-slate-900 mt-1">Total: ${{ totalUsd.toFixed(2) }} / Bs. {{ (totalUsd * bcvRate).toFixed(2) }}</div>
          </div>
        </div>

        <div class="p-5 bg-white/80 backdrop-blur-md border-t border-slate-200/60 flex gap-4 shrink-0">
          <button @click="previewModalVisible = false" class="flex-1 py-3 bg-slate-200/80 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-all cursor-pointer">返回修改</button>
          <button @click="confirmAndPrint" class="flex-1 py-3 bg-emerald-600 hover:bg-emerald-500 text-white rounded-xl text-sm font-black shadow-lg shadow-emerald-600/30 transition-all cursor-pointer">确认出单并打印</button>
        </div>
      </div>
    </div>

    <!-- 快捷键指南弹窗 -->
    <PosHelpModal :visible="helpModalVisible" @close="helpModalVisible = false" />

    <!-- 客户快速搜索 Modal -->
    <div v-if="clientModalVisible" @click.self="clientModalVisible = false" class="fixed inset-0 bg-slate-950/40 backdrop-blur-md flex items-center justify-center z-50 p-6 cursor-pointer">
      <div class="bg-white/90 backdrop-blur-2xl rounded-3xl shadow-2xl max-w-4xl w-full h-[88vh] max-h-[900px] overflow-hidden border border-white/80 flex flex-col cursor-default">
        <div class="p-5 border-b border-slate-200/60 flex items-center justify-between bg-white/50 shrink-0">
          <h3 class="font-extrabold text-base text-slate-900">快捷选择客户</h3>
          <button @click="clientModalVisible = false" class="text-slate-400 hover:text-slate-700 font-bold text-base">✕</button>
        </div>
        <div class="p-4 border-b border-slate-200/60 bg-white/40 shrink-0">
          <input ref="clientModalInputRef" v-model="clientFilterQuery" @keydown="handleClientModalKeydown" type="text" placeholder="输入客户名称或电话搜索..." class="w-full bg-white/90 border border-slate-200 rounded-xl px-4 py-3 text-xs outline-none focus:border-blue-500 shadow-2xs font-bold text-slate-900" />
        </div>
        <div class="flex-1 overflow-y-auto p-5 space-y-2 bg-white/20">
          <div v-for="c in filteredModalClients" :key="c.id" @click="selectClient(c.name)" class="p-3.5 rounded-2xl border border-slate-200/80 bg-white/80 backdrop-blur-md cursor-pointer hover:bg-blue-500/10 hover:border-blue-300 transition-all flex items-center justify-between text-xs shadow-2xs">
            <div>
              <div class="font-black text-slate-900 text-sm">🏢 {{ c.name }}</div>
              <div class="text-xs text-slate-500 font-mono mt-0.5">RIF: {{ c.rif_or_cedula || '-' }} | 📞 {{ c.phone || '无电话' }}</div>
            </div>
            <span class="text-blue-600 font-bold bg-blue-50 px-3 py-1.5 rounded-lg border border-blue-200">选择此客户 ↵</span>
          </div>
        </div>
        <div class="p-5 bg-white/80 backdrop-blur-md border-t border-slate-200/60 flex justify-end shrink-0">
          <button @click="clientModalVisible = false" class="px-6 py-2.5 bg-slate-200/80 hover:bg-slate-300 text-slate-700 rounded-xl text-xs font-bold transition-all cursor-pointer">
            取消
          </button>
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
    const addVal = parseInt(parts[1])
    if (!isNaN(multiplier) && multiplier > 0) {
      if (!isNaN(addVal) && addVal > 0) {
        targetQty = multiplier * addVal
      } else {
        targetQty = multiplier
      }
    }
  } else {
    const parsed = parseInt(raw)
    if (!isNaN(parsed) && parsed > 0) {
      targetQty = parsed
    }
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

// 商品含税商品原始总额
const goodsTotalUsd = computed(() => {
  return props.cartItems.reduce((sum, item) => sum + (item.price * item.quantity), 0)
})

// 不含税总额 (Base Imponible)
const totalBaseUsd = computed(() => {
  return props.cartItems.reduce((sum, item) => {
    const rate = item.tax_rate ?? 0.16
    const lineTotal = item.price * item.quantity
    if (rate > 0) {
      return sum + (lineTotal / (1.0 + rate))
    }
    return sum + lineTotal
  }, 0)
})

// 增值税额 (IVA)
const totalTaxUsd = computed(() => {
  return props.cartItems.reduce((sum, item) => {
    const rate = item.tax_rate ?? 0.16
    const lineTotal = item.price * item.quantity
    if (rate > 0) {
      const baseSub = lineTotal / (1.0 + rate)
      return sum + (lineTotal - baseSub)
    }
    return sum
  }, 0)
})

// 外汇/美元现金支付产生的 3% IGTF
const igtfAmountUsd = computed(() => {
  const cUsd = Number(paymentSplit.value.cashUsd) || 0
  return Number((cUsd * 0.03).toFixed(2))
})

// 最终总应付金额 = 商品总额 + IGTF
const totalUsd = computed(() => {
  return Number((goodsTotalUsd.value + igtfAmountUsd.value).toFixed(2))
})

const totalPaidUsd = computed(() => {
  const cCard = Number(paymentSplit.value.cardPos) || 0
  const cPago = Number(paymentSplit.value.pagoMovil) || 0
  const cBs = Number(paymentSplit.value.cashBs) || 0
  const cUsd = Number(paymentSplit.value.cashUsd) || 0

  const rate = props.bcvRate || 1
  const paidInUsd = (cCard / rate) + (cPago / rate) + (cBs / rate) + cUsd
  return Number(paidInUsd.toFixed(2))
})

const balanceRemaining = computed(() => {
  return Number((totalUsd.value - totalPaidUsd.value).toFixed(2))
})

const isFullyPaid = computed(() => {
  return totalUsd.value > 0 && totalPaidUsd.value >= totalUsd.value
})

// 🌟 核心键盘逻辑：优化回执编号防护 & 订单跳转
const handlePaymentKeydown = (e, channelKey) => {
  const orderSequence = ['cardPos', 'pagoMovil', 'cashBs', 'cashUsd', 'reference']
  const currentIndex = orderSequence.indexOf(channelKey)

  // 1. [Ctrl + Enter] 直接弹出确认出单预览
  if (e.ctrlKey && e.key === 'Enter') {
    e.preventDefault()
    if (isFullyPaid.value && props.cartItems.length > 0) {
      openPreviewModal()
    }
    return
  }

  // 2. 如果当前聚焦在回执编号框 (reference)，直接允许正常输入及默认上下光标移动，不触发通道切换
  if (channelKey === 'reference') {
    return
  }

  // 3. [空格键] 或 [= 键] 一键补齐差额（精准包含 IGTF 拆分）
  if (e.key === ' ' || e.key === '=') {
    e.preventDefault()

    const rate = props.bcvRate || 1
    const currentCashUsd = Number(paymentSplit.value.cashUsd) || 0
    const currentIgtf = Number((currentCashUsd * 0.03).toFixed(2))
    const currentTotalUsd = Number((goodsTotalUsd.value + currentIgtf).toFixed(2))

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

    const neededTotalUsd = Math.max(0, currentTotalUsd - otherPaidInUsd)

    if (channelKey === 'cashUsd') {
      const baseCashNeeded = neededTotalUsd / 1.03
      paymentSplit.value.cashUsd = Number(baseCashNeeded.toFixed(2))
    } else {
      paymentSplit.value[channelKey] = Number((neededTotalUsd * rate).toFixed(2))
    }
    return
  }

  // 4. [ArrowDown 向下方向键] 顺延跳到下一项
  if (e.key === 'ArrowDown') {
    e.preventDefault()
    if (currentIndex !== -1 && currentIndex < orderSequence.length - 1) {
      const nextKey = orderSequence[currentIndex + 1]
      focusPaymentChannel(nextKey)
    }
    return
  }

  // 5. [ArrowUp 向上方向键] 回溯跳到上一项
  if (e.key === 'ArrowUp') {
    e.preventDefault()
    if (currentIndex > 0) {
      const prevKey = orderSequence[currentIndex - 1]
      focusPaymentChannel(prevKey)
    }
    return
  }

  // 6. [Enter 回车键] 智能顺延跳转与一键结账
  if (e.key === 'Enter') {
    e.preventDefault()
    
    if (isFullyPaid.value) {
      openPreviewModal()
      return
    }

    if (currentIndex !== -1 && currentIndex < orderSequence.length - 1) {
      const nextKey = orderSequence[currentIndex + 1]
      focusPaymentChannel(nextKey)
    }
  }
}

// 辅助方法：精准控制各个支付输入框聚焦
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
  cardPos: { amount: 0, count: 0 },
  pagoMovil: { amount: 0, count: 0 },
  cashBs: { amount: 0, count: 0 },
  cashUsd: { amount: 0, count: 0 },
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
    const payload = {
      system_card_pos: shiftStats.value.cardPos.amount * (props.bcvRate || 1),
      system_pagomovil_usd: shiftStats.value.pagoMovil.amount * (props.bcvRate || 1),
      system_cash_bs: shiftStats.value.cashBs.amount * (props.bcvRate || 1),
      system_cash_usd: shiftStats.value.cashUsd.amount,
      system_debt_usd: 0,
      system_total_usd: shiftStats.value.totalUsd,
      
      actual_card_pos: actualCounts.value.cardPos || 0,
      actual_pago_movil: actualCounts.value.pagoMovil || 0,
      actual_cash_bs: actualCounts.value.cashBs || 0,
      actual_cash_usd: actualCounts.value.cashUsd || 0,
      
      notes: handoverNotes.value
    }
    const res = await apiFetch('/api/pos/shift-handover', { method: 'POST', body: JSON.stringify(payload) })
    if (!res.ok) throw new Error('交接班归档失败')
    showToast('🔒 交接班成功，班次已成功锁定归档！', 'success')
    shiftReportModalVisible.value = false
  } catch (err) { showToast('❌ ' + err.message, 'error') }
}

const previewModalVisible = ref(false)
const isPreviewReady = ref(false)
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

const handleClientModalKeydown = (e) => {
  if (e.key === 'Enter') {
    const matched = filteredModalClients.value
    if (matched.length > 0) {
      selectClient(matched[0].name)
    }
  }
}

const filteredModalClients = computed(() => {
  if (!props.clientsList) return []
  if (!clientFilterQuery.value.trim()) return props.clientsList
  const q = clientFilterQuery.value.toUpperCase()
  return props.clientsList.filter(c => c.name.toUpperCase().includes(q) || (c.phone && c.phone.toUpperCase().includes(q)))
})

const filteredParts = computed(() => {
  const qStr = deskSearchQuery.value.trim().toUpperCase()
  if (!qStr) return []
  return props.partsList.filter(p => p.oem.toUpperCase().includes(qStr) || p.name.toUpperCase().includes(qStr)).slice(0, 10)
})

const selectAndAddToCart = (part) => {
  if (part.stock <= 0) {
    showToast(`商品 ${part.oem} 库存不足`, 'error')
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
    let cardAmt = 0, pUsd = 0, cBs = 0, cUsd = 0, tUsd = 0
    ordersData.forEach(o => {
      tUsd += o.totalUsd
      if (o.paymentMethod === 'Card_POS') cardAmt += o.totalUsd
      else if (o.paymentMethod === 'Pago_Movil') pUsd += o.totalUsd
      else if (o.paymentMethod === 'Cash_Bs') cBs += o.totalUsd
      else if (o.paymentMethod === 'Cash_USD') cUsd += o.totalUsd
    })
    shiftStats.value = {
      cardPos: { amount: cardAmt, count: 0 },
      pagoMovil: { amount: pUsd, count: 0 },
      cashBs: { amount: cBs, count: 0 },
      cashUsd: { amount: cUsd, count: ordersData.length },
      totalUsd: tUsd,
      totalCount: ordersData.length
    }

    actualCounts.value = {
      cardPos: Number((cardAmt * (props.bcvRate || 1)).toFixed(2)),
      pagoMovil: Number((pUsd * (props.bcvRate || 1)).toFixed(2)),
      cashBs: Number((cBs * (props.bcvRate || 1)).toFixed(2)),
      cashUsd: cUsd
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

const openPreviewModal = () => { 
  if (props.cartItems.length === 0 || !isFullyPaid.value) return
  previewModalVisible.value = true
  isPreviewReady.value = false
  setTimeout(() => {
    isPreviewReady.value = true
  }, 300)
}

const confirmAndPrint = async () => {
  try {
    const payload = {
      client_name: quoteClientName.value || "Cliente General",
      payment_method: 'Card_POS',
      payment_reference: paymentReference.value,
      bcv_rate: props.bcvRate,
      payment_split: paymentSplit.value,
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

const handleGlobalKeydown = (e) => {
  // 🌟 全局监听 Ctrl + Enter 触发确认出单
  if (e.ctrlKey && e.key === 'Enter') {
    e.preventDefault()
    if (isFullyPaid.value && props.cartItems.length > 0 && !previewModalVisible.value) {
      openPreviewModal()
    }
    return
  }

  if (previewModalVisible.value) {
    if (e.key === 'Enter') { 
      e.preventDefault() 
      if (isPreviewReady.value) { 
        confirmAndPrint() 
      }
      return 
    }
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

  if (e.key === 'F4') { e.preventDefault(); if (cardPosInputRef.value) cardPosInputRef.value.focus(); return }
  if (e.key === 'F5') { e.preventDefault(); if (pagoMovilInputRef.value) pagoMovilInputRef.value.focus(); return }
  if (e.key === 'F6') { e.preventDefault(); if (cashBsInputRef.value) cashBsInputRef.value.focus(); return }
  if (e.key === 'F7') { e.preventDefault(); if (cashUsdInputRef.value) cashUsdInputRef.value.focus(); return }

  if (e.key === '/' && document.activeElement !== searchInputRef.value) { e.preventDefault(); focusSearch(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'f') { e.preventDefault(); openClientSearchModal(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'h') { e.preventDefault(); holdCurrentOrder(); return }
  if (e.ctrlKey && e.key.toLowerCase() === 'r') { e.preventDefault(); openRecallModal(); return }
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

/* 🌟 隐藏 Chrome、Safari、Edge 等数字输入框原生的上下微调小箭头 */
input.no-spinner::-webkit-outer-spin-button,
input.no-spinner::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
/* 隐藏 Firefox 原生上下箭头 */
input[type=number].no-spinner {
  -moz-appearance: textfield;
}
</style>