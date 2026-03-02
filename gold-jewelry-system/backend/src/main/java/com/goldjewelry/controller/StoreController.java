package com.goldjewelry.controller;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.Store;
import com.goldjewelry.service.StoreService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 店铺控制器
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@RestController
@RequestMapping("/v1/stores")
@RequiredArgsConstructor
@Tag(name = "店铺管理", description = "店铺相关接口")
public class StoreController {

    private final StoreService storeService;

    /**
     * 添加店铺
     */
    @Operation(summary = "添加店铺")
    @PostMapping
    public ApiResponse<Store> addStore(@RequestBody Store store) {
        log.info("添加店铺：{}", store.getName());
        return storeService.addStore(store);
    }

    /**
     * 更新店铺
     */
    @Operation(summary = "更新店铺")
    @PutMapping("/{id}")
    public ApiResponse<Store> updateStore(@PathVariable Long id, @RequestBody Store store) {
        log.info("更新店铺：{}", id);
        return storeService.updateStore(id, store);
    }

    /**
     * 删除店铺
     */
    @Operation(summary = "删除店铺")
    @DeleteMapping("/{id}")
    public ApiResponse<Void> deleteStore(@PathVariable Long id) {
        log.info("删除店铺：{}", id);
        return storeService.deleteStore(id);
    }

    /**
     * 根据店铺 ID 查询店铺
     */
    @Operation(summary = "根据店铺 ID 查询店铺")
    @GetMapping("/{id}")
    public ApiResponse<Store> getStoreById(@PathVariable Long id) {
        return storeService.getStoreById(id);
    }

    /**
     * 查询所有店铺
     */
    @Operation(summary = "查询所有店铺")
    @GetMapping
    public ApiResponse<List<Store>> getAllStores() {
        return storeService.getAllStores();
    }

    /**
     * 根据状态查询店铺
     */
    @Operation(summary = "根据状态查询店铺")
    @GetMapping("/status/{status}")
    public ApiResponse<List<Store>> getStoresByStatus(@PathVariable Integer status) {
        return storeService.getStoresByStatus(status);
    }
}
