package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

@Entity
@Table(name = "produce_order_item")
public class ProduceOrderItem {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    public Integer orderId;
    public Integer layerNo;
    public Integer rollId;
    @Column(length = 200)
    public String rollName;
    public Double quantity = 0d;
    public Double unitPrice = 0d;
    public Double amount = 0d;
    @Lob
    @Column(columnDefinition = "text")
    public String remark;
}
