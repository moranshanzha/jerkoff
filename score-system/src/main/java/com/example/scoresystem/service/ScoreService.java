package com.example.scoresystem.service;

import com.example.scoresystem.entity.Score;
import com.example.scoresystem.repository.ScoreRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;
import java.util.Optional;

@Service
@Transactional
public class ScoreService {
    
    @Autowired
    private ScoreRepository scoreRepository;
    
    /**
     * 保存得分记录
     * @param score 得分记录
     * @return 保存后的得分记录
     */
    public Score saveScore(Score score) {
        return scoreRepository.save(score);
    }
    
    /**
     * 根据ID获取得分记录
     * @param id 得分记录ID
     * @return 得分记录
     */
    public Optional<Score> getScoreById(Long id) {
        return scoreRepository.findById(id);
    }
    
    /**
     * 获取所有得分记录
     * @return 得分记录列表
     */
    public List<Score> getAllScores() {
        return scoreRepository.findAll();
    }
    
    /**
     * 获取最高分
     * @return 最高分记录
     */
    public Optional<Score> getHighScore() {
        return Optional.ofNullable(scoreRepository.findTopByOrderByScoreDesc());
    }
    
    /**
     * 获取前N名的得分记录
     * @param limit 限制数量
     * @return 前N名的得分记录列表
     */
    public Iterable<Score> getTopScores(int limit) {
        return scoreRepository.findTopScores(limit);
    }
    
    /**
     * 删除得分记录
     * @param id 得分记录ID
     */
    public void deleteScore(Long id) {
        scoreRepository.deleteById(id);
    }
}