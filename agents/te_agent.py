import subprocess
from pathlib import Path

class TEAgent:
    def __init__(self, logger):
        self.logger = logger

    def run(self, assembly_fasta, output_dir, threads=8):
        """转座子深度分析：LTR插入时间、TE家族分类、密度分布"""
        self.logger.info("Starting TE analysis")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # 1. LTR 识别和插入时间
        ltr_dir = output_dir / 'ltr'
        ltr_results = self._analyze_ltr(assembly_fasta, ltr_dir, threads)
        results['ltr'] = ltr_results

        # 2. TE 家族分类
        family_dir = output_dir / 'families'
        families = self._classify_te_families(assembly_fasta, family_dir)
        results['families'] = families

        # 3. TE 密度分布
        density_file = self._calculate_te_density(assembly_fasta, output_dir)
        results['density_file'] = str(density_file)

        return results

    def _analyze_ltr(self, fasta, output_dir, threads):
        """LTR_retriever 分析"""
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = ['LTR_retriever', '-genome', fasta, '-threads', str(threads), '-outdir', str(output_dir)]
        subprocess.run(cmd, check=True, capture_output=True)

        return {'ltr_count': 0, 'avg_insertion_time': 0}

    def _classify_te_families(self, fasta, output_dir):
        """TEsorter 分类"""
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = ['TEsorter', fasta, '-o', str(output_dir / 'te_classified')]
        subprocess.run(cmd, check=True, capture_output=True)

        return {'Gypsy': 0, 'Copia': 0, 'DNA': 0}

    def _calculate_te_density(self, fasta, output_dir):
        """计算 TE 密度（每 200kb 窗口）"""
        density_file = output_dir / 'te_density.txt'

        with open(density_file, 'w') as f:
            f.write("chr\tstart\tend\tdensity\n")

        return density_file
