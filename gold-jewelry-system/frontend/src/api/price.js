import request from '@/utils/request'

/**
 * 价格 API
 */

/**
 * 获取实时金价
 */
export function getGoldPrice() {
  return request({
    url: '/v1/prices/gold-price',
    method: 'get'
  })
}

/**
 * 计算商品售价
 */
export function calculatePrice(data) {
  return request({
    url: '/v1/prices/calculate',
    method: 'post',
    data
  })
}
