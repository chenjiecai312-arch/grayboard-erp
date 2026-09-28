package com.grayboard.erp.domain;

import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "supplier")
public class Supplier {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    public String name;
    public String contact;
    public String phone;
    public String address;
    public String paymentTerm;
    public String salesman;
    public String taxNo;
    public String level;
    public String remark;
    public String createdAt;
}
