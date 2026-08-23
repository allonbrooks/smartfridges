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
    submitting: false,
    newName: '',
    newQuantity: '1',
    newExpiryDate: addDays(7),
    // 编辑
    showEdit: false,
    editItemId: '',
    editName: '',
    editQuantity: '1',
    editExpiryDate: addDays(7),
    editSpaceId: '',
    allSpaces: [],
    editSpaceIndex: 0,
    // 删除空间
    showDeleteSpace: false,
    selectedMoveTo: '',
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
      const [detailRes, spacesRes] = await Promise.all([
        api.spaces.detail(this.data.spaceId),
        api.spaces.list(),
      ])
      if (detailRes.success) {
        const items = (detailRes.data.items || []).map(item => ({
          ...item,
          expiryDisplay: item.expiry_date ? item.expiry_date.slice(5) : '',
          createdDisplay: item.created_at ? item.created_at.split('T')[0].slice(5) : '',
        }))
        this.setData({
          space: detailRes.data.space,
          items,
          allSpaces: spacesRes.success ? (spacesRes.data || []) : [],
        })
        wx.setNavigationBarTitle({ title: detailRes.data.space.name })
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
    if (this.data.submitting) return
    if (!this.data.newName.trim()) {
      wx.showToast({ title: '请输入物品名称', icon: 'none' })
      return
    }
    this.setData({ submitting: true })
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
      console.error('addItem error:', e)
      wx.showToast({ title: e?.error || e?.errMsg || '请求失败，请检查网络', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
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

  // --- 编辑物品 ---

  onEditItem(e) {
    const id = e.currentTarget.dataset.id
    const item = this.data.items.find(i => i.id === id)
    if (!item) return
    const spaceIdx = this.data.allSpaces.findIndex(s => s.id === (item.storage_space || this.data.spaceId))
    this.setData({
      showEdit: true,
      editItemId: id,
      editName: item.name,
      editQuantity: String(item.quantity || 1),
      editExpiryDate: item.expiry_date || addDays(7),
      editSpaceId: item.storage_space || this.data.spaceId,
      editSpaceIndex: spaceIdx >= 0 ? spaceIdx : 0,
    })
  },

  hideEditDialog() {
    this.setData({ showEdit: false })
  },

  onEditNameInput(e) { this.setData({ editName: e.detail.value }) },
  onEditQuantityInput(e) { this.setData({ editQuantity: e.detail.value }) },
  onEditExpiryDateChange(e) { this.setData({ editExpiryDate: e.detail.value }) },
  onEditSpaceChange(e) {
    const idx = e.detail.value
    const space = this.data.allSpaces[idx]
    if (space) {
      this.setData({ editSpaceId: space.id, editSpaceIndex: idx })
    }
  },

  async updateItem() {
    if (this.data.submitting) return
    if (!this.data.editName.trim()) {
      wx.showToast({ title: '请输入物品名称', icon: 'none' })
      return
    }
    this.setData({ submitting: true })
    try {
      const res = await api.items.update(this.data.editItemId, {
        name: this.data.editName.trim(),
        quantity: Number(this.data.editQuantity) || 1,
        expiry_date: this.data.editExpiryDate,
        storage_space: this.data.editSpaceId,
      })
      if (res.success) {
        wx.showToast({ title: '已更新', icon: 'success' })
        this.hideEditDialog()
        this.loadSpaceDetail()
      }
    } catch (e) {
      console.error('update item error:', e)
      wx.showToast({ title: e?.error || '更新失败', icon: 'none' })
    } finally {
      this.setData({ submitting: false })
    }
  },

  // --- 删除空间 ---

  onDeleteSpace() {
    const items = this.data.items
    if (items.length === 0) {
      // 空间为空，直接确认删除
      wx.showModal({
        title: '删除空间',
        content: `确定要删除空间「${this.data.space.name}」吗？`,
        success: (res) => {
          if (res.confirm) this.confirmDeleteSpace()
        }
      })
    } else {
      // 有物品，显示迁移弹窗
      this.setData({
        showDeleteSpace: true,
        selectedMoveTo: '',
      })
    }
  },

  hideDeleteSpaceDialog() {
    this.setData({ showDeleteSpace: false })
  },

  onMoveToChange(e) {
    const idx = e.detail.value
    const space = this.data.allSpaces.filter(s => s.id !== this.data.spaceId)[idx]
    if (space) {
      this.setData({ selectedMoveTo: space.id })
    }
  },

  async confirmDeleteSpace() {
    const spaceId = this.data.spaceId
    const items = this.data.items
    try {
      if (items.length > 0 && !this.data.selectedMoveTo) {
        wx.showToast({ title: '请选择目标空间', icon: 'none' })
        return
      }
      wx.showLoading({ title: '删除中...' })
      const res = await api.spaces.delete(spaceId, items.length > 0 ? this.data.selectedMoveTo : null)
      wx.hideLoading()
      if (res.success) {
        wx.showToast({ title: '已删除', icon: 'success' })
        this.hideDeleteSpaceDialog()
        wx.navigateBack()
      }
    } catch (e) {
      wx.hideLoading()
      console.error('delete space error:', e)
      wx.showToast({ title: e?.error || '删除失败', icon: 'none' })
    }
  },
})