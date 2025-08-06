[**T-Developer API Reference v1.0.0**](../../../README.md)

***

[T-Developer API Reference](../../../modules.md) / [middleware/rate-limiter](../README.md) / RateLimiter

# Class: RateLimiter

Defined in: src/middleware/rate-limiter.ts:11

## Constructors

### Constructor

> **new RateLimiter**(): `RateLimiter`

Defined in: src/middleware/rate-limiter.ts:14

#### Returns

`RateLimiter`

## Methods

### apiLimits()

> **apiLimits**(): `object`

Defined in: src/middleware/rate-limiter.ts:66

#### Returns

`object`

##### ai()

> **ai**: (`req`, `res`, `next`) => `Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

###### Parameters

###### req

`Request`

###### res

`Response`

###### next

`NextFunction`

###### Returns

`Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

##### auth()

> **auth**: (`req`, `res`, `next`) => `Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

###### Parameters

###### req

`Request`

###### res

`Response`

###### next

`NextFunction`

###### Returns

`Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

##### create()

> **create**: (`req`, `res`, `next`) => `Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

###### Parameters

###### req

`Request`

###### res

`Response`

###### next

`NextFunction`

###### Returns

`Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

##### general()

> **general**: (`req`, `res`, `next`) => `Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

###### Parameters

###### req

`Request`

###### res

`Response`

###### next

`NextFunction`

###### Returns

`Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

***

### middleware()

> **middleware**(`options`): (`req`, `res`, `next`) => `Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

Defined in: src/middleware/rate-limiter.ts:22

#### Parameters

##### options

[`RateLimitOptions`](../interfaces/RateLimitOptions.md)

#### Returns

> (`req`, `res`, `next`): `Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>

##### Parameters

###### req

`Request`

###### res

`Response`

###### next

`NextFunction`

##### Returns

`Promise`\<`undefined` \| `Response`\<`any`, `Record`\<`string`, `any`\>\>\>
