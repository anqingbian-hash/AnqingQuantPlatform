/**
 * 编码生成工具类
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
export class CodeGenerator {

  /**
   * 生成订单编号
   * 格式：SO + 年月日时分秒 + 4位随机数
   * 示例：SO2026022418300001
   */
  static generateOrderNo() {
    const dateStr = new Date().toISOString().replace(/[-:.]/g, '').slice(0, 14)
    const randomStr = Math.floor(Math.random() * 10000).toString().padStart(4, '0')
    return `SO${dateStr}${randomStr}`
  }

  /**
   * 生成调拨编号
   * 格式：TF + 年月日时分秒 + 4位随机数
   * 示例：TF2026022418300001
   */
  static generateTransferNo() {
    const dateStr = new Date().toISOString().replace(/[-:.]/g, '').slice(0, 14)
    const randomStr = Math.floor(Math.random() * 10000).toString().padStart(4, '0')
    return `TF${dateStr}${randomStr}`
  }

  /**
   * 生成盘点编号
   * 格式：ST + 年月日时分秒 + 4位随机数
   * 示例：ST2026022418300001
   */
  static generateStocktakeNo() {
    const dateStr = new Date().toISOString().replace(/[-:.]/g, '').slice(0, 14)
    const randomStr = Math.floor(Math.random() * 10000).toString().padStart(4, '0')
    return `ST${dateStr}${randomStr}`
  }
}

export default CodeGenerator
