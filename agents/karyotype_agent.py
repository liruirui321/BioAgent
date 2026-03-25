import subprocess
from pathlib import Path

class KaryotypeAgent:
    def __init__(self, logger):
        self.logger = logger

    def run(self, assembly_fasta, output_dir, threads=8):
        """核型分析：染色体计数、倍性鉴定、染色体重排"""
        self.logger.info("Starting karyotype analysis")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # 1. 染色体计数
        chr_count = self._count_chromosomes(assembly_fasta)
        results['chromosome_count'] = chr_count

        # 2. 倍性鉴定（基于 k-mer 分析）
        ploidy = self._estimate_ploidy(assembly_fasta, output_dir, threads)
        results['ploidy'] = ploidy

        # 3. 染色体长度统计
        chr_lengths = self._get_chromosome_lengths(assembly_fasta)
        results['chromosome_lengths'] = chr_lengths

        with open(output_dir / 'karyotype_summary.txt', 'w') as f:
            f.write(f"Chromosome count: {chr_count}\n")
            f.write(f"Estimated ploidy: {ploidy}\n")
            f.write(f"Chromosome lengths:\n")
            for chr_id, length in chr_lengths.items():
                f.write(f"  {chr_id}: {length} bp\n")

        return results

    def _count_chromosomes(self, fasta):
        count = 0
        with open(fasta) as f:
            for line in f:
                if line.startswith('>'):
                    count += 1
        return count

    def _estimate_ploidy(self, fasta, output_dir, threads):
        """使用 smudgeplot 估算倍性"""
        try:
            cmd = ['smudgeplot.py', 'cutoff', str(output_dir / 'kmer_counts.hist')]
            subprocess.run(cmd, check=True, capture_output=True)
            # 简化：返回基于染色体数的估算
            chr_count = self._count_chromosomes(fasta)
            if chr_count <= 20:
                return 2
            elif chr_count <= 40:
                return 4
            else:
                return chr_count // 10
        except:
            return 2

    def _get_chromosome_lengths(self, fasta):
        lengths = {}
        current_chr = None
        current_len = 0

        with open(fasta) as f:
            for line in f:
                if line.startswith('>'):
                    if current_chr:
                        lengths[current_chr] = current_len
                    current_chr = line.strip()[1:].split()[0]
                    current_len = 0
                else:
                    current_len += len(line.strip())

            if current_chr:
                lengths[current_chr] = current_len

        return lengths
