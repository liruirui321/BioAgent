import yaml
from pathlib import Path

class ToolSelector:
    def __init__(self):
        config_dir = Path(__file__).parent.parent / 'config'

        with open(config_dir / 'tools.yaml') as f:
            self.tools = yaml.safe_load(f)

        with open(config_dir / 'species_profiles.yaml') as f:
            self.species_profiles = yaml.safe_load(f)

    def get_assembly_tool(self, data_type='hifi', species='plant'):
        tools = self.tools['assembly'].get(data_type, [])
        for tool in sorted(tools, key=lambda x: x['priority']):
            if species in tool['species']:
                return tool['name']
        return 'hifiasm'

    def get_repeat_tools(self, species='plant'):
        denovo = self.tools['repeat']['denovo'][0]['name']
        masking = self.tools['repeat']['masking'][0]['name']
        return denovo, masking

    def get_structural_tool(self, species='plant', has_rnaseq=True):
        for tool in sorted(self.tools['structural'], key=lambda x: x['priority']):
            if species in tool['species']:
                if 'requires' in tool and 'rnaseq' in tool['requires'] and not has_rnaseq:
                    continue
                return tool['name']
        return 'BRAKER3'

    def get_functional_tool(self, species='plant'):
        for tool in sorted(self.tools['functional'], key=lambda x: x['priority']):
            if species in tool['species']:
                return tool['name']
        return 'eggNOG-mapper'

    def get_species_profile(self, species):
        return self.species_profiles.get(species, self.species_profiles['plant'])
