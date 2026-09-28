package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "purchase_order_item")
public class PurchaseOrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    public Integer orderId;
    public Integer categoryId;
    public Double gram;
    public Double width;
    @Column(length = 20)
    public String unit = "吨";
    public Double quantity = 0d;
    public Double unitPrice = 0d;
    public Double amount = 0d;
    @Column(length = 20)
    public String deliveryDate;
    @Column(length = 200)
    public String remark;
    public Double arrivedQuantity = 0d;
    @Column(length = 20)
    public String status = "pending";
}
