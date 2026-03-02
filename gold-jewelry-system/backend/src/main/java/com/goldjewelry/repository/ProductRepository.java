package com.goldjewelry.repository;

import com.goldjewelry.entity.Product;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 商品 Repository
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Repository
public interface ProductRepository extends JpaRepository<Product, Long> {

    /**
     * 根据商品编号查询商品
     */
    Optional<Product> findByProductCode(String productCode);

    /**
     * 根据分类 ID 查询商品列表
     */
    List<Product> findByCategoryId(Integer categoryId);

    /**
     * 根据状态查询商品列表
     */
    List<Product> findByStatus(Integer status);

    /**
     * 根据供应商 ID 查询商品列表
     */
    List<Product> findBySupplierId(Long supplierId);

    /**
     * 模糊查询商品
     */
    @Query("SELECT p FROM Product p WHERE " +
           "(p.name LIKE %:keyword% OR p.productCode LIKE %:keyword%) " +
           "AND p.status = 1")
    Page<Product> searchByKeyword(@Param("keyword") String keyword, Pageable pageable);

    /**
     * 检查商品编号是否存在
     */
    boolean existsByProductCode(String productCode);
}
