package com.goldjewelry.service;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.Inventory;
import com.goldjewelry.repository.InventoryRepository;
import com.goldjewelry.util.CodeGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;

/**
 * 调拨服务
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class TransferService {

    private final InventoryRepository inventoryRepository;

    /**
     * 创建调拨单
     */
    @Transactional
    public ApiResponse<String> createTransferOrder(Long productId, Long fromStoreId, Long toStoreId, Integer quantity, Long operatorId) {
        log.info("创建调拨单：商品={}, 从={}, 到={}, 数量={}", productId, fromStoreId, toStoreId, quantity);

        // 1. 调出店铺库存检查
        Optional<Inventory> optionalFromInventory = inventoryRepository.findByProductIdAndStoreId(productId, fromStoreId);
        if (optionalFromInventory.isEmpty()) {
            return ApiResponse.error("调出店铺库存不存在");
        }

        Inventory fromInventory = optionalFromInventory.get();
        if (fromInventory.getQuantity() < quantity) {
            return ApiResponse.error("库存不足，当前库存：" + fromInventory.getQuantity());
        }

        // 2. 冻结调出店铺库存
        int beforeFrozen = fromInventory.getFrozenQuantity();
        fromInventory.setFrozenQuantity(beforeFrozen + quantity);
        inventoryRepository.save(fromInventory);

        // 3. 生成调拨编号
        String transferNo = CodeGenerator.generateTransferNo();

        log.info("调拨单创建成功：{}", transferNo);
        return ApiResponse.success("调拨单创建成功", transferNo);
    }

    /**
     * 确认调拨（调出店铺出库）
     */
    @Transactional
    public ApiResponse<Void> confirmTransfer(String transferNo, Long productId, Long fromStoreId, Long toStoreId, Integer quantity, Long operatorId) {
        log.info("确认调拨：{}", transferNo);

        // 1. 调出店铺库存
        Optional<Inventory> optionalFromInventory = inventoryRepository.findByProductIdAndStoreId(productId, fromStoreId);
        if (optionalFromInventory.isEmpty()) {
            return ApiResponse.error("调出店铺库存不存在");
        }

        Inventory fromInventory = optionalFromInventory.get();

        // 2. 扣减冻结数量
        int beforeFrozen = fromInventory.getFrozenQuantity();
        if (beforeFrozen < quantity) {
            return ApiResponse.error("冻结数量不足");
        }

        fromInventory.setFrozenQuantity(beforeFrozen - quantity);

        // 3. 扣减库存
        int beforeQuantity = fromInventory.getQuantity();
        fromInventory.setQuantity(beforeQuantity - quantity);

        inventoryRepository.save(fromInventory);

        log.info("调拨确认成功：{}", transferNo);
        return ApiResponse.success("调拨确认成功");
    }

    /**
     * 接收调拨（调入店铺入库）
     */
    @Transactional
    public ApiResponse<Void> receiveTransfer(String transferNo, Long productId, Long toStoreId, Integer quantity, Long operatorId) {
        log.info("接收调拨：{}", transferNo);

        // 1. 获取或创建调入店铺库存
        Optional<Inventory> optionalToInventory = inventoryRepository.findByProductIdAndStoreId(productId, toStoreId);
        Inventory toInventory;

        if (optionalToInventory.isEmpty()) {
            toInventory = new Inventory();
            toInventory.setProductId(productId);
            toInventory.setStoreId(toStoreId);
            toInventory.setQuantity(0);
            toInventory.setFrozenQuantity(0);
        } else {
            toInventory = optionalToInventory.get();
        }

        // 2. 增加库存
        int beforeQuantity = toInventory.getQuantity();
        toInventory.setQuantity(beforeQuantity + quantity);

        inventoryRepository.save(toInventory);

        log.info("调拨接收成功：{}", transferNo);
        return ApiResponse.success("调拨接收成功");
    }
}
