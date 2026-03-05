package com.pacingscore.backend.model;

import io.swagger.v3.oas.annotations.media.Schema;
import java.time.LocalDateTime;

public class VideoAnalysisResultDto {
    @Schema(description = "ID de l'analyse", example = "1")
    private Long id;

    @Schema(description = "ID de la vidéo", example = "video_123")
    private String videoId;

    @Schema(description = "Score de rythme (0-100)", example = "85.5")
    private Double pacingScore;

    @Schema(description = "Temps total analysé (secondes)", example = "1320")
    private Integer totalDuration;

    @Schema(description = "Date de l'analyse")
    private LocalDateTime analyzedAt;

    // Constructeurs
    public VideoAnalysisResultDto() {}

    public VideoAnalysisResultDto(Long id, String videoId, Double pacingScore, Integer totalDuration, LocalDateTime analyzedAt) {
        this.id = id;
        this.videoId = videoId;
        this.pacingScore = pacingScore;
        this.totalDuration = totalDuration;
        this.analyzedAt = analyzedAt;
    }

    // Getters et setters
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }

    public String getVideoId() { return videoId; }
    public void setVideoId(String videoId) { this.videoId = videoId; }

    public Double getPacingScore() { return pacingScore; }
    public void setPacingScore(Double pacingScore) { this.pacingScore = pacingScore; }

    public Integer getTotalDuration() { return totalDuration; }
    public void setTotalDuration(Integer totalDuration) { this.totalDuration = totalDuration; }

    public LocalDateTime getAnalyzedAt() { return analyzedAt; }
    public void setAnalyzedAt(LocalDateTime analyzedAt) { this.analyzedAt = analyzedAt; }
}
