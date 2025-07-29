#!/usr/bin/env ts-node

import { Command } from 'commander';
import { EnvironmentPresetManager } from '../backend/src/dev/environment-presets';
import chalk from 'chalk';

const program = new Command();
const manager = new EnvironmentPresetManager();

program
  .name('preset')
  .description('Manage development environment presets')
  .version('1.0.0');

program
  .command('list')
  .description('List available presets')
  .action(async () => {
    await manager.loadPresets();
    const presets = manager.listPresets();
    
    console.log(chalk.blue('\n📦 Available Presets:'));
    presets.forEach(preset => {
      const status = preset.active ? chalk.green('(active)') : '';
      console.log(`  ${preset.name} - ${preset.description} ${status}`);
    });
  });

program
  .command('activate <name>')
  .description('Activate a preset')
  .action(async (name: string) => {
    await manager.loadPresets();
    await manager.activatePreset(name);
  });

program
  .command('deactivate')
  .description('Deactivate current preset')
  .action(async () => {
    await manager.deactivatePreset();
  });

program.parse();