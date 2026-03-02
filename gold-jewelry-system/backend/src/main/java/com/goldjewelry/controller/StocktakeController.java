package com.goldjewelry.controller;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.StocktakeOrder;
import com.goldjewelry.service.StocktakeService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 盘点控制器
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@RestController
@RequestMapping("/v1/stocktakes")
@RequiredArgsConstructor
@Tag(name = "盘点管理", description = "盘点相关接口")
public class StocktakeController {

    private final StocktakeService stocktakeService;

    /**
     * 创建盘点单
     */
    @Operation(summary = "创建盘点单")
    @PostMapping
    public ApiResponse<StocktakeOrder> createStocktakeOrder(
            @RequestParam Long storeId,
            @RequestParam(defaultValue = "1") Integer type,
            @RequestParam Long operatorId) {
        log.info("创建盘点单：店铺={}, 类型={}", storeId, type);
        return stocktakeService.createStocktakeOrder(storeId, type, operatorId);
    }

    /**
     * 添加盘点明细
     */
    @Operation(summary = "添加盘点明细")
    @PostMapping("/items")
    public ApiResponse<StocktakeItem> addStocktakeItem(
            @RequestParam Long stocktakeId,
            @RequestParam Long productId,
            @RequestParam Integer actualQuantity,
            @RequestParam Long operatorId) {
        log.info("添加盘点明细：盘点单={}, 商品={}, 实际={}", stocktakeId, productId, actualQuantity);
        return stocktakeService.addStocktakeItem(stocktakeId, productId, actualQuantity, operatorId);
    }

    /**
     * 完成盘点
     */
    @Operation(summary = "完成盘点")
    @PostMapping("/{id}/complete")
    public ApiResponse<StocktakeOrder> completeStocktake(
            @PathVariable Long id,
            @RequestParam Long operatorId) {
        log.info("完成盘点：{}", id);
        return stocktakeService.completeStocktake(id, operatorId);
    }

    /**
     * 审核盘点单
     */
    @Operation(summary = "审核盘点单")
    @PostMapping("/{id}/review")
    public ApiResponse<Void> reviewStocktake(
            @PathVariable Long id,
            @RequestParam Boolean approved,
            @RequestParam Long operatorId) {
        log.info("审核盘点单：{}, 审核结果={}", id, approved);
        return stocktakeService.reviewStocktake(id, approved, operatorId);
    }

    /**
     * 根据店铺 ID 查询盘点单列表
     */
    @Operation(summary = "根据店铺 ID 查询盘点单列表")
    @GetMapping("/store/{storeId}")
    public ApiResponse<List<StocktakeOrder>> getStocktakesByStore(@PathVariable Long storeId) {
        return ApiResponse.success(stocktakeService.getStocktakeOrderByStoreId(storeId));
    }

    /**
     * 根据盘点单 ID 查询明细列表
     */
    @Operation(summary = "根据盘点单 ID 查询明细列表")
    @GetMapping("/{id}/items")
    public ApiResponse<List<StocktakeItem>> getStocktakeItems(@PathVariable Long id) {
        return ApiResponse.success(stocktakeService.getStocktakeItemsByStocktakeId(id));
    }
}
