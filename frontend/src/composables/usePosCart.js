// src/composables/usePosCart.js
//
// 开单购物车状态。App.vue 与收银台共用。

import { computed, ref } from 'vue'

const cartItems = ref([])
const quoteClientName = ref('Cliente General')
const selectedPaymentMethod = ref('Cash_USD')
const paymentReference = ref('')

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
        quantity: 1
      })
    }
  }

  const clearCart = () => {
    cartItems.value = []
  }

  const cartTotalUsd = computed(() =>
    cartItems.value.reduce((sum, i) => sum + i.price * i.quantity, 0)
  )

  return {
    cartItems,
    quoteClientName,
    selectedPaymentMethod,
    paymentReference,
    cartTotalUsd,
    addToCart,
    clearCart
  }
}
