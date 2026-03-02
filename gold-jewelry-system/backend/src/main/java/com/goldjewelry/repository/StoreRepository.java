package com.goldjewelry.repository;

import com.goldjewelry.entity.Store;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * 店铺 Repository
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Repository
public interface StoreRepository extends JpaRepository<Store, Long> {

    /**
     * 根据名称查询店铺
     */
    Store findByName(String name);

    /**
     * 根据状态查询店铺列表
     */
    List<Store> findByStatus(Integer status);

    /**
     * 检查名称是否存在
     */
    boolean existsByName(String name);
}
