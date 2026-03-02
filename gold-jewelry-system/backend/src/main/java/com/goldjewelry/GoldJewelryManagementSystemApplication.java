package com.goldjewelry;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 黄金白银贵金属首饰管理系统 - 主启动类
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@SpringBootApplication
@EnableCaching
@EnableAsync
@EnableScheduling
public class GoldJewelryManagementSystemApplication {

    public static void main(String[] args) {
        SpringApplication.run(GoldJewelryManagementSystemApplication.class, args);
        System.out.println("\n========================================");
        System.out.println("黄金白银贵金属首饰管理系统启动成功！");
        System.out.println("访问地址: http://localhost:8080/api");
        System.out.println("========================================\n");
    }
}
