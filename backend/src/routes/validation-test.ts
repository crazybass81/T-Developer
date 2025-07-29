import { Router } from 'express';
import { validate, validationSchemas } from '../security/input-validation';

const router = Router();

router.post('/project', validate(validationSchemas.createProject), (req, res) => {
  res.json({
    message: 'Project validation passed',
    data: req.body
  });
});

router.post('/user', validate(validationSchemas.registerUser), (req, res) => {
  res.json({
    message: 'User validation passed',
    data: req.body
  });
});

export default router;