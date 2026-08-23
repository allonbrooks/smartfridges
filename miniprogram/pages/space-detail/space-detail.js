const api = require('../../utils/api')

function addDays(n) {
  const d = new Date()
  d.setDate(d.getDate() + n)
  return d.toISOString().split('T')[0]
}

Page({
  data: {
    space: null,
    items: [],
    loading: true,
    spaceId: '',
    showAdd: false,
    newName: '',
    newQuantity: '1',
    newExpiryDate: addDays(7),
  },

  onLoad(options) {
    this.setData({
      spaceId: options.spaceId || '',
      itemId: options.itemId || '',
    })
  },

  noop() {},

  onShow() {
    if (this.data.spaceId) {
      this.loadSpaceDetail()
    } else if (this.data.itemId) {
      this.loadItemDetail()
    }
  },

  async loadSpaceDetail() {
    this.setData({ loading: true })
    try {
      const res = await api.spaces.detail(this.data.spaceId)
      if (res.success) {
        const items = (res.data.items || []).map(item => ({
          ...item,
          expiryDisplay: item.expiry_date ? item.expiry_date.slice(5) : '',
          createdDisplay: item.created_at ? item.created_at.split('T')[0].slice(5) : '',
        }))
        this.setData({
          space: res.data.space,
          items,
        })
        wx.setNavigationBarTitle({ title: res.data.space.name })
      }
    } catch (e) {
      console.error(e)
    } finally {
      this.setData({ loading: false })
    }
  },

  async loadItemDetail() {
    this.setData({ loading: true })
    try {
      const res = await api.items.detail(this.data.itemId)
      if (res.success) {
        const item = {
          ...res.data,
          expiryDisplay: res.data.expiry_date ? res.data.expiry_date.slice(5) : '',
          createdDisplay: res.data.created_at ? res.data.created_at.split('T')[0].slice(5) : '',
        }
        this.setData({
          items: [item],
          space: { name: '物品详情' },
        })
      }
    } catch (e) {
      console.error(e)
    } finally {
      this.setData({ loading: false })
    }
  },

  showAddDialog() {
    this.setData({ showAdd: true, newName: '', newQuantity: '1', newExpiryDate: addDays(7) })
  },

  hideAddDialog() {
    this.setData({ showAdd: false })
  },

  onNameInput(e) { this.setData({ newName: e.detail.value }) },
  onQuantityInput(e) { this.setData({ newQuantity: e.detail.value }) },
  onExpiryDateChange(e) { this.setData({ newExpiryDate: e.detail.value }) },

  async addItem() {
    if (!this.data.newName.trim()) {
      wx.showToast({ title: '请输入物品名称', icon: 'none' })
      return
    }
    try {
      const res = await api.items.create({
        name: this.data.newName.trim(),
        quantity: Number(this.data.newQuantity) || 1,
        expiry_date: this.data.newExpiryDate,
        storage_space: this.data.spaceId,
      })
      if (res.success) {
        wx.showToast({ title: '添加成功', icon: 'success' })
        this.hideAddDialog()
        this.loadSpaceDetail()
      }
    } catch (e) {
      console.error(e)
    }
  },

  onConsume(e) {
    const id = e.currentTarget.dataset.id
    wx.showActionSheet({
      itemList: ['消耗1个', '消耗全部'],
      success: (res) => {
        const quantity = res.tapIndex === 0 ? 1 : 999
        api.items.consume(id, quantity).then(() => {
          wx.showToast({ title: '已消耗', icon: 'success' })
          this.loadSpaceDetail()
        })
      }
    })
  },

  onDelete(e) {
    const id = e.currentTarget.dataset.id
    wx.showModal({
      title: '确认',
      content: '确定要删除该物品吗？',
      success: (res) => {
        if (res.confirm) {
          api.items.delete(id).then(() => {
            wx.showToast({ title: '已删除', icon: 'success' })
            this.loadSpaceDetail()
          })
        }
      }
    })
  },
})