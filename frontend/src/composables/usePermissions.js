// 权限判定 + 默认落地页决策。
// 依赖 useAuth 单例暴露的 currentUserObj，与 App.vue 内部状态保持同源。
import { useAuth } from './useAuth'

export function usePermissions() {
  const { currentUserObj } = useAuth()

  // 权限校验工具
  const hasPermission = (permKey) => {
    if (!currentUserObj.value) return false
    const role = currentUserObj.value.role || 'staff'
    const perms = currentUserObj.value.permissions || []
    if (role === 'super_admin' || role === 'admin' || perms.includes('*')) return true
    return perms.includes(permKey)
  }

  // 获取用户默认应当进入的页面
  const getDefaultAllowedTab = () => {
    const role = currentUserObj.value?.role || 'staff'
    if (role === 'super_admin' || role === 'admin') return 'dashboard'

    if (hasPermission('parts:view')) return 'parts'
    if (hasPermission('clients:view')) return 'clients'
    if (hasPermission('transactions:history')) return 'transactions'
    if (hasPermission('financial:view')) return 'financial'
    if (hasPermission('users:manage')) return 'staff'
    if (hasPermission('pos:access')) return 'desk'

    return 'dashboard'
  }

  return { hasPermission, getDefaultAllowedTab }
}
