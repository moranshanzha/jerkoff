package com.example.scoresystem.repository;

import com.example.scoresystem.entity.Score;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

@Repository
public interface ScoreRepository extends JpaRepository<Score, Long> {
    
    /**
     * 查询最高分
     * @return 最高分记录
     */
    Score findTopByOrderByScoreDesc();
    
    /**
     * 查询前N名的得分记录
     * @param limit 限制数量
     * @return 前N名的得分记录列表
     */
    @Query("SELECT s FROM Score s ORDER BY s.score DESC LIMIT ?1")
    Iterable<Score> findTopScores(int limit);
}