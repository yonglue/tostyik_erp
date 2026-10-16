<!-- src/components/ProcurementCenterView.vue -->
<template>
  <div class="space-y-6">
    
    <!-- 🌟 顶部 Tab 页签切换栏 -->
    <div class="flex items-center justify-between bg-white px-6 py-3 rounded-2xl border border-slate-200/80 shadow-xs">
      <div class="flex items-center gap-2 bg-slate-100 p-1 rounded-xl">
        <button 
          @click="activeSubTab = 'orders'"
          :class="['px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer', 
            activeSubTab === 'orders' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900']"
        >
          📦 采购订单与收货管理
        </button>
        <button 
          @click="activeSubTab = 'replenish'"
          :class="['px-4 py-2 rounded-lg text-xs font-bold transition-all cursor-pointer', 
            activeSubTab === 'replenish' ? 'bg-white text-blue-600 shadow-xs' : 'text-slate-600 hover:text-slate-900']"
        >
          ⚡ 智能补货建议与下单
        </button>
      </div>

      <div class="text-xs font-mono text-slate-400 hidden sm:block">
        供应链状态: <span class="text-emerald-600 font-bold">在线正常</span>
      </div>
    </div>

    <!-- 🌟 子视图 1：采购订单与收货管理（完美解析 JSON 明细） -->
    <div v-if="activeSubTab === 'orders'" class="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-4 md:p-6 space-y-6">
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <h3 class="font-bold text-slate-900 text-base">采购订单与收货管理</h3>
          <p class="text-xs text-slate-500 mt-0.5">管理供应商采购订单，支持一键验货入库、状态流转与商品明细解析</p>
        </div>
        <button 
          @click="fetchPurchaseOrders"
          class="bg-slate-100 hover:bg-slate-200 text-slate-700 text-xs font-semibold px-4 py-2 rounded-xl transition-colors cursor-pointer flex items-center gap-1.5"
        >
          🔄 刷新订单列表
        </button>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[850px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3.5 px-6">订单编号 (PO No.)</th>
              <th class="py-3.5 px-6">供应商</th>
              <th class="py-3.5 px-6">采购明细解析 (SKU & 数量)</th>
              <th class="py-3.5 px-6">订单状态</th>
              <th class="py-3.5 px-6">创建时间</th>
              <th class="py-3.5 px-6 text-right">操作 / 验货入库</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="orderList.length === 0">
              <td colspan="6" class="text-center py-12 text-slate-400 text-xs">
                暂无采购订单数据，请前往“智能补货建议”生成采购单
              </td>
            </tr>
            <tr v-for="order in orderList" :key="order.id" class="hover:bg-slate-50/50 transition-colors">
              <td class="py-4 px-6 font-mono font-bold text-slate-800">{{ order.po_no }}</td>
              <td class="py-4 px-6 font-medium text-slate-900">
                <span class="bg-slate-100 px-2.5 py-1 rounded-md text-xs">{{ order.supplier_name || 'TOSTIKYK 优选供应商' }}</span>
              </td>
              <!-- 🌟 核心改进：安全解析并渲染美观的采购明细标签，彻底告别丑陋的原始 JSON 串 -->
              <td class="py-4 px-6 text-slate-600 text-xs">
                <div class="flex flex-wrap gap-1.5 max-w-md">
                  <span v-for="(item, idx) in parseOrderItems(order.items_json)" :key="idx" class="bg-blue-50 text-blue-700 border border-blue-200/60 px-2.5 py-1 rounded-lg font-mono">
                    <strong class="text-blue-900">{{ item.oem || item.code }}</strong>: {{ item.name }} <span class="text-emerald-600 font-bold">x{{ item.quantity || item.suggested_qty }}</span>
                  </span>
                </div>
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

    <!-- 🌟 子视图 2：智能补货建议与下单 -->
    <div v-if="activeSubTab === 'replenish'" class="bg-white rounded-2xl border border-slate-200/80 shadow-xs p-4 md:p-6 space-y-6">
      <div class="flex flex-wrap items-center justify-between gap-4 border-b border-slate-100 pb-4">
        <div>
          <h3 class="font-bold text-slate-900 text-base">智能补货建议与缺货预警</h3>
          <p class="text-xs text-slate-500 mt-0.5">实时监测库存不足的汽车配件，计算系统建议补货数量与预估成本</p>
        </div>
        
        <div class="flex items-center gap-3 flex-wrap">
          <select 
            v-model="procurementBrand" 
            class="bg-slate-50 border border-slate-200 text-slate-700 text-xs rounded-xl px-3 py-2 outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="ALL">全部品牌</option>
            <option v-for="b in uniqueBrands" :key="b" :value="b">{{ b }}</option>
          </select>

          <select 
            v-model="procurementCategory" 
            class="bg-slate-50 border border-slate-200 text-slate-700 text-xs rounded-xl px-3 py-2 outline-none focus:border-blue-500 cursor-pointer"
          >
            <option value="ALL">全部类目</option>
            <option v-for="c in uniqueCategories" :key="c" :value="c">{{ c }}</option>
          </select>
        </div>
      </div>

      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[750px]">
          <thead>
            <tr class="bg-slate-50/75 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
              <th class="py-3.5 px-6">配件编码</th>
              <th class="py-3.5 px-6">OEM 号</th>
              <th class="py-3.5 px-6">配件名称</th>
              <th class="py-3.5 px-6">适配品牌</th>
              <th class="py-3.5 px-6">所属类目</th>
              <th class="py-3.5 px-6">当前库存</th>
              <th class="py-3.5 px-6 text-blue-600 font-bold">建议补货量</th>
              <th class="py-3.5 px-6">预估成本 (USD)</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-slate-100 text-sm">
            <tr v-if="filteredProcurementList.length === 0">
              <td colspan="8" class="text-center py-12 text-slate-400 text-xs">
                当前库存充足，暂无需要补货的汽配商品
              </td>
            </tr>
            <tr v-for="item in filteredProcurementList" :key="item.code" class="hover:bg-slate-50/50 transition-colors">
              <td class="py-4 px-6 font-mono font-semibold text-slate-700">{{ item.code }}</td>
              <td class="py-4 px-6 font-mono text-slate-600">{{ item.oem }}</td>
              <td class="py-4 px-6 font-medium text-slate-900">{{ item.name }}</td>
              <td class="py-4 px-6"><span class="bg-slate-100 px-2.5 py-1 rounded-md text-xs font-medium">{{ item.brand }}</span></td>
              <td class="py-4 px-6"><span class="bg-blue-50 text-blue-600 px-2 py-0.5 rounded text-xs font-semibold">{{ item.category }}</span></td>
              <td class="py-4 px-6 font-bold text-rose-600">{{ item.current_stock }}</td>
              <td class="py-4 px-6 font-black text-blue-600 text-base">+ {{ item.suggested_qty }}</td>
              <td class="py-4 px-6 font-bold text-emerald-600">$ {{ (item.estimated_cost || 0).toFixed(2) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { apiFetch } from '../utils/api'

// 子视图切换：orders（采购订单管理） / replenish（智能补货建议）
const activeSubTab = ref('orders')

const orderList = ref([])
const loadingId = ref(null)
const procurementList = ref([])
const procurementBrand = ref('ALL')
const procurementCategory = ref('ALL')

// 安全解析订单明细 JSON 字符串
const parseOrderItems = (jsonStr) => {
  if (!jsonStr) return []
  try {
    const parsed = JSON.parse(jsonStr)
    return Array.isArray(parsed) ? parsed : [parsed]
  } catch (e) {
    return [{ name: jsonStr, quantity: 1 }]
  }
}

// 获取采购订单列表
const fetchPurchaseOrders = async () => {
  try {
    const res = await apiFetch('/api/purchase-orders')
    if (res.ok) {
      const data = await res.json()
      orderList.value = Array.isArray(data) ? data : (data.items || data.orders || [])
    }
  } catch (e) {
    console.error("获取采购订单失败", e)
  }
}

// 获取智能补货列表数据（已修正接口请求路径，避免 404）
const fetchProcurementData = async () => {
  try {
    const res = await apiFetch('/api/parts') // 如果有独立的补货接口可换成对应的路由，这里默认从 parts 获取商品并进行库存检查
    if (res.ok) {
      const data = await res.json()
      const parts = Array.isArray(data) ? data : (data.items || [])
      
      // 自动计算库存低于安全线（例如 <= 5）的商品作为智能补货建议
      procurementList.value = parts
        .filter(p => (p.stock ?? p.current_stock ?? 0) <= 5)
        .map(p => ({
          code: p.code || p.oem || 'SKU-' + p.id,
          oem: p.oem || 'N/A',
          name: p.name || '未知配件',
          brand: p.brand || 'TOSTIKYK',
          category: p.category || '通用类目',
          current_stock: p.stock ?? p.current_stock ?? 0,
          suggested_qty: 10, // 默认建议补货量
          estimated_cost: (p.price || p.cost || 10.0) * 10
        }))
    }
  } catch (e) {
    console.error("获取补货建议失败", e)
  }
}

// 过滤筛选补货列表
const uniqueBrands = computed(() => {
  return [...new Set(procurementList.value.map(i => i.brand).filter(Boolean))]
})

const uniqueCategories = computed(() => {
  return [...new Set(procurementList.value.map(i => i.category).filter(Boolean))]
})

const filteredProcurementList = computed(() => {
  return procurementList.value.filter(item => {
    const matchBrand = procurementBrand.value === 'ALL' || item.brand === procurementBrand.value
    const matchCat = procurementCategory.value === 'ALL' || item.category === procurementCategory.value
    return matchBrand && matchCat
  })
})

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
      await fetchPurchaseOrders()
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
  fetchProcurementData()
})
</script>