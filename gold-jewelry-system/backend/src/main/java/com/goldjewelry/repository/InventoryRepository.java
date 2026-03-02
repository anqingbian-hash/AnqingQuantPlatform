package com.goldjewelry.repository;

import com.goldjewelry.entity.Inventory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 库存 Repository
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Repository
public interface InventoryRepository extends JpaRepository<Inventory, Long> {

    /**
     * 根据商品 ID 和店铺 ID 查询库存
     */
    Optional<Inventory> findByProductIdAndStoreId(Long productId, Long storeId);

    /**
     * 根据店铺 ID 查询库存列表
     */
    List<Inventory> findByStoreId(Long storeId);

    /**
     * 根据商品 ID 查询库存列表
     */
    List<Inventory> findByProductId(Long productId);

    /**
     * 根据店铺 ID 查询低库存商品
     */
    @Query("SELECT i FROM Inventory i WHERE i.storeId = :storeId AND i.quantity < :threshold")
    List<Inventory> findLowStockByStoreId(@Param("storeId") Long storeId, @Param("threshold") Integer threshold);

    /**
     * 根据店铺 ID 统计库存总数
     */
    @Query("SELECT SUM(i.quantity) FROM Inventory i WHERE i.storeId = :storeId")
    Integer sumQuantityByStoreId(@Param("storeId") Long storeId);
}
