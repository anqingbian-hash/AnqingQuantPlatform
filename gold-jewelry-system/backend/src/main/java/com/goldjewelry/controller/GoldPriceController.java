package com.goldjewelry.controller;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.service.GoldPriceService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.math.BigDecimal;

/**
 * 金价控制器
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@RestController
@RequestMapping("/v1/prices")
@RequiredArgsConstructor
@Tag(name = "价格管理", description = "价格相关接口")
public class GoldPriceController {

    private final GoldPriceService goldPriceService;

    /**
     * 获取实时金价
     */
    @Operation(summary = "获取实时金价")
    @GetMapping("/gold-price")
    public ApiResponse<BigDecimal> getGoldPrice() {
        BigDecimal price = goldPriceService.getGoldPrice();
        log.info("获取实时金价：{} 元/克", price);
        return ApiResponse.success(price);
    }

    /**
     * 计算商品售价
     */
    @Operation(summary = "计算商品售价")
    @PostMapping("/calculate")
    public ApiResponse<BigDecimal> calculatePrice(
            @RequestParam BigDecimal goldPrice,
            @RequestParam BigDecimal weight,
            @RequestParam String purity,
            @RequestParam BigDecimal craftFee) {
        BigDecimal price = goldPriceService.calculatePrice(goldPrice, weight, purity, craftFee);
        log.info("计算售价：金价={}, 金重={}, 成色={}, 工费={}, 售价={}",
                goldPrice, weight, purity, craftFee, price);
        return ApiResponse.success(price);
    }
}
