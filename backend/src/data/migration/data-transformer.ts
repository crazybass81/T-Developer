export interface TransformationRule<T, U> {
  name: string;
  condition: (item: T) => boolean;
  transform: (item: T) => U;
}

export class DataTransformer {
  private rules: Map<string, TransformationRule<any, any>[]> = new Map();

  addRule<T, U>(entityType: string, rule: TransformationRule<T, U>): void {
    if (!this.rules.has(entityType)) {
      this.rules.set(entityType, []);
    }
    this.rules.get(entityType)!.push(rule);
  }

  transform<T, U>(entityType: string, items: T[]): U[] {
    const entityRules = this.rules.get(entityType) || [];
    
    return items.map(item => {
      let transformed = item as any;
      
      for (const rule of entityRules) {
        if (rule.condition(transformed)) {
          transformed = rule.transform(transformed);
        }
      }
      
      return transformed as U;
    });
  }

  // Common transformation patterns
  static renameField<T>(oldField: string, newField: string): TransformationRule<T, T> {
    return {
      name: `rename-${oldField}-to-${newField}`,
      condition: (item: any) => item.hasOwnProperty(oldField),
      transform: (item: any) => {
        const transformed = { ...item };
        transformed[newField] = transformed[oldField];
        delete transformed[oldField];
        return transformed;
      }
    };
  }

  static addDefaultField<T>(field: string, defaultValue: any): TransformationRule<T, T> {
    return {
      name: `add-default-${field}`,
      condition: (item: any) => !item.hasOwnProperty(field),
      transform: (item: any) => ({
        ...item,
        [field]: defaultValue
      })
    };
  }

  static removeField<T>(field: string): TransformationRule<T, T> {
    return {
      name: `remove-${field}`,
      condition: (item: any) => item.hasOwnProperty(field),
      transform: (item: any) => {
        const transformed = { ...item };
        delete transformed[field];
        return transformed;
      }
    };
  }

  static transformValue<T>(field: string, transformer: (value: any) => any): TransformationRule<T, T> {
    return {
      name: `transform-${field}`,
      condition: (item: any) => item.hasOwnProperty(field),
      transform: (item: any) => ({
        ...item,
        [field]: transformer(item[field])
      })
    };
  }
}