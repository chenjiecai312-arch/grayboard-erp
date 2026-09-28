package com.grayboard.erp.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.grayboard.erp.common.BizException;
import com.grayboard.erp.common.OperationLogService;
import com.grayboard.erp.common.Times;
import com.grayboard.erp.domain.FinancePayable;
import com.grayboard.erp.domain.PhysicalCategory;
import com.grayboard.erp.domain.ProductName;
import com.grayboard.erp.domain.PurchaseOrder;
import com.grayboard.erp.domain.PurchaseOrderItem;
import com.grayboard.erp.domain.RawRoll;
import com.grayboard.erp.repo.FinancePayableRepository;
import com.grayboard.erp.repo.PhysicalCategoryRepository;
import com.grayboard.erp.repo.ProductNameRepository;
import com.grayboard.erp.repo.PurchaseOrderItemRepository;
import com.grayboard.erp.repo.PurchaseOrderRepository;
import com.grayboard.erp.repo.RawRollRepository;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class PurchaseOrderService {
    private final PurchaseOrderRepository orders;
    private final PurchaseOrderItemRepository items;
    private final RawRollRepository rolls;
    private final PhysicalCategoryRepository categories;
    private final ProductNameRepository productNames;
    private final FinancePayableRepository payables;
    private final OperationLogService logs;

    public PurchaseOrderService(PurchaseOrderRepository orders, PurchaseOrderItemRepository items, RawRollRepository rolls,
                                PhysicalCategoryRepository categories, ProductNameRepository productNames,
                                FinancePayableRepository payables, OperationLogService logs) {
        this.orders = orders;
        this.items = items;
        this.rolls = rolls;
        this.categories = categories;
        this.productNames = productNames;
        this.payables = payables;
        this.logs = logs;
    }

    public List<PurchaseOrder> list() {
        return orders.findAll(Sort.by(Sort.Direction.DESC, "id"));
    }

    public Map<String, Object> get(Integer id) {
        PurchaseOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("采购单不存在"));
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("id", order.id);
        body.put("order_no", order.orderNo);
        body.put("supplier", order.supplier);
        body.put("delivery_address", order.deliveryAddress);
        body.put("order_date", order.orderDate);
        body.put("remark", order.remark);
        body.put("maker", order.maker);
        body.put("checker", order.checker);
        body.put("status", order.status);
        body.put("total_amount", order.totalAmount);
        body.put("created_at", order.createdAt);
        body.put("items", items.findByOrderId(id));
        return body;
    }

    @Transactional
    public PurchaseOrder create(JsonNode body) {
        String orderNo = text(body, "order_no");
        if (orderNo == null || orderNo.isBlank()) {
            String prefix = "PO" + Times.compactToday();
            orderNo = prefix + String.format("%03d", orders.countByOrderNoStartingWith(prefix) + 1);
        }
        PurchaseOrder order = new PurchaseOrder();
        order.orderNo = orderNo;
        order.supplier = text(body, "supplier");
        order.deliveryAddress = text(body, "delivery_address");
        order.orderDate = text(body, "order_date") == null ? Times.today() : text(body, "order_date");
        order.remark = text(body, "remark");
        order.maker = text(body, "maker");
        order.checker = text(body, "checker");
        order.status = "pending";
        order.totalAmount = dbl(body, "total_amount");
        order.createdAt = Times.now();
        PurchaseOrder saved = orders.save(order);
        saveItems(saved.id, body.get("items"));
        logs.log("卷料仓", "新增采购单", "采购单", saved.id,
                "新增采购单：" + saved.orderNo + "，供应商" + saved.supplier + "，金额" + saved.totalAmount);
        return saved;
    }

    @Transactional
    public PurchaseOrder update(Integer id, JsonNode body) {
        PurchaseOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("采购单不存在"));
        order.supplier = text(body, "supplier");
        order.deliveryAddress = text(body, "delivery_address");
        order.orderDate = text(body, "order_date");
        order.remark = text(body, "remark");
        order.maker = text(body, "maker");
        order.checker = text(body, "checker");
        order.totalAmount = dbl(body, "total_amount");
        items.deleteByOrderId(id);
        saveItems(order.id, body.get("items"));
        logs.log("卷料仓", "修改采购单", "采购单", order.id, "修改采购单：" + order.orderNo + "，供应商" + order.supplier);
        return orders.save(order);
    }

    @Transactional
    public Map<String, Object> delete(Integer id) {
        PurchaseOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("采购单不存在"));
        items.deleteByOrderId(id);
        logs.log("卷料仓", "删除采购单", "采购单", id, "删除采购单：" + order.orderNo + "，供应商" + order.supplier);
        orders.delete(order);
        return Map.of("ok", true);
    }

    @Transactional
    public Map<String, Object> arrive(Integer id, JsonNode body) {
        PurchaseOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("采购单不存在"));
        List<Map<String, Object>> createdRolls = new ArrayList<>();
        boolean allArrived = true;
        double arriveAmountTotal = 0;
        JsonNode itemNodes = body.get("items");
        if (itemNodes != null && itemNodes.isArray()) {
            for (JsonNode arriveItem : itemNodes) {
                Integer itemId = arriveItem.has("item_id") ? arriveItem.get("item_id").asInt() : null;
                if (itemId == null) continue;
                PurchaseOrderItem item = items.findById(itemId).orElse(null);
                if (item == null) continue;
                double arriveQty = dbl(arriveItem, "arrive_quantity");
                if (arriveQty <= 0) continue;
                item.arrivedQuantity = nz(item.arrivedQuantity) + arriveQty;
                arriveAmountTotal += arriveQty * nz(item.unitPrice);
                if (item.arrivedQuantity >= nz(item.quantity)) {
                    item.status = "arrived";
                } else {
                    item.status = "partial";
                    allArrived = false;
                }
                items.save(item);
                List<RollDetail> details = rollDetails(arriveItem, arriveQty);
                for (int idx = 0; idx < details.size(); idx++) {
                    RollDetail detail = details.get(idx);
                    RawRoll roll = new RawRoll();
                    roll.rawNo = detail.rollNo;
                    roll.productNameId = resolveProductNameId(item.categoryId);
                    roll.categoryId = item.categoryId;
                    roll.width = item.width;
                    roll.gram = item.gram;
                    roll.weight = detail.weight;
                    roll.stockWeight = detail.weight;
                    roll.tonPrice = item.unitPrice;
                    roll.remark = detail.remark != null ? detail.remark
                            : "采购单" + order.orderNo + "到货，第" + (idx + 1) + "/" + details.size() + "支";
                    RawRoll saved = rolls.save(roll);
                    Map<String, Object> created = new HashMap<>();
                    created.put("id", saved.id);
                    created.put("raw_no", detail.rollNo);
                    created.put("weight", detail.weight);
                    createdRolls.add(created);
                }
            }
        }
        if (arriveAmountTotal > 0) {
            String today = Times.today();
            FinancePayable exist = payables.findByPurchaseOrderId(order.id).orElse(null);
            if (exist != null) {
                exist.amount = nz(exist.amount) + arriveAmountTotal;
                exist.balance = nz(exist.balance) + arriveAmountTotal;
                exist.arriveDate = today;
                exist.status = nz(exist.paidAmount) > 0 ? "partial" : "unpaid";
                payables.save(exist);
            } else {
                FinancePayable pay = new FinancePayable();
                pay.supplierName = order.supplier;
                pay.purchaseOrderId = order.id;
                pay.orderNo = order.orderNo;
                pay.amount = arriveAmountTotal;
                pay.paidAmount = 0d;
                pay.balance = arriveAmountTotal;
                pay.arriveDate = today;
                pay.status = "unpaid";
                pay.createdAt = Times.now();
                payables.save(pay);
            }
        }
        order.status = allArrived ? "completed" : "partial";
        double weightSum = createdRolls.stream().mapToDouble(r -> ((Number) r.get("weight")).doubleValue()).sum();
        logs.log("卷料仓", "采购到货", "采购单", order.id,
                String.format("采购单到货：%s，生成%d支卷筒，总重量%.3f吨，应付%.2f元",
                        order.orderNo, createdRolls.size(), weightSum, arriveAmountTotal));
        orders.save(order);
        Map<String, Object> result = new LinkedHashMap<>();
        result.put("ok", true);
        result.put("created_rolls", createdRolls);
        result.put("count", createdRolls.size());
        return result;
    }

    private List<RollDetail> rollDetails(JsonNode arriveItem, double arriveQty) {
        List<RollDetail> list = new ArrayList<>();
        JsonNode rollsNode = arriveItem.get("rolls");
        if (rollsNode != null && rollsNode.isArray() && !rollsNode.isEmpty()) {
            for (JsonNode roll : rollsNode) {
                String rollNo = text(roll, "roll_no");
                double weight = dbl(roll, "weight");
                if (rollNo != null && !rollNo.isBlank() && weight > 0) {
                    list.add(new RollDetail(rollNo, weight, text(roll, "remark")));
                }
            }
            if (!list.isEmpty()) return list;
        }
        int rollCount = Math.max(1, arriveItem.has("roll_count") ? arriveItem.get("roll_count").asInt() : 1);
        double per = Math.round(arriveQty / rollCount * 1_000_000d) / 1_000_000d;
        String prefix = "JD" + LocalDateTime.now().format(DateTimeFormatter.ofPattern("yyyyMMddHHmmss"));
        for (int i = 0; i < rollCount; i++) {
            list.add(new RollDetail(prefix + String.format("%03d", i + 1), per, null));
        }
        return list;
    }

    private Integer resolveProductNameId(Integer categoryId) {
        if (categoryId == null) return null;
        PhysicalCategory cat = categories.findById(categoryId).orElse(null);
        if (cat == null) return null;
        if (cat.parentId != null) {
            return ensureName(cat.name);
        }
        List<PhysicalCategory> children = categories.findByParentId(cat.id);
        if (children.isEmpty()) return null;
        return ensureName(children.get(0).name);
    }

    private Integer ensureName(String name) {
        return productNames.findFirstByName(name).map(existing -> existing.id).orElseGet(() -> {
            ProductName created = new ProductName();
            created.name = name;
            return productNames.save(created).id;
        });
    }

    private void saveItems(Integer orderId, JsonNode array) {
        if (array == null || !array.isArray()) return;
        for (JsonNode it : array) {
            PurchaseOrderItem row = new PurchaseOrderItem();
            row.orderId = orderId;
            row.categoryId = it.has("category_id") && !it.get("category_id").isNull() ? it.get("category_id").asInt() : null;
            row.gram = dbl(it, "gram");
            row.width = dbl(it, "width");
            row.unit = text(it, "unit") == null ? "吨" : text(it, "unit");
            row.quantity = dbl(it, "quantity");
            row.unitPrice = dbl(it, "unit_price");
            row.amount = dbl(it, "amount");
            row.deliveryDate = text(it, "delivery_date");
            row.remark = text(it, "remark");
            row.arrivedQuantity = 0d;
            row.status = "pending";
            items.save(row);
        }
    }

    private static String text(JsonNode node, String field) {
        if (node == null || !node.has(field) || node.get(field).isNull()) return null;
        return node.get(field).asText();
    }

    private static double dbl(JsonNode node, String field) {
        if (node == null || !node.has(field) || node.get(field).isNull()) return 0;
        return node.get(field).asDouble();
    }

    private static double nz(Double value) {
        return value == null ? 0 : value;
    }

    private record RollDetail(String rollNo, double weight, String remark) {}
}
