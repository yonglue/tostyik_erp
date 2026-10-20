// src/composables/usePosCart.js
import { computed, ref } from 'vue'

const cartItems = ref([])
const quoteClientName = ref('Cliente General')
const paymentReference = ref('')

// 🌟 支付流水列表（替换掉原来的单一对象）
// 结构: { id, method: 'Cash_USD', amount: 20, currency: 'USD' | 'BS' }
const paymentRecords = ref([])

export function usePosCart() {
  const addToCart = (part) => {
    const existing = cartItems.value.find((i) => i.oem === part.oem)
    if (existing) {
      existing.quantity += 1
    } else {
      cartItems.value.push({
        oem: part.oem,
        name: part.name,
        brand: part.brand,
        price: part.price,
        tax_rate: part.tax_rate ?? 0.16,
        quantity: 1
      })
    }
  }

  const clearCart = () => {
    cartItems.value = []
    paymentRecords.value = [] // 清空购物车时连带清空支付流水
    quoteClientName.value = 'Cliente General'
    paymentReference.value = ''
  }

  // 添加一笔支付流水
  const addPaymentRecord = (method, amount, currency, bcvRate) => {
    const numAmount = Number(amount) || 0
    if (numAmount <= 0) return false
    
    // 统一折算为 USD 金额
    const amountUsd = currency === 'BS' ? (numAmount / (bcvRate || 1)) : numAmount

    paymentRecords.value.push({
      id: Date.now() + Math.random().toString(36).substring(2, 7),
      method,
      originalAmount: numAmount,
      currency,
      amountUsd: Number(amountUsd.toFixed(2))
    })
    return true
  }

  // 删除一笔支付流水
  const removePaymentRecord = (id) => {
    paymentRecords.value = paymentRecords.value.filter(r => r.id !== id)
  }

  const cartTotalUsd = computed(() =>
    cartItems.value.reduce((sum, i) => sum + (Math.round(i.price * 100) * i.quantity), 0) / 100
  )

  // 计算总 IGTF (仅对 Cash_USD 的支付流水征收 3%)
  const totalIgtfUsd = computed(() => {
    const cashUsdRecords = paymentRecords.value.filter(r => r.method === 'Cash_USD')
    const totalCashUsd = cashUsdRecords.reduce((sum, r) => sum + r.amountUsd, 0)
    return Math.round(totalCashUsd * 100 * 0.03) / 100
  })

  // 计算已付总额 (USD 等值)
  const totalPaidUsd = computed(() => {
    const paidCents = paymentRecords.value.reduce((sum, r) => sum + Math.round(r.amountUsd * 100), 0)
    return paidCents / 100
  })

  return {
    cartItems,
    quoteClientName,
    paymentReference,
    paymentRecords, // 导出流水
    cartTotalUsd,
    totalIgtfUsd,
    totalPaidUsd,
    addToCart,
    clearCart,
    addPaymentRecord,
    removePaymentRecord
  }
}