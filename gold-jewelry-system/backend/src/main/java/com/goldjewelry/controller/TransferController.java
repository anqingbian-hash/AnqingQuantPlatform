package com.goldjewelry.controller;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.service.TransferService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

/**
 * 调拨控制器
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@RestController
@RequestMapping("/v1/transfers")
@RequiredArgsConstructor
@Tag(name = "调拨管理", description = "调拨相关接口")
public class TransferController {

    private final TransferService transferService;

    /**
     * 创建调拨单
     */
    @Operation(summary = "创建调拨单")
    @PostMapping
    public ApiResponse<String> createTransferOrder(
            @RequestParam Long productId,
            @RequestParam Long fromStoreId,
            @RequestParam Long toStoreId,
            @RequestParam Integer quantity,
            @RequestParam Long operatorId) {
        log.info("创建调拨单：from={} to={}", fromStoreId, toStoreId);
        return transferService.createTransferOrder(productId, fromStoreId, toStoreId, quantity, operatorId);
    }

    /**
     * 确认调拨
     */
    @Operation(summary = "确认调拨")
    @PostMapping("/{transferNo}/confirm")
    public ApiResponse<Void> confirmTransfer(
            @PathVariable String transferNo,
            @RequestParam Long productId,
            @RequestParam Long fromStoreId,
            @RequestParam Long toStoreId,
            @RequestParam Integer quantity,
            @RequestParam Long operatorId) {
        log.info("确认调拨：{}", transferNo);
        return transferService.confirmTransfer(transferNo, productId, fromStoreId, toStoreId, quantity, operatorId);
    }

    /**
     * 接收调拨
     */
    @Operation(summary = "接收调拨")
    @PostMapping("/{transferNo}/receive")
    public ApiResponse<Void> receiveTransfer(
            @PathVariable String transferNo,
            @RequestParam Long productId,
            @RequestParam Long toStoreId,
            @RequestParam Integer quantity,
            @RequestParam Long operatorId) {
        log.info("接收调拨：{}", transferNo);
        return transferService.receiveTransfer(transferNo, productId, toStoreId, quantity, operatorId);
    }
}
