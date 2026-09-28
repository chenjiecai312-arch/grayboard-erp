package com.grayboard.erp.repo;

import com.grayboard.erp.domain.ProductName;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface ProductNameRepository extends JpaRepository<ProductName, Integer> {
    Optional<ProductName> findFirstByName(String name);
}
