package com.grayboard.erp.repo;

import com.grayboard.erp.domain.PurchaseOrderItem;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface PurchaseOrderItemRepository extends JpaRepository<PurchaseOrderItem, Integer> {
    List<PurchaseOrderItem> findByOrderId(Integer orderId);
    void deleteByOrderId(Integer orderId);
}
