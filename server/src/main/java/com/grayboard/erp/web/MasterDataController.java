package com.grayboard.erp.web;

import com.grayboard.erp.domain.*;
import com.grayboard.erp.service.MasterDataService;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
public class MasterDataController {
    private final MasterDataService service;

    public MasterDataController(MasterDataService service) {
        this.service = service;
    }

    @GetMapping("/api/customer")
    public List<Customer> listCustomers() { return service.listCustomers(); }

    @PostMapping("/api/customer")
    public Customer createCustomer(@RequestBody Customer item) { return service.createCustomer(item); }

    @PutMapping("/api/customer/{id}")
    public Customer updateCustomer(@PathVariable Integer id, @RequestBody Customer item) { return service.updateCustomer(id, item); }

    @DeleteMapping("/api/customer/{id}")
    public Map<String, Object> deleteCustomer(@PathVariable Integer id) { return service.deleteCustomer(id); }

    @GetMapping("/api/supplier")
    public List<Supplier> listSuppliers() { return service.listSuppliers(); }

    @PostMapping("/api/supplier")
    public Supplier createSupplier(@RequestBody Supplier item) { return service.createSupplier(item); }

    @PutMapping("/api/supplier/{id}")
    public Supplier updateSupplier(@PathVariable Integer id, @RequestBody Supplier item) { return service.updateSupplier(id, item); }

    @DeleteMapping("/api/supplier/{id}")
    public Map<String, Object> deleteSupplier(@PathVariable Integer id) { return service.deleteSupplier(id); }

    @GetMapping("/api/physical_category")
    public List<PhysicalCategory> listPhysical() { return service.listPhysicalCategories(); }

    @PostMapping("/api/physical_category")
    public PhysicalCategory createPhysical(@RequestBody PhysicalCategory item) { return service.createPhysicalCategory(item); }

    @PutMapping("/api/physical_category/{id}")
    public PhysicalCategory updatePhysical(@PathVariable Integer id, @RequestBody PhysicalCategory item) { return service.updatePhysicalCategory(id, item); }

    @DeleteMapping("/api/physical_category/{id}")
    public Map<String, Object> deletePhysical(@PathVariable Integer id) { return service.deletePhysicalCategory(id); }

    @GetMapping("/api/product_name")
    public List<ProductName> listNames() { return service.listProductNames(); }

    @PostMapping("/api/product_name")
    public ProductName createName(@RequestBody ProductName item) { return service.createProductName(item); }

    @GetMapping("/api/product_category")
    public List<ProductCategory> listProductCategories() { return service.listProductCategories(); }

    @PostMapping("/api/product_category")
    public ProductCategory createProductCategory(@RequestBody ProductCategory item) { return service.createProductCategory(item); }

    @PutMapping("/api/product_category/{id}")
    public ProductCategory updateProductCategory(@PathVariable Integer id, @RequestBody ProductCategory item) { return service.updateProductCategory(id, item); }

    @DeleteMapping("/api/product_category/{id}")
    public Map<String, Object> deleteProductCategory(@PathVariable Integer id) { return service.deleteProductCategory(id); }

    @GetMapping("/api/product_name_finished")
    public List<ProductNameFinished> listFinished() { return service.listFinishedNames(); }

    @PostMapping("/api/product_name_finished")
    public ProductNameFinished createFinished(@RequestBody ProductNameFinished item) { return service.createFinishedName(item); }

    @DeleteMapping("/api/product_name_finished/{id}")
    public Map<String, Object> deleteFinished(@PathVariable Integer id) { return service.deleteFinishedName(id); }

    @GetMapping("/api/aux_category")
    public List<AuxCategory> listAuxCategories() { return service.listAuxCategories(); }

    @PostMapping("/api/aux_category")
    public AuxCategory createAuxCategory(@RequestBody AuxCategory item) { return service.createAuxCategory(item); }

    @DeleteMapping("/api/aux_category/{id}")
    public Map<String, Object> deleteAuxCategory(@PathVariable Integer id) { return service.deleteAuxCategory(id); }

    @GetMapping("/api/aux_material")
    public List<AuxMaterial> listAux() { return service.listAuxMaterials(); }

    @PostMapping("/api/aux_material")
    public AuxMaterial createAux(@RequestBody AuxMaterial item) { return service.createAuxMaterial(item); }

    @PutMapping("/api/aux_material/{id}")
    public AuxMaterial updateAux(@PathVariable Integer id, @RequestBody AuxMaterial item) { return service.updateAuxMaterial(id, item); }

    @DeleteMapping("/api/aux_material/{id}")
    public Map<String, Object> deleteAux(@PathVariable Integer id) { return service.deleteAuxMaterial(id); }

    @PostMapping("/api/aux_material/{id}/adjust")
    public AuxMaterial adjust(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        return service.adjustAux(id, ((Number) body.get("adjust_quantity")).doubleValue());
    }
}
