package com.goldjewelry.controller;

import com.goldjewelry.dto.ApiResponse;
import com.goldjewelry.entity.Product;
import com.goldjewelry.service.ProductService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.data.domain.Page;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * 商品控制器
 *
 * @author Company Engine Enterprise
 * @version 1.0.0
 * @since 2026-02-24
 */
@Slf4j
@RestController
@RequestMapping("/v1/products")
@RequiredArgsConstructor
@Tag(name = "商品管理", description = "商品相关接口")
public class ProductController {

    private final ProductService productService;

    /**
     * 添加商品
     */
    @Operation(summary = "添加商品")
    @PostMapping
    public ApiResponse<Product> addProduct(@RequestBody Product product) {
        log.info("添加商品：{}", product.getName());
        return productService.addProduct(product);
    }

    /**
     * 更新商品
     */
    @Operation(summary = "更新商品")
    @PutMapping("/{id}")
    public ApiResponse<Product> updateProduct(@PathVariable Long id, @RequestBody Product product) {
        log.info("更新商品：{}", id);
        return productService.updateProduct(id, product);
    }

    /**
     * 删除商品
     */
    @Operation(summary = "删除商品")
    @DeleteMapping("/{id}")
    public ApiResponse<Void> deleteProduct(@PathVariable Long id) {
        log.info("删除商品：{}", id);
        return productService.deleteProduct(id);
    }

    /**
     * 根据商品编号查询商品
     */
    @Operation(summary = "根据商品编号查询商品")
    @GetMapping("/code/{productCode}")
    public ApiResponse<Product> getProductByCode(@PathVariable String productCode) {
        return productService.getProductByCode(productCode);
    }

    /**
     * 根据分类查询商品列表
     */
    @Operation(summary = "根据分类查询商品列表")
    @GetMapping("/category/{categoryId}")
    public ApiResponse<List<Product>> getProductsByCategory(@PathVariable Integer categoryId) {
        return productService.getProductsByCategory(categoryId);
    }

    /**
     * 分页查询商品
     */
    @Operation(summary = "分页查询商品")
    @GetMapping
    public ApiResponse<Page<Product>> getProducts(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) String keyword) {
        return productService.getProducts(page, size, keyword);
    }

    /**
     * 查询所有商品
     */
    @Operation(summary = "查询所有商品")
    @GetMapping("/all")
    public ApiResponse<List<Product>> getAllProducts() {
        return productService.getAllProducts();
    }
}
