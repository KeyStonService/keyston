import { Request, Response } from 'express';

import { sendSuccess, sendError, createTimestamp, getErrorMessage } from '../middleware/response';
import { ProvenanceService } from '../services/provenance';
import { PathValidationError } from '../errors';

export class ProvenanceController {
  private provenanceService: ProvenanceService;

  constructor() {
    this.provenanceService = new ProvenanceService();
  }

  /**
   * 創建構建認證
   */
  createAttestation = async (req: Request, res: Response): Promise<void> => {
    try {
      const { filePath, builder, metadata } = req.body;

      if (!filePath) {
        sendError(res, 'filePath is required', { status: 400, includeTimestamp: true });
        return;
      }

      if (!builder) {
        sendError(res, 'builder is required', { status: 400, includeTimestamp: true });
        return;
      }

      const attestation = await this.provenanceService.createBuildAttestation(
        filePath,
        builder,
        metadata
      );

      sendSuccess(res, attestation, {
        message: 'Build attestation created successfully',
        status: 201,
      });
    } catch (error) {
      const nodeError = error as NodeJS.ErrnoException;
      if (error instanceof PathValidationError || nodeError.code === 'ENOENT') {
        sendError(res, 'File not found', { status: 404, includeTimestamp: true });
      } else {
        sendError(res, getErrorMessage(error, 'Failed to create attestation'), {
          status: 500,
          includeTimestamp: true,
        });
      }
    }
  };

  /**
   * 驗證認證
   */
  verifyAttestation = async (req: Request, res: Response): Promise<void> => {
    try {
      const { attestation } = req.body;

      if (!attestation) {
        sendError(res, 'attestation is required', { status: 400, includeTimestamp: true });
        return;
      }

      const isValid = await this.provenanceService.verifyAttestation(attestation);

      sendSuccess(
        res,
        {
          valid: isValid,
          attestationId: attestation.id,
          timestamp: createTimestamp(),
        },
        {
          message: isValid ? 'Attestation is valid' : 'Attestation is invalid',
        }
      );
    } catch (error) {
      sendError(res, getErrorMessage(error, 'Failed to verify attestation'), {
        status: 500,
        includeTimestamp: true,
      });
    }
  };

  /**
   * 獲取文件摘要
   */
  getFileDigest = async (req: Request, res: Response): Promise<void> => {
    try {
      const filePath = req.params.filePath || req.params[0]; // 支援通配符路由

      if (!filePath) {
        sendError(res, 'filePath is required', { status: 404, includeTimestamp: true });
        return;
      }

      // 解碼URL編碼的路徑
      const decodedPath = decodeURIComponent(filePath);
      const digest = await this.provenanceService.generateFileDigest(decodedPath);

      sendSuccess(
        res,
        {
          filePath: decodedPath,
          digest,
          timestamp: createTimestamp(),
        },
        {
          message: 'File digest generated successfully',
        }
      );
    } catch (error) {
      const nodeError = error as NodeJS.ErrnoException;
      if (error instanceof PathValidationError || nodeError.code === 'ENOENT') {
        sendError(res, 'File not found', { status: 404, includeTimestamp: true });
      } else {
        sendError(res, getErrorMessage(error, 'Failed to generate file digest'), {
          status: 500,
          includeTimestamp: true,
        });
      }
    }
  };

  /**
   * 導入認證
   */
  importAttestation = async (req: Request, res: Response): Promise<void> => {
    try {
      const { attestationJson } = req.body;

      if (!attestationJson) {
        sendError(res, 'attestationJson is required', { status: 400, includeTimestamp: true });
        return;
      }

      const attestation = this.provenanceService.importAttestation(attestationJson);

      sendSuccess(res, attestation, {
        message: 'Attestation imported successfully',
      });
    } catch (error) {
      sendError(res, getErrorMessage(error, 'Invalid JSON data or attestation format'), {
        status: 400,
        includeTimestamp: true,
      });
    }
  };

  /**
   * 導出認證
   */
  exportAttestation = async (req: Request, res: Response): Promise<void> => {
    try {
      const { id } = req.params;

      // 這裡應該從數據庫獲取認證，現在返回格式化消息
      sendSuccess(
        res,
        {
          message: `Attestation export for ID: ${id}`,
          format: 'json',
          timestamp: createTimestamp(),
        },
        {
          message: 'Attestation export endpoint',
        }
      );
    } catch (error) {
      sendError(res, getErrorMessage(error, 'Failed to export attestation'), {
        status: 500,
        includeTimestamp: true,
      });
    }
  };
}
