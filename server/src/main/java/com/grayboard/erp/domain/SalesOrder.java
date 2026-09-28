package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import jakarta.persistence.Transient;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "sales_order")
public class SalesOrder {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    @Column(length = 50, unique = true)
    public String orderNo;
    public Integer customerId;
    public String customerName;
    public String customerOrderNo;
    public String receiver;
    public String receiverPhone;
    public String deliveryAddress;
    public String deliveryDate;
    public Double totalAmount = 0d;
    @Column(length = 20)
    public String status = "pending";
    public String maker;
    public String salesman;
    public String remark = "";
    public String createdAt;

    @Transient
    public List<SalesOrderItem> items = new ArrayList<>();
}
