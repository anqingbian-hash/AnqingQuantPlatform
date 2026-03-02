package com.goldjewelry.service;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.SalesOrder;
import com.goldjewelry.repository.SalesOrderRepository;
import com.goldjewelry.util.CodeGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDateTime;
import java.util.List;

/**
 * 销售服务
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class SalesService {

    private final SalesOrderRepository salesOrderRepository;

    /**
     * 创建销售订单
     */
    @Transactional
    public ApiResponse<SalesOrder> createOrder(SalesOrder order) {
        log.info("创建销售订单：{}", order.getOrderNo());

        // 生成订单编号
        if (order.getOrderNo() == null || order.getOrderNo().isEmpty()) {
            order.setOrderNo(CodeGenerator.generateOrderNo());
        }

        // 设置默认状态
        if (order.getStatus() == null) {
            order.setStatus(0); // 待支付
        }

        if (order.getPaymentStatus() == null) {
            order.setPaymentStatus(0); // 未支付
        }

        SalesOrder savedOrder = salesOrderRepository.save(order);
        log.info("销售订单创建成功：{}", savedOrder.getOrderNo());

        return ApiResponse.success("开单成功", savedOrder);
    }

    /**
     * 取消订单
     */
    @Transactional
    public ApiResponse<Void> cancelOrder(Long orderId) {
        log.info("取消订单：{}", orderId);

        SalesOrder order = salesOrderRepository.findById(orderId).orElse(null);
        if (order == null) {
            return ApiResponse.error("订单不存在");
        }

        if (order.getStatus() == 1) {
            return ApiResponse.error("订单已完成，无法取消");
        }

        order.setStatus(2); // 已取消
        salesOrderRepository.save(order);

        log.info("订单取消成功：{}", order.getOrderNo());
        return ApiResponse.success("取消成功");
    }

    /**
     * 根据订单编号查询订单
     */
    public ApiResponse<SalesOrder> getOrderByNo(String orderNo) {
        SalesOrder order = salesOrderRepository.findByOrderNo(orderNo).orElse(null);
        if (order == null) {
            return ApiResponse.error("订单不存在");
        }
        return ApiResponse.success(order);
    }

    /**
     * 根据店铺 ID 查询订单列表
     */
    public ApiResponse<List<SalesOrder>> getOrdersByStore(Long storeId) {
        List<SalesOrder> orders = salesOrderRepository.findByStoreId(storeId);
        return ApiResponse.success(orders);
    }

    /**
     * 分页查询订单
     */
    public ApiResponse<Page<SalesOrder>> getOrders(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Page<SalesOrder> orders = salesOrderRepository.findAll(pageable);
        return ApiResponse.success(orders);
    }
}
