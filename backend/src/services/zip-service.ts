/**
 * ZIP Service
 * 프로젝트를 ZIP 파일로 압축하는 서비스
 */

import * as fs from 'fs-extra';
import * as path from 'path';
import archiver from 'archiver';
import { v4 as uuidv4 } from 'uuid';

export class ZipService {
  private downloadPath: string;

  constructor() {
    this.downloadPath = path.join(__dirname, '../../../downloads');
    fs.ensureDirSync(this.downloadPath);
  }

  /**
   * 프로젝트를 ZIP 파일로 압축
   */
  async createZip(projectPath: string, projectName: string): Promise<string> {
    return new Promise((resolve, reject) => {
      const zipFileName = `${projectName}-${uuidv4().slice(0, 8)}.zip`;
      const zipFilePath = path.join(this.downloadPath, zipFileName);
      
      // ZIP 파일 생성
      const output = fs.createWriteStream(zipFilePath);
      const archive = archiver('zip', {
        zlib: { level: 9 } // 최대 압축
      });

      output.on('close', () => {
        console.log(`ZIP created: ${archive.pointer()} bytes`);
        resolve(zipFilePath);
      });

      output.on('end', () => {
        console.log('Data has been drained');
      });

      archive.on('warning', (err) => {
        if (err.code === 'ENOENT') {
          console.warn('ZIP Warning:', err);
        } else {
          reject(err);
        }
      });

      archive.on('error', (err) => {
        reject(err);
      });

      // 파이프 설정
      archive.pipe(output);

      // 프로젝트 폴더 추가
      archive.directory(projectPath, projectName);

      // 압축 완료
      archive.finalize();
    });
  }

  /**
   * ZIP 파일 정보 가져오기
   */
  async getZipInfo(zipPath: string): Promise<{
    size: number;
    sizeInMB: string;
    filename: string;
    path: string;
  }> {
    const stats = await fs.stat(zipPath);
    return {
      size: stats.size,
      sizeInMB: (stats.size / (1024 * 1024)).toFixed(2) + ' MB',
      filename: path.basename(zipPath),
      path: zipPath
    };
  }

  /**
   * 오래된 ZIP 파일 정리 (24시간 이상)
   */
  async cleanupOldZips(): Promise<number> {
    const now = Date.now();
    const oneDay = 24 * 60 * 60 * 1000;
    let deletedCount = 0;

    const files = await fs.readdir(this.downloadPath);
    
    for (const file of files) {
      if (file.endsWith('.zip')) {
        const filePath = path.join(this.downloadPath, file);
        const stats = await fs.stat(filePath);
        
        if (now - stats.mtimeMs > oneDay) {
          await fs.remove(filePath);
          deletedCount++;
          console.log(`Deleted old ZIP: ${file}`);
        }
      }
    }
    
    return deletedCount;
  }

  /**
   * ZIP 파일 스트림 가져오기
   */
  getZipStream(zipPath: string): fs.ReadStream {
    if (!fs.existsSync(zipPath)) {
      throw new Error(`ZIP file not found: ${zipPath}`);
    }
    return fs.createReadStream(zipPath);
  }
}

export const zipService = new ZipService();