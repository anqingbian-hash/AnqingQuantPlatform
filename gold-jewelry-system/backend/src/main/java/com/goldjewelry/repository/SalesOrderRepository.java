package com.goldjewelry.repository;

import com.goldjewelry.entity.SalesOrder;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 销售订单 Repository
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Repository
public interface SalesOrderRepository extends JpaRepository<SalesOrder, Long> {

    /**
     * 根据订单编号查询订单
     */
    Optional<SalesOrder> findByOrderNo(String orderNo);

    /**
     * 根据店铺 ID 查询订单列表
     */
    List<SalesOrder> findByStoreId(Long storeId);

    /**
     * 根据店铺 ID 分页查询订单
     */
    Page<SalesOrder> findByStoreId(Long storeId, Pageable pageable);

    /**
     * 根据店铺 ID 和状态查询订单
     */
    List<SalesOrder> findByStoreIdAndStatus(Long storeId, Integer status);

    /**
     * 统计店铺销售总额
     */
    Long sumTotalAmountByStoreId(Long storeId);
}
