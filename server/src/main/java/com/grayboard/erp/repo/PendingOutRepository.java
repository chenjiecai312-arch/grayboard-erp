package com.grayboard.erp.repo;

import com.grayboard.erp.domain.PendingOut;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface PendingOutRepository extends JpaRepository<PendingOut, Integer> {
    List<PendingOut> findByStatusOrderByIdDesc(String status);
    List<PendingOut> findByReasonContainingAndStatus(String reason, String status);
}
