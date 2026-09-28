package com.grayboard.erp.auth;

import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

public final class AccessCatalog {
    public static final List<String> ALL = List.of(
            "customer", "supplier", "catalog", "ware_product", "ware_roll", "ware_material",
            "purchase", "sales", "produce", "finance", "log", "staff"
    );

    public static final List<Map<String, String>> PERMISSIONS = List.of(
            item("customer", "客户档案"),
            item("supplier", "供应商管理"),
            item("catalog", "目录管理"),
            item("ware_product", "成品仓"),
            item("ware_roll", "卷料仓"),
            item("ware_material", "辅料仓"),
            item("purchase", "采购单"),
            item("sales", "销售订单"),
            item("produce", "生产管理"),
            item("finance", "财务结算"),
            item("log", "操作日志"),
            item("staff", "人员权限")
    );

    public static final List<Map<String, Object>> ROLES = List.of(
            role("ADMIN", "系统管理员", ALL),
            role("SALES", "业务员", List.of("customer", "catalog", "sales")),
            role("WAREHOUSE", "仓管", List.of("supplier", "catalog", "ware_product", "ware_roll", "ware_material", "purchase")),
            role("PRODUCE", "生产", List.of("catalog", "produce")),
            role("FINANCE", "财务", List.of("finance"))
    );

    private static final Map<String, Set<String>> READERS = Map.ofEntries(
            Map.entry("customer", Set.of("customer", "sales", "produce", "ware_product")),
            Map.entry("supplier", Set.of("supplier", "purchase")),
            Map.entry("ware_product", Set.of("ware_product", "sales")),
            Map.entry("ware_roll", Set.of("ware_roll", "purchase", "produce", "sales")),
            Map.entry("ware_material", Set.of("ware_material")),
            Map.entry("purchase", Set.of("purchase")),
            Map.entry("sales", Set.of("sales", "produce")),
            Map.entry("produce", Set.of("produce")),
            Map.entry("finance", Set.of("finance")),
            Map.entry("log", Set.of("log")),
            Map.entry("staff", Set.of("staff"))
    );

    private AccessCatalog() {}

    public static boolean allowed(String method, String path, Set<String> permissions) {
        if (path.startsWith("/api/auth/")) {
            return true;
        }
        String module = moduleOf(path);
        if (module == null) {
            return false;
        }
        boolean read = "GET".equalsIgnoreCase(method) || "HEAD".equalsIgnoreCase(method);
        if (isCatalogPath(path)) {
            boolean owns = permissions.contains("catalog") || permissions.contains(module);
            if (!read) {
                return owns;
            }
            Set<String> readers = READERS.getOrDefault(module, Set.of(module));
            return owns || permissions.stream().anyMatch(readers::contains);
        }
        if (read) {
            Set<String> readers = READERS.getOrDefault(module, Set.of(module));
            return permissions.stream().anyMatch(readers::contains);
        }
        return permissions.contains(module);
    }

    public static boolean isCatalogPath(String path) {
        return path.startsWith("/api/product_category")
                || path.startsWith("/api/product_name")
                || path.startsWith("/api/physical_category")
                || path.startsWith("/api/aux_category");
    }

    public static String moduleOf(String path) {
        if (path.startsWith("/api/staff")) return "staff";
        if (path.startsWith("/api/finance")) return "finance";
        if (path.startsWith("/api/operation_log")) return "log";
        if (path.startsWith("/api/sales_order")) return "sales";
        if (path.startsWith("/api/produce_order")) return "produce";
        if (path.startsWith("/api/purchase_order")) return "purchase";
        if (path.startsWith("/api/pending_out")) return "ware_product";
        if (path.startsWith("/api/product_category")) return "ware_product";
        if (path.startsWith("/api/product_name_finished")) return "ware_product";
        if (path.startsWith("/api/product_name")) return "ware_roll";
        if (path.startsWith("/api/product")) return "ware_product";
        if (path.startsWith("/api/rawroll")) return "ware_roll";
        if (path.startsWith("/api/physical_category")) return "ware_roll";
        if (path.startsWith("/api/aux_category") || path.startsWith("/api/aux_material")) return "ware_material";
        if (path.startsWith("/api/customer")) return "customer";
        if (path.startsWith("/api/supplier")) return "supplier";
        return null;
    }

    public static String join(List<String> permissions) {
        return String.join(",", permissions);
    }

    private static Map<String, String> item(String code, String name) {
        Map<String, String> row = new LinkedHashMap<>();
        row.put("code", code);
        row.put("name", name);
        return row;
    }

    private static Map<String, Object> role(String code, String name, List<String> permissions) {
        Map<String, Object> row = new LinkedHashMap<>();
        row.put("code", code);
        row.put("name", name);
        row.put("permissions", permissions);
        return row;
    }
}
