package com.pacingscore.backend.model;

import io.swagger.v3.oas.annotations.media.Schema;

public class ShowDto {
    @Schema(description = "ID de la série/émission", example = "12345")
    private String id;

    @Schema(description = "Titre", example = "Les Aventures de Petit Ours")
    private String title;

    @Schema(description = "Nombre de saisons", example = "3")
    private Integer seasonsCount;

    @Schema(description = "Nombre total d'épisodes", example = "52")
    private Integer episodesCount;

    // Constructeurs
    public ShowDto() {}

    public ShowDto(String id, String title, Integer seasonsCount, Integer episodesCount) {
        this.id = id;
        this.title = title;
        this.seasonsCount = seasonsCount;
        this.episodesCount = episodesCount;
    }

    // Getters et setters
    public String getId() { return id; }
    public void setId(String id) { this.id = id; }

    public String getTitle() { return title; }
    public void setTitle(String title) { this.title = title; }

    public Integer getSeasonsCount() { return seasonsCount; }
    public void setSeasonsCount(Integer seasonsCount) { this.seasonsCount = seasonsCount; }

    public Integer getEpisodesCount() { return episodesCount; }
    public void setEpisodesCount(Integer episodesCount) { this.episodesCount = episodesCount; }
}
