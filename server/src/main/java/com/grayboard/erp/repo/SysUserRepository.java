package com.grayboard.erp.repo;

import com.grayboard.erp.domain.SysUser;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.Optional;

public interface SysUserRepository extends JpaRepository<SysUser, Integer> {
    Optional<SysUser> findByUsername(String username);
}
