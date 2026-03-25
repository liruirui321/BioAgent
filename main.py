#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path
from orchestrator.orchestrator import Orchestrator
from utils.logger import setup_logger

def main():
    parser = argparse.ArgumentParser(description='Genome Assembly Multi-Agent System')
    parser.add_argument('--input', required=True, help='Input HiFi reads (fq.gz)')
    parser.add_argument('--hic-r1', help='Hi-C R1 reads')
    parser.add_argument('--hic-r2', help='Hi-C R2 reads')
    parser.add_argument('--rnaseq', help='RNA-seq BAM file')
    parser.add_argument('--species', required=True, choices=['plant', 'animal', 'fungus'])
    parser.add_argument('--ploidy', type=int, default=2)
    parser.add_argument('--heterozygosity', choices=['low', 'medium', 'high'], default='medium')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--threads', type=int, default=8)

    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger = setup_logger(output_dir / 'audit.log')
    logger.info(f"Starting genome assembly pipeline with args: {args}")

    orchestrator = Orchestrator(args, logger)
    success = orchestrator.run()

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()
