package com.goldjewelry.service;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.Inventory;
import com.goldjewelry.entity.StocktakeItem;
import com.goldjewelry.entity.StocktakeOrder;
import com.goldjewelry.repository.InventoryRepository;
import com.goldjewelry.repository.StocktakeItemRepository;
import com.goldjewelry.repository.StocktakeOrderRepository;
import com.goldjewelry.util.CodeGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

/**
 * 盘点服务
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class StocktakeService {

    private final StocktakeOrderRepository stocktakeOrderRepository;
    private final StocktakeItemRepository stocktakeItemRepository;
    private final InventoryRepository inventoryRepository;

    /**
     * 创建盘点单
     */
    @Transactional
    public ApiResponse<StocktakeOrder> createStocktakeOrder(Long storeId, Integer type, Long operatorId) {
        log.info("创建盘点单：店铺={}, 类型={}", storeId, type);

        StocktakeOrder order = new StocktakeOrder();
        order.setStocktakeNo(CodeGenerator.generateStocktakeNo());
        order.setStoreId(storeId);
        order.setType(type);
        order.setStatus(0); // 盘点中
        order.setOperatorId(operatorId);

        StocktakeOrder savedOrder = stocktakeOrderRepository.save(order);
        log.info("盘点单创建成功：{}", savedOrder.getStocktakeNo());

        return ApiResponse.success("盘点单创建成功", savedOrder);
    }

    /**
     * 添加盘点明细
     */
    @Transactional
    public ApiResponse<StocktakeItem> addStocktakeItem(Long stocktakeId, Long productId, Integer actualQuantity, Long operatorId) {
        log.info("添加盘点明细：盘点单={}, 商品={}, 实际数量={}", stocktakeId, productId, actualQuantity);

        // 获取盘点单
        Optional<StocktakeOrder> optionalOrder = stocktakeOrderRepository.findById(stocktakeId);
        if (optionalOrder.isEmpty()) {
            return ApiResponse.error("盘点单不存在");
        }

        StocktakeOrder order = optionalOrder.get();

        // 获取账面库存
        Optional<Inventory> optionalInventory = inventoryRepository.findByProductIdAndStoreId(productId, order.getStoreId());
        if (optionalInventory.isEmpty()) {
            return ApiResponse.error("库存不存在");
        }

        Inventory inventory = optionalInventory.get();

        // 创建盘点明细
        StocktakeItem item = new StocktakeItem();
        item.setStocktakeId(stocktakeId);
        item.setProductId(productId);
        item.setBookQuantity(inventory.getQuantity());
        item.setActualQuantity(actualQuantity);
        item.setDiffQuantity(actualQuantity - inventory.getQuantity());
        item.setStatus(item.getDiffQuantity() == 0 ? 0 : 1); // 0-正常 1-异常

        StocktakeItem savedItem = stocktakeItemRepository.save(item);
        log.info("盘点明细添加成功");

        return ApiResponse.success("盘点明细添加成功", savedItem);
    }

    /**
     * 完成盘点
     */
    @Transactional
    public ApiResponse<StocktakeOrder> completeStocktake(Long stocktakeId, Long operatorId) {
        log.info("完成盘点：{}", stocktakeId);

        // 获取盘点单
        Optional<StocktakeOrder> optionalOrder = stocktakeOrderRepository.findById(stocktaketakeId);
        if (optionalOrder.isEmpty()) {
            return ApiResponse.error("盘点单不存在");
        }

        StocktakeOrder order = optionalOrder.get();

        // 获取所有盘点明细
        List<StocktakeItem> items = stocktakeItemRepository.findByStocktakeId(stocktakeId);

        // 统计
        int totalCount = items.size();
        int diffCount = 0;

        for (StocktakeItem item : items) {
            if (item.getStatus() == 1) {
                diffCount++;
            }
        }

        // 更新盘点单
        order.setTotalCount(totalCount);
        order.setDiffCount(diffCount);
        order.setStatus(2); // 已完成
        order.setReviewOperatorId(operatorId);

        StocktakeOrder savedOrder = stocktakeOrderRepository.save(order);
        log.info("盘点完成：总数={}, 差异={}", totalCount, diffCount);

        return ApiResponse.success("盘点完成", savedOrder);
    }

    /**
     * 审核盘点单
     */
    @Transactional
    public ApiResponse<Void> reviewStocktake(Long stocktakeId, boolean approved, Long operatorId) {
        log.info("审核盘点单：{}, 审核结果={}", stocktakeId, approved);

        // 获取盘点单
        Optional<StocktakeOrder> optionalOrder = stocktakeOrderRepository.findById(stocktakeId);
        if (optionalOrder.isEmpty()) {
            return ApiResponse.error("盘点单不存在");
        }

        StocktakeOrder order = optionalOrder.get();

        if (approved) {
            // 审核通过，更新库存
            List<StocktakeItem> items = stocktakeItemRepository.findByStocktakeId(stocktakeId);
            for (StocktakeItem item : items) {
                Optional<Inventory> optionalInventory = inventoryRepository.findByProductIdAndStoreId(item.getProductId(), order.getStoreId());
                if (optionalInventory.isPresent()) {
                    Inventory inventory = optionalInventory.get();
                    inventory.setQuantity(item.getActualQuantity());
                    inventoryRepository.save(inventory);
                }
            }
        }

        // 更新盘点单状态
        order.setStatus(approved ? 3 : 4); // 3-已完成 4-已取消

        StocktakeOrder savedOrder = stocktakeOrderRepository.save(order);
        log.info("盘点单审核完成：{}", approved ? "通过" : "拒绝");

        return ApiResponse.success(approved ? "审核通过" : "审核拒绝");
    }
}
