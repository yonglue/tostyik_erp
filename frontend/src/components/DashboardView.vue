<!-- src/views/DashboardView.vue -->
<template>
  <div class="p-4 sm:p-6 md:p-8 space-y-6 max-w-7xl mx-auto">
    
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
      totalAssetUSD: 669.50,
      totalAssetBs: 586248.01,
      totalSalesUSD: 14250.00,
      totalSalesBs: 12478500.00,
      totalSKUs: 320,
      lowStockCount: 4
    })
  },
  bcvRate: {
    type: Number,
    default: 876.7976
  }
})

defineEmits(['navigate'])
</script>