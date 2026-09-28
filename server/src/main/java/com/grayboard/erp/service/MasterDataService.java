package com.grayboard.erp.service;

import com.grayboard.erp.common.BizException;
import com.grayboard.erp.common.OperationLogService;
import com.grayboard.erp.common.Times;
import com.grayboard.erp.domain.*;
import com.grayboard.erp.repo.*;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
public class MasterDataService {
    private final CustomerRepository customers;
    private final SupplierRepository suppliers;
    private final ProductCategoryRepository productCategories;
    private final ProductNameFinishedRepository finishedNames;
    private final ProductNameRepository productNames;
    private final PhysicalCategoryRepository physicalCategories;
    private final AuxCategoryRepository auxCategories;
    private final AuxMaterialRepository auxMaterials;
    private final ProductRepository products;
    private final OperationLogService logs;

    public MasterDataService(CustomerRepository customers, SupplierRepository suppliers,
                             ProductCategoryRepository productCategories, ProductNameFinishedRepository finishedNames,
                             ProductNameRepository productNames, PhysicalCategoryRepository physicalCategories,
                             AuxCategoryRepository auxCategories, AuxMaterialRepository auxMaterials,
                             ProductRepository products, OperationLogService logs) {
        this.customers = customers;
        this.suppliers = suppliers;
        this.productCategories = productCategories;
        this.finishedNames = finishedNames;
        this.productNames = productNames;
        this.physicalCategories = physicalCategories;
        this.auxCategories = auxCategories;
        this.auxMaterials = auxMaterials;
        this.products = products;
        this.logs = logs;
    }

    public List<Customer> listCustomers() {
        return customers.findAll(Sort.by(Sort.Direction.DESC, "id"));
    }

    @Transactional
    public Customer createCustomer(Customer item) {
        item.id = null;
        return customers.save(item);
    }

    @Transactional
    public Customer updateCustomer(Integer id, Customer item) {
        Customer obj = customers.findById(id).orElseThrow(() -> BizException.notFound("客户不存在"));
        obj.customerName = item.customerName;
        obj.contact = item.contact;
        obj.phone = item.phone;
        obj.address = item.address;
        obj.paymentTerms = item.paymentTerms;
        obj.salesperson = item.salesperson;
        obj.taxNo = item.taxNo;
        obj.customerLevel = item.customerLevel;
        return customers.save(obj);
    }

    @Transactional
    public Map<String, Object> deleteCustomer(Integer id) {
        Customer obj = customers.findById(id).orElseThrow(() -> BizException.notFound("客户不存在"));
        long used = products.countByCustomerId(id);
        if (used > 0) {
            throw BizException.bad("该客户下还有 " + used + " 条成品记录，请先移到其他客户再删除");
        }
        customers.delete(obj);
        return Map.of("ok", true);
    }

    public List<Supplier> listSuppliers() {
        return suppliers.findAll(Sort.by(Sort.Direction.DESC, "id"));
    }

    @Transactional
    public Supplier createSupplier(Supplier item) {
        item.id = null;
        item.createdAt = Times.now();
        Supplier saved = suppliers.save(item);
        logs.log("供应商管理", "新增", "供应商", saved.id, "新增供应商：" + saved.name);
        return saved;
    }

    @Transactional
    public Supplier updateSupplier(Integer id, Supplier item) {
        Supplier obj = suppliers.findById(id).orElseThrow(() -> BizException.notFound("供应商不存在"));
        obj.name = item.name;
        obj.contact = item.contact;
        obj.phone = item.phone;
        obj.address = item.address;
        obj.paymentTerm = item.paymentTerm;
        obj.salesman = item.salesman;
        obj.taxNo = item.taxNo;
        obj.level = item.level;
        obj.remark = item.remark;
        Supplier saved = suppliers.save(obj);
        logs.log("供应商管理", "修改", "供应商", saved.id, "修改供应商：" + saved.name);
        return saved;
    }

    @Transactional
    public Map<String, Object> deleteSupplier(Integer id) {
        Supplier obj = suppliers.findById(id).orElseThrow(() -> BizException.notFound("供应商不存在"));
        logs.log("供应商管理", "删除", "供应商", id, "删除供应商：" + obj.name);
        suppliers.delete(obj);
        return Map.of("ok", true);
    }

    public List<PhysicalCategory> listPhysicalCategories() {
        return physicalCategories.findAll();
    }

    @Transactional
    public PhysicalCategory createPhysicalCategory(PhysicalCategory item) {
        item.id = null;
        return physicalCategories.save(item);
    }

    @Transactional
    public PhysicalCategory updatePhysicalCategory(Integer id, PhysicalCategory item) {
        PhysicalCategory cat = physicalCategories.findById(id).orElseThrow(() -> BizException.notFound("分类不存在"));
        cat.name = item.name;
        cat.warnThreshold = item.warnThreshold;
        return physicalCategories.save(cat);
    }

    @Transactional
    public Map<String, Object> deletePhysicalCategory(Integer id) {
        if (!physicalCategories.existsById(id)) {
            throw BizException.notFound("分类不存在");
        }
        List<Integer> ids = descendantIds(id, true);
        physicalCategories.deleteAllById(ids);
        Map<String, Object> body = new HashMap<>();
        body.put("ok", true);
        body.put("deleted_count", ids.size());
        return body;
    }

    private List<Integer> descendantIds(Integer parentId, boolean physical) {
        List<Integer> ids = new ArrayList<>();
        ids.add(parentId);
        List<?> children = physical ? physicalCategories.findByParentId(parentId) : productCategories.findByParentId(parentId);
        for (Object child : children) {
            Integer cid = physical ? ((PhysicalCategory) child).id : ((ProductCategory) child).id;
            ids.addAll(descendantIds(cid, physical));
        }
        return ids;
    }

    public List<ProductName> listProductNames() {
        return productNames.findAll();
    }

    @Transactional
    public ProductName createProductName(ProductName item) {
        item.id = null;
        return productNames.save(item);
    }

    public List<ProductCategory> listProductCategories() {
        return productCategories.findAll();
    }

    @Transactional
    public ProductCategory createProductCategory(ProductCategory item) {
        item.id = null;
        return productCategories.save(item);
    }

    @Transactional
    public ProductCategory updateProductCategory(Integer id, ProductCategory item) {
        ProductCategory obj = productCategories.findById(id).orElseThrow(() -> BizException.notFound("分类不存在"));
        if (item.name != null) obj.name = item.name;
        if (item.parentId != null) obj.parentId = item.parentId;
        if (item.warnThreshold != null) obj.warnThreshold = item.warnThreshold;
        return productCategories.save(obj);
    }

    @Transactional
    public Map<String, Object> deleteProductCategory(Integer id) {
        if (!productCategories.existsById(id)) {
            throw BizException.notFound("分类不存在");
        }
        List<Integer> ids = descendantIds(id, false);
        productCategories.deleteAllById(ids);
        Map<String, Object> body = new HashMap<>();
        body.put("ok", true);
        body.put("deleted_count", ids.size());
        return body;
    }

    public List<ProductNameFinished> listFinishedNames() {
        return finishedNames.findAll();
    }

    @Transactional
    public ProductNameFinished createFinishedName(ProductNameFinished item) {
        item.id = null;
        return finishedNames.save(item);
    }

    @Transactional
    public Map<String, Object> deleteFinishedName(Integer id) {
        ProductNameFinished obj = finishedNames.findById(id).orElseThrow(() -> BizException.notFound("品名不存在"));
        finishedNames.delete(obj);
        return Map.of("ok", true);
    }

    public List<AuxCategory> listAuxCategories() {
        return auxCategories.findAll();
    }

    @Transactional
    public AuxCategory createAuxCategory(AuxCategory item) {
        item.id = null;
        return auxCategories.save(item);
    }

    @Transactional
    public Map<String, Object> deleteAuxCategory(Integer id) {
        AuxCategory cat = auxCategories.findById(id).orElseThrow(() -> BizException.notFound("分类不存在"));
        auxCategories.delete(cat);
        return Map.of("ok", true);
    }

    public List<AuxMaterial> listAuxMaterials() {
        return auxMaterials.findAll();
    }

    @Transactional
    public AuxMaterial createAuxMaterial(AuxMaterial item) {
        item.id = null;
        return auxMaterials.save(item);
    }

    @Transactional
    public AuxMaterial updateAuxMaterial(Integer id, AuxMaterial item) {
        AuxMaterial obj = auxMaterials.findById(id).orElseThrow(() -> BizException.notFound("辅料不存在"));
        if (item.name != null) obj.name = item.name;
        if (item.categoryId != null) obj.categoryId = item.categoryId;
        if (item.quantity != null) obj.quantity = item.quantity;
        if (item.unit != null) obj.unit = item.unit;
        if (item.remark != null) obj.remark = item.remark;
        return auxMaterials.save(obj);
    }

    @Transactional
    public Map<String, Object> deleteAuxMaterial(Integer id) {
        AuxMaterial obj = auxMaterials.findById(id).orElseThrow(() -> BizException.notFound("辅料不存在"));
        auxMaterials.delete(obj);
        return Map.of("ok", true);
    }

    @Transactional
    public AuxMaterial adjustAux(Integer id, double adjustQuantity) {
        AuxMaterial obj = auxMaterials.findById(id).orElseThrow(() -> BizException.notFound("辅料不存在"));
        double current = obj.quantity == null ? 0 : obj.quantity;
        double next = current + adjustQuantity;
        if (next < 0) {
            throw BizException.bad("库存不足，当前库存：" + current + " " + obj.unit);
        }
        obj.quantity = next;
        return auxMaterials.save(obj);
    }
}
