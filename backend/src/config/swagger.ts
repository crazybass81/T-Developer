import swaggerJsdoc from 'swagger-jsdoc';
import swaggerUi from 'swagger-ui-express';
import { Express } from 'express';

const swaggerOptions: swaggerJsdoc.Options = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'T-Developer API',
      version: '1.0.0',
      description: 'AI-powered multi-agent development platform API',
      contact: {
        name: 'T-Developer Team',
        email: 'support@t-developer.com'
      },
      license: {
        name: 'MIT',
        url: 'https://opensource.org/licenses/MIT'
      }
    },
    servers: [
      {
        url: 'http://localhost:8000/api/v1',
        description: 'Development server'
      },
      {
        url: 'https://api.t-developer.com/v1',
        description: 'Production server'
      }
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT'
        },
        apiKey: {
          type: 'apiKey',
          in: 'header',
          name: 'X-API-Key'
        }
      }
    }
  },
  apis: [
    './src/routes/*.ts',
    './src/models/*.ts',
    './src/controllers/*.ts'
  ]
};

export function setupSwagger(app: Express): void {
  const swaggerSpec = swaggerJsdoc(swaggerOptions);
  
  // Swagger UI
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec, {
    explorer: true,
    customCss: '.swagger-ui .topbar { display: none }',
    customSiteTitle: 'T-Developer API Documentation'
  }));
  
  // JSON spec endpoint
  app.get('/api-docs.json', (req, res) => {
    res.setHeader('Content-Type', 'application/json');
    res.send(swaggerSpec);
  });
}

/**
 * @swagger
 * components:
 *   schemas:
 *     Project:
 *       type: object
 *       required:
 *         - id
 *         - name
 *         - description
 *         - status
 *       properties:
 *         id:
 *           type: string
 *           description: Project unique identifier
 *         name:
 *           type: string
 *           description: Project name
 *         description:
 *           type: string
 *           description: Natural language project description
 *         projectType:
 *           type: string
 *           enum: [web, api, mobile, desktop, cli]
 *         status:
 *           type: string
 *           enum: [analyzing, building, testing, completed, failed]
 *         createdAt:
 *           type: string
 *           format: date-time
 */

/**
 * @swagger
 * /projects:
 *   post:
 *     summary: Create a new project
 *     tags: [Projects]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             required:
 *               - name
 *               - description
 *             properties:
 *               name:
 *                 type: string
 *                 description: Project name
 *               description:
 *                 type: string
 *                 description: Natural language project description
 *               projectType:
 *                 type: string
 *                 enum: [web, api, mobile, desktop, cli]
 *               targetPlatforms:
 *                 type: array
 *                 items:
 *                   type: string
 *     responses:
 *       201:
 *         description: Project created successfully
 *         content:
 *           application/json:
 *             schema:
 *               $ref: '#/components/schemas/Project'
 *       400:
 *         description: Invalid request
 *       401:
 *         description: Unauthorized
 */