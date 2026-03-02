package com.goldjewelry.service;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.Product;
import com.goldjewelry.repository.ProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Pageable;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

/**
 * 商品服务
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@Service
@RequiredArgsConstructor
public class ProductService {

    private final ProductRepository productRepository;

    /**
     * 添加商品
     */
    @Transactional
    public ApiResponse<Product> addProduct(Product product) {
        log.info("添加商品：{}", product.getName());

        // 检查商品编号是否已存在
        if (productRepository.existsByProductCode(product.getProductCode())) {
            return ApiResponse.error("商品编号已存在");
        }

        Product savedProduct = productRepository.save(product);
        log.info("商品添加成功：{}", savedProduct.getProductCode());

        return ApiResponse.success("商品添加成功", savedProduct);
    }

    /**
     * 更新商品
     */
    @Transactional
    public ApiResponse<Product> updateProduct(Long id, Product product) {
        log.info("更新商品：{}", id);

        Optional<Product> optionalProduct = productRepository.findById(id);
        if (optionalProduct.isEmpty()) {
            return ApiResponse.error("商品不存在");
        }

        Product existingProduct = optionalProduct.get();

        // 如果商品编号改变，检查新编号是否已存在
        if (!existingProduct.getProductCode().equals(product.getProductCode())) {
            if (productRepository.existsByProductCode(product.getProductCode())) {
                return ApiResponse.error("商品编号已存在");
            }
        }

        // 更新商品信息
        existingProduct.setProductCode(product.getProductCode());
        existingProduct.setName(product.getName());
        existingProduct.setCategoryId(product.getCategoryId());
        existingProduct.setWeight(product.getWeight());
        existingProduct.setPurity(product.getPurity());
        existingProduct.setCraftFee(product.getCraftFee());
        existingProduct.setSupplierId(product.getSupplierId());
        existingProduct.setCertificateNo(product.getCertificateNo());
        existingProduct.setImageUrl(product.getImageUrl());
        existingProduct.setRemark(product.getRemark());
        existingProduct.setStatus(product.getStatus());

        Product savedProduct = productRepository.save(existingProduct);
        log.info("商品更新成功：{}", savedProduct.getProductCode());

        return ApiResponse.success("商品更新成功", savedProduct);
    }

    /**
     * 删除商品（逻辑删除）
     */
    @Transactional
    public ApiResponse<Void> deleteProduct(Long id) {
        log.info("删除商品：{}", id);

        Optional<Product> optionalProduct = productRepository.findById(id);
        if (optionalProduct.isEmpty()) {
            return ApiResponse.error("商品不存在");
        }

        Product product = optionalProduct.get();
        product.setStatus(0); // 逻辑删除
        productRepository.save(product);

        log.info("商品删除成功：{}", product.getProductCode());
        return ApiResponse.success("商品删除成功");
    }

    /**
     * 根据商品编号查询商品
     */
    public ApiResponse<Product> getProductByCode(String productCode) {
        Optional<Product> optionalProduct = productRepository.findByProductCode(productCode);
        if (optionalProduct.isEmpty()) {
            return ApiResponse.error("商品不存在");
        }
        return ApiResponse.success(optionalProduct.get());
    }

    /**
     * 根据分类查询商品列表
     */
    public ApiResponse<List<Product>> getProductsByCategory(Integer categoryId) {
        List<Product> products = productRepository.findByCategoryId(categoryId);
        return ApiResponse.success(products);
    }

    /**
     * 分页查询商品
     */
    public ApiResponse<Page<Product>> getProducts(int page, int size, String keyword) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Page<Product> products;

        if (keyword != null && !keyword.isEmpty()) {
            products = productRepository.searchByKeyword(keyword, pageable);
        } else {
            products = productRepository.findAll(pageable);
        }

        return ApiResponse.success(products);
    }

    /**
     * 查询所有商品
     */
    public ApiResponse<List<Product>> getAllProducts() {
        List<Product> products = productRepository.findByStatus(1);
        return ApiResponse.success(products);
    }
}
