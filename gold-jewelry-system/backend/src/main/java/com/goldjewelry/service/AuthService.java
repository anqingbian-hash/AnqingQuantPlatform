package com.goldjewelry.service;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.User;
import com.goldjewelry.repository.UserRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;

/**
 * 认证服务
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    /**
     * 用户登录
     */
    public ApiResponse<Map<String, Object>> login(String username, String password) {
        log.info("用户登录：{}", username);

        // 查找用户
        Optional<User> optionalUser = userRepository.findByUsernameAndStatus(username);
        if (optionalUser.isEmpty()) {
            return ApiResponse.error("用户名或密码错误");
        }

        User user = optionalUser.get();

        // 验证密码
        if (!passwordEncoder.matches(password, user.getPassword())) {
            return ApiResponse.error("用户名或密码错误");
        }

        // 检查用户状态
        if (user.getStatus() != 1) {
            return ApiResponse.error("账号已被禁用");
        }

        // 生成 token（简化版本，实际应该使用 JWT）
        String token = generateToken(user);

        // 返回用户信息
        Map<String, Object> data = new HashMap<>();
        data.put("token", token);
        data.put("userInfo", user);

        log.info("用户登录成功：{}", username);
        return ApiResponse.success("登录成功", data);
    }

    /**
     * 生成 Token（简化版本）
     */
    private String generateToken(User user) {
        // 实际项目中应该使用 JWT
        // 这里使用简化的 token 生成方式
        return "token_" + user.getId() + "_" + System.currentTimeMillis();
    }
}
