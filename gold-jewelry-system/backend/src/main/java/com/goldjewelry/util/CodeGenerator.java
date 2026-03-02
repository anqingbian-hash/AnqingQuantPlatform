package com.goldjewelry.util;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.Random;

/**
 * 编码生成器
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
public class CodeGenerator {

    /**
     * 生成商品编号
     * 格式：GJ + 年月日 + 4位随机数
     * 示例：GJ20260224001
     */
    public static String generateProductCode() {
        String dateStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMdd"));
        String randomStr = String.format("%04d", new Random().nextInt(10000));
        return "GJ" + dateStr + randomStr;
    }

    /**
     * 生成订单编号
     * 格式：SO + 年月日时分秒 + 4位随机数
     * 示例：SO2026022418300001
     */
    public static String generateOrderNo() {
        String dateStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        String randomStr = String.format("%04d", new Random().nextInt(10000));
        return "SO" + dateStr + randomStr;
    }

    /**
     * 生成调拨编号
     * 格式：TF + 年月日时分秒 + 4位随机数
     * 示例：TF2026022418300001
     */
    public static String generateTransferNo() {
        String dateStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        String randomStr = String.format("%04d", new Random().nextInt(10000));
        return "TF" + dateStr + randomStr;
    }

    /**
     * 生成盘点编号
     * 格式：ST + 年月日时分秒 + 4位随机数
     * 示例：ST2026022418300001
     */
    public static String generateStocktakeNo() {
        String dateStr = LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        String randomStr = String.format("%04d", new Random().nextInt(10000));
        return "ST" + dateStr + randomStr;
    }
}
