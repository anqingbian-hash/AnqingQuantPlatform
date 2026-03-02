package com.goldjewelry.entity;

import jakarta.persistence.*;
import lombok.Data;
import org.hibernate.annotations.Comment;

import java.time.LocalDateTime;

/**
 * 用户实体类
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Data
@Entity
@Table(name = "t_user", indexes = {
    @Index(name = "idx_store_id", columnList = "storeId"),
    @Index(name = "idx_username", columnList = "username")
})
@Comment("用户表")
public class User {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id")
    private Long id;

    @Column(name = "username", nullable = false, unique = true, length = 50)
    @Comment("用户名")
    private String username;

    @Column(name = "password", nullable = false, length = 100)
    @Comment("密码（加密）")
    private String password;

    @Column(name = "real_name", length = 50)
    @Comment("真实姓名")
    private String realName;

    @Column(name = "phone", length = 20)
    @Comment("手机号")
    private String phone;

    @Column(name = "email", length = 100)
    @Comment("邮箱")
    private String email;

    @Column(name = "store_id")
    @Comment("所属店铺 ID")
    private Long storeId;

    @Column(name = "role_id", nullable = false)
    @Comment("角色 ID：1-超级管理员 2-店长 3-店员 4-财务")
    private Integer roleId;

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
