package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "produce_material_log")
public class ProduceMaterialLog {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    public Integer orderId;
    public Integer itemId;
    @Column(length = 20)
    public String type;
    @Column(length = 20)
    public String materialType;
    public Integer materialId;
    public Double quantity;
    public String createdAt;
}
