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
class VideoAnalysisControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void testAnalyzeVideoShouldReturnOk() throws Exception {
        String videoUrl = "https://www.youtube.com/watch?v=dQw4w9WgXcQ";
        mockMvc.perform(post("/api/video-analysis/analyze")
                .param("videoUrl", videoUrl))
               .andExpect(status().isOk());
    }
}
