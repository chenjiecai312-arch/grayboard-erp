package com.grayboard.erp.common;

import com.grayboard.erp.domain.OperationLog;
import com.grayboard.erp.repo.OperationLogRepository;
import org.springframework.stereotype.Service;

@Service
public class OperationLogService {
    private final OperationLogRepository repository;

    public OperationLogService(OperationLogRepository repository) {
        this.repository = repository;
    }

    public void log(String module, String action, String targetType, Integer targetId, String detail) {
        OperationLog row = new OperationLog();
        row.module = module;
        row.action = action;
        row.targetType = targetType;
        row.targetId = targetId;
        row.detail = detail;
        row.createdAt = Times.now();
        repository.save(row);
    }
}
