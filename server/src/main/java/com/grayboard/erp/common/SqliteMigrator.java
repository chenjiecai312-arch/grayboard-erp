package com.grayboard.erp.common;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.core.annotation.Order;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Component;

import java.nio.file.Files;
import java.nio.file.Path;
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.ResultSetMetaData;
import java.sql.Statement;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

@Component
@Order(20)
public class SqliteMigrator implements CommandLineRunner {
    private static final List<String> TABLES = List.of(
            "customer", "supplier", "physical_category", "product_category", "product_name", "product_name_finished",
            "aux_category", "aux_material", "raw_roll", "product", "sales_order", "sales_order_item",
            "pending_out", "purchase_order", "purchase_order_item", "produce_order", "produce_order_item",
            "produce_material_log", "finance_account", "finance_transaction", "finance_receivable", "finance_payable",
            "operation_log", "cost_template"
    );

    private final JdbcTemplate mysql;
    private final String sqlitePath;

    public SqliteMigrator(JdbcTemplate mysql, @Value("${grayboard.sqlite-path}") String sqlitePath) {
        this.mysql = mysql;
        this.sqlitePath = sqlitePath;
    }

    @Override
    public void run(String... args) throws Exception {
        Path path = Path.of(sqlitePath);
        if (!path.isAbsolute()) {
            path = Path.of(System.getProperty("user.dir")).resolve(path).normalize();
        }
        if (!Files.exists(path)) {
            return;
        }
        try (Connection sqlite = DriverManager.getConnection("jdbc:sqlite:" + path)) {
            for (String table : TABLES) {
                Integer count = mysql.queryForObject("SELECT COUNT(*) FROM " + table, Integer.class);
                if (count != null && count > 0) {
                    continue;
                }
                if (!sqliteTableExists(sqlite, table)) {
                    continue;
                }
                List<String> mysqlColumns = mysql.queryForList(
                        "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = ?",
                        String.class, table);
                int copied = copyTable(sqlite, table, mysqlColumns);
                if (copied > 0) {
                    Integer maxId = mysql.queryForObject("SELECT COALESCE(MAX(id), 0) FROM " + table, Integer.class);
                    mysql.execute("ALTER TABLE " + table + " AUTO_INCREMENT = " + ((maxId == null ? 0 : maxId) + 1));
                }
            }
        }
    }

    private boolean sqliteTableExists(Connection sqlite, String table) throws Exception {
        try (ResultSet rs = sqlite.getMetaData().getTables(null, null, table, null)) {
            if (rs.next()) return true;
        }
        try (ResultSet rs = sqlite.getMetaData().getTables(null, null, table.toUpperCase(Locale.ROOT), null)) {
            return rs.next();
        }
    }

    private int copyTable(Connection sqlite, String table, List<String> mysqlColumns) throws Exception {
        try (Statement statement = sqlite.createStatement();
             ResultSet rs = statement.executeQuery("SELECT * FROM " + table)) {
            ResultSetMetaData meta = rs.getMetaData();
            List<String> columns = new ArrayList<>();
            List<Integer> indexes = new ArrayList<>();
            for (int i = 1; i <= meta.getColumnCount(); i++) {
                String name = meta.getColumnName(i);
                if (mysqlColumns.stream().anyMatch(col -> col.equalsIgnoreCase(name))) {
                    columns.add(name);
                    indexes.add(i);
                }
            }
            if (columns.isEmpty()) return 0;
            String sql = "INSERT INTO " + table + " (" + String.join(",", columns) + ") VALUES ("
                    + "?,".repeat(columns.size()).replaceAll(",$", "") + ")";
            int copied = 0;
            while (rs.next()) {
                Object[] values = new Object[indexes.size()];
                for (int i = 0; i < indexes.size(); i++) {
                    values[i] = rs.getObject(indexes.get(i));
                }
                mysql.update(sql, values);
                copied++;
            }
            return copied;
        }
    }
}
