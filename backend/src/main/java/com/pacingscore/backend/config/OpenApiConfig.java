package com.pacingscore.backend.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestTemplate;

@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI springShopOpenAPI() {
        return new OpenAPI()
                .info(new Info()
                        .title("PacingScore API")
                        .description("API pour l'analyse de rythme des contenus jeunesse")
                        .version("v1.0.0")
                );
    }

    @Bean
    public RestTemplate restTemplate() {
        return new RestTemplate();
    }
}
