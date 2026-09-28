package com.grayboard.erp.auth;

import com.grayboard.erp.common.BizException;
import com.grayboard.erp.common.OperationLogService;
import com.grayboard.erp.domain.SysUser;
import com.grayboard.erp.repo.SysUserRepository;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.ArrayList;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.stream.Collectors;

@Service
public class StaffService {
    private final SysUserRepository users;
    private final PasswordEncoder passwordEncoder;
    private final OperationLogService logs;

    public StaffService(SysUserRepository users, PasswordEncoder passwordEncoder, OperationLogService logs) {
        this.users = users;
        this.passwordEncoder = passwordEncoder;
        this.logs = logs;
    }

    public Map<String, Object> meta() {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("permissions", AccessCatalog.PERMISSIONS);
        body.put("roles", AccessCatalog.ROLES);
        return body;
    }

    public Map<String, Object> me() {
        return view(currentUser());
    }

    public List<Map<String, Object>> list() {
        return users.findAll().stream()
                .sorted((a, b) -> Integer.compare(b.id, a.id))
                .map(this::view)
                .toList();
    }

    @Transactional
    public Map<String, Object> create(StaffRequest request) {
        String username = required(request.username, "请填写账号").trim();
        if (users.findByUsername(username).isPresent()) {
            throw BizException.bad("账号已存在");
        }
        if (request.password == null || request.password.length() < 6) {
            throw BizException.bad("密码至少 6 位");
        }
        SysUser user = new SysUser();
        user.username = username;
        user.password = passwordEncoder.encode(request.password);
        apply(user, request);
        SysUser saved = users.save(user);
        logs.log("人员权限", "新增", "后台人员", saved.id, "新增人员：" + saved.username + "，角色" + saved.role);
        return view(saved);
    }

    @Transactional
    public Map<String, Object> update(Integer id, StaffRequest request) {
        SysUser user = users.findById(id).orElseThrow(() -> BizException.notFound("人员不存在"));
        boolean self = user.username.equals(currentUsername());
        if (request.password != null && !request.password.isBlank()) {
            if (request.password.length() < 6) throw BizException.bad("密码至少 6 位");
            user.password = passwordEncoder.encode(request.password);
        }
        apply(user, request);
        if (self && !user.enabled) throw BizException.bad("不能停用自己的账号");
        if (self && !permissionsOf(user).contains("staff")) throw BizException.bad("不能取消自己的人员权限");
        ensureStaffAdminRemains(user);
        SysUser saved = users.save(user);
        logs.log("人员权限", "修改", "后台人员", saved.id, "修改人员：" + saved.username + "，角色" + saved.role);
        return view(saved);
    }

    @Transactional
    public Map<String, Object> delete(Integer id) {
        SysUser user = users.findById(id).orElseThrow(() -> BizException.notFound("人员不存在"));
        if (user.username.equals(currentUsername())) throw BizException.bad("不能删除自己的账号");
        user.enabled = false;
        user.permissions = "";
        ensureStaffAdminRemains(user);
        logs.log("人员权限", "删除", "后台人员", id, "删除人员：" + user.username);
        users.delete(user);
        return Map.of("ok", true);
    }

    public SysUser currentUser() {
        return users.findByUsername(currentUsername()).orElseThrow(() -> BizException.notFound("账号不存在"));
    }

    public static Set<String> permissionsOf(SysUser user) {
        if (user == null) return Set.of();
        if ("ADMIN".equals(user.role) && (user.permissions == null || user.permissions.isBlank())) {
            return Set.copyOf(AccessCatalog.ALL);
        }
        if (user.permissions == null || user.permissions.isBlank()) return Set.of();
        return Arrays.stream(user.permissions.split(","))
                .map(String::trim)
                .filter(code -> AccessCatalog.ALL.contains(code))
                .collect(Collectors.toSet());
    }

    private void apply(SysUser user, StaffRequest request) {
        user.realName = blankToNull(request.realName);
        user.phone = blankToNull(request.phone);
        String role = request.role == null || request.role.isBlank() ? "SALES" : request.role;
        user.role = role;
        List<String> permissions = "ADMIN".equals(role) ? AccessCatalog.ALL : clean(request.permissions);
        if (permissions.isEmpty()) throw BizException.bad("请至少选择一项权限");
        user.permissions = AccessCatalog.join(permissions);
        if (request.enabled != null) user.enabled = request.enabled;
    }

    private void ensureStaffAdminRemains(SysUser candidate) {
        boolean candidateOk = candidate.enabled && permissionsOf(candidate).contains("staff");
        long others = users.findAll().stream()
                .filter(user -> candidate.id == null || !candidate.id.equals(user.id))
                .filter(user -> user.enabled && permissionsOf(user).contains("staff"))
                .count();
        if (!candidateOk && others == 0) {
            throw BizException.bad("至少保留一名可登录的人员管理员");
        }
    }

    private List<String> clean(List<String> permissions) {
        if (permissions == null) return List.of();
        List<String> result = new ArrayList<>();
        for (String code : permissions) {
            if (AccessCatalog.ALL.contains(code) && !result.contains(code)) result.add(code);
        }
        return result;
    }

    private Map<String, Object> view(SysUser user) {
        Map<String, Object> body = new LinkedHashMap<>();
        body.put("id", user.id);
        body.put("username", user.username);
        body.put("real_name", user.realName);
        body.put("phone", user.phone);
        body.put("role", user.role);
        body.put("permissions", new ArrayList<>(permissionsOf(user)));
        body.put("enabled", user.enabled);
        return body;
    }

    private static String currentUsername() {
        var authentication = SecurityContextHolder.getContext().getAuthentication();
        if (authentication instanceof JwtAuthenticationToken jwtAuth) {
            Jwt jwt = jwtAuth.getToken();
            String username = jwt.getClaimAsString("username");
            if (username != null && !username.isBlank()) return username;
            return jwt.getSubject();
        }
        throw BizException.bad("未登录");
    }

    private static String required(String value, String message) {
        if (value == null || value.isBlank()) throw BizException.bad(message);
        return value;
    }

    private static String blankToNull(String value) {
        return value == null || value.isBlank() ? null : value.trim();
    }

    public static class StaffRequest {
        public String username;
        public String password;
        public String realName;
        public String phone;
        public String role;
        public List<String> permissions;
        public Boolean enabled;
    }
}
