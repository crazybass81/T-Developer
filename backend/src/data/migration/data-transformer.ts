/**
 * Data Transformer for Migration Operations
 * Handles data transformation during schema changes
 */

export interface TransformRule {
  field: string;
  transformer: (value: any) => any;
  condition?: (item: any) => boolean;
}

export class DataTransformer {
  private rules: TransformRule[] = [];

  public addRule(rule: TransformRule): this {
    this.rules.push(rule);
    return this;
  }

  public transform(data: any): any {
    let transformed = { ...data };
    
    for (const rule of this.rules) {
      if (!rule.condition || rule.condition(transformed)) {
        if (transformed[rule.field] !== undefined) {
          transformed[rule.field] = rule.transformer(transformed[rule.field]);
        }
      }
    }
    
    return transformed;
  }

  public transformBatch(items: any[]): any[] {
    return items.map(item => this.transform(item));
  }
}