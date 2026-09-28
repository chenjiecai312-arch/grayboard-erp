package com.grayboard.erp.auth;

import com.grayboard.erp.domain.SysUser;
import com.grayboard.erp.repo.SysUserRepository;
import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import org.springframework.http.MediaType;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.Set;

@Component
public class PermissionFilter extends OncePerRequestFilter {
    private final SysUserRepository users;

    public PermissionFilter(SysUserRepository users) {
        this.users = users;
    }

    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain)
            throws ServletException, IOException {
        String path = request.getRequestURI();
        if (!path.startsWith("/api/") || "OPTIONS".equalsIgnoreCase(request.getMethod()) || path.startsWith("/api/auth/")) {
            filterChain.doFilter(request, response);
            return;
        }
        var authentication = SecurityContextHolder.getContext().getAuthentication();
        if (!(authentication instanceof JwtAuthenticationToken jwtAuth)) {
            filterChain.doFilter(request, response);
            return;
        }
        Jwt jwt = jwtAuth.getToken();
        String username = jwt.getClaimAsString("username");
        if (username == null || username.isBlank()) username = jwt.getSubject();
        SysUser user = users.findByUsername(username).orElse(null);
        if (user == null || !user.enabled) {
            write(response, 401, "账号已停用或不存在");
            return;
        }
        Set<String> permissions = StaffService.permissionsOf(user);
        if (!AccessCatalog.allowed(request.getMethod(), path, permissions)) {
            write(response, 403, "没有权限");
            return;
        }
        filterChain.doFilter(request, response);
    }

    private void write(HttpServletResponse response, int status, String detail) throws IOException {
        response.setStatus(status);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        response.setCharacterEncoding("UTF-8");
        response.getWriter().write("{\"detail\":\"" + detail + "\"}");
    }
}
