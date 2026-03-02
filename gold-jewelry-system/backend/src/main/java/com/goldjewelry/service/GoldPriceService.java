package com.goldjewelry.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;

/**
 * 金价服务
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@Service
public class GoldPriceService {

    @Value("${gold-price.enabled:true}")
    private boolean enabled;

    private final RestTemplate restTemplate = new RestTemplate();

    /**
     * 获取实时金价（上海黄金交易所）
     * 缓存 1 小时
     */
    @Cacheable(value = "goldPrice", key = "'current'", unless = "#result == null")
    public BigDecimal getGoldPrice() {
        if (!enabled) {
            log.info("金价接口未启用，返回默认价格");
            return new BigDecimal("550.00"); // 默认金价：550 元/克
        }

        try {
            // TODO: 实际对接上海黄金交易所 API
            // 这里使用模拟数据
            BigDecimal price = fetchGoldPriceFromSource();
            log.info("获取实时金价：{} 元/克", price);
            return price;
        } catch (Exception e) {
            log.error("获取金价失败，使用默认价格", e);
            return new BigDecimal("550.00"); // 默认金价
        }
    }

    /**
     * 根据商品信息计算售价
     * 售价 = (金价 × 金重 × 成色 / 100) + 工费
     */
    public BigDecimal calculatePrice(BigDecimal goldPrice, BigDecimal weight, String purity, BigDecimal craftFee) {
        // 成色转换为小数
        BigDecimal purityValue = convertPurityToValue(purity);

        // 计算材料费
        BigDecimal materialPrice = goldPrice.multiply(weight).multiply(purityValue);

        // 计算总价
        BigDecimal totalPrice = materialPrice.add(craftFee);

        log.debug("计算售价：金价={}, 金重={}, 成色={}, 工费={}, 售价={}",
                goldPrice, weight, purity, craftFee, totalPrice);

        return totalPrice;
    }

    /**
     * 从数据源获取金价
     */
    private BigDecimal fetchGoldPriceFromSource() {
        // 模拟 API 调用
        // 实际项目中需要对接上海黄金交易所或其他金价数据源

        // 模拟返回金价：550-560 之间随机
        double randomPrice = 550 + Math.random() * 10;
        return new BigDecimal(String.format("%.2f", randomPrice));
    }

    /**
     * 成色转换为小数
     */
    private BigDecimal convertPurityToValue(String purity) {
        Map<String, BigDecimal> purityMap = new HashMap<>();
        purityMap.put("Au99.99", new BigDecimal("0.9999"));
        purityMap.put("Au99.95", new BigDecimal("0.9995"));
        purityMap.put("Au99.5", new BigDecimal("0.995"));
        purityMap.put("Au99", new BigDecimal("0.99"));
        purityMap.put("Au91.6", new BigDecimal("0.916"));
        purityMap.put("Au75", new BigDecimal("0.75"));

        return purityMap.getOrDefault(purity, new BigDecimal("0.9999"));
    }
}
