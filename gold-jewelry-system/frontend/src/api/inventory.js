import request from '@/utils/request'

/**
 * 库存 API
 */

/**
 * 获取库存
 */
export function getInventory(productId, storeId) {
  return request({
    url: '/v1/inventory',
    method: 'get',
    params: { productId, storeId }
  })
}

/**
 * 获取店铺库存列表
 */
export function getInventoryByStore(storeId) {
  return request({
    url: `/v1/inventory/store/${storeId}`,
    method: 'get'
  })
}

/**
 * 入库
 */
export function stockIn(data) {
  return request({
    url: '/v1/inventory/stock-in',
    method: 'post',
    data
  })
}

/**
 * 出库
 */
export function stockOut(data) {
  return request({
    url: '/v1/inventory/stock-out',
    method: 'post',
    data
  })
}

/**
 * 获取低库存商品
 */
export function getLowStock(storeId, threshold) {
  return request({
    url: '/v1/inventory/low-stock',
    method: 'get',
    params: { storeId, threshold }
  })
}

/**
 * 统计店铺库存总数
 */
export function sumQuantityByStoreId(storeId) {
  return request({
    url: `/v1/inventory/store/${storeId}/total`,
    method: 'get'
  })
}
