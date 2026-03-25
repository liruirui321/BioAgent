import subprocess
from pathlib import Path

class FunctionalAgent:
    def __init__(self, logger):
        self.logger = logger

    def run(self, protein_file, output_dir, threads=8):
        self.logger.info("Starting functional annotation with eggNOG-mapper")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = [
            'emapper.py',
            '-i', protein_file,
            '--output', 'annotation',
            '--output_dir', str(output_dir),
            '--cpu', str(threads),
            '-m', 'diamond'
        ]

        self.logger.info(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, check=True, capture_output=True)

        annotation_file = output_dir / 'annotation.emapper.annotations'
        coverage = self._calculate_coverage(annotation_file)

        return {
            'annotation_file': str(annotation_file),
            'annotation_coverage': coverage
        }

    def _calculate_coverage(self, annotation_file):
        if not Path(annotation_file).exists():
            return 0.0

        total = 0
        annotated = 0
        with open(annotation_file) as f:
            for line in f:
                if line.startswith('#'):
                    continue
                total += 1
                if line.split('\t')[5] != '-':
                    annotated += 1

        return (annotated / total * 100) if total > 0 else 0.0
