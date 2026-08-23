const api = require('../../utils/api')

Page({
  data: {
    items: [],
    selectedIds: [],
    loading: false,
    recipes: null,
    error: '',
    // 饮食偏好
    prefOptions: [
      { value: '', label: '无限制' },
      { value: '减脂', label: '减脂（低卡低脂）' },
      { value: '增肌', label: '增肌（高蛋白）' },
      { value: '均衡', label: '均衡营养' },
      { value: '清淡', label: '清淡少油少盐' },
    ],
    prefIndex: 0,
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
    try {
      const id = e.currentTarget.dataset.id
      console.log('toggleItem clicked, id:', id)
      if (!id) {
        console.error('toggleItem: id is undefined')
        return
      }
      const selected = [...this.data.selectedIds]
      const idx = selected.indexOf(id)
      if (idx > -1) {
        selected.splice(idx, 1)
      } else {
        selected.push(id)
      }
      this.setData({ selectedIds: selected, recipes: null, error: '' })
      console.log('toggleItem done, selectedIds:', selected, 'count:', selected.length)
    } catch (err) {
      console.error('toggleItem error:', err)
    }
  },

  onPrefChange(e) {
    this.setData({ prefIndex: e.detail.value, recipes: null, error: '' })
  },

  async generateRecipe() {
    if (this.data.selectedIds.length === 0) {
      wx.showToast({ title: '请至少选择3样食材', icon: 'none' })
      return
    }
    this.setData({ loading: true, recipes: null, error: '' })
    try {
      const pref = this.data.prefOptions[this.data.prefIndex].value
      const res = await api.recipes.generate(this.data.selectedIds, pref)
      if (res.success) {
        this.setData({ recipes: res.data?.recipes || [] })
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