package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "finance_receivable")
public class FinanceReceivable {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    public Integer customerId;
    @Column(length = 200)
    public String customerName;
    public Integer salesOrderId;
    @Column(length = 50)
    public String orderNo;
    public Double amount = 0d;
    public Double receivedAmount = 0d;
    public Double balance = 0d;
    @Column(length = 20)
    public String shipDate;
    @Column(length = 20)
    public String dueDate;
    @Column(length = 20)
    public String status = "unpaid";
    public String remark = "";
    public String createdAt;
}
