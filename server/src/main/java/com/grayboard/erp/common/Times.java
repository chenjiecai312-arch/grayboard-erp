package com.grayboard.erp.common;

import java.time.LocalDate;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

public final class Times {
    public static final DateTimeFormatter DATE_TIME = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    public static final DateTimeFormatter DATE = DateTimeFormatter.ofPattern("yyyy-MM-dd");
    public static final DateTimeFormatter COMPACT_DATE = DateTimeFormatter.ofPattern("yyyyMMdd");

    private Times() {}

    public static String now() {
        return LocalDateTime.now().format(DATE_TIME);
    }

    public static String today() {
        return LocalDate.now().format(DATE);
    }

    public static String compactToday() {
        return LocalDate.now().format(COMPACT_DATE);
    }
}
