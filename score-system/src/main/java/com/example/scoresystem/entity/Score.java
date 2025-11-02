package com.example.scoresystem.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Positive;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import java.time.LocalDateTime;

@Data
@NoArgsConstructor
@AllArgsConstructor
@Entity
@Table(name = "score_records")
public class Score {
    
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @NotBlank(message = "玩家名称不能为空")
    private String playerName;
    
    @Positive(message = "得分必须为正数")
    private int score;
    
    private LocalDateTime gameTime;
    
    @PrePersist
    protected void onCreate() {
        gameTime = LocalDateTime.now();
    }
}