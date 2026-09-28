package com.grayboard.erp.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.grayboard.erp.common.BizException;
import com.grayboard.erp.common.OperationLogService;
import com.grayboard.erp.common.Times;
import com.grayboard.erp.domain.Customer;
import com.grayboard.erp.domain.FinanceReceivable;
import com.grayboard.erp.domain.PendingOut;
import com.grayboard.erp.domain.Product;
import com.grayboard.erp.domain.ProductNameFinished;
import com.grayboard.erp.domain.SalesOrder;
import com.grayboard.erp.domain.SalesOrderItem;
import com.grayboard.erp.repo.CustomerRepository;
import com.grayboard.erp.repo.FinanceReceivableRepository;
import com.grayboard.erp.repo.PendingOutRepository;
import com.grayboard.erp.repo.ProductNameFinishedRepository;
import com.grayboard.erp.repo.ProductRepository;
import com.grayboard.erp.repo.SalesOrderItemRepository;
import com.grayboard.erp.repo.SalesOrderRepository;
import jakarta.persistence.criteria.Predicate;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class SalesOrderService {
    private static final Map<String, String> STATUS_MAP = Map.ofEntries(
            Map.entry("草稿", "draft"), Map.entry("draft", "draft"),
            Map.entry("待出库", "pending"), Map.entry("待发货", "pending"), Map.entry("pending", "pending"),
            Map.entry("已出库", "shipped"), Map.entry("已发货", "shipped"), Map.entry("shipped", "shipped"),
            Map.entry("已完成", "completed"), Map.entry("completed", "completed"),
            Map.entry("已取消", "cancelled"), Map.entry("取消", "cancelled"), Map.entry("cancelled", "cancelled")
    );

    private final SalesOrderRepository orders;
    private final SalesOrderItemRepository items;
    private final ProductRepository products;
    private final ProductNameFinishedRepository finishedNames;
    private final PendingOutRepository pendingOuts;
    private final CustomerRepository customers;
    private final FinanceReceivableRepository receivables;
    private final OperationLogService logs;

    public SalesOrderService(SalesOrderRepository orders, SalesOrderItemRepository items, ProductRepository products,
                             ProductNameFinishedRepository finishedNames, PendingOutRepository pendingOuts,
                             CustomerRepository customers, FinanceReceivableRepository receivables, OperationLogService logs) {
        this.orders = orders;
        this.items = items;
        this.products = products;
        this.finishedNames = finishedNames;
        this.pendingOuts = pendingOuts;
        this.customers = customers;
        this.receivables = receivables;
        this.logs = logs;
    }

    public List<SalesOrder> list(String customerName, Integer customerId, String status, String startDate, String endDate,
                                 String searchField, String searchValue) {
        Specification<SalesOrder> spec = (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            if (customerId != null) predicates.add(cb.equal(root.get("customerId"), customerId));
            if (customerName != null && !customerName.isBlank()) {
                predicates.add(cb.like(root.get("customerName"), "%" + customerName + "%"));
            }
            if (status != null && !status.isBlank()) predicates.add(cb.equal(root.get("status"), status));
            if (startDate != null && !startDate.isBlank()) predicates.add(cb.greaterThanOrEqualTo(root.get("deliveryDate"), startDate));
            if (endDate != null && !endDate.isBlank()) predicates.add(cb.lessThanOrEqualTo(root.get("deliveryDate"), endDate));
            if (searchField != null && searchValue != null && !searchValue.isBlank()) {
                if ("status".equals(searchField)) {
                    predicates.add(cb.equal(root.get("status"), STATUS_MAP.getOrDefault(searchValue, searchValue)));
                } else if (List.of("orderNo", "customerName", "salesman", "receiver", "deliveryDate").contains(toCamel(searchField))) {
                    predicates.add(cb.like(root.get(toCamel(searchField)), "%" + searchValue + "%"));
                }
            }
            return cb.and(predicates.toArray(Predicate[]::new));
        };
        List<SalesOrder> result = orders.findAll(spec, Sort.by(Sort.Direction.DESC, "id"));
        result.forEach(this::fillItems);
        return result;
    }

    @Transactional
    public SalesOrder create(JsonNode body) {
        SalesOrder order = new SalesOrder();
        order.orderNo = nextOrderNo();
        order.customerId = intVal(body, "customer_id");
        order.customerName = text(body, "customer_name");
        order.customerOrderNo = text(body, "customer_order_no");
        order.receiver = text(body, "receiver");
        order.receiverPhone = text(body, "receiver_phone");
        order.deliveryAddress = text(body, "delivery_address");
        order.deliveryDate = text(body, "delivery_date");
        order.status = body.has("status") && !body.get("status").isNull() ? body.get("status").asText() : "pending";
        order.maker = text(body, "maker");
        order.salesman = text(body, "salesman");
        order.remark = text(body, "remark") == null ? "" : text(body, "remark");
        order.createdAt = Times.now();
        order.totalAmount = 0d;
        SalesOrder saved = orders.save(order);
        saved.totalAmount = replaceItems(saved.id, body.get("items"), true);
        saved = orders.save(saved);
        logs.log("销售订单", "新增", "销售订单", saved.id,
                "新增订单：" + saved.orderNo + "，客户" + saved.customerName + "，金额" + saved.totalAmount + "，状态" + saved.status);
        if ("pending".equals(saved.status)) {
            lockLimited(saved);
        }
        fillItems(saved);
        return saved;
    }

    public SalesOrder get(Integer id) {
        SalesOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("订单不存在"));
        fillItems(order);
        return order;
    }

    @Transactional
    public SalesOrder update(Integer id, JsonNode body) {
        SalesOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("订单不存在"));
        if (body.has("customer_id")) order.customerId = intVal(body, "customer_id");
        if (body.has("customer_name")) order.customerName = text(body, "customer_name");
        if (body.has("customer_order_no")) order.customerOrderNo = text(body, "customer_order_no");
        if (body.has("receiver")) order.receiver = text(body, "receiver");
        if (body.has("receiver_phone")) order.receiverPhone = text(body, "receiver_phone");
        if (body.has("delivery_address")) order.deliveryAddress = text(body, "delivery_address");
        if (body.has("delivery_date")) order.deliveryDate = text(body, "delivery_date");
        if (body.has("status")) order.status = text(body, "status");
        if (body.has("maker")) order.maker = text(body, "maker");
        if (body.has("salesman")) order.salesman = text(body, "salesman");
        if (body.has("remark")) order.remark = text(body, "remark");
        if (body.has("items") && body.get("items").isArray()) {
            order.totalAmount = replaceItems(order.id, body.get("items"), true);
        }
        if ("draft".equals(order.status)) {
            releasePending(order.orderNo);
        }
        if ("pending".equals(order.status)) {
            releasePending(order.orderNo);
            lockFull(order);
        }
        SalesOrder saved = orders.save(order);
        logs.log("销售订单", "修改", "销售订单", saved.id,
                "修改订单：" + saved.orderNo + "，客户" + saved.customerName + "，金额" + saved.totalAmount + "，状态" + saved.status);
        fillItems(saved);
        return saved;
    }

    @Transactional
    public SalesOrder ship(Integer id) {
        SalesOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("订单不存在"));
        if (!"pending".equals(order.status)) throw BizException.bad("只有待出库状态的订单才能出库");
        for (PendingOut record : pendingOuts.findByReasonContainingAndStatus(order.orderNo, "pending")) {
            products.findById(record.productId).ifPresent(product -> {
                product.quantity = nz(product.quantity) - nz(record.quantity);
                product.pendingOutQty = nz(product.pendingOutQty) - nz(record.quantity);
                products.save(product);
            });
            record.status = "confirmed";
            pendingOuts.save(record);
        }
        order.status = "shipped";
        if (receivables.findBySalesOrderId(order.id).isEmpty()) {
            int terms = 0;
            if (order.customerId != null) {
                Customer customer = customers.findById(order.customerId).orElse(null);
                if (customer != null && customer.paymentTerms != null) terms = customer.paymentTerms;
            }
            String due = null;
            try {
                due = LocalDate.parse(order.deliveryDate, DateTimeFormatter.ISO_LOCAL_DATE).plusDays(terms).toString();
            } catch (Exception ignored) {
                due = null;
            }
            FinanceReceivable rec = new FinanceReceivable();
            rec.customerId = order.customerId;
            rec.customerName = order.customerName;
            rec.salesOrderId = order.id;
            rec.orderNo = order.orderNo;
            rec.amount = nz(order.totalAmount);
            rec.receivedAmount = 0d;
            rec.balance = nz(order.totalAmount);
            rec.shipDate = Times.today();
            rec.dueDate = due;
            rec.status = "unpaid";
            rec.createdAt = Times.now();
            receivables.save(rec);
        }
        SalesOrder saved = orders.save(order);
        fillItems(saved);
        return saved;
    }

    @Transactional
    public Map<String, Object> delete(Integer id) {
        SalesOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("订单不存在"));
        releasePending(order.orderNo);
        items.deleteByOrderId(id);
        orders.delete(order);
        return Map.of("ok", true);
    }

    private void lockLimited(SalesOrder order) {
        for (SalesOrderItem detail : items.findByOrderIdOrderByLineNoAsc(order.id)) {
            Product product = matchProduct(detail);
            if (product == null) continue;
            double remain = nz(detail.quantity);
            double available = nz(product.quantity) - nz(product.pendingOutQty);
            if (remain <= 0 || available <= 0) continue;
            double lock = Math.min(available, remain);
            product.pendingOutQty = nz(product.pendingOutQty) + lock;
            products.save(product);
            savePending(product.id, lock, order.orderNo);
        }
    }

    private void lockFull(SalesOrder order) {
        for (SalesOrderItem detail : items.findByOrderIdOrderByLineNoAsc(order.id)) {
            Product product = matchProduct(detail);
            if (product == null) continue;
            product.pendingOutQty = nz(product.pendingOutQty) + nz(detail.quantity);
            products.save(product);
            savePending(product.id, nz(detail.quantity), order.orderNo);
        }
    }

    private Product matchProduct(SalesOrderItem detail) {
        if (detail.productId != null) {
            return products.findById(detail.productId).orElse(null);
        }
        if (detail.productName == null) return null;
        ProductNameFinished name = finishedNames.findFirstByName(detail.productName).orElse(null);
        if (name == null) return null;
        return products.findFirstByProductNameIdAndSpec(name.id, detail.spec).orElse(null);
    }

    private void savePending(Integer productId, double quantity, String orderNo) {
        PendingOut record = new PendingOut();
        record.productId = productId;
        record.quantity = quantity;
        record.reason = "销售订单 " + orderNo;
        record.status = "pending";
        record.createdAt = Times.now();
        pendingOuts.save(record);
    }

    private void releasePending(String orderNo) {
        for (PendingOut rec : pendingOuts.findByReasonContainingAndStatus(orderNo, "pending")) {
            products.findById(rec.productId).ifPresent(product -> {
                product.pendingOutQty = nz(product.pendingOutQty) - nz(rec.quantity);
                products.save(product);
            });
            rec.status = "cancelled";
            pendingOuts.save(rec);
        }
    }

    private double replaceItems(Integer orderId, JsonNode array, boolean deleteOld) {
        if (deleteOld) items.deleteByOrderId(orderId);
        if (array == null || !array.isArray()) return 0;
        double total = 0;
        int idx = 0;
        for (JsonNode it : array) {
            idx++;
            double unitPrice = it.has("unit_price") && !it.get("unit_price").isNull() ? it.get("unit_price").asDouble()
                    : (it.has("price") ? it.get("price").asDouble() : 0);
            double quantity = it.has("quantity") && !it.get("quantity").isNull() ? it.get("quantity").asDouble() : 0;
            double amount = quantity * unitPrice;
            total += amount;
            SalesOrderItem detail = new SalesOrderItem();
            detail.orderId = orderId;
            detail.lineNo = it.has("line_no") && !it.get("line_no").isNull() ? it.get("line_no").asInt() : idx;
            detail.productId = intVal(it, "product_id");
            detail.productName = text(it, "product_name");
            detail.spec = text(it, "spec");
            detail.length = dbl(it, "length");
            detail.width = dbl(it, "width");
            detail.nominalGram = dbl(it, "nominal_gram");
            detail.actualGram = dbl(it, "actual_gram");
            detail.unit = text(it, "unit") == null ? "张" : text(it, "unit");
            detail.quantity = quantity;
            detail.tonPrice = dbl(it, "ton_price");
            detail.price = unitPrice;
            detail.unitPrice = unitPrice;
            detail.amount = amount;
            detail.cost = dbl(it, "cost");
            detail.wasteRate = it.has("waste_rate") && !it.get("waste_rate").isNull() ? it.get("waste_rate").asDouble() : 3;
            detail.laminationFee = it.has("lamination_fee") && !it.get("lamination_fee").isNull() ? it.get("lamination_fee").asDouble() : 300;
            detail.costLayers = it.has("cost_layers") && !it.get("cost_layers").isNull()
                    ? (it.get("cost_layers").isTextual() ? it.get("cost_layers").asText() : it.get("cost_layers").toString())
                    : null;
            detail.remark = text(it, "remark") == null ? "" : text(it, "remark");
            items.save(detail);
        }
        return total;
    }

    private void fillItems(SalesOrder order) {
        order.items = items.findByOrderIdOrderByLineNoAsc(order.id);
    }

    private String nextOrderNo() {
        String prefix = "XS-" + Times.compactToday() + "-";
        long count = orders.countByOrderNoStartingWith(prefix);
        return prefix + String.format("%03d", count + 1);
    }

    private static String toCamel(String snake) {
        if ("order_no".equals(snake)) return "orderNo";
        if ("customer_name".equals(snake)) return "customerName";
        if ("delivery_date".equals(snake)) return "deliveryDate";
        return snake;
    }

    private static String text(JsonNode node, String field) {
        if (node == null || !node.has(field) || node.get(field).isNull()) return null;
        return node.get(field).asText();
    }

    private static Integer intVal(JsonNode node, String field) {
        if (node == null || !node.has(field) || node.get(field).isNull()) return null;
        return node.get(field).asInt();
    }

    private static double dbl(JsonNode node, String field) {
        if (node == null || !node.has(field) || node.get(field).isNull()) return 0;
        return node.get(field).asDouble();
    }

    private static double nz(Double value) {
        return value == null ? 0 : value;
    }
}
