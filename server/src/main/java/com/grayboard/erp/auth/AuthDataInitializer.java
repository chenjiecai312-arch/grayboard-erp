package com.grayboard.erp.auth;

import com.grayboard.erp.domain.SysUser;
import com.grayboard.erp.repo.SysUserRepository;

import java.util.ArrayList;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import org.springframework.boot.CommandLineRunner;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.core.AuthorizationGrantType;
import org.springframework.security.oauth2.core.ClientAuthenticationMethod;
import org.springframework.security.oauth2.server.authorization.client.RegisteredClient;
import org.springframework.security.oauth2.server.authorization.client.RegisteredClientRepository;
import org.springframework.security.oauth2.server.authorization.settings.ClientSettings;
import org.springframework.security.oauth2.server.authorization.settings.OAuth2TokenFormat;
import org.springframework.security.oauth2.server.authorization.settings.TokenSettings;
import org.springframework.stereotype.Component;

import java.time.Duration;
import java.util.UUID;

@Component
public class AuthDataInitializer implements CommandLineRunner {
    private final SysUserRepository users;
    private final PasswordEncoder passwordEncoder;
    private final RegisteredClientRepository clients;

    public AuthDataInitializer(SysUserRepository users, PasswordEncoder passwordEncoder, RegisteredClientRepository clients) {
        this.users = users;
        this.passwordEncoder = passwordEncoder;
        this.clients = clients;
    }

    @Override
    public void run(String... args) {
        users.findByUsername("admin").ifPresentOrElse(admin -> {
            if (admin.permissions == null || admin.permissions.isBlank()) {
                admin.role = "ADMIN";
                admin.realName = admin.realName == null ? "系统管理员" : admin.realName;
                admin.permissions = AccessCatalog.join(AccessCatalog.ALL);
                admin.enabled = true;
                users.save(admin);
            }
        }, () -> {
            SysUser admin = new SysUser();
            admin.username = "admin";
            admin.password = passwordEncoder.encode("admin123");
            admin.realName = "系统管理员";
            admin.role = "ADMIN";
            admin.permissions = AccessCatalog.join(AccessCatalog.ALL);
            admin.enabled = true;
            users.save(admin);
        });
        for (SysUser user : users.findAll()) {
            Set<String> perms = new LinkedHashSet<>(StaffService.permissionsOf(user));
            if ("ADMIN".equals(user.role)) {
                perms.addAll(AccessCatalog.ALL);
            } else if (("SALES".equals(user.role) || "WAREHOUSE".equals(user.role) || "PRODUCE".equals(user.role))
                    && !perms.contains("catalog")) {
                perms.add("catalog");
            } else {
                continue;
            }
            List<String> ordered = new ArrayList<>();
            for (String code : AccessCatalog.ALL) {
                if (perms.contains(code)) ordered.add(code);
            }
            String joined = AccessCatalog.join(ordered);
            if (!joined.equals(user.permissions)) {
                user.permissions = joined;
                users.save(user);
            }
        }
        if (clients.findByClientId("grayboard-web") == null) {
            RegisteredClient client = RegisteredClient.withId(UUID.randomUUID().toString())
                    .clientId("grayboard-web")
                    .clientSecret(passwordEncoder.encode("grayboard-secret"))
                    .clientName("灰板产销系统")
                    .clientAuthenticationMethod(ClientAuthenticationMethod.CLIENT_SECRET_POST)
                    .clientAuthenticationMethod(ClientAuthenticationMethod.CLIENT_SECRET_BASIC)
                    .authorizationGrantType(new AuthorizationGrantType("password"))
                    .authorizationGrantType(AuthorizationGrantType.REFRESH_TOKEN)
                    .scope("erp")
                    .clientSettings(ClientSettings.builder().requireAuthorizationConsent(false).build())
                    .tokenSettings(TokenSettings.builder()
                            .accessTokenTimeToLive(Duration.ofHours(2))
                            .refreshTokenTimeToLive(Duration.ofDays(7))
                            .reuseRefreshTokens(false)
                            .accessTokenFormat(OAuth2TokenFormat.SELF_CONTAINED)
                            .build())
                    .build();
            clients.save(client);
        }
    }
}
