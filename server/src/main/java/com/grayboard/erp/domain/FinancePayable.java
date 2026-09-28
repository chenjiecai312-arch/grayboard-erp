package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "finance_payable")
public class FinancePayable {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    @Column(length = 200)
    public String supplierName;
    public Integer purchaseOrderId;
    @Column(length = 50)
    public String orderNo;
    public Double amount = 0d;
    public Double paidAmount = 0d;
    public Double balance = 0d;
    @Column(length = 20)
    public String arriveDate;
    @Column(length = 20)
    public String dueDate;
    @Column(length = 20)
    public String status = "unpaid";
    public String remark = "";
    public String createdAt;
}
