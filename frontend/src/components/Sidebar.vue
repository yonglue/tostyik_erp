<!-- src/components/Sidebar.vue -->
<template>
  <div 
    v-if="mobileMenuOpen" 
    @click="$emit('update:mobileMenuOpen', false)"
    class="fixed inset-0 bg-slate-950/45 backdrop-blur-md z-20 md:hidden transition-opacity"
  ></div>

  <aside :class="['fixed md:static inset-y-0 left-0 z-30 w-64 bg-white/75 backdrop-blur-xl border-r border-white/60 flex flex-col transition-transform duration-300 shrink-0 shadow-xl',
    mobileMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0']">
    
    <!-- Logo 区域 -->
    <div class="h-16 px-6 border-b border-slate-200/60 flex items-center justify-between shrink-0 bg-white/40">
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
    <nav class="flex-1 px-3.5 py-4 space-y-3.5 overflow-y-auto">
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
          :class="['w-full flex items-center gap-3 px-4 py-2.5 rounded-2xl font-medium text-sm transition-all duration-200 cursor-pointer', 
            activeTab === item.key 
              ? 'bg-blue-600 text-white shadow-md shadow-blue-500/25' 
              : 'text-slate-600 bg-white/70 hover:bg-blue-50/90 hover:text-blue-700 border border-slate-200/80 hover:border-blue-300 shadow-2xs hover:scale-[1.02]']"
        >
          <component :is="item.icon" :size="18" class="shrink-0" />
          <span class="truncate leading-tight text-left">
            {{ t.menu[item.labelKey || item.key] }}
          </span>
        </button>

        <!-- 组间分隔线 -->
        <div v-if="groupIndex < groupedMenuItems.length - 1" class="pt-2.5 mx-3 border-b border-slate-200/50"></div>
      </div>
    </nav>

    <!-- 底部实时时间胶囊 -->
    <div class="p-3.5 border-t border-slate-200/60 shrink-0 bg-white/40">
      <div v-if="currentDateTime" class="bg-white/80 backdrop-blur-md rounded-2xl px-3.5 py-2.5 flex items-center justify-center gap-2 border border-white shadow-2xs text-xs font-mono font-semibold text-slate-700">
        <span>📅</span>
        <span class="truncate">{{ currentDateTime }}</span>
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
  mobileMenuOpen: Boolean,
  currentDateTime: String
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
      ]
    },
    {
      title: t.value.menu.groupWarehouse,
      items: [
        { key: 'parts', icon: Package, requiredPerm: 'parts:view' },
      ]
    },
    {
      title: t.value.menu.groupSales,
      items: [
        { key: 'clients', icon: Users, requiredPerm: 'clients:view' },
        { key: 'procurement', icon: ShoppingCart, requiredPerm: 'procurement:view' },
        { key: 'transactions', icon: History, requiredPerm: 'transactions:history' },
        { key: 'desk', icon: Calculator, requiredPerm: 'pos:access' },
        // 🌟 新增：报价单列表入口
        { key: 'quotations', labelKey: 'quotations', icon: FileText, requiredPerm: 'pos:access' },
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