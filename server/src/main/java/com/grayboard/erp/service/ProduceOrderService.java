package com.grayboard.erp.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.grayboard.erp.common.BizException;
import com.grayboard.erp.common.OperationLogService;
import com.grayboard.erp.common.Times;
import com.grayboard.erp.domain.PhysicalCategory;
import com.grayboard.erp.domain.ProduceMaterialLog;
import com.grayboard.erp.domain.ProduceOrder;
import com.grayboard.erp.domain.ProduceOrderItem;
import com.grayboard.erp.domain.Product;
import com.grayboard.erp.domain.ProductNameFinished;
import com.grayboard.erp.domain.RawRoll;
import com.grayboard.erp.repo.PhysicalCategoryRepository;
import com.grayboard.erp.repo.ProduceMaterialLogRepository;
import com.grayboard.erp.repo.ProduceOrderItemRepository;
import com.grayboard.erp.repo.ProduceOrderRepository;
import com.grayboard.erp.repo.ProductNameFinishedRepository;
import com.grayboard.erp.repo.ProductRepository;
import com.grayboard.erp.repo.RawRollRepository;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class ProduceOrderService {
    private final ProduceOrderRepository orders;
    private final ProduceOrderItemRepository items;
    private final ProduceMaterialLogRepository materialLogs;
    private final RawRollRepository rolls;
    private final PhysicalCategoryRepository categories;
    private final ProductNameFinishedRepository finishedNames;
    private final ProductRepository products;
    private final OperationLogService logs;

    public ProduceOrderService(ProduceOrderRepository orders, ProduceOrderItemRepository items,
                               ProduceMaterialLogRepository materialLogs, RawRollRepository rolls,
                               PhysicalCategoryRepository categories, ProductNameFinishedRepository finishedNames,
                               ProductRepository products, OperationLogService logs) {
        this.orders = orders;
        this.items = items;
        this.materialLogs = materialLogs;
        this.rolls = rolls;
        this.categories = categories;
        this.finishedNames = finishedNames;
        this.products = products;
        this.logs = logs;
    }

    public List<ProduceOrder> list() {
        List<ProduceOrder> result = orders.findAll(Sort.by(Sort.Direction.DESC, "id"));
        result.forEach(this::fill);
        return result;
    }

    @Transactional
    public ProduceOrder create(JsonNode body) {
        ProduceOrder order = read(new ProduceOrder(), body, true);
        if (order.orderNo == null || order.orderNo.isBlank()) order.orderNo = nextNo();
        if (order.produceDate == null) order.produceDate = Times.today();
        if (order.createdAt == null) order.createdAt = Times.now();
        order.totalAmount = sumAmount(body.get("items"));
        ProduceOrder saved = orders.save(order);
        replaceItems(saved.id, body.get("items"));
        fill(saved);
        return saved;
    }

    @Transactional
    public ProduceOrder update(Integer id, JsonNode body) {
        ProduceOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("工单不存在"));
        read(order, body, false);
        order.totalAmount = sumAmount(body.get("items"));
        items.deleteByOrderId(id);
        replaceItems(order.id, body.get("items"));
        ProduceOrder saved = orders.save(order);
        fill(saved);
        return saved;
    }

    @Transactional
    public Map<String, Object> delete(Integer id) {
        ProduceOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("工单不存在"));
        items.deleteByOrderId(id);
        orders.delete(order);
        return Map.of("ok", true);
    }

    @Transactional
    public Map<String, Object> pick(Integer id) {
        ProduceOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("工单不存在"));
        for (ProduceOrderItem item : items.findByOrderIdOrderByLayerNoAsc(id)) {
            if (item.rollId == null) continue;
            RawRoll roll = rolls.findById(item.rollId).orElse(null);
            if (roll == null) continue;
            if (nz(roll.stockWeight) < nz(item.quantity)) {
                throw BizException.bad(String.format("卷料[%s]库存不足，当前剩余%.3f吨", roll.rawNo, nz(roll.stockWeight)));
            }
            roll.stockWeight = nz(roll.stockWeight) - nz(item.quantity);
            rolls.save(roll);
            ProduceMaterialLog log = new ProduceMaterialLog();
            log.orderId = id;
            log.itemId = item.id;
            log.type = "pick";
            log.materialType = "roll";
            log.materialId = item.rollId;
            log.quantity = item.quantity;
            log.createdAt = Times.now();
            materialLogs.save(log);
        }
        order.status = "picking";
        orders.save(order);
        return Map.of("ok", true, "message", "领料成功，卷料库存已锁定");
    }

    @Transactional
    public Map<String, Object> returnMaterial(Integer id, JsonNode body) {
        ProduceOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("工单不存在"));
        if (body != null && body.isArray()) {
            for (JsonNode ri : body) {
                double quantity = ri.has("quantity") ? ri.get("quantity").asDouble() : 0;
                if (quantity <= 0 || !ri.has("item_id")) continue;
                ProduceOrderItem item = items.findById(ri.get("item_id").asInt()).orElse(null);
                if (item == null || item.rollId == null) continue;
                rolls.findById(item.rollId).ifPresent(roll -> {
                    roll.stockWeight = nz(roll.stockWeight) + quantity;
                    rolls.save(roll);
                });
                ProduceMaterialLog log = new ProduceMaterialLog();
                log.orderId = id;
                log.itemId = item.id;
                log.type = "return";
                log.materialType = "roll";
                log.materialId = item.rollId;
                log.quantity = quantity;
                log.createdAt = Times.now();
                materialLogs.save(log);
            }
        }
        order.status = "finished";
        logs.log("生产管理", "退料", "生产工单", id, "退料完成：" + order.orderNo + "，退回剩余卷料");
        orders.save(order);
        return Map.of("ok", true, "message", "退料成功");
    }

    @Transactional
    public Map<String, Object> schedule(JsonNode body) {
        String date = body.get("schedule_date").asText();
        int count = 0;
        for (JsonNode idNode : body.get("ids")) {
            ProduceOrder order = orders.findById(idNode.asInt()).orElse(null);
            if (order == null) continue;
            order.scheduleDate = date;
            order.status = "scheduled";
            orders.save(order);
            logs.log("生产管理", "排单", "生产工单", order.id, "排单：" + order.orderNo + "，排单日期" + date);
            count++;
        }
        return Map.of("ok", true, "count", count);
    }

    @Transactional
    public Map<String, Object> start(Integer id) {
        ProduceOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("工单不存在"));
        for (ProduceOrderItem item : items.findByOrderIdOrderByLayerNoAsc(id)) {
            if (item.rollId == null) continue;
            RawRoll roll = rolls.findById(item.rollId).orElse(null);
            if (roll == null) continue;
            if (nz(roll.stockWeight) < nz(item.quantity)) {
                throw BizException.bad(String.format("卷料 %s%s 库存不足，当前剩余 %.3f 吨",
                        roll.rawNo, categoryPath(roll.categoryId), nz(roll.stockWeight)));
            }
            roll.stockWeight = nz(roll.stockWeight) - nz(item.quantity);
            rolls.save(roll);
        }
        order.status = "pending";
        logs.log("生产管理", "移入待生产", "生产工单", id, "移入待生产：" + order.orderNo + "，锁定卷料库存");
        orders.save(order);
        return Map.of("ok", true, "status", "pending");
    }

    @Transactional
    public Map<String, Object> finish(Integer id) {
        ProduceOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("工单不存在"));
        ProductNameFinished name = null;
        if (order.productName != null && !order.productName.isBlank()) {
            name = finishedNames.findFirstByName(order.productName).orElse(null);
            if (name == null) {
                name = new ProductNameFinished();
                name.name = order.productName;
                name = finishedNames.save(name);
            }
        }
        String spec = order.specWidth != null ? (order.specWidth + "x" + order.specLength) : "";
        Product product = new Product();
        product.productNameId = name == null ? null : name.id;
        product.workOrderNo = order.orderNo;
        product.spec = spec;
        product.actualGram = nz(order.totalGram);
        product.nominalGram = nz(order.totalGram);
        product.quantity = nz(order.quantity);
        product.pendingOutQty = 0d;
        product.unit = "令";
        product.remark = "生产工单 " + order.orderNo + " 自动入库";
        Product savedProduct = products.save(product);
        order.status = "finished";
        logs.log("生产管理", "完成生产", "生产工单", id, "完成生产：" + order.orderNo + "，成品自动入库" + order.quantity + "令");
        orders.save(order);
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("ok", true);
        body.put("status", "finished");
        body.put("product_id", savedProduct.id);
        return body;
    }

    @Transactional
    public Map<String, Object> cancelSchedule(Integer id) {
        ProduceOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("工单不存在"));
        if (!"scheduled".equals(order.status)) throw BizException.bad("只有已排单状态的工单才能取消排单");
        order.status = "draft";
        order.scheduleDate = null;
        logs.log("生产管理", "取消排单", "生产工单", id, "取消排单：" + order.orderNo + "，工单回到草稿");
        orders.save(order);
        return Map.of("ok", true, "status", "draft");
    }

    @Transactional
    public Map<String, Object> backToDraft(Integer id) {
        ProduceOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("工单不存在"));
        if (!"pending".equals(order.status)) throw BizException.bad("只有待生产状态的工单才能打回草稿");
        for (ProduceOrderItem item : items.findByOrderIdOrderByLayerNoAsc(id)) {
            if (item.rollId == null) continue;
            rolls.findById(item.rollId).ifPresent(roll -> {
                roll.stockWeight = nz(roll.stockWeight) + nz(item.quantity);
                rolls.save(roll);
            });
        }
        order.status = "draft";
        order.scheduleDate = null;
        logs.log("生产管理", "打回草稿", "生产工单", id, "打回草稿：" + order.orderNo + "，卷料库存已退回");
        orders.save(order);
        return Map.of("ok", true, "status", "draft");
    }

    @Transactional
    public Map<String, Object> reschedule(Integer id) {
        ProduceOrder order = orders.findById(id).orElseThrow(() -> BizException.notFound("工单不存在"));
        if (!"pending".equals(order.status)) throw BizException.bad("只有待生产状态的工单才能重新排单");
        order.status = "scheduled";
        logs.log("生产管理", "重新排单", "生产工单", id, "重新排单：" + order.orderNo + "，移回已排单可重新选日期");
        orders.save(order);
        return Map.of("ok", true, "status", "scheduled");
    }

    private String categoryPath(Integer categoryId) {
        if (categoryId == null) return "";
        List<String> path = new ArrayList<>();
        PhysicalCategory cur = categories.findById(categoryId).orElse(null);
        while (cur != null) {
            path.add(0, cur.name);
            cur = cur.parentId == null ? null : categories.findById(cur.parentId).orElse(null);
        }
        return path.isEmpty() ? "" : " " + String.join("\\", path);
    }

    private ProduceOrder read(ProduceOrder order, JsonNode body, boolean creating) {
        if (creating && body.has("order_no")) order.orderNo = text(body, "order_no");
        order.poNo = text(body, "po_no");
        order.customerId = intVal(body, "customer_id");
        order.customerName = text(body, "customer_name");
        order.productName = text(body, "product_name");
        order.quantity = dbl(body, "quantity");
        order.specWidth = dbl(body, "spec_width");
        order.specLength = dbl(body, "spec_length");
        order.totalGram = dbl(body, "total_gram");
        order.customerOrderNo = text(body, "customer_order_no");
        order.thickness = text(body, "thickness");
        order.humidity = text(body, "humidity");
        order.brand = text(body, "brand");
        order.sizeError = text(body, "size_error");
        order.diagonalError = text(body, "diagonal_error") == null ? "2MM内" : text(body, "diagonal_error");
        order.packageMethod = text(body, "package_method");
        order.lossLimit = text(body, "loss_limit") == null ? "2%" : text(body, "loss_limit");
        order.maker = text(body, "maker");
        order.checker = text(body, "checker");
        order.scheduleDate = text(body, "schedule_date");
        order.salesOrderId = intVal(body, "sales_order_id");
        order.craft = text(body, "craft");
        order.produceDate = text(body, "produce_date");
        order.layers = body.has("layers") && !body.get("layers").isNull() ? body.get("layers").asInt() : 1;
        order.status = text(body, "status") == null ? "draft" : text(body, "status");
        order.remark = text(body, "remark");
        return order;
    }

    private void replaceItems(Integer orderId, JsonNode array) {
        if (array == null || !array.isArray()) return;
        for (JsonNode it : array) {
            ProduceOrderItem row = new ProduceOrderItem();
            row.orderId = orderId;
            row.layerNo = it.has("layer_no") ? it.get("layer_no").asInt() : 1;
            row.rollId = intVal(it, "roll_id");
            row.rollName = text(it, "roll_name") == null ? "" : text(it, "roll_name");
            row.quantity = dbl(it, "quantity");
            row.unitPrice = dbl(it, "unit_price");
            row.amount = row.quantity * row.unitPrice;
            row.remark = text(it, "remark");
            items.save(row);
        }
    }

    private double sumAmount(JsonNode array) {
        if (array == null || !array.isArray()) return 0;
        double total = 0;
        for (JsonNode it : array) total += dbl(it, "quantity") * dbl(it, "unit_price");
        return total;
    }

    private void fill(ProduceOrder order) {
        order.items = items.findByOrderIdOrderByLayerNoAsc(order.id);
    }

    private String nextNo() {
        String prefix = "GD" + Times.compactToday();
        return prefix + "-" + String.format("%03d", orders.countByOrderNoStartingWith(prefix) + 1);
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
