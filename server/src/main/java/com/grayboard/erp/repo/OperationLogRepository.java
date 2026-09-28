package com.grayboard.erp.repo;

import com.grayboard.erp.domain.OperationLog;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface OperationLogRepository extends JpaRepository<OperationLog, Integer> {
    List<OperationLog> findTop500ByOrderByIdDesc();
}
