<!-- src/components/DashboardView.vue -->
<template>
  <div class="space-y-6 max-w-7xl mx-auto">
    
    <!-- 欢迎横幅与系统概览 -->
    <div class="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-3xl p-6 sm:p-8 text-white shadow-xl shadow-blue-500/15 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl md:text-3xl font-black tracking-tight">{{ t.dashWelcomeTitle }}</h1>
        <p class="text-blue-100 text-xs sm:text-sm mt-1">{{ t.dashWelcomeSub }}</p>
      </div>
      <div class="flex items-center gap-3 bg-white/10 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-white/20 text-xs sm:text-sm shadow-sm">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>{{ t.dashBcvRateLabel }} <strong class="font-mono text-white">{{ bcvRate }}</strong></span>
      </div>
    </div>

    <!-- 📊 核心指标卡片网格：毛玻璃背景 + 划过悬浮高亮 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      
      <!-- 卡片 1：当前库存总资产 -->
      <div class="bg-white/75 backdrop-blur-xl rounded-3xl p-5 sm:p-6 border border-white/60 shadow-lg hover:shadow-xl transition-all flex flex-col justify-between hover:scale-[1.01]">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ t.dashAssetTitle }}</span>
          <div class="w-10 h-10 rounded-2xl bg-blue-500/10 text-blue-600 flex items-center justify-center">
            <Package :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-slate-900 font-mono">$ {{ stats.totalAssetUSD?.toLocaleString() || '0.00' }}</div>
          <div class="text-xs text-slate-400 font-mono mt-1">Bs. {{ stats.totalAssetBs?.toLocaleString() || '0.00' }}</div>
        </div>
      </div>

      <!-- 卡片 2：累计销售总额 -->
      <div class="bg-white/75 backdrop-blur-xl rounded-3xl p-5 sm:p-6 border border-white/60 shadow-lg hover:shadow-xl transition-all flex flex-col justify-between hover:scale-[1.01]">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ t.dashSalesTitle }}</span>
          <div class="w-10 h-10 rounded-2xl bg-emerald-500/10 text-emerald-600 flex items-center justify-center">
            <TrendingUp :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-slate-900 font-mono">$ {{ stats.totalSalesUSD?.toLocaleString() || '0.00' }}</div>
          <div class="text-xs text-slate-400 font-mono mt-1">Bs. {{ stats.totalSalesBs?.toLocaleString() || '0.00' }}</div>
        </div>
      </div>

      <!-- 卡片 3：配件总SKU数 -->
      <div class="bg-white/75 backdrop-blur-xl rounded-3xl p-5 sm:p-6 border border-white/60 shadow-lg hover:shadow-xl transition-all flex flex-col justify-between hover:scale-[1.01]">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ t.dashSkuTitle }}</span>
          <div class="w-10 h-10 rounded-2xl bg-amber-500/10 text-amber-600 flex items-center justify-center">
            <Layers :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-slate-900 font-mono">{{ stats.totalSKUs || 0 }} {{ t.itemsUnit }}</div>
          <div class="text-xs text-amber-600 font-medium mt-1">{{ t.dashSkuSub }}</div>
        </div>
      </div>

      <!-- 卡片 4：库存低水位预警 -->
      <div class="bg-white/75 backdrop-blur-xl rounded-3xl p-5 sm:p-6 border border-white/60 shadow-lg hover:shadow-xl transition-all flex flex-col justify-between hover:scale-[1.01]">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">{{ t.dashWarningTitle }}</span>
          <div class="w-10 h-10 rounded-2xl bg-rose-500/10 text-rose-600 flex items-center justify-center">
            <AlertTriangle :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-rose-600 font-mono">{{ stats.lowStockCount || 0 }} {{ t.itemsUnit }}</div>
          <div class="text-xs text-slate-400 mt-1">{{ t.dashWarningSub }}</div>
        </div>
      </div>

    </div>

    <!-- 🚀 快捷业务直达面板 (Quick Actions) -->
    <div class="bg-white/75 backdrop-blur-xl rounded-3xl p-6 border border-white/60 shadow-lg space-y-4">
      <h3 class="font-bold text-slate-800 text-base flex items-center gap-2">
        ⚡ 常用功能快捷直达 (Quick Navigation)
      </h3>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <button 
          @click="$emit('navigate', 'quotation')" 
          class="bg-blue-50/60 hover:bg-blue-500 hover:text-white text-blue-700 border border-blue-200/80 p-4 rounded-2xl font-bold text-xs flex flex-col items-center gap-2 transition-all cursor-pointer shadow-2xs hover:scale-[1.02]"
        >
          <span class="text-2xl">🛒</span>
          <span>进入开单收银台</span>
        </button>

        <button 
          @click="$emit('navigate', 'financial')" 
          class="bg-emerald-50/60 hover:bg-emerald-600 hover:text-white text-emerald-700 border border-emerald-200/80 p-4 rounded-2xl font-bold text-xs flex flex-col items-center gap-2 transition-all cursor-pointer shadow-2xs hover:scale-[1.02]"
        >
          <span class="text-2xl">📈</span>
          <span>查看财务利润</span>
        </button>

        <button 
          @click="$emit('navigate', 'inventory')" 
          class="bg-amber-50/60 hover:bg-amber-500 hover:text-white text-amber-800 border border-amber-200/80 p-4 rounded-2xl font-bold text-xs flex flex-col items-center gap-2 transition-all cursor-pointer shadow-2xs hover:scale-[1.02]"
        >
          <span class="text-2xl">📦</span>
          <span>配件库存与条码</span>
        </button>

        <button 
          @click="$emit('navigate', 'clients')" 
          class="bg-purple-50/60 hover:bg-purple-600 hover:text-white text-purple-700 border border-purple-200/80 p-4 rounded-2xl font-bold text-xs flex flex-col items-center gap-2 transition-all cursor-pointer shadow-2xs hover:scale-[1.02]"
        >
          <span class="text-2xl">👥</span>
          <span>客户与挂账管理</span>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { Package, TrendingUp, Layers, AlertTriangle } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'

const { t } = useI18n()

defineProps({
  stats: {
    type: Object,
    default: () => ({
      totalAssetUSD: 0,
      totalAssetBs: 0,
      totalSalesUSD: 0,
      totalSalesBs: 0,
      totalSKUs: 0,
      lowStockCount: 0
    })
  },
  bcvRate: {
    type: Number,
    default: 36.50
  }
})

defineEmits(['navigate'])
</script>