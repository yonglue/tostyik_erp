<!-- src/components/Header.vue -->
<template>
  <header class="bg-white border-b border-slate-200 shrink-0 z-10">
    <!-- 🌟 容器：手机端双行布局，桌面端单行布局 -->
    <div class="flex flex-col md:flex-row md:items-center justify-between px-3 md:px-8 py-2 md:py-0 md:h-16 gap-2 md:gap-0">
      
      <!-- 📌 第一行（移动端主栏 / 桌面端左侧）：放大版汉堡菜单、Logo、完整标题与身份/退出 -->
      <div class="flex items-center justify-between md:justify-start gap-2.5 min-w-0">
        <div class="flex items-center gap-2.5 min-w-0 flex-1">
          
          <!-- 🌟 优化放大后的移动端汉堡菜单按钮（更大更易按） -->
          <button 
            @click="$emit('toggle-mobile-menu')" 
            class="md:hidden p-2 text-slate-800 hover:bg-slate-100 active:bg-slate-200 rounded-xl shrink-0 cursor-pointer transition-colors flex items-center justify-center -ml-1"
            aria-label="打开导航菜单"
          >
            <span class="text-2xl leading-none font-bold">☰</span>
          </button>

          <!-- 🌟 手机端与桌面端均显示的 Logo 图标 -->
          <div class="w-8 h-8 sm:w-9 sm:h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/25 shrink-0">
            <Cpu :size="18" />
          </div>

          <!-- 模块标题 -->
          <h2 class="text-sm sm:text-base md:text-lg font-black tracking-tight text-slate-900 truncate">
            {{ getActiveTabTitle }}
          </h2>
        </div>

        <!-- 移动端第一行右侧：管理员身份与带文字提示的退出按钮 -->
        <div class="flex items-center gap-1.5 md:hidden shrink-0">
          <div class="flex items-center gap-1 text-[11px] font-semibold text-slate-700 bg-slate-100/80 px-2 py-1 rounded-full border border-slate-200/60">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span class="max-w-[65px] truncate">{{ currentAdminUser }}</span>
          </div>
          <button 
            @click="$emit('logout')" 
            class="px-2 py-1 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-lg text-xs font-bold transition-colors flex items-center gap-1 cursor-pointer"
            title="退出登录"
          >
            <span>🚪</span>
            <span>{{ t.logoutBtn || '退出' }}</span>
          </button>
        </div>
      </div>

      <!-- 📌 第二行（移动端工具子栏 / 桌面端右侧）：汇率、带图标的语言选择器、桌面端管理员身份与退出 -->
      <div class="flex items-center justify-between md:justify-end gap-2 shrink-0 pt-1.5 md:pt-0 border-t border-slate-100 md:border-t-0">
        
        <!-- ⚡ BCV 汇率展示卡片 -->
        <div class="flex items-center gap-1 bg-slate-50 border border-slate-200/80 px-2.5 sm:px-3 py-1 md:py-1.5 rounded-full text-xs font-mono">
          <span class="text-slate-400 font-sans font-medium">BCV =</span>
          <span class="font-bold text-blue-600">{{ bcvRate }}</span>
          <button @click="$emit('refresh-bcv')" class="text-slate-400 hover:text-blue-600 transition-colors ml-0.5 cursor-pointer" title="刷新汇率">
            <RefreshCw :size="12" />
          </button>
        </div>

        <!-- 🌐 带地球图标的多语言切换选择器 -->
        <div class="flex items-center gap-1.5 bg-slate-50 border border-slate-200/80 px-2.5 py-1 md:py-1.5 rounded-xl text-xs">
          <Globe :size="13" class="text-slate-400 shrink-0" />
          <select 
            v-model="currentLang" 
            class="bg-transparent text-slate-700 font-bold outline-none cursor-pointer text-xs"
          >
            <option value="es">Español (ES)</option>
            <option value="zh">中文 (ZH)</option>
            <option value="en">English (EN)</option>
          </select>
        </div>

        <!-- 👑 桌面端展示的管理员身份与退出按钮 -->
        <div class="hidden md:flex items-center gap-3 ml-1">
          <div class="flex items-center gap-1.5 text-xs font-semibold text-slate-700 bg-slate-50 border border-slate-200/80 px-3 py-1.5 rounded-full">
            <span class="w-2 h-2 rounded-full bg-emerald-500"></span>
            <span>Admin: <strong class="text-slate-900">{{ currentAdminUser }}</strong></span>
          </div>

          <button 
            @click="$emit('logout')" 
            class="text-xs px-3 py-1.5 bg-rose-50 hover:bg-rose-100 text-rose-600 rounded-xl font-bold transition-colors flex items-center gap-1 shrink-0 cursor-pointer shadow-2xs"
          >
            <span>🚪</span> 
            <span>{{ t.logoutBtn || '退出' }}</span>
          </button>
        </div>

      </div>

    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { Cpu, RefreshCw, Globe } from 'lucide-vue-next'
import { useI18n } from '../composables/useI18n'

const props = defineProps({
  activeTab: String,
  bcvRate: Number,
  currentDateTime: String
})

defineEmits(['toggle-mobile-menu', 'refresh-bcv', 'logout'])

const { currentLang, t } = useI18n()

// 获取当前登录用户名
const currentAdminUser = computed(() => {
  return localStorage.getItem('tostiyk_username') || 'admin'
})

const getActiveTabTitle = computed(() => {
  const map = {
    dashboard: t.value.tabDashboard,
    parts: t.value.tabParts,
    clients: t.value.tabClients,
    procurement: t.value.tabProcurement,
    transactions: t.value.tabTrans,
    desk: t.value.tabDesk,
    quotations: t.value.tabQuotations,
    backup: t.value.tabBackup,
    warehouse: t.value.tabWarehouse,
    staff: t.value.tabStaff,
    cash_register: t.value.tabCashRegister,
    audit_logs: t.value.tabAuditLogs
  }
  return map[props.activeTab] || 'TOSTIKYK ERP'
})
</script>