[**T-Developer API Reference v1.0.0**](../../README.md)

***

[T-Developer API Reference](../../modules.md) / [DocumentationStandards](../README.md) / ProjectService

# Class: ProjectService

Defined in: src/standards/documentation.ts:52

프로젝트 생성 서비스

 ProjectService

## Description

자연어 설명을 기반으로 프로젝트를 생성하고 관리하는 서비스

## Example

```typescript
const projectService = new ProjectService();
const project = await projectService.createProject({
  name: "My E-commerce Platform",
  description: "Create a modern e-commerce platform with React and Node.js"
});
```

## Constructors

### Constructor

> **new ProjectService**(): `ProjectService`

#### Returns

`ProjectService`

## Methods

### createProject()

> **createProject**(`dto`): `Promise`\<[`Project`](../interfaces/Project.md)\>

Defined in: src/standards/documentation.ts:70

새로운 프로젝트 생성

#### Parameters

##### dto

[`CreateProjectDto`](../interfaces/CreateProjectDto.md)

프로젝트 생성 정보

#### Returns

`Promise`\<[`Project`](../interfaces/Project.md)\>

생성된 프로젝트 정보

#### Throws

입력 데이터가 유효하지 않은 경우

#### Throws

프로젝트 생성 한도 초과

#### Since

1.0.0

#### Author

T-Developer Team
