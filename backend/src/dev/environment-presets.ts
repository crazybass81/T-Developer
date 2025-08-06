import { promises as fs } from 'fs';
import path from 'path';
import yaml from 'js-yaml';
import dotenv from 'dotenv';
import { spawn, exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

interface EnvironmentPreset {
  name: string;
  description: string;
  env?: Record<string, string | number | boolean>;
  services?: ServiceConfig[];
  mocks?: MockConfig;
  data?: DataConfig;
  scripts?: {
    setup?: string[];
    teardown?: string[];
  };
}

interface ServiceConfig {
  name: string;
  type: 'docker' | 'process' | 'mock';
  image?: string;
  command?: string;
  ports?: string[];
  env?: Record<string, string>;
  cwd?: string;
}

interface MockConfig {
  enabled: boolean;
  services?: string[];
  latency?: { min: number; max: number };
  errors?: { rate: number };
}

interface DataConfig {
  target: string;
  generators?: Array<{ type: string; count: number }>;
}

interface PresetInfo {
  name: string;
  description: string;
  active: boolean;
}

export class EnvironmentPresetManager {
  private presets: Map<string, EnvironmentPreset> = new Map();
  private currentPreset?: string;
  
  constructor(private presetsDir: string = './config/presets') {}
  
  async loadPresets(): Promise<void> {
    try {
      const files = await fs.readdir(this.presetsDir);
      
      for (const file of files) {
        if (file.endsWith('.yaml') || file.endsWith('.yml')) {
          const content = await fs.readFile(path.join(this.presetsDir, file), 'utf-8');
          const preset = yaml.load(content) as EnvironmentPreset;
          const name = path.basename(file, path.extname(file));
          
          this.presets.set(name, preset);
          console.log(`📦 Loaded preset: ${name}`);
        }
      }
    } catch (error) {
      console.warn('Presets directory not found, creating default presets');
      await this.createDefaultPresets();
    }
  }
  
  async activatePreset(name: string): Promise<void> {
    const preset = this.presets.get(name);
    if (!preset) throw new Error(`Preset '${name}' not found`);
    
    console.log(`🚀 Activating preset: ${name}`);
    
    if (preset.env) await this.applyEnvironmentVariables(preset.env);
    if (preset.services) await this.startServices(preset.services);
    if (preset.mocks) await this.configureMocks(preset.mocks);
    if (preset.scripts?.setup) await this.runScripts(preset.scripts.setup);
    
    this.currentPreset = name;
    console.log(`✅ Preset '${name}' activated`);
  }
  
  async deactivatePreset(): Promise<void> {
    if (!this.currentPreset) return;
    
    const preset = this.presets.get(this.currentPreset);
    if (!preset) return;
    
    console.log(`🛑 Deactivating preset: ${this.currentPreset}`);
    
    if (preset.scripts?.teardown) await this.runScripts(preset.scripts.teardown);
    if (preset.services) await this.stopServices(preset.services);
    
    this.currentPreset = undefined;
  }
  
  private async applyEnvironmentVariables(env: Record<string, string | number | boolean>): Promise<void> {
    Object.entries(env).forEach(([key, value]) => {
      process.env[key] = String(value);
    });
    
    const envPath = path.join(process.cwd(), '.env.preset');
    const envContent = Object.entries(env)
      .map(([key, value]) => `${key}=${value}`)
      .join('\n');
    
    await fs.writeFile(envPath, envContent);
    dotenv.config({ path: envPath, override: true });
  }
  
  private async startServices(services: ServiceConfig[]): Promise<void> {
    for (const service of services) {
      console.log(`🔧 Starting service: ${service.name}`);
      
      if (service.type === 'docker') {
        await this.startDockerService(service);
      }
    }
  }
  
  private async startDockerService(service: ServiceConfig): Promise<void> {
    const args = ['run', '--rm', '-d'];
    
    if (service.ports) {
      service.ports.forEach(port => args.push('-p', port));
    }
    
    if (service.env) {
      Object.entries(service.env).forEach(([key, value]) => {
        args.push('-e', `${key}=${value}`);
      });
    }
    
    args.push('--name', `t-dev-${service.name}`, service.image!);
    
    const docker = spawn('docker', args);
    docker.on('error', (error) => {
      console.error(`Failed to start ${service.name}:`, error);
    });
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
  
  private async configureMocks(mocks: MockConfig): Promise<void> {
    if (mocks.latency) {
      process.env.MOCK_LATENCY_MIN = String(mocks.latency.min);
      process.env.MOCK_LATENCY_MAX = String(mocks.latency.max);
    }
    
    if (mocks.errors) {
      process.env.MOCK_ERROR_RATE = String(mocks.errors.rate);
    }
  }
  
  private async runScripts(scripts: string[]): Promise<void> {
    for (const script of scripts) {
      console.log(`📜 Running script: ${script}`);
      
      try {
        const { stdout, stderr } = await execAsync(script);
        if (stdout) console.log(stdout);
        if (stderr) console.error(stderr);
      } catch (error) {
        console.error(`Script failed: ${script}`, error);
      }
    }
  }
  
  listPresets(): PresetInfo[] {
    return Array.from(this.presets.entries()).map(([name, preset]) => ({
      name,
      description: preset.description,
      active: name === this.currentPreset
    }));
  }
  
  async createPreset(name: string, config: EnvironmentPreset): Promise<void> {
    await fs.mkdir(this.presetsDir, { recursive: true });
    
    const filePath = path.join(this.presetsDir, `${name}.yaml`);
    const content = yaml.dump(config);
    
    await fs.writeFile(filePath, content);
    this.presets.set(name, config);
    
    console.log(`✅ Created preset: ${name}`);
  }
  
  private async createDefaultPresets(): Promise<void> {
    await fs.mkdir(this.presetsDir, { recursive: true });
    
    const presets = {
      minimal: {
        name: 'minimal',
        description: 'Minimal setup for quick development',
        env: {
          NODE_ENV: 'development',
          USE_MOCKS: false,
          LOG_LEVEL: 'debug'
        },
        services: [{
          name: 'dynamodb',
          type: 'docker' as const,
          image: 'amazon/dynamodb-local',
          ports: ['8000:8000']
        }]
      },
      'full-mocks': {
        name: 'full-mocks',
        description: 'All services mocked for offline development',
        env: {
          NODE_ENV: 'development',
          USE_MOCKS: true,
          MOCK_LATENCY: true
        },
        mocks: {
          enabled: true,
          services: ['bedrock', 'dynamodb', 's3'],
          latency: { min: 100, max: 500 }
        }
      }
    };
    
    for (const [name, preset] of Object.entries(presets)) {
      await this.createPreset(name, preset);
    }
  }
}