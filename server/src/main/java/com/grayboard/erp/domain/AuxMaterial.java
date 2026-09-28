package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "aux_material")
public class AuxMaterial {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    @Column(length = 200)
    public String name;
    public Integer categoryId;
    public Double quantity = 0d;
    @Column(length = 20)
    public String unit = "个";
    public String remark = "";
}
