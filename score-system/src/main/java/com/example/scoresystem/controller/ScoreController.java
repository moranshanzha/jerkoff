package com.example.scoresystem.controller;

import com.example.scoresystem.entity.Score;
import com.example.scoresystem.service.ScoreService;
import jakarta.validation.Valid;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Optional;

@RestController
@RequestMapping("/api/scores")
public class ScoreController {
    
    @Autowired
    private ScoreService scoreService;
    
    /**
     * 创建得分记录
     * @param score 得分记录
     * @return 创建后的得分记录
     */
    @PostMapping
    public ResponseEntity<Score> createScore(@Valid @RequestBody Score score) {
        Score savedScore = scoreService.saveScore(score);
        return new ResponseEntity<>(savedScore, HttpStatus.CREATED);
    }
    
    /**
     * 根据ID获取得分记录
     * @param id 得分记录ID
     * @return 得分记录
     */
    @GetMapping("/{id}")
    public ResponseEntity<Score> getScoreById(@PathVariable Long id) {
        Optional<Score> score = scoreService.getScoreById(id);
        return score.map(ResponseEntity::ok)
                   .orElseGet(() -> ResponseEntity.notFound().build());
    }
    
    /**
     * 获取所有得分记录
     * @return 得分记录列表
     */
    @GetMapping
    public ResponseEntity<List<Score>> getAllScores() {
        List<Score> scores = scoreService.getAllScores();
        return ResponseEntity.ok(scores);
    }
    
    /**
     * 获取最高分
     * @return 最高分记录
     */
    @GetMapping("/high")
    public ResponseEntity<Score> getHighScore() {
        Optional<Score> highScore = scoreService.getHighScore();
        return highScore.map(ResponseEntity::ok)
                       .orElseGet(() -> ResponseEntity.notFound().build());
    }
    
    /**
     * 获取前N名的得分记录
     * @param limit 限制数量
     * @return 前N名的得分记录列表
     */
    @GetMapping("/top")
    public ResponseEntity<Iterable<Score>> getTopScores(@RequestParam(defaultValue = "10") int limit) {
        Iterable<Score> topScores = scoreService.getTopScores(limit);
        return ResponseEntity.ok(topScores);
    }
    
    /**
     * 更新得分记录
     * @param id 得分记录ID
     * @param score 得分记录
     * @return 更新后的得分记录
     */
    @PutMapping("/{id}")
    public ResponseEntity<Score> updateScore(@PathVariable Long id, @Valid @RequestBody Score score) {
        Optional<Score> existingScore = scoreService.getScoreById(id);
        
        if (existingScore.isPresent()) {
            score.setId(id);
            Score updatedScore = scoreService.saveScore(score);
            return ResponseEntity.ok(updatedScore);
        } else {
            return ResponseEntity.notFound().build();
        }
    }
    
    /**
     * 删除得分记录
     * @param id 得分记录ID
     * @return 响应状态
     */
    @DeleteMapping("/{id}")
    public ResponseEntity<Void> deleteScore(@PathVariable Long id) {
        Optional<Score> score = scoreService.getScoreById(id);
        
        if (score.isPresent()) {
            scoreService.deleteScore(id);
            return ResponseEntity.noContent().build();
        } else {
            return ResponseEntity.notFound().build();
        }
    }
}