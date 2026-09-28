package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;

@Entity
@Table(name = "cost_template")
public class CostTemplate {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    @Column(length = 200)
    public String name;
    @Lob
    @Column(columnDefinition = "text")
    public String layers;
    public Double wasteRate = 3d;
    public Double laminationFee = 300d;
    public String createdAt;
    public String updatedAt;
}
