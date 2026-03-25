class BacktrackEngine:
    def __init__(self, logger, max_backtrack=2):
        self.logger = logger
        self.max_backtrack = max_backtrack
        self.history = []

    def check_backtrack(self, current_step, qc_results):
        """检查是否需要回溯"""
        if len(self.history) >= self.max_backtrack:
            self.logger.warning(f"已回溯 {self.max_backtrack} 次，停止回溯")
            return None, None

        if current_step == 'structural':
            return self._check_structural_backtrack(qc_results)

        return None, None

    def _check_structural_backtrack(self, qc_results):
        """检查结构注释步骤是否需要回溯"""
        structural_busco = qc_results.get('structural', {}).get('busco', {}).get('complete', 0)
        assembly_busco = qc_results.get('assembly', {}).get('busco', {}).get('complete', 0)
        repeat_content = qc_results.get('repeat', {}).get('repeat_content', 0)

        # 规则1: 结构注释 BUSCO < 组装 BUSCO
        if structural_busco < assembly_busco - 5:
            reason = "结构注释 BUSCO 低于组装 BUSCO，组装可能不完整"
            self.logger.warning(f"触发回溯: {reason}")
            self.history.append(('structural', 'assembly', reason))
            return 'assembly', reason

        # 规则2: 单外显子基因过多 + 重复含量低
        single_exon_ratio = qc_results.get('structural', {}).get('single_exon_ratio', 0)
        if single_exon_ratio > 0.3 and repeat_content < 20:
            reason = "单外显子基因过多且重复含量低，softmasking 不足"
            self.logger.warning(f"触发回溯: {reason}")
            self.history.append(('structural', 'repeat', reason))
            return 'repeat', reason

        return None, None

    def record_backtrack(self, from_step, to_step, reason):
        """记录回溯历史"""
        self.history.append((from_step, to_step, reason))
        self.logger.info(f"回溯记录: {from_step} -> {to_step}, 原因: {reason}")
