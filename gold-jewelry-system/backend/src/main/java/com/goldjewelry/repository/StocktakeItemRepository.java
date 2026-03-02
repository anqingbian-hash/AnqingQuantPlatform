package com.goldjewelry.repository;

import com.goldjewelry.entity.StocktakeItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 盘点明细 Repository
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Repository
public interface StocktakeItemRepository extends JpaRepository<StocktakeItem, Long> {

    /**
     * 根据盘点单 ID 查询明细列表
     */
    List<StocktakeItem> findByStocktakeId(Long stocktakeId);

    /**
     * 根据盘点单 ID 和商品 ID 查询明细
     */
    List<StocktakeItem> findByStocktakeIdAndProductId(Long stocktakeId, Long productId);
}
