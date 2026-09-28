package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "product")
public class Product {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    public Integer productNameId;
    public Integer categoryId;
    public Integer customerId;
    public String workOrderNo;
    public String spec = "";
    public Double actualGram = 0d;
    public Double nominalGram = 0d;
    public Double quantity = 0d;
    public Double pendingOutQty = 0d;
    @Column(length = 20)
    public String unit = "令";
    public String remark = "";
}
