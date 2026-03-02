package com.goldjewelry.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.Comment;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 销售订单实体类
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Data
@Entity
@Table(name = "t_sales_order", indexes = {
    @Index(name = "idx_order_no", columnList = "orderNo", unique = true),
    @Index(name = "idx_store_id", columnList = "storeId"),
    @Index(name = "idx_created_at", columnList = "createdAt")
})
@Comment("销售订单表")
public class SalesOrder {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "order_no", nullable = false, unique = true, length = 50)
    @Comment("订单编号")
    private String orderNo;

    @Column(name = "store_id", nullable = false)
    @Comment("店铺 ID")
    private Long storeId;

    @Column(name = "customer_name", length = 50)
    @Comment("客户姓名")
    private String customerName;

    @Column(name = "customer_phone", length = 20)
    @Comment("客户电话")
    private String customerPhone;

    @Column(name = "total_amount", nullable = false, precision = 12, scale = 2)
    @Comment("订单总额")
    private BigDecimal totalAmount;

    @Column(name = "payment_method", length = 20)
    @Comment("支付方式：wechat-alipay-cash-card")
    private String paymentMethod;

    @Column(name = "payment_status")
    @Comment("支付状态：0-未支付 1-已支付")
    private Integer paymentStatus = 0;

    @Column(name = "operator_id", nullable = false)
    @Comment("操作人 ID")
    private Long operatorId;

    @Column(name = "status")
    @Comment("订单状态：0-待支付 1-已完成 2-已取消")
    private Integer status = 0;

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
