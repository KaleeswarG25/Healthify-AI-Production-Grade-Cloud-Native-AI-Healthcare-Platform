import { reportApi } from './api';


class ReportService {

  async generateUploadUrl(fileName, fileType) {
    try {
      const response = await reportApi.get(
        '/generate-upload-url',
        {
          params: {
            file_name: fileName,
            content_type: fileType,
          },
        }
      );

      return response.data;

    } catch (error) {
      throw (
        error.response?.data?.detail ||
        'Failed to generate upload URL'
      );
    }
  }


  async uploadToS3(uploadUrl, file, onProgress) {
    try {
      const response = await fetch(
        uploadUrl,
        {
          method: 'PUT',
          headers: {
            'Content-Type': file.type,
          },
          body: file,
        }
      );

      if (!response.ok) {
        throw new Error(
          `S3 upload failed with status ${response.status}`
        );
      }

      if (onProgress) {
        onProgress(100);
      }

      return true;

    } catch (error) {
      throw (
        error.message ||
        'File upload failed'
      );
    }
  }


  async saveReport(fileName, fileKey) {
    try {
      const response = await reportApi.post(
        '/save-report',
        {
          file_name: fileName,
          file_key: fileKey,
        }
      );

      return response.data;

    } catch (error) {
      throw (
        error.response?.data?.detail ||
        'Failed to save report'
      );
    }
  }


  async getUserReports() {
    try {
      const response = await reportApi.get(
        '/reports'
      );

      return response.data;

    } catch (error) {
      throw (
        error.response?.data?.detail ||
        'Failed to retrieve reports'
      );
    }
  }


  async deleteReport(reportId) {
    try {
      const response = await reportApi.delete(
        `/reports/${reportId}`
      );

      return response.data;

    } catch (error) {
      throw (
        error.response?.data?.detail ||
        'Failed to delete report'
      );
    }
  }
}


export default new ReportService();