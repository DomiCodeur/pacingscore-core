package com.pacingscore.backend.controller;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@SpringBootTest
@AutoConfigureMockMvc
class AnalysisControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testScanTMDBShouldReturnOk() throws Exception {
        mockMvc.perform(post("/api/analysis/scan-tmdb"))
               .andExpect(status().isOk());
    }

    @Test
    void testPopulateShouldReturnOk() throws Exception {
        mockMvc.perform(post("/api/analysis/populate"))
               .andExpect(status().isOk());
    }
}
