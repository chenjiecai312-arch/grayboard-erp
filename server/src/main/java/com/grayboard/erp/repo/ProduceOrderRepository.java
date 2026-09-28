package com.grayboard.erp.repo;

import com.grayboard.erp.domain.ProduceOrder;
import org.springframework.data.jpa.repository.JpaRepository;

public interface ProduceOrderRepository extends JpaRepository<ProduceOrder, Integer> {
    long countByOrderNoStartingWith(String prefix);
}
