package com.grayboard.erp.web;

import com.fasterxml.jackson.databind.JsonNode;
import com.grayboard.erp.domain.OperationLog;
import com.grayboard.erp.domain.SalesOrder;
import com.grayboard.erp.repo.OperationLogRepository;
import com.grayboard.erp.service.ProduceOrderService;
import com.grayboard.erp.service.PurchaseOrderService;
import com.grayboard.erp.service.SalesOrderService;
import org.springframework.data.domain.PageRequest;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
public class OrderController {
    private final SalesOrderService sales;
    private final PurchaseOrderService purchase;
    private final ProduceOrderService produce;
    private final OperationLogRepository logs;

    public OrderController(SalesOrderService sales, PurchaseOrderService purchase, ProduceOrderService produce,
                           OperationLogRepository logs) {
        this.sales = sales;
        this.purchase = purchase;
        this.produce = produce;
        this.logs = logs;
    }

    @GetMapping("/api/operation_log")
    public List<OperationLog> logs(@RequestParam(defaultValue = "200") int limit) {
        return logs.findAll(PageRequest.of(0, Math.min(limit, 1000), org.springframework.data.domain.Sort.by(org.springframework.data.domain.Sort.Direction.DESC, "id"))).getContent();
    }

    @PostMapping("/api/operation_log")
    public Map<String, Object> addLog() { return Map.of("ok", true); }

    @GetMapping("/api/sales_order")
    public List<SalesOrder> listSales(@RequestParam(value = "customer_name", required = false) String customerName,
                                      @RequestParam(value = "customer_id", required = false) Integer customerId,
                                      @RequestParam(required = false) String status,
                                      @RequestParam(value = "start_date", required = false) String startDate,
                                      @RequestParam(value = "end_date", required = false) String endDate,
                                      @RequestParam(value = "search_field", required = false) String searchField,
                                      @RequestParam(value = "search_value", required = false) String searchValue) {
        return sales.list(customerName, customerId, status, startDate, endDate, searchField, searchValue);
    }

    @PostMapping("/api/sales_order")
    public SalesOrder createSales(@RequestBody JsonNode body) { return sales.create(body); }

    @GetMapping("/api/sales_order/{id}")
    public SalesOrder getSales(@PathVariable Integer id) { return sales.get(id); }

    @PutMapping("/api/sales_order/{id}")
    public SalesOrder updateSales(@PathVariable Integer id, @RequestBody JsonNode body) { return sales.update(id, body); }

    @PostMapping("/api/sales_order/{id}/ship")
    public SalesOrder ship(@PathVariable Integer id) { return sales.ship(id); }

    @DeleteMapping("/api/sales_order/{id}")
    public Map<String, Object> deleteSales(@PathVariable Integer id) { return sales.delete(id); }

    @GetMapping("/api/purchase_order")
    public List<com.grayboard.erp.domain.PurchaseOrder> listPurchase() { return purchase.list(); }

    @GetMapping("/api/purchase_order/{id}")
    public Map<String, Object> getPurchase(@PathVariable Integer id) { return purchase.get(id); }

    @PostMapping("/api/purchase_order")
    public com.grayboard.erp.domain.PurchaseOrder createPurchase(@RequestBody JsonNode body) { return purchase.create(body); }

    @PutMapping("/api/purchase_order/{id}")
    public com.grayboard.erp.domain.PurchaseOrder updatePurchase(@PathVariable Integer id, @RequestBody JsonNode body) {
        return purchase.update(id, body);
    }

    @DeleteMapping("/api/purchase_order/{id}")
    public Map<String, Object> deletePurchase(@PathVariable Integer id) { return purchase.delete(id); }

    @PostMapping("/api/purchase_order/{id}/arrive")
    public Map<String, Object> arrive(@PathVariable Integer id, @RequestBody JsonNode body) { return purchase.arrive(id, body); }

    @GetMapping("/api/produce_order")
    public List<com.grayboard.erp.domain.ProduceOrder> listProduce() { return produce.list(); }

    @PostMapping("/api/produce_order")
    public com.grayboard.erp.domain.ProduceOrder createProduce(@RequestBody JsonNode body) { return produce.create(body); }

    @PutMapping("/api/produce_order/{id}")
    public com.grayboard.erp.domain.ProduceOrder updateProduce(@PathVariable Integer id, @RequestBody JsonNode body) {
        return produce.update(id, body);
    }

    @DeleteMapping("/api/produce_order/{id}")
    public Map<String, Object> deleteProduce(@PathVariable Integer id) { return produce.delete(id); }

    @PostMapping("/api/produce_order/{id}/pick_material")
    public Map<String, Object> pick(@PathVariable Integer id) { return produce.pick(id); }

    @PostMapping("/api/produce_order/{id}/return_material")
    public Map<String, Object> returnMaterial(@PathVariable Integer id, @RequestBody JsonNode body) {
        return produce.returnMaterial(id, body);
    }

    @PostMapping("/api/produce_order/schedule")
    public Map<String, Object> schedule(@RequestBody JsonNode body) { return produce.schedule(body); }

    @PostMapping("/api/produce_order/{id}/start_production")
    public Map<String, Object> start(@PathVariable Integer id) { return produce.start(id); }

    @PostMapping("/api/produce_order/{id}/finish_production")
    public Map<String, Object> finish(@PathVariable Integer id) { return produce.finish(id); }

    @PostMapping("/api/produce_order/{id}/cancel_schedule")
    public Map<String, Object> cancelSchedule(@PathVariable Integer id) { return produce.cancelSchedule(id); }

    @PostMapping("/api/produce_order/{id}/back_to_draft")
    public Map<String, Object> back(@PathVariable Integer id) { return produce.backToDraft(id); }

    @PostMapping("/api/produce_order/{id}/reschedule")
    public Map<String, Object> reschedule(@PathVariable Integer id) { return produce.reschedule(id); }
}
