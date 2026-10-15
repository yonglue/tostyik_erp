<!-- src/components/Sidebar.vue -->
<template>
  <div 
    v-if="mobileMenuOpen" 
    @click="$emit('update:mobileMenuOpen', false)"
    class="fixed inset-0 bg-slate-900/50 backdrop-blur-xs z-20 md:hidden transition-opacity"
  ></div>

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
      <button @click="$emit('update:mobileMenuOpen', false)" class="md:hidden p-1.5 text-slate-400 hover:text-slate-700 rounded-lg">
        ✕
      </button>
    </div>

    <!-- 导航菜单列表 -->
    <nav class="flex-1 px-4 py-4 space-y-4 overflow-y-auto">
      <div v-for="(group, groupIndex) in groupedMenuItems" :key="groupIndex" class="space-y-1">
        <!-- 分组标题 -->
        <div v-if="group.title" class="px-3 pb-1 text-[11px] font-bold tracking-wider text-slate-400 uppercase">
          {{ group.title }}
        </div>
        
        <!-- 组内菜单项 -->
        <button
          v-for="item in group.items"
          :key="item.key"
          @click="handleMenuClick(item.key)"
          :class="['w-full flex items-center gap-3 px-4 py-2.5 rounded-xl font-medium text-sm transition-all duration-200 cursor-pointer', 
            activeTab === item.key ? 'bg-blue-600 text-white shadow-md shadow-blue-500/25' : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900']"
        >
          <component :is="item.icon" :size="18" class="shrink-0" />
          <span class="truncate leading-tight text-left">
            <!-- 🌟 将系统设置菜单项名称固定显示为系统设置 -->
            {{ item.key === 'backup' ? '系统设置' : (t[item.labelKey] || item.defaultLabel) }}
          </span>
        </button>

        <!-- 组间分隔线 -->
        <div v-if="groupIndex < groupedMenuItems.length - 1" class="pt-3 mx-3 border-b border-slate-100"></div>
      </div>
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
  ShieldCheck, 
  Users, 
  ShoppingCart, 
  History, 
  Calculator, 
  FileText, 
  Database,
  ShieldAlert,
  Settings
} from 'lucide-vue-next'

const props = defineProps({
  activeTab: String,
  mobileMenuOpen: Boolean
})
const emit = defineEmits(['update:activeTab', 'update:mobileMenuOpen', 'menu-click'])

const { t } = useI18n()

const handleMenuClick = (key) => {
  emit('update:activeTab', key)
  emit('update:mobileMenuOpen', false)
  emit('menu-click', key)
}

const groupedMenuItems = computed(() => {
  const groups = [
    {
      title: t.value.groupCore || '核心概览',
      items: [
        { key: 'dashboard', labelKey: 'menuDashboard', icon: LayoutDashboard },
        { key: 'financial', labelKey: 'menuFinancial', icon: TrendingUp, adminOnly: true },
      ]
    },
    {
      title: t.value.groupWarehouse || '仓储与商品',
      items: [
        { key: 'parts', labelKey: 'menuParts', icon: Package },
      ]
    },
    {
      title: t.value.groupSales || '销售与业务',
      items: [
        { key: 'clients', labelKey: 'menuClients', icon: Users },
        { key: 'procurement', labelKey: 'menuProcurement', icon: ShoppingCart },
        { key: 'transactions', labelKey: 'menuTrans', icon: History },
        { key: 'desk', labelKey: 'menuDesk', icon: Calculator },
        { key: 'cash_register', labelKey: 'menuCashRegister', icon: Calculator },
      ]
    },
    {
      title: t.value.groupSystem || '系统与管理',
      items: [
        { key: 'staff', labelKey: 'menuStaff', icon: ShieldCheck, adminOnly: true },
        { key: 'audit_logs', labelKey: 'menuAuditLogs', icon: ShieldAlert, adminOnly: true },
        { key: 'backup', labelKey: 'menuBackup', icon: Settings, adminOnly: true }, // 🌟 图标改为 Settings，文字直接显示系统设置
      ]
    }
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

  return groups.map(group => {
    const filteredItems = group.items.filter(item => {
      if (userRole === 'super_admin' || userRole === 'admin') return true
      return !item.adminOnly
    })
    return {
      title: group.title,
      items: filteredItems
    }
  }).filter(group => group.items.length > 0)
})
</script>