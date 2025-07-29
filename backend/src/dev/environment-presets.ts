import { promises as fs } from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import { spawn, exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface EnvironmentPreset {
  name: string;
  description: string;
  env?: Record<string, string>;
  services?: ServiceConfig[];
  mocks?: { enabled: boolean; services?: string[] };
  scripts?: { setup?: string[]; teardown?: string[] };
}

interface ServiceConfig {
  name: string;
  type: 'docker' | 'process';
  image?: string;
  command?: string;
  ports?: string[];
  env?: Record<string, string>;
}

export class EnvironmentPresetManager {
  private presets: Map<string, EnvironmentPreset> = new Map();
  private currentPreset?: string;
  
  constructor(private presetsDir: string = './config/presets') {}
  
  async loadPresets(): Promise<void> {
    try {
      const files = await fs.readdir(this.presetsDir);
      
      for (const file of files.filter(f => f.endsWith('.yaml'))) {
        const content = await fs.readFile(path.join(this.presetsDir, file), 'utf-8');
        const preset = yaml.load(content) as EnvironmentPreset;
        const name = path.basename(file, '.yaml');
        
        this.presets.set(name, preset);
        console.log(`📦 Loaded preset: ${name}`);
      }
    } catch (error) {
      console.warn('No presets directory found, using defaults');
      this.loadDefaultPresets();
    }
  }
  
  async activatePreset(name: string): Promise<void> {
    const preset = this.presets.get(name);
    if (!preset) throw new Error(`Preset '${name}' not found`);
    
    console.log(`🚀 Activating preset: ${name}`);
    
    // Apply environment variables
    if (preset.env) {
      Object.entries(preset.env).forEach(([key, value]) => {
        process.env[key] = value;
      });
    }
    
    // Start services
    if (preset.services) {
      await this.startServices(preset.services);
    }
    
    // Run setup scripts
    if (preset.scripts?.setup) {
      await this.runScripts(preset.scripts.setup);
    }
    
    this.currentPreset = name;
    console.log(`✅ Preset '${name}' activated`);
  }
  
  async deactivatePreset(): Promise<void> {
    if (!this.currentPreset) return;
    
    const preset = this.presets.get(this.currentPreset);
    if (!preset) return;
    
    console.log(`🛑 Deactivating preset: ${this.currentPreset}`);
    
    // Run teardown scripts
    if (preset.scripts?.teardown) {
      await this.runScripts(preset.scripts.teardown);
    }
    
    // Stop services
    if (preset.services) {
      await this.stopServices(preset.services);
    }
    
    this.currentPreset = undefined;
  }
  
  private async startServices(services: ServiceConfig[]): Promise<void> {
    for (const service of services) {
      console.log(`🔧 Starting service: ${service.name}`);
      
      if (service.type === 'docker') {
        const args = ['run', '--rm', '-d', '--name', `t-dev-${service.name}`];
        
        if (service.ports) {
          service.ports.forEach(port => args.push('-p', port));
        }
        
        if (service.env) {
          Object.entries(service.env).forEach(([key, value]) => {
            args.push('-e', `${key}=${value}`);
          });
        }
        
        args.push(service.image!);
        
        spawn('docker', args, { detached: true, stdio: 'ignore' });
      } else if (service.type === 'process' && service.command) {
        const [cmd, ...args] = service.command.split(' ');
        spawn(cmd, args, { 
          detached: true, 
          stdio: 'ignore',
          env: { ...process.env, ...service.env }
        });
      }
    }
  }
  
  private async stopServices(services: ServiceConfig[]): Promise<void> {
    for (const service of services) {
      if (service.type === 'docker') {
        try {
          await execAsync(`docker stop t-dev-${service.name}`);
        } catch (error) {
          // Service might not be running
        }
      }
    }
  }
  
  private async runScripts(scripts: string[]): Promise<void> {
    for (const script of scripts) {
      console.log(`📜 Running: ${script}`);
      try {
        const { stdout } = await execAsync(script);
        if (stdout) console.log(stdout);
      } catch (error) {
        console.error(`Script failed: ${script}`);
      }
    }
  }
  
  listPresets(): Array<{ name: string; description: string; active: boolean }> {
    return Array.from(this.presets.entries()).map(([name, preset]) => ({
      name,
      description: preset.description,
      active: name === this.currentPreset
    }));
  }
  
  private loadDefaultPresets(): void {
    const defaults: Record<string, EnvironmentPreset> = {
      minimal: {
        name: 'minimal',
        description: 'Minimal setup for quick development',
        env: {
          NODE_ENV: 'development',
          USE_MOCKS: 'false',
          LOG_LEVEL: 'debug'
        },
        services: [{
          name: 'dynamodb',
          type: 'docker',
          image: 'amazon/dynamodb-local',
          ports: ['8000:8000']
        }]
      },
      'full-mocks': {
        name: 'full-mocks',
        description: 'All services mocked for offline development',
        env: {
          NODE_ENV: 'development',
          USE_MOCKS: 'true',
          MOCK_BEDROCK: 'true',
          MOCK_DYNAMODB: 'true',
          MOCK_S3: 'true'
        },
        mocks: {
          enabled: true,
          services: ['bedrock', 'dynamodb', 's3']
        }
      },
      testing: {
        name: 'testing',
        description: 'Environment for integration testing',
        env: {
          NODE_ENV: 'test',
          USE_MOCKS: 'true',
          LOG_LEVEL: 'error'
        },
        services: [
          {
            name: 'dynamodb',
            type: 'docker',
            image: 'amazon/dynamodb-local',
            ports: ['8000:8000']
          },
          {
            name: 'redis',
            type: 'docker',
            image: 'redis:7-alpine',
            ports: ['6379:6379']
          }
        ],
        scripts: {
          setup: ['npm run test:setup'],
          teardown: ['npm run test:cleanup']
        }
      }
    };
    
    Object.entries(defaults).forEach(([name, preset]) => {
      this.presets.set(name, preset);
    });
  }
}