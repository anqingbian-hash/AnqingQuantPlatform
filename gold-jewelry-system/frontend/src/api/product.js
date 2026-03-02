import request from '@/utils/request'

/**
 * 商品 API
 */

/**
 * 获取商品列表
 */
export function getProductList(params) {
  return request({
    url: '/v1/products',
    method: 'get',
    params
  })
}

/**
 * 获取所有商品
 */
export function getAllProducts() {
  return request({
    url: '/v1/products/all',
    method: 'get'
  })
}

/**
 * 根据编号查询商品
 */
export function getProductByCode(productCode) {
  return request({
    url: `/v1/products/code/${productCode}`,
    method: 'get'
  })
}

/**
 * 添加商品
 */
export function addProduct(data) {
  return request({
    url: '/v1/products',
    method: 'post',
    data
  })
}

/**
 * 更新商品
 */
export function updateProduct(id, data) {
  return request({
    url: `/v1/products/${id}`,
    method: 'put',
    data
  })
}

/**
 * 删除商品
 */
export function deleteProduct(id) {
  return request({
    url: `/v1/products/${id}`,
    method: 'delete'
  })
}
