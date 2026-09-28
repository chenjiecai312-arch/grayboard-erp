package com.grayboard.erp.web;

import com.grayboard.erp.domain.FinanceAccount;
import com.grayboard.erp.domain.FinancePayable;
import com.grayboard.erp.domain.FinanceReceivable;
import com.grayboard.erp.domain.FinanceTransaction;
import com.grayboard.erp.service.FinanceService;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.data.redis.core.StringRedisTemplate;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
public class FinanceController {
    private final FinanceService service;
    private final StringRedisTemplate redis;

    public FinanceController(FinanceService service, StringRedisTemplate redis) {
        this.service = service;
        this.redis = redis;
    }

    @PostMapping("/api/auth/logout")
    public Map<String, Object> logout(@AuthenticationPrincipal Jwt jwt) {
        if (jwt != null && jwt.getId() != null) {
            redis.delete("auth:access:" + jwt.getId());
        }
        return Map.of("ok", true);
    }

    @GetMapping("/api/finance/account")
    public List<FinanceAccount> accounts() { return service.listAccounts(); }

    @PostMapping("/api/finance/account")
    public FinanceAccount createAccount(@RequestBody FinanceAccount item) { return service.createAccount(item); }

    @PutMapping("/api/finance/account/{id}")
    public FinanceAccount updateAccount(@PathVariable Integer id, @RequestBody FinanceAccount item) {
        return service.updateAccount(id, item);
    }

    @DeleteMapping("/api/finance/account/{id}")
    public Map<String, Object> deleteAccount(@PathVariable Integer id) { return service.deleteAccount(id); }

    @GetMapping("/api/finance/transaction")
    public List<FinanceTransaction> transactions(@RequestParam(required = false) String direction,
                                                 @RequestParam(required = false) String category,
                                                 @RequestParam(value = "account_id", required = false) Integer accountId,
                                                 @RequestParam(required = false) String keyword,
                                                 @RequestParam(value = "start_date", required = false) String startDate,
                                                 @RequestParam(value = "end_date", required = false) String endDate) {
        return service.listTransactions(direction, category, accountId, keyword, startDate, endDate);
    }

    @PostMapping("/api/finance/transaction")
    public FinanceTransaction createTransaction(@RequestBody FinanceTransaction item) { return service.createTransaction(item); }

    @GetMapping("/api/finance/receivable")
    public List<FinanceReceivable> receivables(@RequestParam(required = false) String status,
                                               @RequestParam(required = false) String keyword) {
        return service.listReceivables(status, keyword);
    }

    @PostMapping("/api/finance/receivable/{id}/receive")
    public FinanceReceivable receive(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        return service.receive(id, number(body, "amount"), number(body, "account_id").intValue(),
                str(body, "trans_date"), str(body, "operator"), str(body, "remark"));
    }

    @GetMapping("/api/finance/payable")
    public List<FinancePayable> payables(@RequestParam(required = false) String status,
                                         @RequestParam(required = false) String keyword) {
        return service.listPayables(status, keyword);
    }

    @PostMapping("/api/finance/payable/{id}/pay")
    public FinancePayable pay(@PathVariable Integer id, @RequestBody Map<String, Object> body) {
        return service.pay(id, number(body, "amount"), number(body, "account_id").intValue(),
                str(body, "trans_date"), str(body, "operator"), str(body, "remark"));
    }

    @GetMapping("/api/finance/summary")
    public Map<String, Object> summary() { return service.summary(); }

    private static Double number(Map<String, Object> body, String key) {
        Object value = body.get(key);
        if (value == null) return 0d;
        return ((Number) value).doubleValue();
    }

    private static String str(Map<String, Object> body, String key) {
        Object value = body.get(key);
        return value == null ? "" : value.toString();
    }
}
