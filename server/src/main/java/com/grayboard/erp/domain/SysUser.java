package com.grayboard.erp.domain;

import com.fasterxml.jackson.annotation.JsonIgnore;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.Table;

@Entity
@Table(name = "sys_user")
public class SysUser {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    public Integer id;
    @Column(unique = true, length = 50)
    public String username;
    @JsonIgnore
    public String password;
    public String realName;
    public String phone;
    @Column(length = 50)
    public String role = "SALES";
    @Column(length = 500)
    public String permissions = "";
    public boolean enabled = true;
}
