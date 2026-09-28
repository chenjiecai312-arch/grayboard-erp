package com.grayboard.erp;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.cache.annotation.EnableCaching;

@EnableCaching
@SpringBootApplication
public class GrayboardApplication {
    public static void main(String[] args) {
        SpringApplication.run(GrayboardApplication.class, args);
    }
}
