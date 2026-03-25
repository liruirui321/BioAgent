import subprocess
from pathlib import Path

class RepeatAgent:
    def __init__(self, logger):
        self.logger = logger

    def run(self, assembly_fasta, output_dir, threads=8):
        self.logger.info("Starting repeat annotation")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        # RepeatModeler
        db_name = output_dir / "repeat_db"
        self.logger.info("Building repeat library with RepeatModeler")
        subprocess.run(['BuildDatabase', '-name', str(db_name), assembly_fasta], check=True)
        subprocess.run(['RepeatModeler', '-database', str(db_name), '-threads', str(threads)], check=True)

        # RepeatMasker
        repeat_lib = output_dir / f"{db_name.name}-families.fa"
        masked_fasta = output_dir / "assembly.masked.fasta"
        self.logger.info("Masking repeats with RepeatMasker")
        subprocess.run([
            'RepeatMasker',
            '-lib', str(repeat_lib),
            '-xsmall',
            '-dir', str(output_dir),
            '-pa', str(threads),
            assembly_fasta
        ], check=True)

        return {
            'masked_assembly': str(masked_fasta),
            'repeat_library': str(repeat_lib),
            'repeat_content': self._calculate_repeat_content(output_dir)
        }

    def _calculate_repeat_content(self, output_dir):
        tbl_file = list(output_dir.glob('*.tbl'))
        if not tbl_file:
            return 0.0

        with open(tbl_file[0]) as f:
            for line in f:
                if 'total' in line.lower():
                    parts = line.split()
                    return float(parts[-1].strip('%'))
        return 0.0
