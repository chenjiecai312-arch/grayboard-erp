package com.grayboard.erp.repo;

import com.grayboard.erp.domain.SalesOrderItem;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface SalesOrderItemRepository extends JpaRepository<SalesOrderItem, Integer> {
    List<SalesOrderItem> findByOrderIdOrderByLineNoAsc(Integer orderId);
    void deleteByOrderId(Integer orderId);
}
