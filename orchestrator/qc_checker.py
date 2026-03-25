import re
from pathlib import Path

class QCChecker:
    def __init__(self, thresholds):
        self.thresholds = thresholds

    def parse_busco(self, busco_file):
        """Parse BUSCO short_summary.txt"""
        if not Path(busco_file).exists():
            return {'complete': 0.0}

        with open(busco_file) as f:
            for line in f:
                if 'C:' in line:
                    match = re.search(r'C:(\d+\.?\d*)%', line)
                    if match:
                        return {'complete': float(match.group(1))}
        return {'complete': 0.0}

    def parse_quast(self, quast_file):
        """Parse QUAST report.tsv"""
        if not Path(quast_file).exists():
            return {'n50': 0}

        with open(quast_file) as f:
            for line in f:
                if line.startswith('N50'):
                    return {'n50': int(line.split('\t')[1])}
        return {'n50': 0}

    def check_assembly(self, qc_results):
        busco_ok = qc_results.get('busco', {}).get('complete', 0) >= self.thresholds['assembly']['busco_complete_min']
        n50_ok = qc_results.get('n50', 0) >= self.thresholds['assembly']['n50_min']
        return busco_ok and n50_ok, qc_results

    def check_repeat(self, qc_results, expected_content=0.4, species_profile=None):
        if species_profile:
            expected_content = species_profile.get('expected_repeat_content', 0.4)
        content = qc_results.get('repeat_content', 0)
        min_ok = content >= expected_content * self.thresholds['repeat']['content_min_ratio']
        max_ok = content <= expected_content * self.thresholds['repeat']['content_max_ratio']
        return min_ok and max_ok, qc_results

    def check_structural(self, qc_results):
        busco_ok = qc_results.get('busco', {}).get('complete', 0) >= self.thresholds['structural']['busco_protein_min']
        return busco_ok, qc_results

    def check_functional(self, qc_results):
        coverage = qc_results.get('annotation_coverage', 0)
        return coverage >= self.thresholds['functional']['annotation_coverage_min'], qc_results
