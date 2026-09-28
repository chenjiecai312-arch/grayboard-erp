package com.grayboard.erp.repo;

import com.grayboard.erp.domain.ProductCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ProductCategoryRepository extends JpaRepository<ProductCategory, Integer> {
    List<ProductCategory> findByParentId(Integer parentId);
}
