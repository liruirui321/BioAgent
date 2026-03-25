import subprocess
from pathlib import Path

class ComparativeAgent:
    def __init__(self, logger):
        self.logger = logger

    def run(self, genome_files, protein_files, output_dir, threads=8):
        """
        比较基因组学分析

        Args:
            genome_files: list of genome fasta files
            protein_files: list of protein fasta files
            output_dir: output directory
            threads: number of threads
        """
        self.logger.info("Starting comparative genomics analysis")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # 1. Ortholog clustering
        ortho_dir = output_dir / 'orthofinder'
        results['ortholog'] = self._run_orthofinder(protein_files, ortho_dir, threads)

        # 2. Synteny analysis
        synteny_dir = output_dir / 'synteny'
        results['synteny'] = self._run_synteny(genome_files, protein_files, synteny_dir)

        # 3. Pan-genome analysis
        pangenome_dir = output_dir / 'pangenome'
        results['pangenome'] = self._calculate_pangenome(results['ortholog'], pangenome_dir)

        # 4. Gene CNV analysis
        cnv_dir = output_dir / 'cnv'
        results['cnv'] = self._analyze_cnv(results['ortholog'], cnv_dir)

        return results

    def _run_orthofinder(self, protein_files, output_dir, threads):
        """Run OrthoFinder for ortholog clustering"""
        self.logger.info("Running OrthoFinder")
        output_dir.mkdir(parents=True, exist_ok=True)

        # Create input directory
        input_dir = output_dir / 'input'
        input_dir.mkdir(exist_ok=True)
        for pf in protein_files:
            subprocess.run(['ln', '-s', pf, str(input_dir)], check=True)

        cmd = ['orthofinder', '-f', str(input_dir), '-t', str(threads), '-o', str(output_dir)]
        subprocess.run(cmd, check=True, capture_output=True)

        return {'orthogroups': str(output_dir / 'Results_*/Orthogroups/Orthogroups.tsv')}

    def _run_synteny(self, genome_files, protein_files, output_dir):
        """Run MCScanX for synteny analysis"""
        self.logger.info("Running synteny analysis")
        output_dir.mkdir(parents=True, exist_ok=True)

        synteny_results = []
        for i in range(len(genome_files)-1):
            for j in range(i+1, len(genome_files)):
                pair_dir = output_dir / f'pair_{i}_{j}'
                pair_dir.mkdir(exist_ok=True)

                # Run BLASTP
                blast_out = pair_dir / 'blast.out'
                cmd = ['blastp', '-query', protein_files[i], '-subject', protein_files[j],
                       '-outfmt', '6', '-out', str(blast_out), '-evalue', '1e-5']
                subprocess.run(cmd, check=True, capture_output=True)

                # Run MCScanX
                cmd = ['MCScanX', str(pair_dir / 'blast')]
                subprocess.run(cmd, check=True, capture_output=True)

                synteny_results.append(str(pair_dir / 'blast.collinearity'))

        return {'collinearity_files': synteny_results}

    def _calculate_pangenome(self, ortholog_result, output_dir):
        """Calculate pan-genome statistics"""
        self.logger.info("Calculating pan-genome")
        output_dir.mkdir(parents=True, exist_ok=True)

        ortho_file = ortholog_result['orthogroups']
        core, dispensable, private = 0, 0, 0

        with open(ortho_file) as f:
            for line in f:
                if line.startswith('OG'):
                    continue
                parts = line.strip().split('\t')
                species_count = sum(1 for p in parts[1:] if p)

                if species_count == len(parts) - 1:
                    core += 1
                elif species_count == 1:
                    private += 1
                else:
                    dispensable += 1

        stats = {'core': core, 'dispensable': dispensable, 'private': private}

        with open(output_dir / 'pangenome_stats.txt', 'w') as f:
            for k, v in stats.items():
                f.write(f"{k}\t{v}\n")

        return stats

    def _analyze_cnv(self, ortholog_result, output_dir):
        """Analyze gene copy number variations"""
        self.logger.info("Analyzing gene CNVs")
        output_dir.mkdir(parents=True, exist_ok=True)

        ortho_file = ortholog_result['orthogroups']
        cnv_genes = []

        with open(ortho_file) as f:
            for line in f:
                if line.startswith('OG'):
                    continue
                parts = line.strip().split('\t')
                gene_counts = [len(p.split(',')) if p else 0 for p in parts[1:]]

                if max(gene_counts) > 1:
                    cnv_genes.append(parts[0])

        with open(output_dir / 'cnv_genes.txt', 'w') as f:
            f.write('\n'.join(cnv_genes))

        return {'cnv_count': len(cnv_genes), 'cnv_file': str(output_dir / 'cnv_genes.txt')}
