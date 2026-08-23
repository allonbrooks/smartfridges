const api = require('../../utils/api')

Page({
  data: {
    items: [],
    selectedIds: [],
    loading: false,
    recipes: null,
    error: '',
  },

  onShow() {
    this.loadItems()
  },

  async loadItems() {
    try {
      const res = await api.items.list()
      if (res.success) {
        this.setData({ items: res.data || [] })
      }
    } catch (e) {
      console.error('loadItems error:', e)
      this.setData({ error: '加载食材失败' })
    }
  },

  toggleItem(e) {
    const id = e.currentTarget.dataset.id
    console.log('toggleItem:', id, 'selectedIds:', this.data.selectedIds)
    const selected = [...this.data.selectedIds]
    const idx = selected.indexOf(id)
    if (idx > -1) {
      selected.splice(idx, 1)
    } else {
      selected.push(id)
    }
    this.setData({ selectedIds: selected, recipes: null, error: '' })
    console.log('after toggle, selectedIds:', selected)
  },

  async generateRecipe() {
    if (this.data.selectedIds.length === 0) {
      wx.showToast({ title: '请至少选择3样食材', icon: 'none' })
      return
    }
    this.setData({ loading: true, recipes: null, error: '' })
    try {
      const res = await api.recipes.generate(this.data.selectedIds)
      if (res.success) {
        this.setData({ recipes: res.data.recipes })
      } else {
        this.setData({ error: res.error || '生成失败' })
      }
    } catch (e) {
      this.setData({ error: '网络错误' })
    } finally {
      this.setData({ loading: false })
    }
  },
})