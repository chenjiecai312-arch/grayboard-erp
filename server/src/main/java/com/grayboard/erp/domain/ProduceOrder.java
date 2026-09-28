package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;
import jakarta.persistence.Transient;

import java.util.ArrayList;
import java.util.List;

@Entity
@Table(name = "produce_order")
public class ProduceOrder {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    @Column(length = 50)
    public String orderNo;
    @Column(length = 50)
    public String poNo;
    public Integer customerId;
    @Column(length = 200)
    public String customerName;
    @Column(length = 200)
    public String productName;
    public Double quantity = 0d;
    public Double specWidth = 0d;
    public Double specLength = 0d;
    public Double totalGram = 0d;
    @Column(length = 100)
    public String customerOrderNo;
    @Column(length = 50)
    public String thickness;
    @Column(length = 50)
    public String humidity;
    @Column(length = 100)
    public String brand;
    @Column(length = 50)
    public String sizeError;
    @Column(length = 50)
    public String diagonalError = "2MM内";
    @Column(length = 100)
    public String packageMethod;
    @Column(length = 20)
    public String lossLimit = "2%";
    @Column(length = 50)
    public String maker;
    @Column(length = 50)
    public String checker;
    @Column(length = 20)
    public String scheduleDate;
    public Integer salesOrderId;
    @Column(length = 200)
    public String craft;
    @Column(length = 20)
    public String produceDate;
    public Integer layers = 1;
    public Double totalAmount = 0d;
    @Column(length = 20)
    public String status = "draft";
    @Lob
    @Column(columnDefinition = "text")
    public String remark;
    public String createdAt;

    @Transient
    public List<ProduceOrderItem> items = new ArrayList<>();
}
