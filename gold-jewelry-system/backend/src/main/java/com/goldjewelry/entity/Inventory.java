package com.goldjewelry.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.Comment;

import java.time.LocalDateTime;

/**
 * 库存实体类
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Data
@Entity
@Table(name = "t_inventory",
       uniqueConstraints = {
           @UniqueConstraint(name = "uk_product_store", columnNames = {"product_id", "store_id"})
       },
       indexes = {
           @Index(name = "idx_store_id", columnList = "storeId"),
           @Index(name = "idx_quantity", columnList = "quantity")
       })
@Comment("库存表")
public class Inventory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "product_id", nullable = false)
    @Comment("商品 ID")
    private Long productId;

    @Column(name = "store_id", nullable = false)
    @Comment("店铺 ID")
    private Long storeId;

    @Column(name = "quantity", nullable = false)
    @Comment("库存数量")
    private Integer quantity = 0;

    @Column(name = "frozen_quantity", nullable = false)
    @Comment("冻结数量（调拨中）")
    private Integer frozenQuantity = 0;

    @Column(name = "status")
    @Comment("状态：0-禁用 1-启用")
    private Integer status = 1;

    @Column(name = "created_at", nullable = false, updatable = false)
    @Comment("创建时间")
    private LocalDateTime createdAt;

    @Column(name = "updated_at")
    @Comment("更新时间")
    private LocalDateTime updatedAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
        updatedAt = LocalDateTime.now();
    }

    @PreUpdate
    protected void onUpdate() {
        updatedAt = LocalDateTime.now();
    }
}
