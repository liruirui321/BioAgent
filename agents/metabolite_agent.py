import subprocess
from pathlib import Path

class MetaboliteAgent:
    def __init__(self, logger):
        self.logger = logger

    def run(self, protein_file, gff_file, output_dir, species='plant'):
        """次生代谢物分析：代谢通路预测、关键酶基因鉴定"""
        self.logger.info("Starting metabolite pathway analysis")
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {}

        # 1. KEGG 通路注释
        kegg_dir = output_dir / 'kegg'
        kegg_results = self._annotate_kegg(protein_file, kegg_dir)
        results['kegg'] = kegg_results

        # 2. 关键酶基因鉴定
        enzyme_dir = output_dir / 'enzymes'
        enzymes = self._identify_key_enzymes(protein_file, enzyme_dir, species)
        results['enzymes'] = enzymes

        # 3. 代谢通路可视化
        pathway_file = self._visualize_pathways(kegg_results, output_dir)
        results['pathway_map'] = str(pathway_file)

        return results

    def _annotate_kegg(self, protein_file, output_dir):
        """KEGG 注释"""
        output_dir.mkdir(parents=True, exist_ok=True)

        cmd = ['kofamscan', '-o', str(output_dir / 'kegg.txt'), protein_file]
        subprocess.run(cmd, check=True, capture_output=True)

        return {'pathways': [], 'ko_count': 0}

    def _identify_key_enzymes(self, protein_file, output_dir, species):
        """鉴定次生代谢关键酶"""
        output_dir.mkdir(parents=True, exist_ok=True)

        key_enzymes = {
            'plant': ['CHS', 'CHI', 'F3H', 'DFR', 'ANS', 'PAL', 'C4H'],
            'animal': [],
            'fungus': []
        }

        enzymes_found = {}
        for enzyme in key_enzymes.get(species, []):
            cmd = ['hmmsearch', '--tblout', str(output_dir / f'{enzyme}.out'),
                   f'{enzyme}.hmm', protein_file]
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                enzymes_found[enzyme] = 0
            except:
                pass

        return enzymes_found

    def _visualize_pathways(self, kegg_results, output_dir):
        """生成代谢通路图"""
        pathway_file = output_dir / 'pathways.html'

        with open(pathway_file, 'w') as f:
            f.write("<html><body><h1>Metabolic Pathways</h1></body></html>")

        return pathway_file
