package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "finance_transaction")
public class FinanceTransaction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    @Column(length = 20)
    public String transDate;
    @Column(length = 10)
    public String direction;
    @Column(length = 30)
    public String category = "其他";
    @Column(length = 200)
    public String counterparty = "";
    public Integer accountId;
    public Double amount = 0d;
    @Column(length = 20)
    public String refType = "";
    public Integer refId;
    @Column(length = 50)
    public String refNo = "";
    @Column(length = 50)
    public String operator = "";
    public String remark = "";
    public String createdAt;
}
