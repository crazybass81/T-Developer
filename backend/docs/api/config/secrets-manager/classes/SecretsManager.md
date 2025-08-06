[**T-Developer API Reference v1.0.0**](../../../README.md)

***

[T-Developer API Reference](../../../modules.md) / [config/secrets-manager](../README.md) / SecretsManager

# Class: SecretsManager

Defined in: src/config/secrets-manager.ts:8

## Constructors

### Constructor

> **new SecretsManager**(): `SecretsManager`

Defined in: src/config/secrets-manager.ts:13

#### Returns

`SecretsManager`

## Methods

### createOrUpdateSecret()

> **createOrUpdateSecret**(`secretName`, `secretValue`): `Promise`\<`void`\>

Defined in: src/config/secrets-manager.ts:51

#### Parameters

##### secretName

`string`

##### secretValue

`any`

#### Returns

`Promise`\<`void`\>

***

### getSecret()

> **getSecret**(`secretName`): `Promise`\<`any`\>

Defined in: src/config/secrets-manager.ts:19

#### Parameters

##### secretName

`string`

#### Returns

`Promise`\<`any`\>

***

### loadEnvironmentSecrets()

> **loadEnvironmentSecrets**(): `Promise`\<`void`\>

Defined in: src/config/secrets-manager.ts:84

#### Returns

`Promise`\<`void`\>
