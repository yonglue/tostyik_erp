<!-- src/views/DashboardView.vue -->
<template>
  <div class="p-4 sm:p-6 md:p-8 space-y-6 max-w-7xl mx-auto">
    
    <!-- 欢迎横幅与系统概览 -->
    <div class="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-3xl p-6 sm:p-8 text-white shadow-xl shadow-blue-500/15 flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h1 class="text-xl sm:text-2xl md:text-3xl font-black tracking-tight">TOSTIKYK ERP 经营总览</h1>
        <p class="text-blue-100 text-xs sm:text-sm mt-1">汽车配件与商业库存多币种智能管理系统（Venezuela Market）</p>
      </div>
      <div class="flex items-center gap-3 bg-white/10 backdrop-blur-md px-4 py-2.5 rounded-2xl border border-white/20 text-xs sm:text-sm">
        <span class="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse"></span>
        <span>当前官方汇率: <strong class="font-mono text-white">BCV = {{ bcvRate }}</strong></span>
      </div>
    </div>

    <!-- 📊 核心指标卡片网格 (Grid)：手机单列，平板双列，电脑四列 -->
    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-6">
      
      <!-- 卡片 1：当前库存总资产 -->
      <div class="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">库存总资产 (USD)</span>
          <div class="w-10 h-10 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <Package :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-slate-900 font-mono">$ {{ stats.totalAssetUSD?.toLocaleString() || '0.00' }}</div>
          <div class="text-xs text-slate-400 font-mono mt-1">Bs. {{ stats.totalAssetBs?.toLocaleString() || '0.00' }}</div>
        </div>
      </div>

      <!-- 卡片 2：累计销售总额 -->
      <div class="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">累计销售额 (USD)</span>
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
      <div class="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">配件总 SKU 数</span>
          <div class="w-10 h-10 rounded-2xl bg-amber-500/10 text-amber-600 flex items-center justify-center">
            <Layers :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-slate-900 font-mono">{{ stats.totalSKUs || 0 }} 项</div>
          <div class="text-xs text-amber-600 font-medium mt-1">活跃汽配库存种类</div>
        </div>
      </div>

      <!-- 卡片 4：库存低水位预警 -->
      <div class="bg-white rounded-3xl p-5 sm:p-6 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between">
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-slate-400 uppercase tracking-wider">库存短缺预警</span>
          <div class="w-10 h-10 rounded-2xl bg-rose-500/10 text-rose-600 flex items-center justify-center">
            <AlertTriangle :size="20" />
          </div>
        </div>
        <div class="mt-4">
          <div class="text-2xl sm:text-3xl font-black text-rose-600 font-mono">{{ stats.lowStockCount || 0 }} 项</div>
          <div class="text-xs text-slate-400 mt-1">建议及时向供应商采购补货</div>
        </div>
      </div>

    </div>

    <!-- 快捷操作与最近动态区 -->
    <div class="bg-white rounded-3xl p-6 border border-slate-200/80 shadow-xs">
      <h3 class="font-bold text-slate-900 text-base mb-4">快捷商业导航</h3>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <button @click="$emit('navigate', 'desk')" class="p-4 rounded-2xl bg-slate-50 hover:bg-blue-50 hover:text-blue-600 transition-colors text-left border border-slate-100 group cursor-pointer">
          <Calculator class="text-blue-600 mb-2 group-hover:scale-110 transition-transform" :size="22" />
          <div class="font-bold text-sm text-slate-800">极速开单台</div>
          <div class="text-[11px] text-slate-400 mt-0.5">多币种报价与结算</div>
        </button>
        <button @click="$emit('navigate', 'parts')" class="p-4 rounded-2xl bg-slate-50 hover:bg-blue-50 hover:text-blue-600 transition-colors text-left border border-slate-100 group cursor-pointer">
          <Package class="text-blue-600 mb-2 group-hover:scale-110 transition-transform" :size="22" />
          <div class="font-bold text-sm text-slate-800">汽配库存管理</div>
          <div class="text-[11px] text-slate-400 mt-0.5">OEM与滤清器对查</div>
        </button>
        <button @click="$emit('navigate', 'clients')" class="p-4 rounded-2xl bg-slate-50 hover:bg-blue-50 hover:text-blue-600 transition-colors text-left border border-slate-100 group cursor-pointer">
          <Users class="text-blue-600 mb-2 group-hover:scale-110 transition-transform" :size="22" />
          <div class="font-bold text-sm text-slate-800">客户关系档案</div>
          <div class="text-[11px] text-slate-400 mt-0.5">委内瑞拉本地客户</div>
        </button>
        <button @click="$emit('navigate', 'quotations')" class="p-4 rounded-2xl bg-slate-50 hover:bg-blue-50 hover:text-blue-600 transition-colors text-left border border-slate-100 group cursor-pointer">
          <FileText class="text-blue-600 mb-2 group-hover:scale-110 transition-transform" :size="22" />
          <div class="font-bold text-sm text-slate-800">报价单历史</div>
          <div class="text-[11px] text-slate-400 mt-0.5">PDF生成与导出</div>
        </button>
      </div>
    </div>

  </div>
</template>

<script setup>
import { Package, TrendingUp, Layers, AlertTriangle, Calculator, Users, FileText } from 'lucide-vue-next'

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