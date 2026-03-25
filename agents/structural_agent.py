import subprocess
from pathlib import Path

class StructuralAgent:
    def __init__(self, logger):
        self.logger = logger

    def run(self, masked_assembly, rnaseq_bam, output_dir, threads=8, species='plant'):
        self.logger.info("Starting structural annotation with BRAKER3")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            'braker.pl',
            '--genome', masked_assembly,
            '--bam', rnaseq_bam,
            '--species', f'genome_{species}',
            '--workingdir', str(output_dir),
            '--threads', str(threads),
            '--softmasking'
        ]

        self.logger.info(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, capture_output=True)

        gff_file = output_dir / 'braker.gff3'
        protein_file = output_dir / 'braker.aa'

        # Run BUSCO on proteins
        busco_dir = output_dir / 'busco'
        self._run_busco(protein_file, busco_dir, threads)

        return {
            'gff': str(gff_file),
            'proteins': str(protein_file),
            'busco_report': str(busco_dir / 'short_summary.txt')
        }

    def _run_busco(self, protein_file, output_dir, threads):
        cmd = ['busco', '-i', str(protein_file), '-o', str(output_dir), '-m', 'proteins', '-c', str(threads), '--auto-lineage-euk']
        subprocess.run(cmd, check=True, capture_output=True)
