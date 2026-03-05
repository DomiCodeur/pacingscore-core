package com.pacingscore.backend.util;

import org.springframework.http.ResponseEntity;

import java.util.HashMap;
import java.util.Map;

public final class ApiResponseUtil {

    private ApiResponseUtil() {}

    public static ResponseEntity<Map<String, Object>> ok(Object data) {
        Map<String, Object> body = new HashMap<>();
        body.put("success", true);
        body.put("data", data);
        return ResponseEntity.ok(body);
    }

    public static ResponseEntity<Map<String, Object>> error(String message, int status) {
        Map<String, Object> body = new HashMap<>();
        body.put("success", false);
        body.put("error", message);
        return new ResponseEntity<>(body, org.springframework.http.HttpStatus.valueOf(status));
    }
}
