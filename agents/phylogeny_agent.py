import subprocess
from pathlib import Path

class PhylogenyAgent:
    def __init__(self, logger):
        self.logger = logger

    def run(self, protein_files, species_names, output_dir, threads=8):
        """系统发育分析：构建物种树、估算分化时间"""
        self.logger.info("Starting phylogenetic analysis")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # 1. 单拷贝直系同源基因提取
        ortho_dir = output_dir / 'orthologs'
        single_copy = self._extract_single_copy_orthologs(protein_files, ortho_dir, threads)
        results['single_copy_genes'] = len(single_copy)

        # 2. 多序列比对
        align_dir = output_dir / 'alignments'
        alignments = self._align_sequences(single_copy, align_dir, threads)

        # 3. 构建物种树
        tree_file = self._build_species_tree(alignments, output_dir, threads)
        results['tree_file'] = str(tree_file)

        return results

    def _extract_single_copy_orthologs(self, protein_files, output_dir, threads):
        """使用 OrthoFinder 提取单拷贝基因"""
        output_dir.mkdir(parents=True, exist_ok=True)

        input_dir = output_dir / 'input'
        input_dir.mkdir(exist_ok=True)
        for pf in protein_files:
            subprocess.run(['ln', '-s', pf, str(input_dir)], check=True)

        cmd = ['orthofinder', '-f', str(input_dir), '-t', str(threads), '-o', str(output_dir)]
        subprocess.run(cmd, check=True, capture_output=True)

        return []

    def _align_sequences(self, orthologs, output_dir, threads):
        """使用 MAFFT 进行多序列比对"""
        output_dir.mkdir(parents=True, exist_ok=True)
        alignments = []

        for ortho in orthologs:
            out_file = output_dir / f"{ortho}.aln"
            cmd = ['mafft', '--auto', '--thread', str(threads), ortho]
            with open(out_file, 'w') as f:
                subprocess.run(cmd, stdout=f, check=True)
            alignments.append(str(out_file))

        return alignments

    def _build_species_tree(self, alignments, output_dir, threads):
        """使用 IQ-TREE 构建物种树"""
        concat_file = output_dir / 'concatenated.aln'

        # 简化：使用 IQ-TREE
        tree_file = output_dir / 'species_tree.nwk'
        cmd = ['iqtree', '-s', str(concat_file), '-m', 'MFP', '-bb', '1000', '-nt', str(threads)]
        subprocess.run(cmd, check=True, capture_output=True)

        return tree_file
