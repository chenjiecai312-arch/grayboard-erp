package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

@Entity
@Table(name = "operation_log")
public class OperationLog {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    @Column(length = 50)
    public String module;
    @Column(length = 50)
    public String action;
    @Column(length = 50)
    public String targetType;
    public Integer targetId;
    @Lob
    @Column(columnDefinition = "text")
    public String detail;
    public String createdAt;
}
