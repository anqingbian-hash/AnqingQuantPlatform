package com.goldjewelry.service;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.Store;
import com.goldjewelry.repository.StoreRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.Optional;

/**
 * 店铺服务
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class StoreService {

    private final StoreRepository storeRepository;

    /**
     * 添加店铺
     */
    public ApiResponse<Store> addStore(Store store) {
        log.info("添加店铺：{}", store.getName());

        Store savedStore = storeRepository.save(store);
        log.info("店铺添加成功：{}", savedStore.getName());

        return ApiResponse.success("店铺添加成功", savedStore);
    }

    /**
     * 更新店铺
     */
    public ApiResponse<Store> updateStore(Long id, Store store) {
        log.info("更新店铺：{}", id);

        Optional<Store> optionalStore = storeRepository.findById(id);
        if (optionalStore.isEmpty()) {
            return ApiResponse.error("店铺不存在");
        }

        Store existingStore = optionalStore.get();
        existingStore.setName(store.getName());
        existingStore.setAddress(store.getAddress());
        existingStore.setPhone(store.getPhone());
        existingStore.setStatus(store.getStatus());

        Store savedStore = storeRepository.save(existingStore);
        log.info("店铺更新成功：{}", savedStore.getName());

        return ApiResponse.success("店铺更新成功", savedStore);
    }

    /**
     * 删除店铺（逻辑删除）
     */
    public ApiResponse<Void> deleteStore(Long id) {
        log.info("删除店铺：{}", id);

        Optional<Store> optionalStore = storeRepository.findById(id);
        if (optionalStore.isEmpty()) {
            return ApiResponse.error("店铺不存在");
        }

        Store store = optionalStore.get();
        store.setStatus(0); // 逻辑删除
        storeRepository.save(store);

        log.info("店铺删除成功：{}", store.getName());
        return ApiResponse.success("店铺删除成功");
    }

    /**
     * 根据店铺 ID 查询店铺
     */
    public ApiResponse<Store> getStoreById(Long id) {
        Optional<Store> optionalStore = storeRepository.findById(id);
        if (optionalStore.isEmpty()) {
            return ApiResponse.error("店铺不存在");
        }
        return ApiResponse.success(optionalStore.get());
    }

    /**
     * 查询所有店铺
     */
    public ApiResponse<List<Store>> getAllStores() {
        List<Store> stores = storeRepository.findAll();
        return ApiResponse.success(stores);
    }

    /**
     * 根据状态查询店铺
     */
    public ApiResponse<List<Store>> getStoresByStatus(Integer status) {
        List<Store> stores = storeRepository.findByStatus(status);
        return ApiResponse.success(stores);
    }
}
