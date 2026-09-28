package com.grayboard.erp.repo;

import com.grayboard.erp.domain.FinanceTransaction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;

public interface FinanceTransactionRepository extends JpaRepository<FinanceTransaction, Integer>, JpaSpecificationExecutor<FinanceTransaction> {
    long countByAccountId(Integer accountId);
}
