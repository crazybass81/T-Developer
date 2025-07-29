#!/usr/bin/env ts-node

import { EnvCrypto } from '../backend/src/utils/crypto';

async function generateKey(): Promise<void> {
  const crypto = new EnvCrypto();
  await crypto.generateKey();
}

if (require.main === module) {
  generateKey();
}