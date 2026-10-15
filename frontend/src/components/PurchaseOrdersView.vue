<!-- src/components/PurchaseOrdersView.vue -->
<template>
  <div class="space-y-6">
    <div class="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-4 md:p-6 space-y-6">
      
      <!-- 顶部标题与操作栏 -->
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <h3 class="font-bold text-slate-900 text-base">采购订单与收货管理</h3>
          <p class="text-xs text-slate-500 mt-0.5">管理供应商采购订单，支持一键验货入库、状态流转与防重复提交</p>
        </div>
        
        <div class="flex items-center gap-3">
          <button 
            @click="fetchPurchaseOrders"
            class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-4 py-2 rounded-xl transition-colors cursor-pointer flex items-center gap-1.5"
          >
            🔄 刷新订单列表
          </button>
        </div>
      </div>

      <!-- 采购订单列表表格 -->
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[850px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3.5 px-6">订单编号 (PO No.)</th>
              <th class="py-3.5 px-6">供应商</th>
              <th class="py-3.5 px-6">采购明细摘要</th>
              <th class="py-3.5 px-6">订单状态</th>
              <th class="py-3.5 px-6">创建时间</th>
              <th class="py-3.5 px-6 text-right">操作 / 验货入库</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="orderList.length === 0">
              <td colspan="6" class="text-center py-12 text-slate-400 text-xs">
                暂无采购订单数据，请先从智能补缺或新建采购生成
              </td>
            </tr>
            <tr v-for="order in orderList" :key="order.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="py-4 px-6 font-mono font-semibold text-slate-700">{{ order.po_no }}</td>
              <td class="py-4 px-6 font-medium text-slate-900">{{ order.supplier_name }}</td>
              <td class="py-4 px-6 text-slate-600 text-xs max-w-xs truncate" :title="order.items_json">
                {{ order.items_json }}
              </td>
              <td class="py-4 px-6">
                <span 
                  :class="order.status === 'received' 
                    ? 'bg-emerald-50 text-emerald-600 border border-emerald-200/60' 
                    : 'bg-amber-50 text-amber-600 border border-amber-200/60'"
                  class="px-2.5 py-1 rounded-full text-xs font-bold inline-flex items-center gap-1"
                >
                  {{ order.status === 'received' ? '✅ 已收货入库' : '⏳ 待收货' }}
                </span>
              </td>
              <td class="py-4 px-6 text-slate-500 text-xs font-mono">{{ order.created_at || '刚刚' }}</td>
              <td class="py-4 px-6 text-right">
                <button 
                  @click="handleReceive(order.id)"
                  :disabled="order.status === 'received' || loadingId === order.id"
                  :class="order.status === 'received' 
                    ? 'bg-slate-100 text-slate-400 cursor-not-allowed' 
                    : 'bg-blue-600 hover:bg-blue-700 text-white shadow-xs cursor-pointer'"
                  class="text-xs font-semibold px-4 py-2 rounded-xl transition-all"
                >
                  {{ loadingId === order.id ? '处理中...' : (order.status === 'received' ? '已完成收货' : '📦 确认收货入库') }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { apiFetch } from '../utils/api'

const orderList = ref([])
const loadingId = ref(null)

// 获取采购订单列表
const fetchPurchaseOrders = async () => {
  try {
    const res = await apiFetch('/api/purchase-orders')
    if (res.ok) {
      const data = await res.json()
      // 兼容后端返回的数组或对象结构
      orderList.value = Array.isArray(data) ? data : (data.items || data.orders || [])
    }
  } catch (e) {
    console.error("获取采购订单失败", e)
  }
}

// 确认收货动作
const handleReceive = async (poId) => {
  loadingId.value = poId
  try {
    const res = await apiFetch(`/api/purchase-orders/${poId}/receive`, {
      method: 'POST'
    })
    const data = await res.json()
    
    if (res.ok && data.status === 'success') {
      alert(data.message || "收货成功：库存已增加、流水已记录！")
      await fetchPurchaseOrders() // 刷新列表状态
    } else {
      alert(data.detail || data.message || "收货操作失败")
    }
  } catch (e) {
    alert("网络异常或服务器错误：" + e.message)
  } finally {
    loadingId.value = null
  }
}

onMounted(() => {
  fetchPurchaseOrders()
})
</script>