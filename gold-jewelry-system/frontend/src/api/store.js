import request from '@/utils/request'

/**
 * 店铺 API
 */

/**
 * 获取所有店铺
 */
export function getAllStores() {
  return request({
    url: '/v1/stores',
    method: 'get'
  })
}

/**
 * 添加店铺
 */
export function addStore(data) {
  return request({
    url: '/v1/stores',
    method: 'post',
    data
  })
}

/**
 * 更新店铺
 */
export function updateStore(id, data) {
  return request({
    url: `/v1/stores/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除店铺
 */
export function deleteStore(id) {
  return request({
    url: `/v1/stores/${id}`,
    method: 'delete'
  })
}
