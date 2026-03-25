import yaml
from pathlib import Path
from agents.assembly_agent import AssemblyAgent
from agents.repeat_agent import RepeatAgent
from agents.structural_agent import StructuralAgent
from agents.functional_agent import FunctionalAgent
from orchestrator.qc_checker import QCChecker
from orchestrator.backtrack import BacktrackEngine
from utils.tool_selector import ToolSelector

class Orchestrator:
    def __init__(self, args, logger):
        self.args = args
        self.logger = logger
        self.output_dir = Path(args.output)

        # Load QC thresholds
        config_path = Path(__file__).parent.parent / 'config' / 'qc_thresholds.yaml'
        with open(config_path) as f:
            thresholds = yaml.safe_load(f)

        self.qc_checker = QCChecker(thresholds)
        self.backtrack_engine = BacktrackEngine(logger)
        self.tool_selector = ToolSelector()
        self.species_profile = self.tool_selector.get_species_profile(args.species)
        self.qc_results = {}

        # Log selected tools
        self.logger.info(f"Species: {args.species}")
        self.logger.info(f"Expected repeat content: {self.species_profile['expected_repeat_content']*100}%")
        self.logger.info(f"Expected gene count: {self.species_profile['expected_gene_count']}")

    def run(self):
        try:
            assembly_result = self._run_assembly()
            if not assembly_result:
                return False

            repeat_result = self._run_repeat(assembly_result)

            if not self.args.rnaseq:
                self.logger.warning("No RNA-seq data provided, skipping structural annotation")
                return True

            structural_result = self._run_structural(repeat_result)

            # Check backtracking
            target_step, reason = self.backtrack_engine.check_backtrack('structural', self.qc_results)
            if target_step == 'assembly':
                self.logger.info(f"回溯到组装步骤: {reason}")
                assembly_result = self._run_assembly()
                repeat_result = self._run_repeat(assembly_result)
                structural_result = self._run_structural(repeat_result)
            elif target_step == 'repeat':
                self.logger.info(f"回溯到重复注释步骤: {reason}")
                repeat_result = self._run_repeat(assembly_result)
                structural_result = self._run_structural(repeat_result)

            self._run_functional(structural_result)

            self.logger.info("=" * 60)
            self.logger.info("Pipeline completed successfully")
            self.logger.info("=" * 60)
            return True

        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            return False

    def _run_assembly(self):
        self.logger.info("=" * 60)
        self.logger.info("STEP 1: Genome Assembly")
        self.logger.info("=" * 60)
        assembly_agent = AssemblyAgent(self.logger)
        assembly_dir = self.output_dir / 'assembly'
        assembly_result = assembly_agent.run(
            self.args.input,
            assembly_dir,
            threads=self.args.threads,
            ploidy=self.args.ploidy
        )

        if not assembly_result:
            self.logger.error("Assembly failed")
            return None

        busco = self.qc_checker.parse_busco(assembly_result['busco_report'])
        quast = self.qc_checker.parse_quast(assembly_result['quast_report'])
        self.qc_results['assembly'] = {'busco': busco, 'n50': quast['n50']}
        passed, _ = self.qc_checker.check_assembly(self.qc_results['assembly'])
        self.logger.info(f"Assembly QC: {'PASS' if passed else 'FAIL'} - BUSCO: {busco['complete']}%, N50: {quast['n50']}")
        return assembly_result


    def _run_repeat(self, assembly_result):
        self.logger.info("=" * 60)
        self.logger.info("STEP 2: Repeat Annotation")
        self.logger.info("=" * 60)
        repeat_agent = RepeatAgent(self.logger)
        repeat_dir = self.output_dir / 'repeat'
        repeat_result = repeat_agent.run(
            assembly_result['assembly'],
            repeat_dir,
            threads=self.args.threads
        )

        self.qc_results['repeat'] = repeat_result
        passed, _ = self.qc_checker.check_repeat(self.qc_results['repeat'], species_profile=self.species_profile)
        self.logger.info(f"Repeat QC: {'PASS' if passed else 'FAIL'} - Content: {repeat_result['repeat_content']}%")
        return repeat_result

    def _run_structural(self, repeat_result):
        self.logger.info("=" * 60)
        self.logger.info("STEP 3: Structural Annotation")
        self.logger.info("=" * 60)
        structural_agent = StructuralAgent(self.logger)
        structural_dir = self.output_dir / 'structural'
        structural_result = structural_agent.run(
            repeat_result['masked_assembly'],
            self.args.rnaseq,
            structural_dir,
            threads=self.args.threads,
            species=self.args.species
        )

        busco = self.qc_checker.parse_busco(structural_result['busco_report'])
        self.qc_results['structural'] = {'busco': busco}
        passed, _ = self.qc_checker.check_structural(self.qc_results['structural'])
        self.logger.info(f"Structural QC: {'PASS' if passed else 'FAIL'} - BUSCO: {busco['complete']}%")
        return structural_result

    def _run_functional(self, structural_result):
        self.logger.info("=" * 60)
        self.logger.info("STEP 4: Functional Annotation")
        self.logger.info("=" * 60)
        functional_agent = FunctionalAgent(self.logger)
        functional_dir = self.output_dir / 'functional'
        functional_result = functional_agent.run(
            structural_result['proteins'],
            functional_dir,
            threads=self.args.threads
        )

        self.qc_results['functional'] = functional_result
        passed, _ = self.qc_checker.check_functional(self.qc_results['functional'])
        self.logger.info(f"Functional QC: {'PASS' if passed else 'FAIL'} - Coverage: {functional_result['annotation_coverage']}%")
        return functional_result
