package com.grayboard.erp.auth;

import com.grayboard.erp.auth.StaffService.StaffRequest;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;
import java.util.Map;

@RestController
public class StaffController {
    private final StaffService staff;

    public StaffController(StaffService staff) {
        this.staff = staff;
    }

    @GetMapping("/api/auth/me")
    public Map<String, Object> me() {
        return staff.me();
    }

    @GetMapping("/api/staff/meta")
    public Map<String, Object> meta() {
        return staff.meta();
    }

    @GetMapping("/api/staff")
    public List<Map<String, Object>> list() {
        return staff.list();
    }

    @PostMapping("/api/staff")
    public Map<String, Object> create(@RequestBody StaffRequest request) {
        return staff.create(request);
    }

    @PutMapping("/api/staff/{id}")
    public Map<String, Object> update(@PathVariable Integer id, @RequestBody StaffRequest request) {
        return staff.update(id, request);
    }

    @DeleteMapping("/api/staff/{id}")
    public Map<String, Object> delete(@PathVariable Integer id) {
        return staff.delete(id);
    }
}
