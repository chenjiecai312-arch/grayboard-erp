package com.grayboard.erp.repo;

import com.grayboard.erp.domain.ProduceOrderItem;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ProduceOrderItemRepository extends JpaRepository<ProduceOrderItem, Integer> {
    List<ProduceOrderItem> findByOrderIdOrderByLayerNoAsc(Integer orderId);
    void deleteByOrderId(Integer orderId);
}
