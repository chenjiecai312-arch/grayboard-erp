package com.grayboard.erp.web;

import com.grayboard.erp.domain.PendingOut;
import com.grayboard.erp.domain.Product;
import com.grayboard.erp.domain.RawRoll;
import com.grayboard.erp.service.WarehouseService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
public class WarehouseController {
    private final WarehouseService service;

    public WarehouseController(WarehouseService service) {
        this.service = service;
    }

    @GetMapping("/api/product")
    public List<Product> listProducts() { return service.listProducts(); }

    @PostMapping("/api/product")
    public Product createProduct(@RequestBody Product item) { return service.createProduct(item); }

    @PutMapping("/api/product/{id}")
    public Product updateProduct(@PathVariable Integer id, @RequestBody Product item) { return service.updateProduct(id, item); }

    @DeleteMapping("/api/product/{id}")
    public Map<String, Object> deleteProduct(@PathVariable Integer id) { return service.deleteProduct(id); }

    @PostMapping("/api/product/{id}/stock_in")
    public Product stockIn(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        return service.stockIn(id, ((Number) body.get("quantity")).doubleValue());
    }

    @PostMapping("/api/product/{id}/pending_out")
    public PendingOut pendingOut(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        Object reason = body.get("reason");
        return service.createPendingOut(id, ((Number) body.get("quantity")).doubleValue(), reason == null ? "" : reason.toString());
    }

    @GetMapping("/api/pending_out")
    public List<PendingOut> listPending(@RequestParam(required = false) String status) { return service.listPending(status); }

    @PostMapping("/api/pending_out/{id}/cancel")
    public PendingOut cancel(@PathVariable Integer id) { return service.cancelPending(id); }

    @PostMapping("/api/pending_out/{id}/confirm")
    public PendingOut confirm(@PathVariable Integer id) { return service.confirmPending(id); }

    @GetMapping("/api/rawroll")
    public List<RawRoll> listRolls() { return service.listRolls(); }

    @PostMapping("/api/rawroll")
    public RawRoll createRoll(@RequestBody RawRoll item) { return service.createRoll(item); }

    @PostMapping("/api/rawroll/{id}/reduce_stock")
    public RawRoll reduce(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        return service.reduceStock(id, ((Number) body.get("reduce_weight")).doubleValue());
    }

    @DeleteMapping("/api/rawroll/{id}")
    public Map<String, Object> deleteRoll(@PathVariable Integer id) { return service.deleteRoll(id); }
}
