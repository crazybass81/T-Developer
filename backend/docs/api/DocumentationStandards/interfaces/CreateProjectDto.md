[**T-Developer API Reference v1.0.0**](../../README.md)

***

[T-Developer API Reference](../../modules.md) / [DocumentationStandards](../README.md) / CreateProjectDto

# Interface: CreateProjectDto

Defined in: src/standards/documentation.ts:10

프로젝트 생성 요청 DTO

## Properties

### description

> **description**: `string`

Defined in: src/standards/documentation.ts:14

자연어 프로젝트 설명

***

### name

> **name**: `string`

Defined in: src/standards/documentation.ts:12

프로젝트 이름

***

### projectType?

> `optional` **projectType**: `"api"` \| `"mobile"` \| `"web"` \| `"desktop"` \| `"cli"`

Defined in: src/standards/documentation.ts:16

프로젝트 타입

***

### targetPlatforms?

> `optional` **targetPlatforms**: `string`[]

Defined in: src/standards/documentation.ts:18

대상 플랫폼 목록
