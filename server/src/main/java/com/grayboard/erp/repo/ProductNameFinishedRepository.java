package com.grayboard.erp.repo;

import com.grayboard.erp.domain.ProductNameFinished;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface ProductNameFinishedRepository extends JpaRepository<ProductNameFinished, Integer> {
    Optional<ProductNameFinished> findFirstByName(String name);
}
