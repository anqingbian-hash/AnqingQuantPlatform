package com.goldjewelry.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.Comment;

import java.time.LocalDateTime;

/**
 * 库存流水实体类
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Data
@Entity
@Table(name = "t_inventory_log", indexes = {
    @Index(name = "idx_product_id", columnList = "productId"),
    @Index(name = "idx_store_id", columnList = "storeId"),
    @Index(name = "idx_created_at", columnList = "createdAt"),
    @Index(name = "idx_order_no", columnList = "orderNo")
})
@Comment("库存流水表")
public class InventoryLog {

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

    @Column(name = "type", nullable = false)
    @Comment("类型：1-入库 2-出库 3-调拨 4-盘点 5-报损")
    private Integer type;

    @Column(name = "quantity", nullable = false)
    @Comment("变动数量（正数入库，负数出库）")
    private Integer quantity;

    @Column(name = "before_quantity", nullable = false)
    @Comment("变动前数量")
    private Integer beforeQuantity;

    @Column(name = "after_quantity", nullable = false)
    @Comment("变动后数量")
    private Integer afterQuantity;

    @Column(name = "order_no", length = 50)
    @Comment("关联订单号")
    private String orderNo;

    @Column(name = "operator_id", nullable = false)
    @Comment("操作人 ID")
    private Long operatorId;

    @Column(name = "remark", columnDefinition = "TEXT")
    @Comment("备注")
    private String remark;

    @Column(name = "created_at", nullable = false, updatable = false)
    @Comment("创建时间")
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
