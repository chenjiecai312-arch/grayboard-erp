package com.grayboard.erp.service;

import com.grayboard.erp.common.BizException;
import com.grayboard.erp.common.OperationLogService;
import com.grayboard.erp.common.Times;
import com.grayboard.erp.domain.PendingOut;
import com.grayboard.erp.domain.Product;
import com.grayboard.erp.domain.RawRoll;
import com.grayboard.erp.domain.SalesOrder;
import com.grayboard.erp.repo.PendingOutRepository;
import com.grayboard.erp.repo.ProductRepository;
import com.grayboard.erp.repo.RawRollRepository;
import com.grayboard.erp.repo.SalesOrderRepository;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Map;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
public class WarehouseService {
    private static final Pattern ORDER_NO = Pattern.compile("销售订单\\s+(\\S+)");

    private final ProductRepository products;
    private final PendingOutRepository pendingOuts;
    private final RawRollRepository rolls;
    private final SalesOrderRepository salesOrders;
    private final OperationLogService logs;

    public WarehouseService(ProductRepository products, PendingOutRepository pendingOuts, RawRollRepository rolls,
                            SalesOrderRepository salesOrders, OperationLogService logs) {
        this.products = products;
        this.pendingOuts = pendingOuts;
        this.rolls = rolls;
        this.salesOrders = salesOrders;
        this.logs = logs;
    }

    public List<Product> listProducts() {
        return products.findAll();
    }

    @Transactional
    public Product createProduct(Product item) {
        item.id = null;
        if (item.pendingOutQty == null) item.pendingOutQty = 0d;
        Product saved = products.save(item);
        logs.log("成品仓", "新增", "成品", saved.id, "新增成品：" + saved.spec + "，数量" + saved.quantity);
        return saved;
    }

    @Transactional
    public Product updateProduct(Integer id, Product item) {
        Product obj = products.findById(id).orElseThrow(() -> BizException.notFound("成品不存在"));
        obj.productNameId = item.productNameId;
        obj.categoryId = item.categoryId;
        obj.customerId = item.customerId;
        obj.workOrderNo = item.workOrderNo;
        obj.spec = item.spec;
        obj.actualGram = item.actualGram;
        obj.nominalGram = item.nominalGram;
        obj.quantity = item.quantity;
        obj.unit = item.unit;
        obj.remark = item.remark;
        logs.log("成品仓", "修改", "成品", obj.id, "修改成品：" + obj.spec);
        return products.save(obj);
    }

    @Transactional
    public Map<String, Object> deleteProduct(Integer id) {
        Product obj = products.findById(id).orElseThrow(() -> BizException.notFound("成品不存在"));
        if (nz(obj.pendingOutQty) > 0) {
            throw BizException.bad("该成品有待出库记录，请先处理后再删除");
        }
        products.delete(obj);
        logs.log("成品仓", "删除", "成品", id, "删除成品：" + obj.spec + "，原库存" + obj.quantity);
        return Map.of("ok", true);
    }

    @Transactional
    public Product stockIn(Integer id, double quantity) {
        Product obj = products.findById(id).orElseThrow(() -> BizException.notFound("成品不存在"));
        if (quantity <= 0) throw BizException.bad("入库数量必须大于0");
        obj.quantity = nz(obj.quantity) + quantity;
        logs.log("成品仓", "入库", "成品", obj.id, "入库：" + obj.spec + "，入库" + quantity + "，现库存" + obj.quantity);
        return products.save(obj);
    }

    @Transactional
    public PendingOut createPendingOut(Integer productId, double quantity, String reason) {
        Product obj = products.findById(productId).orElseThrow(() -> BizException.notFound("成品不存在"));
        if (quantity <= 0) throw BizException.bad("出库数量必须大于0");
        double available = nz(obj.quantity) - nz(obj.pendingOutQty);
        if (available < quantity) {
            throw BizException.bad(String.format("可用库存不足，当前可用：%.2f %s", available, obj.unit));
        }
        obj.pendingOutQty = nz(obj.pendingOutQty) + quantity;
        products.save(obj);
        PendingOut record = new PendingOut();
        record.productId = productId;
        record.quantity = quantity;
        record.reason = reason == null ? "" : reason;
        record.status = "pending";
        record.createdAt = Times.now();
        return pendingOuts.save(record);
    }

    public List<PendingOut> listPending(String status) {
        if (status != null && !status.isBlank()) {
            return pendingOuts.findByStatusOrderByIdDesc(status);
        }
        return pendingOuts.findAll(Sort.by(Sort.Direction.DESC, "id"));
    }

    @Transactional
    public PendingOut cancelPending(Integer id) {
        PendingOut record = pendingOuts.findById(id).orElseThrow(() -> BizException.notFound("记录不存在"));
        if (!"pending".equals(record.status)) throw BizException.bad("该记录已处理，无法取消");
        products.findById(record.productId).ifPresent(product -> {
            product.quantity = nz(product.quantity) + nz(record.quantity);
            product.pendingOutQty = nz(product.pendingOutQty) - nz(record.quantity);
            products.save(product);
        });
        record.status = "cancelled";
        if (record.reason != null && record.reason.contains("销售订单")) {
            Matcher match = ORDER_NO.matcher(record.reason);
            if (match.find()) {
                salesOrders.findByOrderNo(match.group(1)).ifPresent(order -> {
                    if ("pending".equals(order.status)) {
                        order.status = "draft";
                        salesOrders.save(order);
                    }
                });
            }
        }
        return pendingOuts.save(record);
    }

    @Transactional
    public PendingOut confirmPending(Integer id) {
        PendingOut record = pendingOuts.findById(id).orElseThrow(() -> BizException.notFound("记录不存在"));
        if (!"pending".equals(record.status)) throw BizException.bad("该记录已处理");
        products.findById(record.productId).ifPresent(product -> {
            product.quantity = nz(product.quantity) - nz(record.quantity);
            product.pendingOutQty = nz(product.pendingOutQty) - nz(record.quantity);
            products.save(product);
        });
        record.status = "confirmed";
        return pendingOuts.save(record);
    }

    public List<RawRoll> listRolls() {
        return rolls.findAll();
    }

    @Transactional
    public RawRoll createRoll(RawRoll item) {
        item.id = null;
        item.stockWeight = item.weight;
        if (item.tonPrice == null) item.tonPrice = 0d;
        return rolls.save(item);
    }

    @Transactional
    public RawRoll reduceStock(Integer id, double reduceWeight) {
        RawRoll roll = rolls.findById(id).orElseThrow(() -> BizException.notFound("卷筒不存在"));
        if (reduceWeight <= 0) throw BizException.bad("扣减重量必须大于0");
        if (nz(roll.stockWeight) < reduceWeight) {
            throw BizException.bad(String.format("库存不足，当前剩余:%.3f吨", nz(roll.stockWeight)));
        }
        roll.stockWeight = nz(roll.stockWeight) - reduceWeight;
        return rolls.save(roll);
    }

    @Transactional
    public Map<String, Object> deleteRoll(Integer id) {
        RawRoll roll = rolls.findById(id).orElseThrow(() -> BizException.notFound("卷筒不存在"));
        rolls.delete(roll);
        return Map.of("ok", true);
    }

    static double nz(Double value) {
        return value == null ? 0d : value;
    }
}
