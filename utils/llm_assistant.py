import os
import json
import yaml
from pathlib import Path

class LLMAssistant:
    def __init__(self, logger):
        self.logger = logger
        config_path = Path(__file__).parent.parent / 'config' / 'llm_config.yaml'

        with open(config_path) as f:
            self.config = yaml.safe_load(f)

        self.enabled = self.config.get('enabled', False)

    def analyze_backtrack(self, qc_results):
        if not self.enabled:
            return None, None

        try:
            prompt = self._build_prompt(qc_results)
            response = self._call_llm(prompt)
            result = json.loads(response)

            if result.get('backtrack'):
                return result.get('target'), result.get('reason')
            return None, None

        except Exception as e:
            self.logger.error(f"LLM analysis failed: {e}")
            return None, None

    def _build_prompt(self, qc_results):
        template = self.config['prompt_template']
        return template.format(
            assembly_busco=qc_results.get('assembly', {}).get('busco', ).get('complete', 0),
            assembly_n50=qc_results.get('assembly', {}).get('n50', 0),
            repeat_content=qc_results.get('repeat', {}).get('repeat_content', 0),
            structural_busco=qc_results.get('structural', {}).get('busco', {}).get('complete', 0),
            single_exon_ratio=qc_results.get('structural', ).get('single_exon_ratio', 0)
        )

    def _call_llm(self, prompt):
        provider = self.config['llm']['provider']

        if provider == 'anthropic':
            return self._call_anthropic(prompt)
        elif provider == 'openai':
            return self._call_openai(prompt)

        raise ValueError(f"Unsupported provider: {provider}")

    def _call_anthropic(self, prompt):
        import anthropic
        api_key = os.getenv(self.config['llm']['api_key_env'])
        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model=self.config['llm']['model'],
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}]
        )
        return message.content[0].text

    def _call_openai(self, prompt):
        import openai
        api_key = os.getenv(self.config['llm']['api_key_env'])
        client = openai.OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=self.config['llm']['model'],
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
