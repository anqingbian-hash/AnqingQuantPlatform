package com.goldjewelry.repository;

import com.goldjewelry.entity.InventoryLog;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDateTime;
import java.util.List;

/**
 * 库存流水 Repository
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Repository
public interface InventoryLogRepository extends JpaRepository<InventoryLog, Long> {

    /**
     * 根据商品 ID 查询流水列表
     */
    List<InventoryLog> findByProductId(Long productId);

    /**
     * 根据店铺 ID 查询流水列表
     */
    List<InventoryLog> findByStoreId(Long storeId);

    /**
     * 根据订单号查询流水
     */
    List<InventoryLog> findByOrderNo(String orderNo);

    /**
     * 根据商品 ID 和店铺 ID 查询流水列表
     */
    List<InventoryLog> findByProductIdAndStoreId(Long productId, Long storeId);

    /**
     * 根据时间范围查询流水列表
     */
    List<InventoryLog> findByCreatedAtBetween(LocalDateTime start, LocalDateTime end);
}
