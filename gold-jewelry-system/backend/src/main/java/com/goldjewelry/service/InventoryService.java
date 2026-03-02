package com.goldjewelry.service;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.Inventory;
import com.goldjewelry.entity.InventoryLog;
import com.goldjewelry.repository.InventoryLogRepository;
import com.goldjewelry.repository.InventoryRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

/**
 * 库存服务
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class InventoryService {

    private final InventoryRepository inventoryRepository;
    private final InventoryLogRepository inventoryLogRepository;
    private final GoldPriceService goldPriceService;

    /**
     * 入库
     */
    @Transactional
    public ApiResponse<Inventory> stockIn(Long productId, Long storeId, Integer quantity, Long operatorId, String orderNo) {
        log.info("入库：商品={}, 店铺={}, 数量={}", productId, storeId, quantity);

        // 1. 获取或创建库存记录
        Optional<Inventory> optionalInventory = inventoryRepository.findByProductIdAndStoreId(productId, storeId);
        Inventory inventory;

        if (optionalInventory.isEmpty()) {
            // 创建新库存记录
            inventory = new Inventory();
            inventory.setProductId(productId);
            inventory.setStoreId(storeId);
            inventory.setQuantity(0);
            inventory.setFrozenQuantity(0);
        } else {
            inventory = optionalInventory.get();
        }

        // 2. 更新库存
        int beforeQuantity = inventory.getQuantity();
        inventory.setQuantity(beforeQuantity + quantity);
        Inventory savedInventory = inventoryRepository.save(inventory);

        // 3. 记录库存流水
        InventoryLog log = new InventoryLog();
        log.setProductId(productId);
        log.setStoreId(storeId);
        log.setType(1); // 入库
        log.setQuantity(quantity);
        log.setBeforeQuantity(beforeQuantity);
        log.setAfterQuantity(savedInventory.getQuantity());
        log.setOrderNo(orderNo);
        log.setOperatorId(operatorId);
        inventoryLogRepository.save(log);

        log.info("入库成功：商品={}, 店铺={}, 当前库存={}", productId, storeId, savedInventory.getQuantity());
        return ApiResponse.success("入库成功", savedInventory);
    }

    /**
     * 出库
     */
    @Transactional
    public ApiResponse<Inventory> stockOut(Long productId, Long storeId, Integer quantity, Long operatorId, String orderNo) {
        log.info("出库：商品={}, 店铺={}, 数量={}", productId, storeId, quantity);

        // 1. 获取库存记录
        Optional<Inventory> optionalInventory = inventoryRepository.findByProductIdAndStoreId(productId, storeId);
        if (optionalInventory.isEmpty()) {
            return ApiResponse.error("库存不存在");
        }

        Inventory inventory = optionalInventory.get();

        // 2. 检查库存是否充足
        int currentQuantity = inventory.getQuantity();
        if (currentQuantity < quantity) {
            return ApiResponse.error("库存不足，当前库存：" + currentQuantity);
        }

        // 3. 更新库存
        inventory.setQuantity(currentQuantity - quantity);
        Inventory savedInventory = inventoryRepository.save(inventory);

        // 4. 记录库存流水
        InventoryLog log = new InventoryLog();
        log.setProductId(productId);
        log.setStoreId(storeId);
        log.setType(2); // 出库
        log.setQuantity(-quantity);
        log.setBeforeQuantity(currentQuantity);
        log.setAfterQuantity(savedInventory.getQuantity());
        log.setOrderNo(orderNo);
        log.setOperatorId(operatorId);
        inventoryLogRepository.save(log);

        log.info("出库成功：商品={}, 店铺={}, 当前库存={}", productId, storeId, savedInventory.getQuantity());
        return ApiResponse.success("出库成功", savedInventory);
    }

    /**
     * 根据商品 ID 和店铺 ID 查询库存
     */
    public ApiResponse<Inventory> getInventory(Long productId, Long storeId) {
        Optional<Inventory> optionalInventory = inventoryRepository.findByProductIdAndStoreId(productId, storeId);
        if (optionalInventory.isEmpty()) {
            return ApiResponse.error("库存不存在");
        }
        return ApiResponse.success(optionalInventory.get());
    }

    /**
     * 根据店铺 ID 查询库存列表
     */
    public ApiResponse<List<Inventory>> getInventoryByStore(Long storeId) {
        List<Inventory> inventories = inventoryRepository.findByStoreId(storeId);
        return ApiResponse.success(inventories);
    }

    /**
     * 根据店铺 ID 查询低库存商品
     */
    public ApiResponse<List<Inventory>> getLowStockByStore(Long storeId, Integer threshold) {
        List<Inventory> inventories = inventoryRepository.findLowStockByStoreId(storeId, threshold);
        return ApiResponse.success(inventories);
    }

    /**
     * 根据店铺 ID 统计库存总数
     */
    public ApiResponse<Integer> sumQuantityByStoreId(Long storeId) {
        Integer total = inventoryRepository.sumQuantityByStoreId(storeId);
        return ApiResponse.success(total != null ? total : 0);
    }
}
