[**T-Developer API Reference v1.0.0**](../../../README.md)

***

[T-Developer API Reference](../../../modules.md) / [utils/auth](../README.md) / AuthManager

# Class: AuthManager

Defined in: src/utils/auth.ts:10

## Constructors

### Constructor

> **new AuthManager**(): `AuthManager`

Defined in: src/utils/auth.ts:16

#### Returns

`AuthManager`

## Methods

### generateTokens()

> **generateTokens**(`payload`): `Promise`\<\{ `accessToken`: `string`; `refreshToken`: `string`; \}\>

Defined in: src/utils/auth.ts:25

#### Parameters

##### payload

[`TokenPayload`](../interfaces/TokenPayload.md)

#### Returns

`Promise`\<\{ `accessToken`: `string`; `refreshToken`: `string`; \}\>

***

### hashPassword()

> **hashPassword**(`password`): `Promise`\<`string`\>

Defined in: src/utils/auth.ts:70

#### Parameters

##### password

`string`

#### Returns

`Promise`\<`string`\>

***

### verifyAccessToken()

> **verifyAccessToken**(`token`): `Promise`\<[`TokenPayload`](../interfaces/TokenPayload.md)\>

Defined in: src/utils/auth.ts:48

#### Parameters

##### token

`string`

#### Returns

`Promise`\<[`TokenPayload`](../interfaces/TokenPayload.md)\>

***

### verifyPassword()

> **verifyPassword**(`password`, `hash`): `Promise`\<`boolean`\>

Defined in: src/utils/auth.ts:74

#### Parameters

##### password

`string`

##### hash

`string`

#### Returns

`Promise`\<`boolean`\>

***

### verifyRefreshToken()

> **verifyRefreshToken**(`token`): `Promise`\<\{ `userId`: `string`; \}\>

Defined in: src/utils/auth.ts:59

#### Parameters

##### token

`string`

#### Returns

`Promise`\<\{ `userId`: `string`; \}\>
