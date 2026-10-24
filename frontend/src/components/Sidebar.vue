<!-- src/components/Sidebar.vue -->
<template>
  <div 
    v-if="mobileMenuOpen" 
    @click="$emit('update:mobileMenuOpen', false)"
    class="fixed inset-0 bg-slate-950/45 backdrop-blur-md z-20 md:hidden transition-opacity"
  ></div>

  <aside 
    :class="[
      'fixed md:static inset-y-0 left-0 z-30 bg-white/75 dark:bg-slate-900/75 backdrop-blur-xl border-r border-white/60 dark:border-slate-800 flex flex-col transition-all duration-300 shrink-0 shadow-xl',
      mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0',
      isCollapsed ? 'w-[72px]' : 'w-64'
    ]"
  >
    
    <!-- Logo 区域 -->
    <div class="h-16 px-4 border-b border-slate-200/60 dark:border-slate-800 flex items-center justify-between shrink-0 bg-white/40 dark:bg-slate-900/40 transition-all">
      <div class="flex items-center gap-3 overflow-hidden">
        <div class="w-9 h-9 min-w-[36px] rounded-xl bg-blue-600 flex items-center justify-center text-white shadow-md shadow-blue-500/25 shrink-0">
          <Cpu :size="20" />
        </div>
        <div v-show="!isCollapsed" class="whitespace-nowrap transition-opacity duration-300">
          <h1 class="font-bold text-sm tracking-tight text-slate-900 dark:text-white">TOSTIKYK ERP</h1>
          <p class="text-[10px] text-slate-400 dark:text-slate-500 font-medium tracking-wide">Automotive Parts System</p>
        </div>
      </div>
      <button @click="$emit('update:mobileMenuOpen', false)" class="md:hidden p-1.5 text-slate-400 hover:text-slate-700 dark:text-slate-500 dark:hover:text-slate-300 rounded-lg cursor-pointer">
        ✕
      </button>
    </div>

    <!-- 导航菜单列表 -->
    <nav class="flex-1 px-3 py-4 space-y-3 overflow-y-auto overflow-x-hidden custom-scrollbar">
      <div v-for="(group, groupIndex) in groupedMenuItems" :key="groupIndex" class="space-y-1">
        
        <!-- 分组标题 (折叠时隐藏) -->
        <div v-show="!isCollapsed" class="px-3 pb-1 text-[11px] font-bold tracking-wider text-slate-400 dark:text-slate-500 uppercase whitespace-nowrap transition-all">
          {{ group.title }}
        </div>
        
        <!-- 组内菜单项 -->
        <button
          v-for="item in group.items"
          :key="item.key"
          :data-testid="`nav-${item.key}`"
          @click="handleMenuClick(item.key)"
          :title="isCollapsed ? t.menu[item.labelKey || item.key] : ''"
          :class="[
            'w-full flex items-center gap-3 rounded-2xl font-medium text-sm transition-all duration-200 cursor-pointer',
            isCollapsed ? 'justify-center px-0 py-3' : 'px-4 py-2.5',
            activeTab === item.key 
              ? 'bg-blue-600 text-white shadow-md shadow-blue-500/25' 
              : 'text-slate-600 dark:text-slate-300 bg-white/70 dark:bg-slate-800/60 hover:bg-blue-50/90 dark:hover:bg-slate-700/80 hover:text-blue-700 dark:hover:text-blue-400 border border-slate-200/80 dark:border-slate-700/60 shadow-2xs hover:scale-[1.02]'
          ]"
        >
          <component :is="item.icon" :size="18" class="shrink-0" />
          <span v-show="!isCollapsed" class="truncate leading-tight text-left whitespace-nowrap">
            {{ t.menu[item.labelKey || item.key] }}
          </span>
        </button>

        <!-- 组间分隔线 -->
        <div v-if="groupIndex < groupedMenuItems.length - 1" class="pt-2.5 mx-3 border-b border-slate-200/50 dark:border-slate-700/50"></div>
      </div>
    </nav>

    <!-- 底部实时时间胶囊 -->
    <div class="p-3 border-t border-slate-200/60 dark:border-slate-800 shrink-0 bg-white/40 dark:bg-slate-900/40">
      <div 
        :class="[
          'bg-white/80 dark:bg-slate-800/80 backdrop-blur-md rounded-2xl flex items-center justify-center border border-white dark:border-slate-700 shadow-2xs text-xs font-mono font-semibold text-slate-700 dark:text-slate-300 transition-all',
          isCollapsed ? 'px-2 py-3' : 'px-3.5 py-2.5 gap-2'
        ]"
      >
        <span v-if="!isCollapsed">📅</span>
        <span v-show="!isCollapsed" class="truncate">{{ currentDateTime }}</span>
        <!-- 折叠时只显示时间 -->
        <span v-if="isCollapsed" class="text-[10px] text-center leading-tight text-slate-500 dark:text-slate-400">
          {{ currentDateTime.split(' ')[1] || '⏱' }}
        </span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { computed } from 'vue'
import { useI18n } from '../composables/useI18n'
import { useAuth } from '../composables/useAuth'
import { 
  Cpu,
  LayoutDashboard, 
  TrendingUp, 
  TrendingDown,
  Package, 
  ShieldCheck, 
  Users, 
  ShoppingCart, 
  History, 
  Calculator, 
  FileText, 
  Database,
  ShieldAlert,
  ClipboardList // 盘点图标
} from 'lucide-vue-next'

const props = defineProps({
  activeTab: String,
  mobileMenuOpen: Boolean,
  currentDateTime: String,
  isCollapsed: { type: Boolean, default: false } // 🌟 新增折叠属性
})
const emit = defineEmits(['update:activeTab', 'update:mobileMenuOpen', 'menu-click'])

const { t } = useI18n()
const { currentUserObj } = useAuth()

const handleMenuClick = (key) => {
  emit('update:activeTab', key)
  emit('update:mobileMenuOpen', false)
  emit('menu-click', key)
}

const groupedMenuItems = computed(() => {
  const groups = [
    {
      title: t.value.menu.groupCore,
      items: [
        { key: 'dashboard', icon: LayoutDashboard },
        { key: 'financial', icon: TrendingUp, requiredPerm: 'financial:view' },
        { key: 'expenses', icon: TrendingDown, requiredPerm: 'financial:view' },
      ]
    },
    {
      title: t.value.menu.groupWarehouse,
      items: [
        { key: 'parts', icon: Package, requiredPerm: 'parts:view' },
        { key: 'inventory_audit', labelKey: 'inventoryAudit', icon: ClipboardList, requiredPerm: 'parts:manage' },
      ]
    },
    {
      title: t.value.menu.groupSales,
      items: [
        { key: 'clients', icon: Users, requiredPerm: 'clients:view' },
        { key: 'procurement', icon: ShoppingCart, requiredPerm: 'procurement:view' },
        { key: 'transactions', icon: History, requiredPerm: 'transactions:history' },
        { key: 'pos', icon: Calculator, requiredPerm: 'pos:access' }, // 快速收银
        { key: 'quotation', labelKey: 'quotation', icon: FileText, requiredPerm: 'pos:access' }, // 开单报价
        { key: 'quotations', labelKey: 'quotations', icon: History, requiredPerm: 'pos:access' }, // 历史报价
        { key: 'cash_register', labelKey: 'cashRegister', icon: FileText, requiredPerm: 'shift:report' },
      ]
    },
    {
      title: t.value.menu.groupSystem,
      items: [
        { key: 'staff', icon: ShieldCheck, requiredPerm: 'users:manage' },
        { key: 'audit_logs', labelKey: 'auditLogs', icon: ShieldAlert, requiredPerm: 'users:manage' },
        { key: 'backup', icon: Database, requiredPerm: 'settings:manage' },
      ]
    }
  ]

  const role = currentUserObj.value?.role || 'staff'
  const userPerms = currentUserObj.value?.permissions || []

  return groups.map(group => {
    const filteredItems = group.items.filter(item => {
      if (role === 'super_admin' || role === 'admin' || userPerms.includes('*')) return true
      if (item.requiredPerm) {
        return userPerms.includes(item.requiredPerm)
      }
      return true
    })
    return {
      title: group.title,
      items: filteredItems
    }
  }).filter(group => group.items.length > 0)
})
</script>

<style scoped>
/* 滚动条美化 */
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: transparent transparent; 
  transition: scrollbar-color 0.3s ease;
}
.custom-scrollbar:hover {
  scrollbar-color: rgba(255, 255, 255, 0.6) transparent; 
}
.custom-scrollbar::-webkit-scrollbar { width: 6px; }
.custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: transparent; 
  border-radius: 10px;
  transition: background-color 0.3s ease;
}
.custom-scrollbar:hover::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.6); 
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(255, 255, 255, 0.95); 
}
</style>