package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

@Entity
@Table(name = "purchase_order")
public class PurchaseOrder {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    @Column(length = 50)
    public String orderNo;
    @Column(length = 200)
    public String supplier;
    @Column(length = 200)
    public String deliveryAddress;
    @Column(length = 20)
    public String orderDate;
    @Lob
    @Column(columnDefinition = "text")
    public String remark;
    @Column(length = 50)
    public String maker;
    @Column(length = 50)
    public String checker;
    @Column(length = 20)
    public String status = "draft";
    public Double totalAmount = 0d;
    @Column(length = 30)
    public String createdAt;
}
