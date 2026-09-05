import { aiApi } from './api';


class AIService {

  async analyzeText(reportText, filename = null) {
    try {
      const response = await aiApi.post(
        '/analyze-text',
        {
          report_text: reportText,
          filename,
        }
      );

      return response.data;

    } catch (error) {
      throw (
        error.response?.data?.detail ||
        'Failed to analyze report'
      );
    }
  }


  async analyzePdf(file) {
    try {
      const formData = new FormData();

      formData.append(
        'file',
        file
      );

      const response = await aiApi.post(
        '/analyze-pdf',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      return response.data;

    } catch (error) {
      throw (
        error.response?.data?.detail ||
        'Failed to analyze PDF'
      );
    }
  }


  async sendMessage(message, analysisId) {
    try {
      const response = await aiApi.post(
        '/chat',
        {
          message,
          analysis_id: analysisId,
        }
      );

      return response.data;

    } catch (error) {
      throw (
        error.response?.data?.detail ||
        'Failed to send message'
      );
    }
  }


  async getAnalysisHistory() {
    try {
      const response = await aiApi.get(
        '/history'
      );

      return response.data;

    } catch (error) {
      throw (
        error.response?.data?.detail ||
        'Failed to retrieve analysis history'
      );
    }
  }


  async getAnalysisById(analysisId) {
    try {
      const response = await aiApi.get(
        `/analysis/${analysisId}`
      );

      return response.data;

    } catch (error) {
      throw (
        error.response?.data?.detail ||
        'Failed to retrieve analysis'
      );
    }
  }


  async deleteAnalysis(analysisId) {
    try {
      const response = await aiApi.delete(
        `/analysis/${analysisId}`
      );

      return response.data;

    } catch (error) {
      throw (
        error.response?.data?.detail ||
        'Failed to delete analysis'
      );
    }
  }
}


export default new AIService();