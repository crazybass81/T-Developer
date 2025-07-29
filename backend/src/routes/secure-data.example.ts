import express from 'express';
import { APISecurityMiddleware } from '../security/api-security';
import { EncryptionMiddleware, DataMasking } from '../security/encryption';

const router = express.Router();

// Apply security middleware
router.use(APISecurityMiddleware.apiKeyAuth(['projects:read']));

// Endpoint with encrypted response
router.get('/sensitive-data',
  EncryptionMiddleware.encryptResponse(['personalInfo.ssn', 'personalInfo.creditCard']),
  (req, res) => {
    res.json({
      id: 'user123',
      name: 'John Doe',
      personalInfo: {
        ssn: '123-45-6789',
        creditCard: '1234-5678-9012-3456',
        email: 'john@example.com'
      }
    });
  }
);

// Endpoint with decrypted request
router.post('/update-sensitive',
  EncryptionMiddleware.decryptRequest(['personalInfo.ssn']),
  (req, res) => {
    res.json({
      message: 'Data updated',
      received: req.body
    });
  }
);

// Endpoint with data masking
router.get('/masked-data', (req, res) => {
  const userData = {
    name: 'John Doe',
    email: 'john@example.com',
    phone: '123-456-7890',
    creditCard: '1234-5678-9012-3456'
  };

  const maskedData = DataMasking.maskObject(userData, ['email', 'phone', 'creditCard']);
  
  res.json(maskedData);
});

export default router;