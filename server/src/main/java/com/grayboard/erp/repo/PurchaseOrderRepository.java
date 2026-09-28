package com.grayboard.erp.repo;

import com.grayboard.erp.domain.PurchaseOrder;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PurchaseOrderRepository extends JpaRepository<PurchaseOrder, Integer> {
    long countByOrderNoStartingWith(String prefix);
}
