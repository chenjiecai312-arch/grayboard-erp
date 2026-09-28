package com.grayboard.erp.repo;

import com.grayboard.erp.domain.FinancePayable;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface FinancePayableRepository extends JpaRepository<FinancePayable, Integer> {
    Optional<FinancePayable> findByPurchaseOrderId(Integer purchaseOrderId);
}
