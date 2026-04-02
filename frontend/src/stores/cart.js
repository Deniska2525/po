import { defineStore } from 'pinia'

export const useCartStore = defineStore('cart', {
  state: () => ({
    items: JSON.parse(localStorage.getItem('cart')) || []
  }),
  
  getters: {
    totalItems: (state) => state.items.reduce((s, i) => s + i.quantity, 0),
    totalPrice: (state) => state.items.reduce((s, i) => s + (i.price * i.quantity), 0),
    formattedTotalPrice: (state) => {
      return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB',
        minimumFractionDigits: 0
      }).format(state.totalPrice / 100)
    }
  },
  
  actions: {
    addToCart(product, quantity = 1) {
      const existing = this.items.find(i => i.id === product.id)
      if (existing) {
        existing.quantity += quantity
      } else {
        this.items.push({
          id: product.id,
          name: product.name,
          price: product.price,
          quantity,
          category: product.category
        })
      }
      this._save()
    },
    
    removeFromCart(productId) {
      this.items = this.items.filter(i => i.id !== productId)
      this._save()
    },
    
    updateQuantity(productId, quantity) {
      const item = this.items.find(i => i.id === productId)
      if (item) {
        if (quantity <= 0) {
          this.removeFromCart(productId)
        } else {
          item.quantity = quantity
          this._save()
        }
      }
    },
    
    clearCart() {
      this.items = []
      this._save()
    },
    
    _save() {
      localStorage.setItem('cart', JSON.stringify(this.items))
    }
  }
})