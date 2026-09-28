package com.grayboard.erp.repo;

import com.grayboard.erp.domain.FinanceAccount;
import org.springframework.data.jpa.repository.JpaRepository;

public interface FinanceAccountRepository extends JpaRepository<FinanceAccount, Integer> {}
