package com.grayboard.erp.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "raw_roll")
public class RawRoll {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    public String rawNo;
    public Integer productNameId;
    public Integer categoryId;
    public Double width;
    public Double gram;
    public Double weight;
    public Double stockWeight;
    public Double tonPrice = 0d;
    public String remark;
}
