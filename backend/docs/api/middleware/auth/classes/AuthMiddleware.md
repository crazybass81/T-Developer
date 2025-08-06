[**T-Developer API Reference v1.0.0**](../../../README.md)

***

[T-Developer API Reference](../../../modules.md) / [middleware/auth](../README.md) / AuthMiddleware

# Class: AuthMiddleware

Defined in: src/middleware/auth.ts:12

## Constructors

### Constructor

> **new AuthMiddleware**(): `AuthMiddleware`

Defined in: src/middleware/auth.ts:15

#### Returns

`AuthMiddleware`

## Methods

### authenticate()

> **authenticate**(`req`, `res`, `next`): `Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

Defined in: src/middleware/auth.ts:19

#### Parameters

##### req

`Request`

##### res

`Response`

##### next

`NextFunction`

#### Returns

`Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

***

### requireRole()

> **requireRole**(`role`): (`req`, `res`, `next`) => `undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>

Defined in: src/middleware/auth.ts:37

#### Parameters

##### role

`"user"` | `"admin"`

#### Returns

> (`req`, `res`, `next`): `undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>

##### Parameters

###### req

`Request`

###### res

`Response`

###### next

`NextFunction`

##### Returns

`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>
