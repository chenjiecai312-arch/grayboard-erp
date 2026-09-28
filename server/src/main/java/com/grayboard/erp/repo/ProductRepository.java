package com.grayboard.erp.repo;

import com.grayboard.erp.domain.Product;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface ProductRepository extends JpaRepository<Product, Integer> {
    long countByCustomerId(Integer customerId);
    Optional<Product> findFirstByProductNameIdAndSpec(Integer productNameId, String spec);
}
