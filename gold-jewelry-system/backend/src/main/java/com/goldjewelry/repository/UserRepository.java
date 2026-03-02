package com.goldjewelry.repository;

import com.goldjewelry.entity.User;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * 用户 Repository
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Repository
public interface UserRepository extends JpaRepository<User, Long> {

    /**
     * 根据用户名查询用户
     */
    Optional<User> findByUsername(String username);

    /**
     * 根据店铺 ID 查询用户列表
     */
    List<User> findByStoreId(Long storeId);

    /**
     * 根据角色 ID 查询用户列表
     */
    List<User> findByRoleId(Integer roleId);

    /**
     * 根据状态查询用户列表
     */
    List<User> findByStatus(Integer status);

    /**
     * 根据用户名和状态查询用户
     */
    @Query("SELECT u FROM User u WHERE u.username = :username AND u.status = 1")
    Optional<User> findByUsernameAndStatus(@Param("username") String username);

    /**
     * 检查用户名是否存在
     */
    boolean existsByUsername(String username);
}
