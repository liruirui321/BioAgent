import subprocess
from pathlib import Path

class AssemblyAgent:
    def __init__(self, logger):
        self.logger = logger

    def run(self, input_reads, output_dir, threads=8, ploidy=2):
        self.logger.info("Starting assembly with hifiasm")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        prefix = output_dir / "assembly"
        cmd = [
            'hifiasm',
            '-o', str(prefix),
            '-t', str(threads),
            '--primary',
            input_reads
        ]

        self.logger.info(f"Running: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True, capture_output=True, text=True)

            # Convert GFA to FASTA
            gfa_file = f"{prefix}.bp.p_ctg.gfa"
            fasta_file = output_dir / "assembly.fasta"
            self._gfa_to_fasta(gfa_file, fasta_file)

            # Run QUAST
            quast_dir = output_dir / "quast"
            self._run_quast(fasta_file, quast_dir, threads)

            # Run BUSCO
            busco_dir = output_dir / "busco"
            self._run_busco(fasta_file, busco_dir, threads)

            return {
                'assembly': str(fasta_file),
                'quast_report': str(quast_dir / 'report.tsv'),
                'busco_report': str(busco_dir / 'short_summary.txt')
            }
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Assembly failed: {e}")
            return None

    def _gfa_to_fasta(self, gfa_file, fasta_file):
        with open(gfa_file) as f, open(fasta_file, 'w') as out:
            for line in f:
                if line.startswith('S'):
                    parts = line.strip().split('\t')
                    out.write(f">{parts[1]}\n{parts[2]}\n")

    def _run_quast(self, fasta, output_dir, threads):
        cmd = ['quast.py', '-o', str(output_dir), '-t', str(threads), str(fasta)]
        subprocess.run(cmd, check=True, capture_output=True)

    def _run_busco(self, fasta, output_dir, threads):
        cmd = ['busco', '-i', str(fasta), '-o', str(output_dir), '-m', 'genome', '-c', str(threads), '--auto-lineage-euk']
        subprocess.run(cmd, check=True, capture_output=True)
