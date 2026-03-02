package com.goldjewelry.repository;

import com.goldjewelry.entity.StocktakeOrder;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 盘点单 Repository
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Repository
public interface StocktakeOrderRepository extends JpaRepository<StocktakeOrder, Long> {

    /**
     * 根据店铺 ID 查询盘点单列表
     */
    List<StocktakeOrder> findByStoreId(Long storeId);

    /**
     * 根据状态查询盘点单
     */
    List<StocktakeOrder> findByStatus(Integer status);

    /**
     * 根据店铺 ID 和状态查询盘点单
     */
    List<StocktakeOrder> findByStoreIdAndStatus(Long storeId, Integer status);
}
