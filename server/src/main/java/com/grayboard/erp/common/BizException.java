package com.grayboard.erp.common;

public class BizException extends RuntimeException {
    private final int status;

    public BizException(int status, String detail) {
        super(detail);
        this.status = status;
    }

    public int getStatus() {
        return status;
    }

    public static BizException notFound(String detail) {
        return new BizException(404, detail);
    }

    public static BizException bad(String detail) {
        return new BizException(400, detail);
    }
}
