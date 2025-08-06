import { EnvironmentPresetManager } from './environment-presets';

export async function runPresetCommand(command: string, args: string[] = []): Promise<void> {
  const manager = new EnvironmentPresetManager();
  
  switch (command) {
    case 'list':
      await manager.loadPresets();
      const presets = manager.listPresets();
      console.table(presets);
      break;
      
    case 'activate':
      if (!args[0]) throw new Error('Preset name required');
      await manager.loadPresets();
      await manager.activatePreset(args[0]);
      break;
      
    case 'deactivate':
      await manager.deactivatePreset();
      break;
      
    case 'create':
      if (!args[0]) throw new Error('Preset name required');
      const preset = {
        name: args[0],
        description: args[1] || 'Custom preset',
        env: {
          NODE_ENV: 'development',
          USE_MOCKS: false
        }
      };
      await manager.createPreset(args[0], preset);
      break;
      
    default:
      console.log('Available commands: list, activate <name>, deactivate, create <name>');
  }
}