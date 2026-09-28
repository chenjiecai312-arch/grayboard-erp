package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

@Entity
@Table(name = "sales_order_item")
public class SalesOrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    public Integer orderId;
    public Integer lineNo = 1;
    public Integer productId;
    public String productName;
    public String spec;
    public Double length = 0d;
    public Double width = 0d;
    public Double nominalGram = 0d;
    public Double actualGram = 0d;
    @Column(length = 20)
    public String unit = "张";
    public Double quantity = 0d;
    public Double tonPrice = 0d;
    public Double price = 0d;
    public Double unitPrice = 0d;
    public Double amount = 0d;
    public Double cost = 0d;
    public Double wasteRate = 3d;
    public Double laminationFee = 300d;
    @Lob
    @Column(columnDefinition = "text")
    public String costLayers;
    public String remark = "";
}
