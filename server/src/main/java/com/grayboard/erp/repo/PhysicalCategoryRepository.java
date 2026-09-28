package com.grayboard.erp.repo;

import com.grayboard.erp.domain.PhysicalCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface PhysicalCategoryRepository extends JpaRepository<PhysicalCategory, Integer> {
    List<PhysicalCategory> findByParentId(Integer parentId);
}
