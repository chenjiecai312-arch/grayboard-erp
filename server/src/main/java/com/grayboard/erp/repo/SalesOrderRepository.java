package com.grayboard.erp.repo;

import com.grayboard.erp.domain.SalesOrder;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import java.util.Optional;

public interface SalesOrderRepository extends JpaRepository<SalesOrder, Integer>, JpaSpecificationExecutor<SalesOrder> {
    long countByOrderNoStartingWith(String prefix);
    Optional<SalesOrder> findByOrderNo(String orderNo);
}
