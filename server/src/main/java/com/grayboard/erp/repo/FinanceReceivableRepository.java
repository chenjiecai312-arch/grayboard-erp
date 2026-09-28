package com.grayboard.erp.repo;

import com.grayboard.erp.domain.FinanceReceivable;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface FinanceReceivableRepository extends JpaRepository<FinanceReceivable, Integer> {
    Optional<FinanceReceivable> findBySalesOrderId(Integer salesOrderId);
}
