<!-- src/components/Sidebar.vue -->
<template>
  <!-- 🌟 移动端侧边栏展开时的半透明遮罩背景（点击空白处自动关闭） -->
  <div 
    v-if="mobileMenuOpen" 
    @click="$emit('update:mobileMenuOpen', false)"
    class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-20 md:hidden transition-opacity"
  ></div>

  <!-- 侧边栏主体 -->
  <aside :class="['fixed md:static inset-y-0 left-0 z-30 w-64 bg-white border-r border-slate-200 flex flex-col transition-transform duration-300 shrink-0',
    mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0']">
    
    <!-- Logo 区域 -->
    <div class="h-16 px-6 border-b border-slate-100 flex items-center justify-between shrink-0">
      <div class="flex items-center gap-3">
        <div class="w-9 h-9 rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/25">
          <Cpu :size="20" />
        </div>
        <div>
          <h1 class="font-bold text-sm tracking-tight text-slate-900">TOSTIKYK ERP</h1>
          <p class="text-[10px] text-slate-400 font-medium tracking-wide">Automotive Parts System</p>
        </div>
      </div>
      <!-- 移动端侧边栏内部关闭按钮 -->
      <button @click="$emit('update:mobileMenuOpen', false)" class="md:hidden p-1.5 text-slate-400 hover:text-slate-700 rounded-lg">
        ✕
      </button>
    </div>

    <!-- 导航菜单列表 -->
    <nav class="flex-1 px-4 py-6 space-y-1.5 overflow-y-auto">
      <button
        v-for="item in menuItems"
        :key="item.key"
        @click="handleMenuClick(item.key)"
        :class="['w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 cursor-pointer', 
          activeTab === item.key ? 'bg-blue-600 text-white shadow-md shadow-blue-500/25' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900']"
      >
        <component :is="item.icon" :size="18" class="shrink-0" />
        <span class="truncate leading-tight text-left">{{ t[item.labelKey] || item.defaultLabel }}</span>
      </button>
    </nav>

    <!-- 底部状态 -->
    <div class="p-4 border-t border-slate-100 shrink-0">
      <div class="bg-slate-50 rounded-xl p-3 flex items-center gap-3 border border-slate-100/80">
        <div class="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse"></div>
        <div class="flex-1 min-w-0">
          <p class="text-xs font-semibold text-slate-700 truncate">{{ t.sysStatus }}</p>
          <p class="text-[10px] text-slate-400 font-mono">v4.3.0 Enterprise</p>
        </div>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import { 
  Cpu,
  LayoutDashboard, 
  TrendingUp, 
  Package, 
  Building2, 
  ShieldCheck, 
  Users, 
  ShoppingCart, 
  History, 
  Calculator, 
  FileText, 
  Database,
  ShieldAlert
} from 'lucide-vue-next'

const props = defineProps({
  activeTab: String,
  mobileMenuOpen: Boolean
})
const emit = defineEmits(['update:activeTab', 'update:mobileMenuOpen', 'menu-click'])

const { t } = useI18n()

// 处理菜单点击跳转并自动关闭移动端抽屉菜单
const handleMenuClick = (key) => {
  emit('update:activeTab', key)
  emit('update:mobileMenuOpen', false)
  emit('menu-click', key)
}

const menuItems = computed(() => {
  const allItems = [
    { key: 'dashboard', labelKey: 'menuDashboard', icon: LayoutDashboard },
    { key: 'financial', labelKey: 'menuFinancial', icon: TrendingUp, adminOnly: true },
    { key: 'parts', labelKey: 'menuParts', icon: Package },
    { key: 'warehouse', labelKey: 'menuWarehouse', icon: Building2 },
    { key: 'staff', labelKey: 'menuStaff', icon: ShieldCheck, adminOnly: true },
    { key: 'clients', labelKey: 'menuClients', icon: Users },
    { key: 'procurement', labelKey: 'menuProcurement', icon: ShoppingCart },
    { key: 'transactions', labelKey: 'menuTrans', icon: History },
    { key: 'desk', labelKey: 'menuDesk', icon: Calculator },
    { key: 'quotations', labelKey: 'menuQuotations', icon: FileText },
    { key: 'cash_register', labelKey: 'menuCashRegister', icon: Calculator },
    { key: 'audit_logs', labelKey: 'menuAuditLogs', icon: ShieldAlert, adminOnly: true },
    { key: 'backup', labelKey: 'menuBackup', icon: Database, adminOnly: true },
  ]

  let userRole = 'super_admin'
  try {
    const stored = localStorage.getItem('tostiyk_current_user')
    if (stored) {
      const parsed = JSON.parse(stored)
      userRole = parsed.role || 'super_admin'
    }
  } catch (e) {
    console.error(e)
  }

  if (userRole === 'super_admin' || userRole === 'admin') {
    return allItems
  }
  return allItems.filter(item => !item.adminOnly)
})
</script>