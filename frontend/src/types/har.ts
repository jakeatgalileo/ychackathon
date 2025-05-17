export interface HarParseRequest {
  har_content: any;
  description: string;
}

export interface HarParseResponse {
  curl_command: string;
  request_details?: {
    index: number;
    method: string;
    url: string;
    headers: Record<string, string>;
    query_params: Record<string, string>;
    post_data?: any;
  } | null;
  matched_entry_index?: number | null;
}

export interface CurlExecuteRequest {
  curl_command: string;
}

export interface CurlExecuteResponse {
  success: boolean;
  response_data?: string;
  response_headers?: Record<string, string>;
  status_code?: number;
  error?: string;
} 