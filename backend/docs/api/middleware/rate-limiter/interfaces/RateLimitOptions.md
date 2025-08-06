[**T-Developer API Reference v1.0.0**](../../../README.md)

***

[T-Developer API Reference](../../../modules.md) / [middleware/rate-limiter](../README.md) / RateLimitOptions

# Interface: RateLimitOptions

Defined in: src/middleware/rate-limiter.ts:4

## Properties

### keyGenerator()?

> `optional` **keyGenerator**: (`req`) => `string`

Defined in: src/middleware/rate-limiter.ts:8

#### Parameters

##### req

`Request`

#### Returns

`string`

***

### max

> **max**: `number`

Defined in: src/middleware/rate-limiter.ts:6

***

### message?

> `optional` **message**: `string`

Defined in: src/middleware/rate-limiter.ts:7

***

### windowMs

> **windowMs**: `number`

Defined in: src/middleware/rate-limiter.ts:5
