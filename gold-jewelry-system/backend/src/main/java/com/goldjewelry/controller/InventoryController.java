package com.goldjewelry.controller;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.Inventory;
import com.goldjewelry.service.InventoryService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 库存控制器
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@RestController
@RequestMapping("/v1/inventory")
@RequiredArgsConstructor
@Tag(name = "库存管理", description = "库存相关接口")
public class InventoryController {

    private final InventoryService inventoryService;

    /**
     * 入库
     */
    @Operation(summary = "入库")
    @PostMapping("/stock-in")
    public ApiResponse<Inventory> stockIn(
            @RequestParam Long productId,
            @RequestParam Long storeId,
            @RequestParam Integer quantity,
            @RequestParam Long operatorId,
            @RequestParam(required = false) String orderNo) {
        log.info("入库请求：商品={}, 店铺={}, 数量={}", productId, storeId, quantity);
        return inventoryService.stockIn(productId, storeId, quantity, operatorId, orderNo);
    }

    /**
     * 出库
     */
    @Operation(summary = "出库")
    @PostMapping("/stock-out")
    public ApiResponse<Inventory> stockOut(
            @RequestParam Long productId,
            @RequestParam Long storeId,
            @RequestParam Integer quantity,
            @RequestParam Long operatorId,
            @RequestParam(required = false) String orderNo) {
        log.info("出库请求：商品={}, 店铺={}, 数量={}", productId, storeId, quantity);
        return inventoryService.stockOut(productId, storeId, quantity, operatorId, orderNo);
    }

    /**
     * 查询库存
     */
    @Operation(summary = "查询库存")
    @GetMapping
    public ApiResponse<Inventory> getInventory(
            @RequestParam Long productId,
            @RequestParam Long storeId) {
        return inventoryService.getInventory(productId, storeId);
    }

    /**
     * 根据店铺查询库存列表
     */
    @Operation(summary = "根据店铺查询库存列表")
    @GetMapping("/store/{storeId}")
    public ApiResponse<List<Inventory>> getInventoryByStore(@PathVariable Long storeId) {
        return inventoryService.getInventoryByStore(storeId);
    }

    /**
     * 查询低库存商品
     */
    @Operation(summary = "查询低库存商品")
    @GetMapping("/low-stock")
    public ApiResponse<List<Inventory>> getLowStock(
            @RequestParam Long storeId,
            @RequestParam(defaultValue = "10") Integer threshold) {
        return inventoryService.getLowStockByStore(storeId, threshold);
    }

    /**
     * 统计店铺库存总数
     */
    @Operation(summary = "统计店铺库存总数")
    @GetMapping("/store/{storeId}/total")
    public ApiResponse<Integer> sumQuantityByStoreId(@PathVariable Long storeId) {
        return inventoryService.sumQuantityByStoreId(storeId);
    }
}
