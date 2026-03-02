package com.goldjewelry.controller;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.SalesOrder;
import com.goldjewelry.service.SalesService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 销售控制器
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@RestController
@RequestMapping("/v1/sales")
@RequiredArgsConstructor
@Tag(name = "销售管理", description = "销售相关接口")
public class SalesController {

    private final SalesService salesService;

    /**
     * 创建销售订单
     */
    @Operation(summary = "创建销售订单")
    @PostMapping
    public ApiResponse<SalesOrder> createOrder(@RequestBody SalesOrder order) {
        log.info("创建销售订单：{}", order.getOrderNo());
        return salesService.createOrder(order);
    }

    /**
     * 取消订单
     */
    @Operation(summary = "取消订单")
    @PostMapping("/{id}/cancel")
    public ApiResponse<Void> cancelOrder(@PathVariable Long id) {
        log.info("取消订单：{}", id);
        return salesService.cancelOrder(id);
    }

    /**
     * 根据订单编号查询订单
     */
    @Operation(summary = "根据订单编号查询订单")
    @GetMapping("/order-no/{orderNo}")
    public ApiResponse<SalesOrder> getOrderByNo(@PathVariable String orderNo) {
        return salesService.getOrderByNo(orderNo);
    }

    /**
     * 根据店铺 ID 查询订单列表
     */
    @Operation(summary = "根据店铺 ID 查询订单列表")
    @GetMapping("/store/{storeId}")
    public ApiResponse<List<SalesOrder>> getOrdersByStore(@PathVariable Long storeId) {
        return salesService.getOrdersByStore(storeId);
    }

    /**
     * 分页查询订单
     */
    @Operation(summary = "分页查询订单")
    @GetMapping
    public ApiResponse<Page<SalesOrder>> getOrders(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {
        return salesService.getOrders(page, size);
    }
}
