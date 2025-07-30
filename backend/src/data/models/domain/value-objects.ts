// Value Objects for T-Developer domain

export class Email {
  private readonly value: string;

  constructor(email: string) {
    if (!this.isValid(email)) {
      throw new Error('Invalid email format');
    }
    this.value = email.toLowerCase();
  }

  private isValid(email: string): boolean {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  }

  toString(): string {
    return this.value;
  }

  equals(other: Email): boolean {
    return this.value === other.value;
  }
}

export class Version {
  private readonly major: number;
  private readonly minor: number;
  private readonly patch: number;

  constructor(version: string) {
    const parts = version.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid version format. Expected x.y.z');
    }
    
    this.major = parseInt(parts[0]);
    this.minor = parseInt(parts[1]);
    this.patch = parseInt(parts[2]);
    
    if (isNaN(this.major) || isNaN(this.minor) || isNaN(this.patch)) {
      throw new Error('Version parts must be numbers');
    }
  }

  toString(): string {
    return `${this.major}.${this.minor}.${this.patch}`;
  }

  isGreaterThan(other: Version): boolean {
    if (this.major !== other.major) return this.major > other.major;
    if (this.minor !== other.minor) return this.minor > other.minor;
    return this.patch > other.patch;
  }

  isCompatibleWith(other: Version): boolean {
    return this.major === other.major;
  }
}

export class ProjectName {
  private readonly value: string;

  constructor(name: string) {
    if (!name || name.trim().length === 0) {
      throw new Error('Project name cannot be empty');
    }
    if (name.length > 100) {
      throw new Error('Project name cannot exceed 100 characters');
    }
    if (!/^[a-zA-Z0-9\s\-_]+$/.test(name)) {
      throw new Error('Project name contains invalid characters');
    }
    this.value = name.trim();
  }

  toString(): string {
    return this.value;
  }

  toSlug(): string {
    return this.value.toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9\-]/g, '');
  }
}

export class AgentName {
  private readonly value: string;

  constructor(name: string) {
    if (!name || name.trim().length === 0) {
      throw new Error('Agent name cannot be empty');
    }
    if (!/^[a-z\-]+$/.test(name)) {
      throw new Error('Agent name must be lowercase with hyphens only');
    }
    this.value = name;
  }

  toString(): string {
    return this.value;
  }
}

export class QualityScore {
  private readonly value: number;

  constructor(score: number) {
    if (score < 0 || score > 10) {
      throw new Error('Quality score must be between 0 and 10');
    }
    this.value = Math.round(score * 10) / 10; // Round to 1 decimal
  }

  getValue(): number {
    return this.value;
  }

  isHigh(): boolean {
    return this.value >= 8;
  }

  isMedium(): boolean {
    return this.value >= 5 && this.value < 8;
  }

  isLow(): boolean {
    return this.value < 5;
  }
}