package com.goldjewelry.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.Comment;

import java.math.BigDecimal;
import java.time.LocalDateTime;

/**
 * 商品实体类
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Data
@Entity
@Table(name = "t_product", indexes = {
    @Index(name = "idx_product_code", columnList = "productCode", unique = true),
    @Index(name = "idx_category_id", columnList = "categoryId"),
    @Index(name = "idx_supplier_id", columnList = "supplierId")
})
@Comment("商品表")
public class Product {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "product_code", nullable = false, unique = true, length = 50)
    @Comment("商品编号")
    private String productCode;

    @Column(name = "name", nullable = false, length = 100)
    @Comment("商品名称")
    private String name;

    @Column(name = "category_id", nullable = false)
    @Comment("商品分类 ID")
    private Integer categoryId;

    @Column(name = "weight", nullable = false, precision = 10, scale = 2)
    @Comment("金重（克）")
    private BigDecimal weight;

    @Column(name = "purity", nullable = false, length = 20)
    @Comment("成色：Au99.99/Au99.95/Au99.5/Au99/Au91.6/Au75")
    private String purity;

    @Column(name = "craft_fee", nullable = false, precision = 10, scale = 2)
    @Comment("工费（元）")
    private BigDecimal craftFee;

    @Column(name = "supplier_id")
    @Comment("供应商 ID")
    private Long supplierId;

    @Column(name = "certificate_no", length = 100)
    @Comment("证书编号")
    private String certificateNo;

    @Column(name = "image_url", length = 500)
    @Comment("图片 URL")
    private String imageUrl;

    @Column(name = "remark", columnDefinition = "TEXT")
    @Comment("备注")
    private String remark;

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
