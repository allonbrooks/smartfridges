const api = require('../../utils/api')

Page({
  data: {
    items: [],
    loading: true,
    newItemName: '',
    newItemQuantity: '1',
    showAdd: false,
  },

  onShow() {
    this.loadList()
  },

  noop() {},

  async loadList() {
    this.setData({ loading: true })
    try {
      const res = await api.shopping.list()
      if (res.success) {
        this.setData({ items: res.data || [] })
      }
    } catch (e) {
      if (e?.error?.includes('家庭')) {
        wx.showToast({ title: '请先在首页创建家庭', icon: 'none' })
      } else {
        console.error(e)
      }
    } finally {
      this.setData({ loading: false })
    }
  },

  showAddDialog() {
    this.setData({ showAdd: true, newItemName: '', newItemQuantity: 1 })
  },

  hideAddDialog() {
    this.setData({ showAdd: false })
  },

  onNameInput(e) { this.setData({ newItemName: e.detail.value }) },
  onQuantityInput(e) { this.setData({ newItemQuantity: e.detail.value }) },

  async addItem() {
    if (!this.data.newItemName.trim()) {
      wx.showToast({ title: '请输入名称', icon: 'none' })
      return
    }
    try {
      const res = await api.shopping.create({
        item_name: this.data.newItemName.trim(),
        quantity: Number(this.data.newItemQuantity) || 1,
      })
      if (res.success) {
        wx.showToast({ title: '已添加', icon: 'success' })
        this.hideAddDialog()
        this.loadList()
      }
    } catch (e) {
      console.error(e)
    }
  },

  async toggleItem(e) {
    const id = e.currentTarget.dataset.id
    const is_purchased = e.currentTarget.dataset.purchased === 'true'
    try {
      await api.shopping.toggle(id, !is_purchased)
      this.loadList()
    } catch (e) {
      console.error(e)
    }
  },

  async deleteItem(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认',
      content: '删除该商品？',
      success: (res) => {
        if (res.confirm) {
          api.shopping.delete(id).then(() => this.loadList())
        }
      }
    })
  },

  async clearChecked() {
    wx.showModal({
      title: '确认',
      content: '清空已购买的商品？',
      success: (res) => {
        if (res.confirm) {
          api.shopping.clearChecked().then(() => this.loadList())
        }
      }
    })
  },
})