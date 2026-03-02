import request from '@/utils/request'

/**
 * 盘点 API
 */

/**
 * 根据店铺 ID 查询盘点单列表
 */
export function getStocktakesByStore(storeId) {
  return request({
    url: `/v1/stocktakes/store/${storeId}`,
    method: 'get'
  })
}

/**
 * 创建盘点单
 */
export function createStocktakeOrder(data) {
  return request({
    url: '/v1/stocktakes',
    method: 'post',
    data
  })
}

/**
 * 添加盘点明细
 */
export function addStocktakeItem(data) {
  return request({
    url: '/v1/stocktakes/items',
    method: 'post',
    data
  })
}

/**
 * 完成盘点
 */
export function completeStocktake(id, data) {
  return request({
    url: `/v1/stocktakes/${id}/complete`,
    method: 'post',
    data
  })
}

/**
 * 审核盘点
 */
export function reviewStocktake(id, data) {
  return request({
    url: `/v1/stocktakes/${id}/review`,
    method: 'post',
    data
  })
}

/**
 * 获取盘点明细
 */
export function getStocktakeItems(id) {
  return request({
    url: `/v1/stocktakes/${id}/items`,
    method: 'get'
  })
}
