package com.grayboard.erp.service;

import com.grayboard.erp.common.BizException;
import com.grayboard.erp.common.OperationLogService;
import com.grayboard.erp.common.Times;
import com.grayboard.erp.domain.FinanceAccount;
import com.grayboard.erp.domain.FinancePayable;
import com.grayboard.erp.domain.FinanceReceivable;
import com.grayboard.erp.domain.FinanceTransaction;
import com.grayboard.erp.repo.FinanceAccountRepository;
import com.grayboard.erp.repo.FinancePayableRepository;
import com.grayboard.erp.repo.FinanceReceivableRepository;
import com.grayboard.erp.repo.FinanceTransactionRepository;
import jakarta.persistence.criteria.Predicate;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

@Service
public class FinanceService {
    private final FinanceAccountRepository accounts;
    private final FinanceTransactionRepository transactions;
    private final FinanceReceivableRepository receivables;
    private final FinancePayableRepository payables;
    private final OperationLogService logs;

    public FinanceService(FinanceAccountRepository accounts, FinanceTransactionRepository transactions,
                          FinanceReceivableRepository receivables, FinancePayableRepository payables,
                          OperationLogService logs) {
        this.accounts = accounts;
        this.transactions = transactions;
        this.receivables = receivables;
        this.payables = payables;
        this.logs = logs;
    }

    public List<FinanceAccount> listAccounts() {
        return accounts.findAll(Sort.by(Sort.Direction.ASC, "id"));
    }

    @Transactional
    @CacheEvict(value = "financeSummary", allEntries = true)
    public FinanceAccount createAccount(FinanceAccount item) {
        item.id = null;
        if (item.createdAt == null) item.createdAt = Times.now();
        FinanceAccount saved = accounts.save(item);
        logs.log("财务", "新增账户", "资金账户", saved.id, "新增账户：" + saved.name + "，期初余额" + saved.balance);
        return saved;
    }

    @Transactional
    @CacheEvict(value = "financeSummary", allEntries = true)
    public FinanceAccount updateAccount(Integer id, FinanceAccount item) {
        FinanceAccount obj = accounts.findById(id).orElseThrow(() -> BizException.notFound("账户不存在"));
        obj.name = item.name;
        obj.accountType = item.accountType;
        obj.remark = item.remark;
        return accounts.save(obj);
    }

    @Transactional
    @CacheEvict(value = "financeSummary", allEntries = true)
    public Map<String, Object> deleteAccount(Integer id) {
        FinanceAccount obj = accounts.findById(id).orElseThrow(() -> BizException.notFound("账户不存在"));
        long txCount = transactions.countByAccountId(id);
        if (txCount > 0) throw BizException.bad("该账户有" + txCount + "笔流水记录，不能删除");
        accounts.delete(obj);
        return Map.of("ok", true);
    }

    public List<FinanceTransaction> listTransactions(String direction, String category, Integer accountId,
                                                     String keyword, String startDate, String endDate) {
        Specification<FinanceTransaction> spec = (root, query, cb) -> {
            List<Predicate> predicates = new ArrayList<>();
            if (direction != null && !direction.isBlank()) predicates.add(cb.equal(root.get("direction"), direction));
            if (category != null && !category.isBlank()) predicates.add(cb.equal(root.get("category"), category));
            if (accountId != null) predicates.add(cb.equal(root.get("accountId"), accountId));
            if (keyword != null && !keyword.isBlank()) predicates.add(cb.like(root.get("counterparty"), "%" + keyword + "%"));
            if (startDate != null && !startDate.isBlank()) predicates.add(cb.greaterThanOrEqualTo(root.get("transDate"), startDate));
            if (endDate != null && !endDate.isBlank()) predicates.add(cb.lessThanOrEqualTo(root.get("transDate"), endDate));
            query.orderBy(cb.desc(root.get("transDate")), cb.desc(root.get("id")));
            return cb.and(predicates.toArray(Predicate[]::new));
        };
        return transactions.findAll(spec);
    }

    @Transactional
    @CacheEvict(value = "financeSummary", allEntries = true)
    public FinanceTransaction createTransaction(FinanceTransaction item) {
        if (nz(item.amount) <= 0) throw BizException.bad("金额必须大于0");
        FinanceAccount account = accounts.findById(item.accountId).orElseThrow(() -> BizException.notFound("资金账户不存在"));
        if ("expense".equals(item.direction) && nz(account.balance) < nz(item.amount)) {
            throw BizException.bad(String.format("账户余额不足，当前余额%.2f", nz(account.balance)));
        }
        account.balance = nz(account.balance) + ("income".equals(item.direction) ? nz(item.amount) : -nz(item.amount));
        accounts.save(account);
        item.id = null;
        if (item.createdAt == null) item.createdAt = Times.now();
        FinanceTransaction saved = transactions.save(item);
        logs.log("财务", "手工记账", "资金流水", saved.id,
                ("income".equals(item.direction) ? "收入" : "支出") + item.amount + "（" + item.category + "，" + item.counterparty + "）");
        return saved;
    }

    public List<FinanceReceivable> listReceivables(String status, String keyword) {
        return receivables.findAll(Sort.by(Sort.Direction.DESC, "id")).stream()
                .filter(row -> status == null || status.isBlank() || status.equals(row.status))
                .filter(row -> keyword == null || keyword.isBlank() || (row.customerName != null && row.customerName.contains(keyword)))
                .toList();
    }

    @Transactional
    @CacheEvict(value = "financeSummary", allEntries = true)
    public FinanceReceivable receive(Integer id, double amount, Integer accountId, String transDate, String operator, String remark) {
        FinanceReceivable rec = receivables.findById(id).orElseThrow(() -> BizException.notFound("应收记录不存在"));
        if (amount <= 0) throw BizException.bad("收款金额必须大于0");
        if (amount > nz(rec.balance) + 1e-6) throw BizException.bad(String.format("收款金额不能超过未收余额%.2f", nz(rec.balance)));
        FinanceAccount account = accounts.findById(accountId).orElseThrow(() -> BizException.notFound("资金账户不存在"));
        rec.receivedAmount = nz(rec.receivedAmount) + amount;
        rec.balance = nz(rec.balance) - amount;
        rec.status = rec.balance <= 1e-6 ? "paid" : "partial";
        if (rec.balance <= 1e-6) rec.balance = 0d;
        account.balance = nz(account.balance) + amount;
        accounts.save(account);
        FinanceTransaction tx = new FinanceTransaction();
        tx.transDate = transDate == null || transDate.isBlank() ? Times.today() : transDate;
        tx.direction = "income";
        tx.category = "客户收款";
        tx.counterparty = rec.customerName;
        tx.accountId = account.id;
        tx.amount = amount;
        tx.refType = "receivable";
        tx.refId = rec.id;
        tx.refNo = rec.orderNo;
        tx.operator = operator == null ? "" : operator;
        tx.remark = remark == null ? "" : remark;
        tx.createdAt = Times.now();
        transactions.save(tx);
        logs.log("财务", "收款", "应收账款", rec.id, "收到" + rec.customerName + "货款" + amount + "（" + rec.orderNo + "），入" + account.name);
        return receivables.save(rec);
    }

    public List<FinancePayable> listPayables(String status, String keyword) {
        return payables.findAll(Sort.by(Sort.Direction.DESC, "id")).stream()
                .filter(row -> status == null || status.isBlank() || status.equals(row.status))
                .filter(row -> keyword == null || keyword.isBlank() || (row.supplierName != null && row.supplierName.contains(keyword)))
                .toList();
    }

    @Transactional
    @CacheEvict(value = "financeSummary", allEntries = true)
    public FinancePayable pay(Integer id, double amount, Integer accountId, String transDate, String operator, String remark) {
        FinancePayable pay = payables.findById(id).orElseThrow(() -> BizException.notFound("应付记录不存在"));
        if (amount <= 0) throw BizException.bad("付款金额必须大于0");
        if (amount > nz(pay.balance) + 1e-6) throw BizException.bad(String.format("付款金额不能超过未付余额%.2f", nz(pay.balance)));
        FinanceAccount account = accounts.findById(accountId).orElseThrow(() -> BizException.notFound("资金账户不存在"));
        if (nz(account.balance) < amount) {
            throw BizException.bad(String.format("账户余额不足，%s当前余额%.2f", account.name, nz(account.balance)));
        }
        pay.paidAmount = nz(pay.paidAmount) + amount;
        pay.balance = nz(pay.balance) - amount;
        pay.status = pay.balance <= 1e-6 ? "paid" : "partial";
        if (pay.balance <= 1e-6) pay.balance = 0d;
        account.balance = nz(account.balance) - amount;
        accounts.save(account);
        FinanceTransaction tx = new FinanceTransaction();
        tx.transDate = transDate == null || transDate.isBlank() ? Times.today() : transDate;
        tx.direction = "expense";
        tx.category = "供应商付款";
        tx.counterparty = pay.supplierName;
        tx.accountId = account.id;
        tx.amount = amount;
        tx.refType = "payable";
        tx.refId = pay.id;
        tx.refNo = pay.orderNo;
        tx.operator = operator == null ? "" : operator;
        tx.remark = remark == null ? "" : remark;
        tx.createdAt = Times.now();
        transactions.save(tx);
        logs.log("财务", "付款", "应付账款", pay.id, "付给" + pay.supplierName + amount + "（" + pay.orderNo + "），出" + account.name);
        return payables.save(pay);
    }

    @Cacheable("financeSummary")
    public Map<String, Object> summary() {
        List<FinanceAccount> accountList = accounts.findAll(Sort.by("id"));
        double totalCash = accountList.stream().mapToDouble(a -> nz(a.balance)).sum();
        List<FinanceReceivable> openRec = receivables.findAll().stream().filter(r -> !"paid".equals(r.status)).toList();
        double recBalance = openRec.stream().mapToDouble(r -> nz(r.balance)).sum();
        double payBalance = payables.findAll().stream().filter(p -> !"paid".equals(p.status)).mapToDouble(p -> nz(p.balance)).sum();
        String today = Times.today();
        List<FinanceReceivable> overdue = openRec.stream()
                .filter(r -> r.dueDate != null && r.dueDate.compareTo(today) < 0)
                .toList();
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("total_cash", round2(totalCash));
        body.put("receivable_balance", round2(recBalance));
        body.put("payable_balance", round2(payBalance));
        body.put("overdue_count", overdue.size());
        body.put("overdue_amount", round2(overdue.stream().mapToDouble(r -> nz(r.balance)).sum()));
        body.put("accounts", accountList.stream().map(a -> {
            Map<String, Object> row = new LinkedHashMap<>();
            row.put("id", a.id);
            row.put("name", a.name);
            row.put("balance", a.balance);
            return row;
        }).toList());
        return body;
    }

    private static double round2(double value) {
        return Math.round(value * 100d) / 100d;
    }

    private static double nz(Double value) {
        return value == null ? 0 : value;
    }
}
