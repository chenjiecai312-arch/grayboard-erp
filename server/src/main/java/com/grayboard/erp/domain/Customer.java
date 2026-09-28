package com.grayboard.erp.domain;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "customer")
public class Customer {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    public String customerName;
    public String contact;
    public String phone;
    public String address;
    public Integer paymentTerms = 0;
    public String salesperson;
    public String taxNo;
    public String customerLevel;
}
